#!/usr/bin/env python3
"""ERP MCP server — Dynamics-365-Finance-shaped, discovery-first (mirrors Microsoft's
dynamic ERP MCP: find entity type -> get metadata -> find entities / SQL). Read-only."""
import sys, re, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("erp", "Contoso ERP (Dynamics 365 Finance, company USMF). SIMULATION ONLY.")

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

@S.tool("data_find_entity_type", "Find ERP data entity types matching a natural-language query.",
        {"query": {"type": "string", "description": "e.g. 'customer invoices', 'payment terms'"}}, ["query"])
def find_entity_type(query):
    q = query.lower()
    scored = [{"entity": name, "description": desc}
              for name, (_t, desc) in ENTITIES.items()
              if any(w in (name + " " + desc).lower() for w in re.findall(r"[a-z]+", q))]
    return {"matches": scored or [{"entity": n, "description": d} for n, (_t, d) in ENTITIES.items()]}

def _unknown(entity):
    return {"error": f"unknown entity type '{entity}'",
            "available_entities": sorted(ENTITIES),
            "hint": "use data_find_entity_type to discover entity types"}

@S.tool("data_get_entity_metadata", "Get the field list for an entity type.",
        {"entity": {"type": "string"}}, ["entity"])
def get_entity_metadata(entity):
    if entity not in ENTITIES: return _unknown(entity)
    table, desc = ENTITIES[entity]
    cx = S.db()
    fields = [r["name"] for r in cx.execute(f"PRAGMA table_info({table})")]
    return {"entity": entity, "description": desc, "fields": fields,
            "note": "open remainder on transactions = amount - settled (closed=0 only)"}

@S.tool("data_find_entities", "Query one entity with equality/contains filters. Paged (25 rows).",
        {"entity": {"type": "string"},
         "filters": {"type": "object", "description": "field -> value; strings match case-insensitive substring, numbers match exactly"},
         "page": {"type": "integer"}}, ["entity"])
def find_entities(entity, filters=None, page=1):
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

@S.tool("data_find_entities_sql", "Run a read-only SQL SELECT over ERP entities (tables erp_*). Single statement; LIMIT 200 enforced.",
        {"sql": {"type": "string"}}, ["sql"])
def find_entities_sql(sql):
    s = sql.strip().rstrip(";")
    if not re.match(r"(?is)^\s*select\b", s) or ";" in s:
        raise ValueError("single SELECT statement only")
    for tbl in re.findall(r"(?i)\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", s):
        if not tbl.lower().startswith("erp_"):
            raise ValueError(f"table {tbl} is outside the ERP (only erp_* tables exist here)")
    cx = S.db()
    rows = [dict(r) for r in cx.execute(f"SELECT * FROM ({s}) LIMIT 200").fetchall()]
    return {"rows": rows, "row_count": len(rows), "truncated_at": 200}

@S.tool("get_customer_aged_balances", "LIVE aged AR balances computed from open transactions as of a date (default: today). Paged, sorted by past-due desc.",
        {"as_of": {"type": "string", "description": "YYYY-MM-DD, default world today"},
         "customer_account": {"type": "string"},
         "customer_group": {"type": "string"},
         "page": {"type": "integer"}})
def aged_balances(as_of=None, customer_account=None, customer_group=None, page=1):
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
