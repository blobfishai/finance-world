#!/usr/bin/env python3
"""Subsidiary books MCP server — QuickBooks-Online-shaped, for CES Direct LLC.

Mirrors the Intuit QBO API surface at the AR-relevant slice: entity reads
(CompanyInfo, Customer, Invoice, CreditMemo, Payment), the generic `query` endpoint
(QBO's SQL-ish query language over entities), the standard AR reports
(AgedReceivables, CustomerBalance, TransactionList), and write endpoints that exist
but are scope-denied (our connection carries a read-only grant). SIMULATION ONLY."""
import sys, re, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("books", "CES Direct LLC subsidiary accounting (QuickBooks-style). SIMULATION ONLY.")

QB_ENTITIES = {"Customer": "books_customers", "Invoice": "books_invoices",
               "CreditMemo": "books_credit_memos", "Payment": "books_payments"}

def _scope_denied(op):
    return {"error": f"insufficient scope: this connection is authorized for accounting.read only; "
                     f"'{op}' requires accounting.write", "fault_type": "AUTHORIZATION"}

@S.tool("get_company_info", "CompanyInfo for the subsidiary (name, fiscal year start, base currency).")
def get_company_info():
    return {"CompanyName": "CES Direct LLC (SIMULATED)", "LegalName": "CES Direct LLC",
            "Country": "US", "FiscalYearStartMonth": "January", "Currency": "USD",
            "parent": "Contoso Entertainment System USA (USMF)"}

@S.tool("query", "Run a QBO-style query, e.g. \"SELECT * FROM Invoice WHERE CustomerRef = 'BC-114'\". Entities: Customer, Invoice, CreditMemo, Payment. Operators: =, LIKE.",
        {"q": {"type": "string"}}, ["q"])
def qbo_query(q):
    m = re.match(r"(?is)^\s*select\s+\*\s+from\s+(\w+)(?:\s+where\s+(\w+)\s*(=|like)\s*'([^']*)')?\s*$", q.strip().rstrip(";"))
    if not m:
        return {"error": "unsupported query syntax",
                "hint": "SELECT * FROM <Entity> [WHERE <field> = '<value>'] — entities: " + ", ".join(QB_ENTITIES)}
    entity, field, op, val = m.groups()
    entity = {e.lower(): e for e in QB_ENTITIES}.get(entity.lower())
    if not entity: return {"error": f"unknown entity", "entities": sorted(QB_ENTITIES)}
    table = QB_ENTITIES[entity]
    cx = S.db()
    cols = {r["name"] for r in cx.execute(f"PRAGMA table_info({table})")}
    alias = {"customerref": "customer_id", "docnumber": "doc_number", "txndate": "txn_date"}
    if field:
        f = alias.get(field.lower(), field.lower())
        if f not in cols: return {"error": f"unknown field '{field}'", "fields": sorted(cols)}
        if op.lower() == "like":
            return S.rows(cx, f"SELECT * FROM {table} WHERE LOWER({f}) LIKE ?", (val.lower().replace('%','%'),))
        return S.rows(cx, f"SELECT * FROM {table} WHERE CAST({f} AS TEXT) = ?", (val,))
    return S.rows(cx, f"SELECT * FROM {table}")

@S.tool("list_customers", "List subsidiary customers, optionally filtered by name substring.",
        {"query": {"type": "string"}})
def list_customers(query=None):
    cx = S.db()
    if query:
        return S.rows(cx, "SELECT * FROM books_customers WHERE LOWER(display_name) LIKE ?", (f"%{query.lower()}%",))
    return S.rows(cx, "SELECT * FROM books_customers")

@S.tool("get_customer", "Get one subsidiary customer with open balance summary.",
        {"customer_id": {"type": "string"}}, ["customer_id"])
def get_customer(customer_id):
    cx = S.db()
    c = cx.execute("SELECT * FROM books_customers WHERE id=?", (customer_id,)).fetchone()
    if not c: return {"error": "not found"}
    inv = cx.execute("SELECT ROUND(COALESCE(SUM(balance),0),2) FROM books_invoices WHERE customer_id=? AND status='Open'", (customer_id,)).fetchone()[0]
    cm = cx.execute("SELECT ROUND(COALESCE(SUM(remaining),0),2) FROM books_credit_memos WHERE customer_id=?", (customer_id,)).fetchone()[0]
    return {"customer": dict(c), "open_invoice_balance": inv, "unapplied_credit_memos": cm,
            "net_balance": round(inv - cm, 2)}

@S.tool("query_invoices", "List subsidiary invoices (optionally by customer and/or status Open|Paid).",
        {"customer_id": {"type": "string"}, "status": {"type": "string"}})
def query_invoices(customer_id=None, status=None):
    cx = S.db(); where, args = [], []
    if customer_id: where.append("customer_id=?"); args.append(customer_id)
    if status: where.append("status=?"); args.append(status)
    sql = "SELECT * FROM books_invoices" + (" WHERE " + " AND ".join(where) if where else "")
    return S.rows(cx, sql, args)

@S.tool("get_invoice", "Get one subsidiary invoice by id or doc_number.",
        {"invoice": {"type": "string"}}, ["invoice"])
def get_invoice(invoice):
    cx = S.db()
    r = cx.execute("SELECT * FROM books_invoices WHERE id=? OR doc_number=?", (invoice, invoice)).fetchone()
    return dict(r) if r else {"error": "not found"}

@S.tool("query_credit_memos", "List credit memos (optionally by customer).",
        {"customer_id": {"type": "string"}})
def query_credit_memos(customer_id=None):
    cx = S.db()
    if customer_id:
        return S.rows(cx, "SELECT * FROM books_credit_memos WHERE customer_id=?", (customer_id,))
    return S.rows(cx, "SELECT * FROM books_credit_memos")

@S.tool("query_payments", "List received payments (optionally by customer).",
        {"customer_id": {"type": "string"}})
def query_payments(customer_id=None):
    cx = S.db()
    if customer_id:
        return S.rows(cx, "SELECT * FROM books_payments WHERE customer_id=?", (customer_id,))
    return S.rows(cx, "SELECT * FROM books_payments")

@S.tool("report_aged_receivables", "AgedReceivables report: open invoice balances bucketed by days past due as of a date (default today).",
        {"as_of": {"type": "string"}})
def report_aged_receivables(as_of=None):
    as_of = as_of or S.today
    cx = S.db(); out = {}
    for r in cx.execute("""SELECT c.display_name, i.customer_id, i.due_date, i.balance
                           FROM books_invoices i JOIN books_customers c ON c.id = i.customer_id
                           WHERE i.status='Open'"""):
        days = (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(r["due_date"])).days
        b = out.setdefault(r["customer_id"], {"customer": r["display_name"], "current": 0,
                                              "d1_30": 0, "d31_60": 0, "d61_90": 0, "d90_plus": 0})
        key = "current" if days <= 0 else "d1_30" if days <= 30 else "d31_60" if days <= 60 else "d61_90" if days <= 90 else "d90_plus"
        b[key] = round(b[key] + r["balance"], 2)
    for cid, b in out.items():
        b["total"] = round(b["current"] + b["d1_30"] + b["d31_60"] + b["d61_90"] + b["d90_plus"], 2)
    return {"report": "AgedReceivables", "as_of": as_of, "rows": out,
            "note": "unapplied credit memos are NOT netted in this report (QBO behavior); see query_credit_memos"}

@S.tool("report_customer_balance", "CustomerBalance report: net open balance per customer (invoices minus unapplied credit memos).")
def report_customer_balance():
    cx = S.db(); rows = []
    for c in cx.execute("SELECT * FROM books_customers"):
        inv = cx.execute("SELECT ROUND(COALESCE(SUM(balance),0),2) FROM books_invoices WHERE customer_id=? AND status='Open'", (c["id"],)).fetchone()[0]
        cm = cx.execute("SELECT ROUND(COALESCE(SUM(remaining),0),2) FROM books_credit_memos WHERE customer_id=?", (c["id"],)).fetchone()[0]
        rows.append({"customer_id": c["id"], "customer": c["display_name"],
                     "open_invoices": inv, "unapplied_credits": cm, "net_balance": round(inv - cm, 2)})
    return {"report": "CustomerBalance", "rows": rows}

@S.tool("report_transaction_list", "TransactionList report: invoices, credit memos, and payments in a date range.",
        {"date_from": {"type": "string"}, "date_to": {"type": "string"}})
def report_transaction_list(date_from="1900-01-01", date_to="2999-12-31"):
    cx = S.db()
    txns = []
    for r in cx.execute("SELECT 'Invoice' AS type, doc_number AS ref, txn_date, amount, customer_id FROM books_invoices WHERE txn_date BETWEEN ? AND ?", (date_from, date_to)): txns.append(dict(r))
    for r in cx.execute("SELECT 'CreditMemo' AS type, doc_number AS ref, txn_date, -amount AS amount, customer_id FROM books_credit_memos WHERE txn_date BETWEEN ? AND ?", (date_from, date_to)): txns.append(dict(r))
    for r in cx.execute("SELECT 'Payment' AS type, id AS ref, txn_date, -amount AS amount, customer_id FROM books_payments WHERE txn_date BETWEEN ? AND ?", (date_from, date_to)): txns.append(dict(r))
    txns.sort(key=lambda t: t["txn_date"])
    return {"report": "TransactionList", "from": date_from, "to": date_to, "rows": txns[:100], "total_rows": len(txns)}

@S.tool("create_invoice", "Create an invoice. Requires accounting.write scope.",
        {"invoice": {"type": "object"}}, ["invoice"])
def create_invoice(invoice):
    return _scope_denied("create_invoice")

@S.tool("update_invoice", "Sparse-update an invoice. Requires accounting.write scope.",
        {"invoice": {"type": "object"}}, ["invoice"])
def update_invoice(invoice):
    return _scope_denied("update_invoice")

@S.tool("void_invoice", "Void an invoice. Requires accounting.write scope.",
        {"invoice_id": {"type": "string"}}, ["invoice_id"])
def void_invoice(invoice_id):
    return _scope_denied("void_invoice")

if __name__ == "__main__":
    S.run()
