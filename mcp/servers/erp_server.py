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
import sys, re, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server, PAGE

S = Server("erp", "Contoso ERP (Dynamics 365 Finance, company USMF). SIMULATION ONLY.")
ROLE = "Finance analyst (read-only)"

ENTITIES = {
    "Customers":            ("erp_customers", "Customer master (CustomersV3): account, name, group, terms, credit limit, hold status"),
    "Vendors":              ("erp_vendors", "Vendor master (VendorsV2): account, name, group, terms, payment method"),
    "CustomerTransactions": ("erp_cust_trans", "Posted AR subledger: invoices/payments with due dates, settled amount, open remainder = amount-settled where closed=0"),
    "VendorTransactions":   ("erp_vend_trans", "Posted AP subledger: vendor invoices/payments, due dates, settled, closed"),
    "CustomerSettlements":  ("erp_settlements", "Settlement links between payments and invoices incl. cash discount taken"),
    "PaymentTerms":         ("erp_payment_terms", "Payment terms codes (COD, Net15, Net30, ...)"),
    "CashDiscounts":        ("erp_cash_disc", "Cash discount codes: percent, day window, next-code chain"),
    "CollectionLetters":    ("erp_collection_letters", "Collection letter journal per customer: letter_code 1..4/Collection, date, status, fee"),
    "AgedBalancesSnapshot": ("erp_aging_snapshot", "Batch customer aging snapshot (run_id, as_of, buckets). May lag live transactions."),
    "Companies":            ("erp_companies", "Legal entities"),
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
    return S.rows(cx, sql, args, page)

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
    return {"rows": rows, "row_count": len(rows), "truncated_at": 200}

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
}

@S.tool("api_find_actions", "Finds actions (ICustomAPI AI tools) you can invoke.",
        {"query": {"type": "string"}})
def api_find_actions(query=None):
    q = (query or "").lower()
    return {"actions": [{"name": n, **meta} for n, meta in ACTIONS.items()
                        if not q or q in n.lower() or q in meta["description"].lower()]}

@S.tool("api_invoke_action", "Invokes an action by name with parameters.",
        {"action": {"type": "string"}, "parameters": {"type": "object"}}, ["action"])
def api_invoke_action(action, parameters=None):
    p = parameters or {}
    cx = S.db()
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
    return {"error": f"no action '{action}'", "hint": "use api_find_actions", "available": sorted(ACTIONS)}

# ==================== convenience page alias (kept for walks) ================

@S.tool("get_customer_aged_balances", "LIVE aged AR balances computed from open transactions as of a date (default: today). Paged, sorted by past-due desc. (Alias of the 'Customer aged balances' live view; the batch snapshot entity may differ.)",
        {"as_of": {"type": "string", "description": "YYYY-MM-DD, default world today"},
         "customer_account": {"type": "string"},
         "customer_group": {"type": "string"},
         "page": {"type": "integer"}})
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
