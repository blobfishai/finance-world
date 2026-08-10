#!/usr/bin/env python3
"""Subsidiary books MCP server — 1:1 QuickBooks Online API shapes, for CES Direct LLC.

Mirrors Intuit's QBO v3 API surface (the pattern behind Intuit's official 144-tool MCP):
- `query` — QBO's query language endpoint (`SELECT * FROM Invoice WHERE CustomerRef = '...'`),
  responses wrapped in {"QueryResponse": {"<Entity>": [...], "startPosition", "maxResults"}}
- entity reads by id (GET /v3/company/{realm}/<entity>/<id> shape): {"Customer": {...}} etc.
- reports (real QBO report names): AgedReceivables, CustomerBalance, TransactionList
- writes exist and return QBO Fault JSON (this connection carries accounting.read only)
Entities use QBO field names: Id, DisplayName, Balance, DocNumber, TxnDate, DueDate,
TotalAmt, CustomerRef {value, name}. Errors use {"Fault": {"Error": [...], "type": ...}}.
SIMULATION ONLY."""
import sys, re, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("books", "CES Direct LLC subsidiary accounting (QuickBooks Online API shapes). SIMULATION ONLY.")

ENT = {"Customer": "books_customers", "Invoice": "books_invoices",
       "CreditMemo": "books_credit_memos", "Payment": "books_payments"}

def _fault(msg, ftype="ValidationFault", code="2010"):
    return {"Fault": {"Error": [{"Message": msg, "Detail": msg, "code": code}], "type": ftype},
            "error": msg}  # "error" key keeps framework ok:false semantics

def _cust_name(cx, cid):
    r = cx.execute("SELECT display_name FROM books_customers WHERE id=?", (cid,)).fetchone()
    return r["display_name"] if r else None

def _to_qbo(cx, entity, row):
    r = dict(row)
    if entity == "Customer":
        bal = cx.execute("SELECT ROUND(COALESCE(SUM(balance),0),2) FROM books_invoices WHERE customer_id=? AND status='Open'", (r["id"],)).fetchone()[0]
        return {"Id": r["id"], "DisplayName": r["display_name"], "PrimaryEmailAddr": {"Address": r["email"]},
                "Balance": bal, "Notes": f"ERP ref: {r['erp_ref']}" if r.get("erp_ref") else None}
    if entity == "Invoice":
        return {"Id": r["id"], "DocNumber": r["doc_number"], "TxnDate": r["txn_date"], "DueDate": r["due_date"],
                "TotalAmt": r["amount"], "Balance": r["balance"],
                "CustomerRef": {"value": r["customer_id"], "name": _cust_name(cx, r["customer_id"])},
                "PrivateNote": r["memo"], "status": r["status"]}
    if entity == "CreditMemo":
        return {"Id": r["id"], "DocNumber": r["doc_number"], "TxnDate": r["txn_date"],
                "TotalAmt": r["amount"], "RemainingCredit": r["remaining"],
                "CustomerRef": {"value": r["customer_id"], "name": _cust_name(cx, r["customer_id"])},
                "PrivateNote": r["memo"]}
    if entity == "Payment":
        return {"Id": r["id"], "TxnDate": r["txn_date"], "TotalAmt": r["amount"],
                "CustomerRef": {"value": r["customer_id"], "name": _cust_name(cx, r["customer_id"])},
                "PaymentMethodRef": {"name": r.get("method")}, "PrivateNote": r.get("memo"),
                "LinkedTxn": [{"TxnId": r["applied_to_invoice"], "TxnType": "Invoice"}] if r.get("applied_to_invoice") else []}

ALIAS = {"customerref": "customer_id", "docnumber": "doc_number", "txndate": "txn_date",
         "duedate": "due_date", "displayname": "display_name", "id": "id", "status": "status",
         "balance": "balance", "totalamt": "amount"}

@S.tool("get_company_info", "CompanyInfo (GET /v3/company/{realmId}/companyinfo shape).")
def get_company_info():
    return {"CompanyInfo": {"CompanyName": "CES Direct LLC (SIMULATED)", "LegalName": "CES Direct LLC",
                            "Country": "US", "FiscalYearStartMonth": "January",
                            "SupportedLanguages": "en", "CompanyStartDate": "2024-06-01"},
            "note": "subsidiary of Contoso Entertainment System USA (USMF)"}

@S.tool("query", "QBO query language (GET /v3/company/{realmId}/query shape). E.g. \"SELECT * FROM Invoice WHERE CustomerRef = 'BC-114'\". Entities: Customer, Invoice, CreditMemo, Payment. Operators: =, LIKE.",
        {"q": {"type": "string"}}, ["q"])
def query(q):
    m = re.match(r"(?is)^\s*select\s+\*\s+from\s+(\w+)(?:\s+where\s+(\w+)\s*(=|like)\s*'([^']*)')?\s*$",
                 q.strip().rstrip(";"))
    if not m:
        return _fault("QueryParserError: unsupported syntax. Use SELECT * FROM <Entity> "
                      "[WHERE <Field> = '<value>'] with entities " + ", ".join(ENT), "ValidationFault", "4000")
    entity, field, op, val = m.groups()
    entity = {e.lower(): e for e in ENT}.get(entity.lower())
    if not entity: return _fault(f"Invalid entity. Entities: {', '.join(ENT)}", "ValidationFault", "4001")
    table = ENT[entity]
    cx = S.db()
    cols = {r["name"] for r in cx.execute(f"PRAGMA table_info({table})")}
    if field:
        f = ALIAS.get(field.lower(), field.lower())
        if f not in cols: return _fault(f"Invalid property '{field}' for {entity}", "ValidationFault", "4001")
        if op.lower() == "like":
            rows = cx.execute(f"SELECT * FROM {table} WHERE LOWER({f}) LIKE ?", (val.lower(),)).fetchall()
        else:
            rows = cx.execute(f"SELECT * FROM {table} WHERE CAST({f} AS TEXT) = ?", (val,)).fetchall()
    else:
        rows = cx.execute(f"SELECT * FROM {table}").fetchall()
    ents = [_to_qbo(cx, entity, r) for r in rows[:100]]
    return {"QueryResponse": {entity: ents, "startPosition": 1, "maxResults": len(ents)}}

@S.tool("get_customer", "Read a Customer by Id (GET /v3/.../customer/{id} shape; Balance = open invoice total).",
        {"customer_id": {"type": "string"}}, ["customer_id"])
def get_customer(customer_id):
    cx = S.db()
    r = cx.execute("SELECT * FROM books_customers WHERE id=?", (customer_id,)).fetchone()
    if not r: return _fault(f"Object Not Found: Customer {customer_id}", "ValidationFault", "610")
    cust = _to_qbo(cx, "Customer", r)
    cm = cx.execute("SELECT ROUND(COALESCE(SUM(remaining),0),2) FROM books_credit_memos WHERE customer_id=?", (customer_id,)).fetchone()[0]
    return {"Customer": cust, "UnappliedCredits": cm, "NetBalance": round(cust["Balance"] - cm, 2)}

@S.tool("get_invoice", "Read an Invoice by Id or DocNumber (GET /v3/.../invoice/{id} shape).",
        {"invoice": {"type": "string"}}, ["invoice"])
def get_invoice(invoice):
    cx = S.db()
    r = cx.execute("SELECT * FROM books_invoices WHERE id=? OR doc_number=?", (invoice, invoice)).fetchone()
    if not r: return _fault(f"Object Not Found: Invoice {invoice}", "ValidationFault", "610")
    return {"Invoice": _to_qbo(cx, "Invoice", r)}

@S.tool("get_creditmemo", "Read a CreditMemo by Id or DocNumber (GET /v3/.../creditmemo/{id} shape).",
        {"creditmemo": {"type": "string"}}, ["creditmemo"])
def get_creditmemo(creditmemo):
    cx = S.db()
    r = cx.execute("SELECT * FROM books_credit_memos WHERE id=? OR doc_number=?", (creditmemo, creditmemo)).fetchone()
    if not r: return _fault(f"Object Not Found: CreditMemo {creditmemo}", "ValidationFault", "610")
    return {"CreditMemo": _to_qbo(cx, "CreditMemo", r)}

@S.tool("get_payment", "Read a Payment by Id (GET /v3/.../payment/{id} shape).",
        {"payment_id": {"type": "string"}}, ["payment_id"])
def get_payment(payment_id):
    cx = S.db()
    r = cx.execute("SELECT * FROM books_payments WHERE id=?", (payment_id,)).fetchone()
    if not r: return _fault(f"Object Not Found: Payment {payment_id}", "ValidationFault", "610")
    return {"Payment": _to_qbo(cx, "Payment", r)}

@S.tool("report_aged_receivables", "AgedReceivables report (GET /v3/.../reports/AgedReceivables shape): open invoices bucketed by days past due. Credit memos are NOT netted (QBO behavior).",
        {"as_of": {"type": "string"}})
def report_aged_receivables(as_of=None):
    as_of = as_of or S.today
    cx = S.db(); buckets = {}
    for r in cx.execute("""SELECT c.display_name, i.customer_id, i.due_date, i.balance
                           FROM books_invoices i JOIN books_customers c ON c.id = i.customer_id
                           WHERE i.status='Open'"""):
        days = (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(r["due_date"])).days
        b = buckets.setdefault(r["customer_id"], {"customer": r["display_name"], "current": 0,
                                                  "1_30": 0, "31_60": 0, "61_90": 0, "91_over": 0})
        key = "current" if days <= 0 else "1_30" if days <= 30 else "31_60" if days <= 60 else "61_90" if days <= 90 else "91_over"
        b[key] = round(b[key] + r["balance"], 2)
    rows = []
    for cid, b in buckets.items():
        total = round(b["current"] + b["1_30"] + b["31_60"] + b["61_90"] + b["91_over"], 2)
        rows.append({"ColData": [{"value": b["customer"], "id": cid}, {"value": b["current"]},
                                 {"value": b["1_30"]}, {"value": b["31_60"]}, {"value": b["61_90"]},
                                 {"value": b["91_over"]}, {"value": total}]})
    return {"Header": {"ReportName": "AgedReceivables", "StartPeriod": as_of, "EndPeriod": as_of},
            "Columns": {"Column": [{"ColTitle": t} for t in
                        ["Customer", "Current", "1 - 30", "31 - 60", "61 - 90", "91 and over", "Total"]]},
            "Rows": {"Row": rows}}

@S.tool("report_customer_balance", "CustomerBalance report shape: net open balance per customer.")
def report_customer_balance():
    cx = S.db(); rows = []
    for c in cx.execute("SELECT * FROM books_customers"):
        inv = cx.execute("SELECT ROUND(COALESCE(SUM(balance),0),2) FROM books_invoices WHERE customer_id=? AND status='Open'", (c["id"],)).fetchone()[0]
        rows.append({"ColData": [{"value": c["display_name"], "id": c["id"]}, {"value": inv}]})
    return {"Header": {"ReportName": "CustomerBalance"},
            "Columns": {"Column": [{"ColTitle": "Customer"}, {"ColTitle": "Balance"}]},
            "Rows": {"Row": rows},
            "note": "open invoice balances; unapplied credit memos are separate objects (query CreditMemo)"}

@S.tool("report_transaction_list", "TransactionList report shape: invoices, credit memos, payments in a date range.",
        {"date_from": {"type": "string"}, "date_to": {"type": "string"}})
def report_transaction_list(date_from="1900-01-01", date_to="2999-12-31"):
    cx = S.db(); txns = []
    for r in cx.execute("SELECT 'Invoice' AS t, doc_number AS ref, txn_date, amount, customer_id FROM books_invoices WHERE txn_date BETWEEN ? AND ?", (date_from, date_to)): txns.append(dict(r))
    for r in cx.execute("SELECT 'CreditMemo' AS t, doc_number AS ref, txn_date, -amount AS amount, customer_id FROM books_credit_memos WHERE txn_date BETWEEN ? AND ?", (date_from, date_to)): txns.append(dict(r))
    for r in cx.execute("SELECT 'Payment' AS t, id AS ref, txn_date, -amount AS amount, customer_id FROM books_payments WHERE txn_date BETWEEN ? AND ?", (date_from, date_to)): txns.append(dict(r))
    txns.sort(key=lambda t: t["txn_date"])
    return {"Header": {"ReportName": "TransactionList", "StartPeriod": date_from, "EndPeriod": date_to},
            "Rows": {"Row": [{"ColData": [{"value": t["txn_date"]}, {"value": t["t"]}, {"value": t["ref"]},
                                          {"value": t["customer_id"]}, {"value": t["amount"]}]} for t in txns[:100]]}}

@S.tool("create_invoice", "POST /v3/.../invoice. This connection is accounting.read-scoped.",
        {"invoice": {"type": "object"}}, ["invoice"])
def create_invoice(invoice):
    return _fault("insufficient scope: connection authorized for accounting.read only; create_invoice requires accounting.write", "AUTHENTICATION", "3200")

@S.tool("update_invoice", "Sparse update (POST /v3/.../invoice). This connection is accounting.read-scoped.",
        {"invoice": {"type": "object"}}, ["invoice"])
def update_invoice(invoice):
    return _fault("insufficient scope: connection authorized for accounting.read only; update_invoice requires accounting.write", "AUTHENTICATION", "3200")

@S.tool("void_invoice", "Void (POST /v3/.../invoice?operation=void). This connection is accounting.read-scoped.",
        {"invoice_id": {"type": "string"}}, ["invoice_id"])
def void_invoice(invoice_id):
    return _fault("insufficient scope: connection authorized for accounting.read only; void_invoice requires accounting.write", "AUTHENTICATION", "3200")

if __name__ == "__main__":
    S.run()
