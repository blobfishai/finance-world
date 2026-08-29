#!/usr/bin/env python3
"""ERP MCP server — 1:1 mock of Microsoft's Dynamics 365 ERP MCP server (dynamic).

Tool surface mirrors learn.microsoft.com/dynamics365/.../copilot-mcp exactly:
  data tools (7): data_find_entity_type, data_get_entity_metadata, data_find_entities,
    data_find_entities_sql, data_create_entities, data_update_entities, data_delete_entities
  form tools (13): form_find_menu_item, form_open_menu_item, form_close_form,
    form_find_controls, form_open_or_close_tab, form_filter_form, form_filter_grid,
    form_sort_grid_column, form_select_grid_row, form_click_control, form_open_lookup,
    form_set_control_values, form_save_form
  action tools (2): api_find_actions, api_invoke_action
  (+1 convenience: get_customer_aged_balances, aliasing the "Customer aged balances" page)

Faithful behaviors: role-based rejection of writes (agent role = Finance analyst,
read-only), form tabs closed by default, grid filters support only the "matches" operator,
ISO dates, 25-row pages. All state lives in SQLite (WORLD_DB); form sessions persist in
the erp_form_sessions table. SIMULATION ONLY.
"""
import sys, re, json, json as _json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server, PAGE

S = Server("erp", "Contoso ERP (Dynamics 365 Finance, company USMF). SIMULATION ONLY.")
import os as _os
# Role-based security, like the real server: the task assigns the agent's role
# (task.toml [metadata] agent_role). "analyst" = read-only; "collections" additionally
# unlocks the collections ICustomAPI actions. Raw data/form writes stay denied for both
# (least privilege — write paths are exposed as governed actions, the ICustomAPI pattern).
ROLE_NAME = {"analyst": "Finance analyst (read-only)",
             "collections": "Collections coordinator",
             "accountant": "Staff accountant (GL posting)",
             "controller": "Controller (approver)",
             "treasury": "Treasury analyst (payment runs)"}.get(_os.environ.get("WORLD_ROLE", "analyst"),
                                                           "Finance analyst (read-only)")
ROLE = ROLE_NAME  # used in denial messages
def _role(): return _os.environ.get("WORLD_ROLE", "analyst")

ENTITIES = {
    "Customers":            ("erp_customers", "Customer master (CustomersV3): account, name, group, terms, credit limit, hold status"),
    "Vendors":              ("erp_vendors", "Vendor master (VendorsV2): account, name, group, terms, payment method"),
    "CustomerTransactions": ("erp_cust_trans", "Posted AR subledger: invoices/payments with due dates, settled amount, open remainder = amount-settled where closed=0"),
    "VendorTransactions":   ("erp_vend_trans", "Posted AP subledger: vendor invoices/payments, due dates, settled, closed"),
    "CustomerSettlements":  ("erp_settlements", "Settlement links between payments and invoices incl. cash discount taken"),
    "PaymentTerms":         ("erp_payment_terms", "Payment terms codes (COD, Net15, Net30, ...)"),
    "MainAccounts":         ("erp_main_accounts", "Chart of accounts: code, name, account_type, blocked, reconcilable"),
    "FiscalPeriods":        ("erp_fiscal_periods", "Fiscal periods and their status (open | on_hold | closed)"),
    "LedgerJournals":       ("erp_ledger_journals", "General journal headers: totals, period, state (draft|posted), reversal links"),
    "LedgerJournalLines":   ("erp_ledger_journal_lines", "General journal lines: account, debit, credit, dimension"),
    "ApprovalPolicies":     ("erp_approval_policies", "Delegation-of-authority rules: doc_type, threshold_amount, approving_role"),
    "ApprovalRequests":     ("erp_approval_requests", "Approval inbox: doc_type, doc_id, amount, status, decision"),
    "BankAccounts":         ("erp_bank_accounts", "Bank accounts with available balance as of a timestamp and overdraft limit"),
    "PaymentRuns":          ("erp_payment_runs", "Payment run headers: pay date, cash available, eligible net, state"),
    "PaymentRunLines":      ("erp_payment_run_lines", "Payment run lines: invoice, net, disposition (paid|rejected), reason_code"),
    "ExchangeRates":        ("erp_fx_rates", "FX rates by from/to currency and date"),
    "DeductionReasons":     ("erp_deduction_reasons", "Deduction/short-pay reason codes: validity, owning team, disposition"),
    "WithholdingTax":       ("erp_withholding_tax", "Withholding-tax categories: rate, threshold, statutory reference"),
    "VendorTaxProfile":     ("erp_vendor_tax_profile", "Per-vendor tax category, exemption certificate type, whether it is on file and when it expires"),
    "CashDiscounts":        ("erp_cash_disc", "Cash discount codes: percent, day window, next-code chain"),
    "CollectionLetters":    ("erp_collection_letters", "Collection letter journal per customer: letter_code 1..4/Collection, date, status, fee"),
    "AgedBalancesSnapshot": ("erp_aging_snapshot", "Batch customer aging snapshot (run_id, as_of, buckets). May lag live transactions."),
    "Companies":            ("erp_companies", "Legal entities"),
    "PurchaseOrders":       ("erp_purch_orders", "Purchase order lines: vendor, item, qty ordered, unit price, status"),
    "ProductReceipts":      ("erp_product_receipts", "Product receipt lines against purchase orders: qty received, receipt date"),
    "SalesOrders":          ("erp_sales_orders", "Sales orders: status, hold code (e.g. 'Do not process'), responsible worker, amount"),
    "Activities":           ("erp_activities", "Collections activities/tasks per customer: type, purpose, dates, closed flag, responsible"),
    "CollectionPools":      ("erp_collection_pools", "Collections pool definitions"),
    "CustomerPools":        ("erp_customer_pool", "Customer-to-collections-pool assignments"),
    "MethodsOfPayment":     ("erp_methods_of_payment", "Methods of payment and their payment accounts (customer and vendor sides)"),
    "FinanceCases":         ("erp_finance_cases", "Task-scoped finance work items: immutable case identity, workflow, subject, status, decision, evidence references, rationale, owner, and timestamps"),
}

def _unknown(entity):
    return {"error": f"unknown entity type '{entity}'",
            "available_entities": sorted(ENTITIES),
            "hint": "use data_find_entity_type to discover entity types"}

def _deny(operation, obj):
    return {"error": f"Access denied: role '{ROLE}' does not have the privilege to {operation} "
                     f"'{obj}'. The system rejects calls to actions or objects the user role "
                     f"cannot access.", "role": ROLE}

# ============================== data tools (7) ==============================

@S.tool("data_find_entity_type", "Find OData entity types matching a natural-language query. Returns multiple top hits; you decide which matches.",
        {"query": {"type": "string", "description": "e.g. 'customer invoices', 'payment terms'"}}, ["query"])
def data_find_entity_type(query):
    q = query.lower()
    scored = [{"entity": name, "description": desc}
              for name, (_t, desc) in ENTITIES.items()
              if any(w in (name + " " + desc).lower() for w in re.findall(r"[a-z]+", q))]
    return {"matches": scored or [{"entity": n, "description": d} for n, (_t, d) in ENTITIES.items()]}

@S.tool("data_get_entity_metadata", "Get metadata (field list) for an entity. Needed before find/create/update/delete entity calls.",
        {"entity": {"type": "string"}}, ["entity"])
def data_get_entity_metadata(entity):
    if entity not in ENTITIES: return _unknown(entity)
    table, desc = ENTITIES[entity]
    cx = S.db()
    fields = [r["name"] for r in cx.execute(f"PRAGMA table_info({table})")]
    return {"entity": entity, "description": desc, "fields": fields,
            "note": "open remainder on transactions = amount - settled (closed=0 only); dates are ISO (yyyy-mm-dd)"}

@S.tool("data_find_entities", "Find/read data records for one entity with equality/contains filters. Paged (25 rows).",
        {"entity": {"type": "string"},
         "filters": {"type": "object", "description": "field -> value; strings match case-insensitive substring, numbers match exactly"},
         "page": {"type": "integer"}}, ["entity"])
def data_find_entities(entity, filters=None, page=1):
    if entity not in ENTITIES: return _unknown(entity)
    table, _ = ENTITIES[entity]
    cx = S.db()
    cols = {r["name"] for r in cx.execute(f"PRAGMA table_info({table})")}
    where, args = [], []
    for k, v in (filters or {}).items():
        if k not in cols: return {"error": f"unknown field {k}", "fields": sorted(cols)}
        if isinstance(v, str):
            where.append(f"LOWER({k}) LIKE ?"); args.append(f"%{v.lower()}%")
        else:
            where.append(f"{k} = ?"); args.append(v)
    sql = f"SELECT * FROM {table}" + (" WHERE " + " AND ".join(where) if where else "")
    r = S.rows(cx, sql, args, page)
    out = {"@odata.context": f"$metadata#{entity}", "value": r["rows"], "@odata.count": r["total_rows"]}
    if r["has_more"]:
        out["@odata.nextLink"] = f"data_find_entities?entity={entity}&page={r['page'] + 1}"
    return out

@S.tool("data_find_entities_sql", "Find/read records using SQL (read-only single SELECT over erp_* tables; LIMIT 200 enforced). Replaces OData find in 10.0.48+.",
        {"sql": {"type": "string"}}, ["sql"])
def data_find_entities_sql(sql):
    s = sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", s) or ";" in s:
        raise ValueError("single SELECT statement only")
    for tbl in re.findall(r"(?i)\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", s):
        if not tbl.lower().startswith("erp_"):
            raise ValueError(f"table {tbl} is outside the ERP (only erp_* tables exist here)")
    cx = S.db()
    rows = [dict(r) for r in cx.execute(f"SELECT * FROM ({s}) LIMIT 200").fetchall()]
    return {"@odata.context": "$metadata#sql", "value": rows, "@odata.count": len(rows), "truncated_at": 200}

@S.tool("data_create_entities", "Create data records using OData (no deep inserts). Subject to role security.",
        {"entity": {"type": "string"}, "records": {"type": "array"}}, ["entity", "records"])
def data_create_entities(entity, records):
    if entity not in ENTITIES: return _unknown(entity)
    return _deny("Create records in entity", entity)

@S.tool("data_update_entities", "Update data records using OData. Subject to role security.",
        {"entity": {"type": "string"}, "updates": {"type": "array"}}, ["entity", "updates"])
def data_update_entities(entity, updates):
    if entity not in ENTITIES: return _unknown(entity)
    return _deny("Update records in entity", entity)

@S.tool("data_delete_entities", "Delete data records using OData. Subject to role security.",
        {"entity": {"type": "string"}, "keys": {"type": "array"}}, ["entity", "keys"])
def data_delete_entities(entity, keys):
    if entity not in ENTITIES: return _unknown(entity)
    return _deny("Delete records in entity", entity)

# ============================== form runtime =================================
# View-model semantics per the real server: forms open with tabs CLOSED, grids page at 25,
# grid filters support only the "matches" operator, runtime-calculated fields appear on
# the selected row. Form session state persists in erp_form_sessions (SQL-backed).

FORMS = {
    "CustTable": {"menu_item": "All customers", "title": "Customers", "table": "erp_customers",
                  "grid": ["account", "name", "customer_group", "currency", "payment_term", "credit_max", "on_hold"],
                  "tabs": {"General": ["account", "name", "customer_group", "currency", "credit_rating"],
                           "Credit and collections": ["credit_max", "on_hold", "cash_disc_code"],
                           "Contact information": ["contact_name", "contact_email", "phone", "city", "state"],
                           "Payment defaults": ["payment_term", "cash_disc_code"]},
                  "actions": ["Collections", "OpenTransactions", "AgedBalances"]},
    "VendTable": {"menu_item": "All vendors", "title": "Vendors", "table": "erp_vendors",
                  "grid": ["account", "name", "vendor_group", "currency", "payment_term", "payment_method", "on_hold"],
                  "tabs": {"General": ["account", "name", "vendor_group", "currency"],
                           "Payment": ["payment_term", "cash_disc_code", "payment_method"],
                           "Contact information": ["contact_name", "contact_email", "phone", "city", "state"]},
                  "actions": ["OpenTransactions"]},
    "CustTrans": {"menu_item": "Customer transactions", "title": "Customer transactions", "table": "erp_cust_trans",
                  "grid": ["account", "invoice", "txn_type", "trans_date", "due_date", "currency", "amount", "settled", "closed"],
                  "tabs": {"General": ["voucher", "description", "cash_disc_code"],
                           "Settlement": ["settled", "closed"]},
                  "actions": ["SettleTransactions"], "calc": {"open_amount": "amount - settled"}},
    "VendTrans": {"menu_item": "Vendor transactions", "title": "Vendor transactions", "table": "erp_vend_trans",
                  "grid": ["account", "invoice", "txn_type", "trans_date", "due_date", "currency", "amount", "settled", "closed"],
                  "tabs": {"General": ["voucher", "description", "cash_disc_code"],
                           "Settlement": ["settled", "closed"]},
                  "actions": ["SettleTransactions"], "calc": {"open_amount": "amount - settled"}},
    "CustCollectionLetterJour": {"menu_item": "Collection letter journal", "title": "Collection letter journal",
                  "table": "erp_collection_letters",
                  "grid": ["account", "letter_code", "letter_date", "status", "fee"],
                  "tabs": {"General": ["note"]}, "actions": []},
    "CustAgedBalances": {"menu_item": "Customer aged balances", "title": "Customer aged balances (batch snapshot)",
                  "table": "erp_aging_snapshot",
                  "grid": ["account", "name", "as_of", "not_due", "b1_30", "b31_60", "b61_90", "b90_plus", "total_due"],
                  "tabs": {"General": ["run_id"]}, "actions": []},
    "PurchTable": {"menu_item": "All purchase orders", "title": "Purchase orders", "table": "erp_purch_orders",
                  "grid": ["po_number", "line", "vendor", "item", "qty_ordered", "unit_price", "status"],
                  "tabs": {"General": ["description", "order_date"]}, "actions": []},
    "PaymTerm": {"menu_item": "Payment terms", "title": "Terms of payment", "table": "erp_payment_terms",
                  "grid": ["code", "days", "description"], "tabs": {}, "actions": []},
    "CashDisc": {"menu_item": "Cash discounts", "title": "Cash discounts", "table": "erp_cash_disc",
                  "grid": ["code", "percent", "days", "next_code", "description"], "tabs": {}, "actions": []},
}

def _fs_get(cx, form_id):
    r = cx.execute("SELECT * FROM erp_form_sessions WHERE form_id=?", (form_id,)).fetchone()
    if not r: return None
    return {"form_id": r["form_id"], "form": r["form"], **json.loads(r["state"])}

def _fs_put(cx, form_id, form, state):
    cx.execute("INSERT OR REPLACE INTO erp_form_sessions(form_id, form, state) VALUES(?,?,?)",
               (form_id, form, json.dumps(state)))
    cx.commit()

def _grid_rows(cx, st):
    f = FORMS[st["form"]]
    sql, args = f"SELECT rowid AS _row, * FROM {f['table']}", []
    clauses = []
    for col, val in st.get("filters", {}).items():
        clauses.append(f"LOWER(CAST({col} AS TEXT)) LIKE ?"); args.append(f"%{str(val).lower()}%")
    if st.get("quick_filter"):
        like = f"%{st['quick_filter'].lower()}%"
        qf = " OR ".join(f"LOWER(CAST({c} AS TEXT)) LIKE ?" for c in f["grid"])
        clauses.append(f"({qf})"); args += [like] * len(f["grid"])
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    if st.get("sort"): sql += f" ORDER BY {st['sort']['column']} {'DESC' if st['sort'].get('desc') else 'ASC'}"
    rows = [dict(r) for r in cx.execute(sql, args).fetchall()]
    return rows

def _view_model(cx, st):
    f = FORMS[st["form"]]
    rows = _grid_rows(cx, st)
    page = st.get("page", 1)
    chunk = [{k: r[k] for k in ["_row"] + f["grid"] if k in r} for r in rows[(page-1)*PAGE: page*PAGE]]
    return {"form_id": st["form_id"], "form": st["form"], "title": f["title"],
            "grid": {"columns": f["grid"], "rows": chunk, "page": page, "page_size": PAGE,
                     "total_rows": len(rows), "filter_operator": "matches (only)"},
            "tabs": {t: ("open" if t in st.get("open_tabs", []) else "closed") for t in f["tabs"]},
            "actions": f["actions"] + ["Save", "Close"],
            "selected_row": st.get("selected"),
            "note": "form tabs are closed by default; open a tab to see its fields"}

@S.tool("form_find_menu_item", "Find a menu item (application page) by search term.",
        {"query": {"type": "string"}}, ["query"])
def form_find_menu_item(query):
    q = query.lower()
    hits = [{"form": name, "menu_item": f["menu_item"], "title": f["title"]}
            for name, f in FORMS.items()
            if q in (name + " " + f["menu_item"] + " " + f["title"]).lower()
            or any(w in (name + " " + f["menu_item"] + " " + f["title"]).lower() for w in q.split())]
    return {"menu_items": hits or [{"form": n, "menu_item": f["menu_item"], "title": f["title"]} for n, f in FORMS.items()]}

@S.tool("form_open_menu_item", "Open a menu item (form). Returns the form view model (grid page 1; tabs closed by default).",
        {"menu_item": {"type": "string", "description": "menu item name or form name"}}, ["menu_item"])
def form_open_menu_item(menu_item):
    name = next((n for n, f in FORMS.items()
                 if menu_item.lower() in (n.lower(), f["menu_item"].lower(), f["title"].lower())), None)
    if not name:
        return {"error": f"no menu item '{menu_item}'",
                "hint": "use form_find_menu_item", "available": [f["menu_item"] for f in FORMS.values()]}
    cx = S.db()
    n = cx.execute("SELECT COUNT(*) FROM erp_form_sessions").fetchone()[0]
    form_id = f"fh-{n+1}"
    st = {"form_id": form_id, "form": name, "page": 1, "filters": {}, "open_tabs": [], "selected": None}
    _fs_put(cx, form_id, name, st)
    return _view_model(cx, st)

@S.tool("form_close_form", "Close an open form.", {"form_id": {"type": "string"}}, ["form_id"])
def form_close_form(form_id):
    cx = S.db()
    if not _fs_get(cx, form_id): return {"error": f"no open form '{form_id}'"}
    cx.execute("DELETE FROM erp_form_sessions WHERE form_id=?", (form_id,)); cx.commit()
    return {"closed": form_id}

@S.tool("form_find_controls", "Find controls on an open form. One search term per call.",
        {"form_id": {"type": "string"}, "search": {"type": "string"}}, ["form_id", "search"])
def form_find_controls(form_id, search):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    f = FORMS[st["form"]]; q = search.lower()
    hits = []
    for tab, fields in f["tabs"].items():
        hits += [{"control": fld, "tab": tab, "tab_state": "open" if tab in st["open_tabs"] else "closed"}
                 for fld in fields if q in fld.lower()]
    hits += [{"control": c, "type": "grid_column"} for c in f["grid"] if q in c.lower()]
    hits += [{"control": a, "type": "action"} for a in f["actions"] if q in a.lower()]
    return {"matches": hits or {"note": f"no control matching '{search}'", "tabs": list(f["tabs"])}}

@S.tool("form_open_or_close_tab", "Open or close a tab on the form. Opening reveals the tab's fields for the selected row.",
        {"form_id": {"type": "string"}, "tab": {"type": "string"}, "open": {"type": "boolean"}}, ["form_id", "tab"])
def form_open_or_close_tab(form_id, tab, open=True):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    f = FORMS[st["form"]]
    if tab not in f["tabs"]: return {"error": f"no tab '{tab}'", "tabs": list(f["tabs"])}
    tabs = set(st["open_tabs"]); (tabs.add(tab) if open else tabs.discard(tab))
    st["open_tabs"] = sorted(tabs); _fs_put(cx, form_id, st["form"], st)
    out = _view_model(cx, st)
    if open and st.get("selected") is not None:
        rows = _grid_rows(cx, st)
        row = next((r for r in rows if r["_row"] == st["selected"]), None)
        if row: out["tab_fields"] = {tab: {k: row.get(k) for k in f["tabs"][tab]}}
    return out

@S.tool("form_filter_form", "Apply a quick filter across the form's grid columns.",
        {"form_id": {"type": "string"}, "value": {"type": "string"}}, ["form_id", "value"])
def form_filter_form(form_id, value):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    st["quick_filter"], st["page"] = value, 1
    _fs_put(cx, form_id, st["form"], st)
    return _view_model(cx, st)

@S.tool("form_filter_grid", "Filter the grid on one column. Only the 'matches' (substring) operator is supported.",
        {"form_id": {"type": "string"}, "column": {"type": "string"}, "value": {"type": "string"},
         "operator": {"type": "string", "description": "only 'matches' is supported"}}, ["form_id", "column", "value"])
def form_filter_grid(form_id, column, value, operator="matches"):
    if operator not in (None, "matches"):
        return {"error": f"operator '{operator}' is not supported; grid filters support only 'matches'"}
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    f = FORMS[st["form"]]
    if column not in f["grid"]: return {"error": f"no grid column '{column}'", "columns": f["grid"]}
    st["filters"][column] = value; st["page"] = 1
    _fs_put(cx, form_id, st["form"], st)
    return _view_model(cx, st)

@S.tool("form_sort_grid_column", "Sort the grid by a column.",
        {"form_id": {"type": "string"}, "column": {"type": "string"},
         "direction": {"type": "string", "description": "asc|desc"}}, ["form_id", "column"])
def form_sort_grid_column(form_id, column, direction="asc"):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    f = FORMS[st["form"]]
    if column not in f["grid"]: return {"error": f"no grid column '{column}'", "columns": f["grid"]}
    st["sort"] = {"column": column, "desc": direction == "desc"}; st["page"] = 1
    _fs_put(cx, form_id, st["form"], st)
    return _view_model(cx, st)

@S.tool("form_select_grid_row", "Select a grid row by its _row id. Returns all fields incl. runtime-calculated values.",
        {"form_id": {"type": "string"}, "row": {"type": "integer"}}, ["form_id", "row"])
def form_select_grid_row(form_id, row):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    f = FORMS[st["form"]]
    rows = _grid_rows(cx, st)
    rec = next((r for r in rows if r["_row"] == row), None)
    if not rec: return {"error": f"no row {row} in current grid"}
    st["selected"] = row; _fs_put(cx, form_id, st["form"], st)
    for calc, expr in f.get("calc", {}).items():
        rec[calc] = round(cx.execute(f"SELECT {expr} FROM {f['table']} WHERE rowid=?", (row,)).fetchone()[0], 2)
    return {"selected_row": rec, "open_tabs": st["open_tabs"],
            "note": "closed-tab fields require form_open_or_close_tab"}

@S.tool("form_click_control", "Click a control/action on the form (e.g. Collections, OpenTransactions, AgedBalances).",
        {"form_id": {"type": "string"}, "control": {"type": "string"}}, ["form_id", "control"])
def form_click_control(form_id, control):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    f = FORMS[st["form"]]
    if control == "Close": return form_close_form(form_id)
    if control == "Save": return _deny("execute 'Save' on form", f["title"])
    if control == "SettleTransactions": return _deny("execute action 'Settle transactions' on form", f["title"])
    if control not in f["actions"]:
        return {"error": f"no action '{control}' on this form", "actions": f["actions"] + ["Save", "Close"]}
    if st.get("selected") is None:
        return {"error": "select a grid row first (form_select_grid_row)"}
    rows = _grid_rows(cx, st)
    rec = next((r for r in rows if r["_row"] == st["selected"]), None)
    acct = rec.get("account")
    if control == "AgedBalances" or control == "Collections":
        out = get_customer_aged_balances(customer_account=acct)
        if control == "Collections":
            letters = [dict(r) for r in cx.execute(
                "SELECT letter_code, letter_date, status, fee, note FROM erp_collection_letters WHERE account=? ORDER BY letter_date", (acct,))]
            out["collection_letters"] = letters
        return out
    if control == "OpenTransactions":
        table = "erp_cust_trans" if st["form"] == "CustTable" else "erp_vend_trans"
        txns = [dict(r) for r in cx.execute(
            f"SELECT invoice, txn_type, trans_date, due_date, currency, amount, settled, ROUND(amount-settled,2) AS open_amount, closed FROM {table} WHERE account=? ORDER BY trans_date", (acct,))]
        return {"account": acct, "transactions": txns[:50], "total_rows": len(txns)}

@S.tool("form_open_lookup", "Open a lookup control (e.g. payment_term, cash_disc_code) and list its valid values.",
        {"form_id": {"type": "string"}, "control": {"type": "string"}}, ["form_id", "control"])
def form_open_lookup(form_id, control):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    if "payment_term" in control:
        return {"lookup": control, "values": [dict(r) for r in cx.execute("SELECT * FROM erp_payment_terms")]}
    if "cash_disc" in control:
        return {"lookup": control, "values": [dict(r) for r in cx.execute("SELECT * FROM erp_cash_disc")]}
    if "customer_group" in control:
        return {"lookup": control, "values": [dict(r) for r in cx.execute("SELECT DISTINCT customer_group FROM erp_customers ORDER BY 1")]}
    return {"error": f"control '{control}' has no lookup", "lookups": ["payment_term", "cash_disc_code", "customer_group"]}

@S.tool("form_set_control_values", "Set values on form controls (not lookup controls). Subject to role security.",
        {"form_id": {"type": "string"}, "values": {"type": "object"}}, ["form_id", "values"])
def form_set_control_values(form_id, values):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    return _deny("set control values on form", FORMS[st["form"]]["title"])

@S.tool("form_save_form", "Save the form. Subject to role security.", {"form_id": {"type": "string"}}, ["form_id"])
def form_save_form(form_id):
    cx = S.db(); st = _fs_get(cx, form_id)
    if not st: return {"error": f"no open form '{form_id}'"}
    return _deny("execute 'Save' on form", FORMS[st["form"]]["title"])

# ============================== action tools (2) =============================
# Real server: custom classes exposed via ICustomAPI, environment-specific. These are the
# AI-tool actions "Contoso's developers" published in this environment.

ACTIONS = {
    "ContosoCustAgedBalancesLive": {"description": "Compute live customer aged balances as of a date (params: as_of?, customer_account?, customer_group?)"},
    "ContosoCashDiscountForecast": {"description": "List open vendor invoices whose cash-discount window is still open as of a date, with capturable amounts (params: as_of?, vendor_account?)"},
    "ContosoCollectionStatus": {"description": "Current dunning position for a customer: highest letter level, letters, open balance (params: customer_account)"},
    "ContosoIssueCollectionLetter": {"description": "WRITE (Collections role): post the next collection letter for a customer per the dunning ladder (params: customer_account). Validates sequence, 14-day spacing, and past-due status; posts the letter with its fee.", "requires_role": "collections"},
    "ContosoSetCreditHold": {"description": "WRITE (Collections role): set a customer's credit hold status (params: customer_account, on_hold 'Yes'|'Open', reason).", "requires_role": "collections"},
    # --- write-and-approve surface (docs/HARD-LAYER-DESIGN.md M1/M2/M4; spec in
    #     research/write-surface-spec.md). Two-phase: a propose action returns a
    #     confirm_token + the exact effect; the committing action requires that token.
    "ContosoJournalPropose": {"description": "WRITE (Accountant role): validate and stage a general journal (params: description, posting_date, lines[{account_code, debit?, credit?, description?, dimension_dept?}], voucher_type?). Enforces debit=credit, open period, and non-blocked accounts. Returns journal_id, whether delegation-of-authority approval is required, and a confirm_token for ContosoJournalPost.", "requires_role": "accountant"},
    "ContosoJournalPost": {"description": "WRITE (Accountant role): post a staged journal (params: journal_id, confirm_token). Refuses if the period is closed/on_hold, if the journal is unbalanced, or if DoA approval is required and not yet granted.", "requires_role": "accountant"},
    "ContosoApprovalList": {"description": "Read the delegation-of-authority approval inbox (params: status? 'pending'|'approved'|'rejected', doc_type?).", "requires_role": "controller"},
    "ContosoApprovalDecide": {"description": "WRITE (Controller role): approve or reject a pending request (params: request_id, decision 'approve'|'reject', reason). A rejection requires a reason.", "requires_role": "controller"},
    "ContosoPaymentRunPropose": {"description": "WRITE (Treasury role): build a payment proposal for a pay date against a bank account's available cash (params: pay_date, bank_account, vendor_account?). Returns every eligible obligation ranked, the cash available, and the shortfall if the eligible net exceeds it, plus a confirm_token.", "requires_role": "treasury"},
    "ContosoPaymentRunCommit": {"description": "WRITE (Treasury role): commit a proposed run (params: run_id, confirm_token, paid[invoice...], rejected[{invoice, reason_code, reason}]). Every eligible obligation must appear in exactly one of paid or rejected, and the paid net must not exceed available cash — a short run is committed by naming what goes unpaid, not by dropping it.", "requires_role": "treasury"},
    "ContosoFinanceCaseDecide": {"description": "WRITE: decide one open FinanceCases work item after source review (params: case_id, decision_code, evidence_refs[immutable source ids], rationale). Updates only that case and writes the Dynamics audit trail."},
}

# Reason codes for the rejected half of a payment run. Vocabulary follows ERPNext's
# _partition_payable_invoices plus the D365 hold/discount cases (write-surface-spec.md §4).
REJECT_CODES = {"insufficient_cash", "vendor_on_hold", "awaiting_approval",
                "discount_window_expired", "disputed", "missing_bank_details", "not_yet_due",
                # ~1.5% of disbursements leak as duplicate payments (research/domain-workflows.md
                # chaos pattern 8: "INV-5521" vs "5521-OPS"), so the partition needs a code for it.
                "duplicate"}

PROPOSAL_MAX_LINES = 60   # a payment proposal a human would actually review

LETTER_FEES = {"1": 0.0, "2": 25.0, "3": 40.0}

def _issue_collection_letter(cx, acct):
    cust = cx.execute("SELECT * FROM erp_customers WHERE account=?", (acct,)).fetchone()
    if not cust: return {"error": f"no customer '{acct}'"}
    past_due = cx.execute("""SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans
                             WHERE account=? AND txn_type='Invoice' AND closed=0 AND due_date < ?""",
                          (acct, S.today)).fetchone()[0]
    if past_due <= 0:
        return {"error": f"validation: customer {acct} has no past-due balance; a collection letter cannot be posted"}
    last = cx.execute("SELECT letter_code, letter_date FROM erp_collection_letters WHERE account=? ORDER BY letter_date DESC LIMIT 1", (acct,)).fetchone()
    next_code = str(int(last["letter_code"]) + 1) if last and last["letter_code"].isdigit() else "1"
    if next_code not in LETTER_FEES:
        return {"error": f"validation: customer {acct} is already at the final letter level; escalate to demand/agency, not another letter"}
    if last:
        gap = (dt.date.fromisoformat(S.today) - dt.date.fromisoformat(last["letter_date"])).days
        if gap < 14:
            return {"error": f"validation: only {gap} days since letter {last['letter_code']} ({last['letter_date']}); the runbook requires >=14 days between letters"}
    fee = LETTER_FEES[next_code]
    cx.execute("INSERT INTO erp_collection_letters(dataareaid, account, letter_code, letter_date, status, fee, note) VALUES(?,?,?,?,?,?,?)",
               ("USMF", acct, next_code, S.today, "Sent", fee,
                f"Posted via ContosoIssueCollectionLetter; past-due {past_due} as of {S.today}"))
    cx.commit()
    return {"posted": True, "customer_account": acct, "letter_code": next_code,
            "letter_date": S.today, "fee": fee, "past_due_at_issuance": past_due}

def _set_credit_hold(cx, acct, on_hold, reason):
    if on_hold not in ("Yes", "Open"):
        return {"error": "validation: on_hold must be 'Yes' (held) or 'Open' (released)"}
    cust = cx.execute("SELECT * FROM erp_customers WHERE account=?", (acct,)).fetchone()
    if not cust: return {"error": f"no customer '{acct}'"}
    cx.execute("UPDATE erp_customers SET on_hold=? WHERE account=?", (on_hold, acct))
    cx.commit()
    return {"updated": True, "customer_account": acct, "on_hold": on_hold, "reason": reason or ""}

# ---------------------- write-and-approve implementation ---------------------
# Confirm tokens are DETERMINISTIC by design. The oracle replays solution/walk.json with
# literal arguments (sim/oracle.py), so a random token would be unexpressible in a gold walk
# and every write task would fail spuriously (research/write-surface-spec.md §10.1). Minting
# from (action, target, ordinal) keeps the two-phase gate honest — the agent still cannot
# commit without first calling propose and reading the token out of its result — while
# staying replayable.
def _mint_token(cx, action, target_id, preview):
    seq = cx.execute("SELECT COUNT(*) FROM erp_confirm_tokens WHERE target_id=?", (target_id,)).fetchone()[0] + 1
    token = f"CONF-{target_id}-{seq}"
    cx.execute("INSERT INTO erp_confirm_tokens(token,seq,action,actor,role,target_id,args_hash,"
               "effect_preview,minted_at) VALUES(?,?,?,?,?,?,?,?,?)",
               (token, seq, action, _role(), _role(), target_id, "", _json.dumps(preview)[:2000], S.now))
    cx.commit()
    return token

def _consume_token(cx, action, target_id, token):
    if not token:
        return {"error": f"confirm_token is required: call the matching propose action first and pass the "
                         f"confirm_token it returns. {action} will not run unconfirmed."}
    row = cx.execute("SELECT * FROM erp_confirm_tokens WHERE token=?", (token,)).fetchone()
    if not row or row["target_id"] != target_id:
        return {"error": f"confirm_token '{token}' is not valid for {target_id}"}
    if row["consumed_at"]:
        return {"error": f"confirm_token '{token}' was already used at {row['consumed_at']}; "
                         f"re-propose to obtain a fresh one (no blind retries)"}
    cx.execute("UPDATE erp_confirm_tokens SET consumed_at=? WHERE token=?", (S.now, token))
    return None

def _audit(cx, entity_type, entity_id, action, before=None, after=None):
    cx.execute("INSERT INTO erp_audit_trail(entity_type,entity_id,action,actor,role,at,before_json,after_json)"
               " VALUES(?,?,?,?,?,?,?,?)",
               (entity_type, entity_id, action, _role(), _role(), S.now,
                _json.dumps(before or {})[:2000], _json.dumps(after or {})[:2000]))

def _period_for(cx, date_str):
    return cx.execute("SELECT * FROM erp_fiscal_periods WHERE ? BETWEEN period_start AND period_end",
                      (date_str,)).fetchone()

def _doa_required(cx, doc_type, amount):
    """Lowest active threshold this amount exceeds, for the current role's documents."""
    rows = cx.execute("SELECT * FROM erp_approval_policies WHERE doc_type=? AND active=1 "
                      "ORDER BY threshold_amount", (doc_type,)).fetchall()
    hit = [r for r in rows if amount > (r["threshold_amount"] or 0)]
    return hit[-1] if hit else None

def _journal_propose(cx, p):
    lines = p.get("lines") or []
    if not lines: return {"error": "parameter lines is required (at least two: one debit, one credit)"}
    posting_date = p.get("posting_date") or S.today
    per = _period_for(cx, posting_date)
    if not per: return {"error": f"no fiscal period covers posting_date {posting_date}"}
    if per["status"] != "open":
        return {"error": f"validation: fiscal period {per['period_id']} is '{per['status']}'; "
                         f"a journal cannot be staged into it. Open periods only."}
    tot_d = tot_c = 0.0
    for i, ln in enumerate(lines, 1):
        acct = cx.execute("SELECT * FROM erp_main_accounts WHERE account_code=?", (str(ln.get("account_code")),)).fetchone()
        if not acct:
            return {"error": f"line {i}: no main account '{ln.get('account_code')}'",
                    "hint": "query the MainAccounts entity for the chart of accounts"}
        if acct["blocked"]:
            return {"error": f"line {i}: account {acct['account_code']} ({acct['name']}) is blocked for posting"}
        d, c = float(ln.get("debit") or 0), float(ln.get("credit") or 0)
        if d and c: return {"error": f"line {i}: a line carries either a debit or a credit, not both"}
        if not d and not c: return {"error": f"line {i}: needs a debit or a credit amount"}
        tot_d += d; tot_c += c
    diff = round(tot_d - tot_c, 2)
    if abs(diff) > 0.005:
        # ERPNext's wording: "Total Debit must be equal to Total Credit. The difference is {0}"
        return {"error": f"validation: total debit must equal total credit. The difference is {diff}",
                "total_debit": round(tot_d, 2), "total_credit": round(tot_c, 2)}
    jid = f"GJ-{cx.execute('SELECT COUNT(*) FROM erp_ledger_journals').fetchone()[0] + 1:05d}"
    cx.execute("INSERT INTO erp_ledger_journals(journal_id,dataareaid,voucher,voucher_type,description,"
               "user_remark,posting_date,period_id,currency,total_debit,total_credit,difference,state,"
               "created_by,created_at,source_doc_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,'draft',?,?,?)",
               (jid, "USMF", jid, p.get("voucher_type") or "Journal Entry", p.get("description") or "",
                p.get("user_remark") or "", posting_date, per["period_id"], "USD",
                round(tot_d, 2), round(tot_c, 2), 0.0, _role(), S.now, p.get("source_doc_id")))
    for i, ln in enumerate(lines, 1):
        cx.execute("INSERT INTO erp_ledger_journal_lines(journal_id,line,account_code,description,debit,"
                   "credit,currency,fx_rate,party_type,party,dimension_dept) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (jid, i, str(ln.get("account_code")), ln.get("description") or "",
                    round(float(ln.get("debit") or 0), 2), round(float(ln.get("credit") or 0), 2),
                    "USD", 1.0, ln.get("party_type"), ln.get("party"), ln.get("dimension_dept")))
    pol = _doa_required(cx, "Journal Entry", round(tot_d, 2))
    req_id = None
    if pol:
        req_id = f"APR-{cx.execute('SELECT COUNT(*) FROM erp_approval_requests').fetchone()[0] + 1:05d}"
        cx.execute("INSERT INTO erp_approval_requests(request_id,dataareaid,doc_type,doc_id,amount,currency,"
                   "submitted_by,submitted_at,note,policy_id,required_role,status) "
                   "VALUES(?,?,?,?,?,?,?,?,?,?,?,'pending')",
                   (req_id, "USMF", "Journal Entry", jid, round(tot_d, 2), "USD", _role(), S.now,
                    p.get("description") or "", pol["policy_id"], pol["approving_role"]))
    _audit(cx, "LedgerJournal", jid, "propose", after={"total_debit": round(tot_d, 2)})
    cx.commit()
    preview = {"journal_id": jid, "total_debit": round(tot_d, 2), "posting_date": posting_date,
               "period_id": per["period_id"], "lines": len(lines)}
    return {"staged": True, "journal_id": jid, "state": "draft", "total_debit": round(tot_d, 2),
            "total_credit": round(tot_c, 2), "period_id": per["period_id"],
            "approval_required": bool(pol),
            "approval_request_id": req_id,
            "approval_note": (f"exceeds the {pol['threshold_amount']:.2f} {pol['doc_type']} threshold "
                              f"({pol['policy_id']}); {pol['approving_role']} must approve before posting"
                              if pol else "below all delegation-of-authority thresholds"),
            "confirm_token": _mint_token(cx, "ContosoJournalPost", jid, preview),
            "effect_preview": preview}

def _journal_post(cx, p):
    jid = p.get("journal_id")
    if not jid: return {"error": "parameter journal_id is required"}
    j = cx.execute("SELECT * FROM erp_ledger_journals WHERE journal_id=?", (jid,)).fetchone()
    if not j: return {"error": f"no journal '{jid}'"}
    if j["state"] == "posted": return {"error": f"journal {jid} is already posted"}
    if not p.get("confirm_token"):
        return {"error": "confirm_token is required: call ContosoJournalPropose first and pass the "
                         "confirm_token it returns. ContosoJournalPost will not run unconfirmed."}
    per = cx.execute("SELECT * FROM erp_fiscal_periods WHERE period_id=?", (j["period_id"],)).fetchone()
    if per and per["status"] != "open":
        return {"error": f"validation: fiscal period {per['period_id']} is '{per['status']}'; cannot post"}
    if abs(round(j["total_debit"] - j["total_credit"], 2)) > 0.005:
        return {"error": "validation: journal is out of balance"}
    req = cx.execute("SELECT * FROM erp_approval_requests WHERE doc_type='Journal Entry' AND doc_id=?"
                     " ORDER BY submitted_at DESC LIMIT 1", (jid,)).fetchone()
    if req and req["status"] != "approved":
        return {"error": f"validation: journal {jid} requires {req['required_role']} approval "
                         f"(request {req['request_id']} is '{req['status']}'); it cannot be posted yet"}
    bad = _consume_token(cx, "ContosoJournalPost", jid, p.get("confirm_token"))
    if bad: return bad
    cx.execute("UPDATE erp_ledger_journals SET state='posted', posted_by=?, posted_at=? WHERE journal_id=?",
               (_role(), S.now, jid))
    _audit(cx, "LedgerJournal", jid, "post", before={"state": "draft"}, after={"state": "posted"})
    cx.commit()
    return {"posted": True, "journal_id": jid, "state": "posted", "posting_date": j["posting_date"],
            "total_debit": j["total_debit"], "period_id": j["period_id"]}

def _approval_decide(cx, p):
    rid, decision = p.get("request_id"), (p.get("decision") or "").lower()
    if not rid: return {"error": "parameter request_id is required"}
    if decision not in ("approve", "reject"):
        return {"error": "parameter decision must be 'approve' or 'reject'"}
    r = cx.execute("SELECT * FROM erp_approval_requests WHERE request_id=?", (rid,)).fetchone()
    if not r: return {"error": f"no approval request '{rid}'"}
    if r["status"] != "pending":
        return {"error": f"request {rid} was already {r['status']} at {r['decided_at']}"}
    if decision == "reject" and not (p.get("reason") or "").strip():
        return {"error": "validation: a rejection requires a reason"}
    new = "approved" if decision == "approve" else "rejected"
    cx.execute("UPDATE erp_approval_requests SET status=?, decided_by=?, decided_at=?, decision_reason=?"
               " WHERE request_id=?", (new, _role(), S.now, p.get("reason") or "", rid))
    _audit(cx, "ApprovalRequest", rid, new, before={"status": "pending"}, after={"status": new})
    cx.commit()
    return {"request_id": rid, "status": new, "doc_type": r["doc_type"], "doc_id": r["doc_id"],
            "amount": r["amount"], "decided_at": S.now, "reason": p.get("reason") or ""}

def _eligible_payables(cx, pay_date, vendor_account=None, due_from=None, vendor_group=None):
    """Open AP obligations due on or before pay_date, with the cash discount re-derived (M4).

    D365's payment proposal is always filtered (due-date range / vendor / group); an
    unfiltered proposal over a live subledger is not a thing a treasury analyst builds.
    """
    where, args = ["t.txn_type='Invoice'", "t.closed=0", "t.due_date<=?"], [pay_date]
    if due_from: where.append("t.due_date>=?"); args.append(due_from)
    if vendor_account: where.append("t.account=?"); args.append(vendor_account)
    if vendor_group: where.append("v.vendor_group=?"); args.append(vendor_group)
    out = []
    for r in cx.execute(f"""SELECT t.invoice, t.account, t.trans_date, t.due_date,
                                   ROUND(t.amount - t.settled, 2) AS gross, t.cash_disc_code,
                                   v.name AS vendor_name, v.on_hold
                            FROM erp_vend_trans t LEFT JOIN erp_vendors v ON v.account = t.account
                            WHERE {' AND '.join(where)}
                            ORDER BY t.due_date, t.invoice""", args):
        disc = 0.0
        if r["cash_disc_code"]:
            d = cx.execute("SELECT percent, days FROM erp_cash_disc WHERE code=?", (r["cash_disc_code"],)).fetchone()
            if d:
                deadline = (dt.date.fromisoformat(r["trans_date"]) + dt.timedelta(days=d["days"])).isoformat()
                if pay_date <= deadline:
                    disc = round(r["gross"] * d["percent"] / 100.0, 2)
        # Withholding is re-derived here, never read off anything the agent typed (M4).
        # It applies when the vendor carries a withholding category and does NOT have a
        # valid, unexpired exemption certificate on file as at the pay date - the expiry is
        # the part that bites, because a certificate that lapsed still LOOKS present.
        wh, wh_cat, wh_reason = 0.0, None, None
        prof = cx.execute("SELECT * FROM erp_vendor_tax_profile WHERE account=?", (r["account"],)).fetchone()
        if prof:
            declared = prof["tax_category"] or "none"
            valid_cert = bool(prof["certificate_on_file"]) and (
                not prof["certificate_expiry"] or prof["certificate_expiry"] >= pay_date)
            # A valid certificate buys the DECLARED treatment (which for a treaty claim is a
            # reduced rate, not exemption). Without one, the punitive default applies: the
            # non-resident rate for a foreign payee, backup withholding for a domestic one.
            if valid_cert:
                applies = declared
            else:
                applies = ("foreign_contractor" if declared in ("foreign_treaty", "foreign_contractor")
                           else "backup_withholding")
            cat = cx.execute("SELECT * FROM erp_withholding_tax WHERE tax_category=?",
                             (applies,)).fetchone()
            if cat and cat["rate_pct"] and r["gross"] >= (cat["threshold_amount"] or 0):
                wh = round(r["gross"] * cat["rate_pct"] / 100.0, 2)
                wh_cat = cat["tax_category"]
                wh_reason = (f"{cat['tax_category']} at {cat['rate_pct']:.0f}% - "
                             + ("valid certificate on file" if valid_cert
                                else "no certificate on file" if not prof["certificate_on_file"]
                                else f"{prof['certificate_type'] or 'certificate'} expired {prof['certificate_expiry']}"))
        out.append({"invoice": r["invoice"], "vendor": r["account"], "vendor_name": r["vendor_name"],
                    "due_date": r["due_date"], "gross_amount": r["gross"],
                    "discount_taken": disc, "withholding": wh,
                    "withholding_category": wh_cat, "withholding_reason": wh_reason,
                    "net_amount": round(r["gross"] - disc - wh, 2),
                    "vendor_on_hold": (r["on_hold"] or "") not in ("", "Open", None)})
    return out

def _payment_run_propose(cx, p):
    pay_date = p.get("pay_date") or S.today
    bank = p.get("bank_account") or "USMF-OPER"
    b = cx.execute("SELECT * FROM erp_bank_accounts WHERE bank_account=?", (bank,)).fetchone()
    if not b: return {"error": f"no bank account '{bank}'",
                      "hint": "query the BankAccounts entity"}
    elig = _eligible_payables(cx, pay_date, p.get("vendor_account"), p.get("due_from"), p.get("vendor_group"))
    if not elig:
        return {"error": f"validation: no open vendor obligations match this proposal on or before {pay_date}"}
    if len(elig) > PROPOSAL_MAX_LINES:
        top = {}
        for e in elig: top[e["vendor"]] = top.get(e["vendor"], 0) + 1
        return {"error": f"validation: this proposal selects {len(elig)} obligations, above the "
                         f"{PROPOSAL_MAX_LINES}-line proposal limit. Narrow it with due_from, "
                         f"vendor_account or vendor_group.",
                "selected": len(elig),
                "largest_vendors": sorted(({"vendor": k, "obligations": v} for k, v in top.items()),
                                          key=lambda x: -x["obligations"])[:10]}
    net = round(sum(e["net_amount"] for e in elig), 2)
    cash = round((b["available_balance"] or 0) + (b["overdraft_limit"] or 0), 2)
    rid = f"PR-{cx.execute('SELECT COUNT(*) FROM erp_payment_runs').fetchone()[0] + 1:05d}"
    cx.execute("INSERT INTO erp_payment_runs(run_id,dataareaid,pay_date,bank_account,currency,"
               "period_option,cash_available,eligible_net,total_paid,total_rejected,state,created_by,created_at)"
               " VALUES(?,?,?,?,?,?,?,?,0,0,'proposed',?,?)",
               (rid, "USMF", pay_date, bank, "USD", "Invoice", cash, net, _role(), S.now))
    for i, e in enumerate(elig, 1):
        cx.execute("INSERT INTO erp_payment_run_lines(run_id,line,invoice,vendor,due_date,gross_amount,"
                   "discount_taken,withholding,net_amount,disposition,reason_code,reason,priority_rank)"
                   " VALUES(?,?,?,?,?,?,?,?,?,'proposed',NULL,NULL,?)",
                   (rid, i, e["invoice"], e["vendor"], e["due_date"], e["gross_amount"],
                    e["discount_taken"], e["withholding"], e["net_amount"], i))
    _audit(cx, "PaymentRun", rid, "propose", after={"eligible_net": net, "cash_available": cash})
    cx.commit()
    shortfall = round(net - cash, 2)
    preview = {"run_id": rid, "eligible": len(elig), "eligible_net": net, "cash_available": cash}
    return {"run_id": rid, "pay_date": pay_date, "bank_account": bank, "cash_available": cash,
            "eligible_count": len(elig), "eligible_net": net,
            "shortfall": shortfall if shortfall > 0 else 0.0,
            "fully_fundable": shortfall <= 0,
            "note": ("Eligible obligations exceed available cash. Commit by naming which invoices go "
                     "unpaid and why — every eligible invoice must appear in exactly one of paid or "
                     "rejected." if shortfall > 0 else "Available cash covers every eligible obligation."),
            "reason_codes": sorted(REJECT_CODES),
            "obligations": elig,
            "confirm_token": _mint_token(cx, "ContosoPaymentRunCommit", rid, preview),
            "effect_preview": preview}

def _payment_run_commit(cx, p):
    rid = p.get("run_id")
    if not rid: return {"error": "parameter run_id is required"}
    run = cx.execute("SELECT * FROM erp_payment_runs WHERE run_id=?", (rid,)).fetchone()
    if not run: return {"error": f"no payment run '{rid}'"}
    if run["state"] != "proposed": return {"error": f"run {rid} is already {run['state']}"}
    if not p.get("confirm_token"):
        return {"error": "confirm_token is required: call ContosoPaymentRunPropose first and pass the "
                         "confirm_token it returns. ContosoPaymentRunCommit will not run unconfirmed."}
    lines = {r["invoice"]: dict(r) for r in
             cx.execute("SELECT * FROM erp_payment_run_lines WHERE run_id=?", (rid,))}
    paid = [str(x) for x in (p.get("paid") or [])]
    rejected = p.get("rejected") or []
    if not isinstance(rejected, list) or any(not isinstance(x, dict) for x in rejected):
        return {"error": "parameter rejected must be a list of {invoice, reason_code, reason}"}
    rej_map = {str(x.get("invoice")): x for x in rejected}
    # M2: the partition must be total and disjoint — a short run is committed by naming the
    # unpaid set, never by silently dropping obligations.
    both = sorted(set(paid) & set(rej_map))
    unknown = sorted((set(paid) | set(rej_map)) - set(lines))
    missing = sorted(set(lines) - set(paid) - set(rej_map))
    if unknown: return {"error": f"not eligible obligations in run {rid}: {unknown}"}
    if both: return {"error": f"invoices appear in both paid and rejected: {both}"}
    if missing:
        return {"error": f"validation: every eligible obligation must be either paid or rejected with a "
                         f"reason. Unaccounted for: {missing}"}
    for inv, x in rej_map.items():
        if x.get("reason_code") not in REJECT_CODES:
            return {"error": f"invoice {inv}: reason_code must be one of {sorted(REJECT_CODES)}"}
        if not (x.get("reason") or "").strip():
            return {"error": f"invoice {inv}: a rejection requires a reason"}
    # M4: totals are re-derived from the subledger, never from anything the agent typed.
    total_paid = round(sum(lines[i]["net_amount"] for i in paid), 2)
    total_rej = round(sum(lines[i]["net_amount"] for i in rej_map), 2)
    if total_paid > run["cash_available"] + 0.005:
        return {"error": f"validation: the paid set nets {total_paid:.2f} but only "
                         f"{run['cash_available']:.2f} is available on {run['bank_account']}"}
    bad = _consume_token(cx, "ContosoPaymentRunCommit", rid, p.get("confirm_token"))
    if bad: return bad
    for inv in paid:
        cx.execute("UPDATE erp_payment_run_lines SET disposition='paid' WHERE run_id=? AND invoice=?", (rid, inv))
    for inv, x in rej_map.items():
        cx.execute("UPDATE erp_payment_run_lines SET disposition='rejected', reason_code=?, reason=? "
                   "WHERE run_id=? AND invoice=?", (x["reason_code"], x["reason"], rid, inv))
    cx.execute("UPDATE erp_payment_runs SET state='committed', total_paid=?, total_rejected=?, "
               "committed_at=?, approved_by=? WHERE run_id=?",
               (total_paid, total_rej, S.now, _role(), rid))
    _audit(cx, "PaymentRun", rid, "commit", after={"total_paid": total_paid, "total_rejected": total_rej})
    cx.commit()
    return {"committed": True, "run_id": rid, "paid_count": len(paid), "total_paid": total_paid,
            "rejected_count": len(rej_map), "total_rejected": total_rej,
            "cash_available": run["cash_available"],
            "cash_remaining": round(run["cash_available"] - total_paid, 2)}

@S.tool("api_find_actions", "Finds actions (ICustomAPI AI tools) you can invoke.",
        {"query": {"type": "string"}})
def api_find_actions(query=None):
    q = (query or "").lower()
    # Like the real server: only actions the current role can invoke are returned.
    visible = {n: m for n, m in ACTIONS.items()
               if not m.get("requires_role") or m["requires_role"] == _role()}
    return {"actions": [{"name": n, **{k: v for k, v in meta.items() if k != "requires_role"}}
                        for n, meta in visible.items()
                        if not q or q in n.lower() or q in meta["description"].lower()],
            "role": ROLE_NAME}

@S.tool("api_invoke_action", "Invokes an action by name with parameters.",
        {"action": {"type": "string"}, "parameters": {"type": "object"}}, ["action"])
def api_invoke_action(action, parameters=None):
    p = parameters or {}
    cx = S.db()
    need = ACTIONS.get(action, {}).get("requires_role")
    if need and _role() != need:
        return _deny(f"invoke action '{action}' (requires the {need.title()} role)", "AI tool actions")
    if action == "ContosoIssueCollectionLetter":
        if not p.get("customer_account"): return {"error": "parameter customer_account is required"}
        return _issue_collection_letter(cx, p["customer_account"])
    if action == "ContosoSetCreditHold":
        if not p.get("customer_account"): return {"error": "parameter customer_account is required"}
        return _set_credit_hold(cx, p["customer_account"], p.get("on_hold"), p.get("reason"))
    if action == "ContosoCustAgedBalancesLive":
        return get_customer_aged_balances(**{k: p[k] for k in ("as_of", "customer_account", "customer_group") if k in p})
    if action == "ContosoCashDiscountForecast":
        as_of = p.get("as_of") or S.today
        where, args = ["t.txn_type='Invoice'", "t.closed=0", "t.cash_disc_code IS NOT NULL"], []
        if p.get("vendor_account"): where.append("t.account=?"); args.append(p["vendor_account"])
        rows = []
        for r in cx.execute(f"""SELECT t.account, t.invoice, t.trans_date, t.amount - t.settled AS open,
                                       d.percent, d.days FROM erp_vend_trans t
                                JOIN erp_cash_disc d ON d.code = t.cash_disc_code
                                WHERE {' AND '.join(where)}""", args):
            deadline = (dt.date.fromisoformat(r["trans_date"]) + dt.timedelta(days=r["days"])).isoformat()
            if as_of <= deadline:
                rows.append({"vendor": r["account"], "invoice": r["invoice"], "invoice_date": r["trans_date"],
                             "discount_deadline": deadline, "open_amount": round(r["open"], 2),
                             "discount_pct": r["percent"], "capturable": round(r["open"] * r["percent"] / 100, 2)})
        return {"as_of": as_of, "qualifying": rows, "total_capturable": round(sum(x["capturable"] for x in rows), 2)}
    if action == "ContosoCollectionStatus":
        acct = p.get("customer_account")
        if not acct: return {"error": "parameter customer_account is required"}
        letters = [dict(r) for r in cx.execute("SELECT letter_code, letter_date, status, fee FROM erp_collection_letters WHERE account=? ORDER BY letter_date", (acct,))]
        open_bal = cx.execute("SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE account=? AND txn_type='Invoice' AND closed=0", (acct,)).fetchone()[0]
        return {"customer_account": acct, "highest_letter": max((l["letter_code"] for l in letters), default=None),
                "letters": letters, "open_balance": open_bal}
    if action == "ContosoJournalPropose":
        return _journal_propose(cx, p)
    if action == "ContosoJournalPost":
        return _journal_post(cx, p)
    if action == "ContosoApprovalList":
        where, args = [], []
        if p.get("status"): where.append("status=?"); args.append(p["status"])
        if p.get("doc_type"): where.append("doc_type=?"); args.append(p["doc_type"])
        sql = "SELECT * FROM erp_approval_requests" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY submitted_at"
        return {"requests": [dict(r) for r in cx.execute(sql, args)]}
    if action == "ContosoApprovalDecide":
        return _approval_decide(cx, p)
    if action == "ContosoPaymentRunPropose":
        return _payment_run_propose(cx, p)
    if action == "ContosoPaymentRunCommit":
        return _payment_run_commit(cx, p)
    if action == "ContosoFinanceCaseDecide":
        case_id = str(p.get("case_id") or "").strip()
        decision_code = str(p.get("decision_code") or "").strip()
        evidence_refs = p.get("evidence_refs") or []
        rationale = str(p.get("rationale") or "").strip()
        if not case_id:
            return {"error": "parameter case_id is required"}
        if not decision_code:
            return {"error": "parameter decision_code is required"}
        if not isinstance(evidence_refs, list) or len(evidence_refs) < 4:
            return {"error": "at least four immutable evidence_refs are required"}
        if len(set(map(str, evidence_refs))) != len(evidence_refs):
            return {"error": "evidence_refs must be unique"}
        if len(rationale) < 40:
            return {"error": "rationale must explain the supported decision in at least 40 characters"}
        row = cx.execute(
            "SELECT * FROM erp_finance_cases WHERE case_id=?", (case_id,)
        ).fetchone()
        if not row:
            return {"error": f"FinanceCases record {case_id!r} was not found"}
        if row["status"] != "open":
            return {"error": f"FinanceCases record {case_id!r} is {row['status']!r}, not open"}
        before = dict(row)
        normalized_refs = json.dumps(sorted(map(str, evidence_refs)), separators=(",", ":"))
        cx.execute(
            "UPDATE erp_finance_cases SET status='decided', decision_code=?, "
            "evidence_refs=?, rationale=?, owner=?, decided_at=? WHERE case_id=?",
            (decision_code, normalized_refs, rationale, _role(), S.now, case_id),
        )
        after = dict(
            cx.execute("SELECT * FROM erp_finance_cases WHERE case_id=?", (case_id,)).fetchone()
        )
        _audit(cx, "FinanceCase", case_id, "decide", before=before, after=after)
        cx.commit()
        return {
            "case_id": case_id,
            "status": "decided",
            "decision_code": decision_code,
            "evidence_refs": sorted(map(str, evidence_refs)),
            "decided_at": S.now,
        }
    return {"error": f"no action '{action}'", "hint": "use api_find_actions", "available": sorted(ACTIONS)}

# ==================== internal: live aged balances ==========================
# Not a public tool — the real D365 MCP has no such tool. Reachable the real ways:
# the CustAgedBalances form (form tools) and api_invoke_action(ContosoCustAgedBalancesLive).

def get_customer_aged_balances(as_of=None, customer_account=None, customer_group=None, page=1):
    as_of = as_of or S.today
    cx = S.db()
    where, args = ["t.txn_type='Invoice'", "t.closed=0"], []
    if customer_account: where.append("t.account=?"); args.append(customer_account)
    if customer_group: where.append("c.customer_group=?"); args.append(customer_group)
    agg = {}
    for r in cx.execute(f"""SELECT t.account, c.name, t.due_date, t.amount-t.settled AS open
                            FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account
                            WHERE {' AND '.join(where)}""", args):
        days = (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(r["due_date"])).days
        b = agg.setdefault(r["account"], {"account": r["account"], "name": r["name"],
                                          "not_due": 0, "b1_30": 0, "b31_60": 0, "b61_90": 0, "b90_plus": 0})
        key = "not_due" if days <= 0 else "b1_30" if days <= 30 else "b31_60" if days <= 60 else "b61_90" if days <= 90 else "b90_plus"
        b[key] = round(b[key] + r["open"], 2)
    out = sorted(agg.values(), key=lambda b: -(b["b1_30"] + b["b31_60"] + b["b61_90"] + b["b90_plus"]))
    for b in out:
        b["past_due_total"] = round(b["b1_30"] + b["b31_60"] + b["b61_90"] + b["b90_plus"], 2)
        b["total_open"] = round(b["past_due_total"] + b["not_due"], 2)
    page = max(1, int(page or 1))
    return {"as_of": as_of, "rows": out[(page-1)*25: page*25], "page": page,
            "total_rows": len(out), "has_more": page*25 < len(out),
            "note": "live computation; the batch AgedBalancesSnapshot entity may differ"}

if __name__ == "__main__":
    S.run()
