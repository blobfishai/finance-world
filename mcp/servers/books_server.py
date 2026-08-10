#!/usr/bin/env python3
"""Subsidiary books MCP server — QuickBooks-Online-shaped, for CES Direct LLC. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("books", "CES Direct LLC subsidiary accounting (QuickBooks-style). SIMULATION ONLY.")

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

if __name__ == "__main__":
    S.run()
