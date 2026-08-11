#!/usr/bin/env python3
"""Clone microsoft/FinanceBenchmark erp_qa questions into working finance-world tasks.

Each generated task keeps the benchmark's question **verbatim** (that's the clone) but its
ground truth is **recomputed in-world** from core.sqlite — never copied from the benchmark's
prose, which does not reconcile with its own shipped data (docs/AUDIT.md A3). Grading is
deterministic field checks instead of the benchmark's LLM judge.

Usage: python3 world/etl/clone_fb_erp.py [--per-scenario N] [--out tasks/erp_qa_fb]
"""
import argparse, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
DATASET = ROOT / "research/external/financebenchmark-extracts/data/dataset.yaml"
EPOCH = "2026-03-02"

def slug(s, n=48):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:n]

def resolve(cx, query, segment):
    """Entity by explicit account id, else the longest master-data name appearing in the text."""
    m = re.search(r"\b(SYN(?:CUS|VEN)-\d{4}|US-\d{3}|DE-\d{3}|\b1001\b|\b1002\b)", query)
    if m:
        for tbl in ("erp_customers", "erp_vendors"):
            r = cx.execute(f"SELECT account, name FROM {tbl} WHERE account=?", (m.group(1),)).fetchone()
            if r: return r[0], r[1], ("vend" if tbl == "erp_vendors" else "cust")
    ql = query.lower()
    best = None
    for tbl, side in (("erp_vendors", "vend"), ("erp_customers", "cust")) if segment == "AP" \
                     else (("erp_customers", "cust"), ("erp_vendors", "vend")):
        for acct, name in cx.execute(f"SELECT account, name FROM {tbl}"):
            if name and len(name) > 4 and name.lower() in ql:
                if not best or len(name) > len(best[1]): best = (acct, name, side)
    return best if best else (None, None, None)

def one(cx, sql, args=()):
    r = cx.execute(sql, args).fetchone()
    return r[0] if r and r[0] is not None else 0

# --- scenario handlers: return (fields{name:(value,type)}, walk_steps, hint) ------------
def h_credit_limit(cx, acct, name, side, q):
    v = one(cx, "SELECT credit_max FROM erp_customers WHERE account=?", (acct,))
    return ({"credit_limit": (v, "number"), "customer_name": (name, "contains")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": acct}})],
            {"credit_limit": f"SELECT credit_max FROM erp_customers WHERE account='{acct}'"})

def h_credit_rating(cx, acct, name, side, q):
    v = cx.execute("SELECT credit_rating FROM erp_customers WHERE account=?", (acct,)).fetchone()[0]
    return ({"credit_rating": (v, "contains"), "customer_name": (name, "contains")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": acct}})])

def h_customer_setup(cx, acct, name, side, q):
    v = cx.execute("SELECT payment_term FROM erp_customers WHERE account=?", (acct,)).fetchone()[0]
    return ({"payment_terms": (v, "contains"), "customer_account": (acct, "contains")},
            [("data_find_entities", {"entity": "Customers", "filters": {"account": acct}}),
             ("data_find_entities", {"entity": "PaymentTerms", "filters": {"code": v}})])

def h_outstanding(cx, acct, name, side, q):
    n = one(cx, "SELECT COUNT(*) FROM erp_cust_trans WHERE account=? AND txn_type='Invoice' AND closed=0", (acct,))
    t = round(one(cx, "SELECT SUM(amount-settled) FROM erp_cust_trans WHERE account=? AND txn_type='Invoice' AND closed=0", (acct,)), 2)
    _w = f"account='{acct}' AND txn_type='Invoice' AND closed=0"
    return ({"unpaid_invoice_count": (n, "number"), "unpaid_total": (t, "number")},
            [("data_find_entities_sql", {"sql": f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open FROM erp_cust_trans WHERE {_w}"})],
            {"unpaid_invoice_count": f"SELECT COUNT(*) FROM erp_cust_trans WHERE {_w}",
             "unpaid_total": f"SELECT ROUND(SUM(amount-settled),2) FROM erp_cust_trans WHERE {_w}"})

def h_aged_balance(cx, acct, name, side, q):
    grp = re.search(r"[Gg]roup (\d+)", q)
    if acct and not grp and not re.search(r"top \d+", q, re.I):
        # "aging breakdown / aged balance for <customer>" -> the customer's buckets
        import datetime as _dt
        rows = cx.execute("""SELECT due_date, amount-settled AS open FROM erp_cust_trans
                             WHERE account=? AND txn_type='Invoice' AND closed=0""", (acct,)).fetchall()
        b = {"not_due": 0.0, "b1_30": 0.0, "b31_60": 0.0, "b61_90": 0.0, "b90_plus": 0.0}
        for due, open_amt in rows:
            d = (_dt.date.fromisoformat(EPOCH) - _dt.date.fromisoformat(due)).days
            k = "not_due" if d <= 0 else "b1_30" if d <= 30 else "b31_60" if d <= 60 else "b61_90" if d <= 90 else "b90_plus"
            b[k] = round(b[k] + open_amt, 2)
        past_due = round(b["b1_30"] + b["b31_60"] + b["b61_90"] + b["b90_plus"], 2)
        return ({"total_past_due": (past_due, "number"),
                 "not_yet_due": (round(b["not_due"], 2), "number"),
                 "over_90_days": (b["b90_plus"], "number")},
                [("api_find_actions", {"query": "aged balances"}),
                 ("api_invoke_action", {"action": "ContosoCustAgedBalancesLive",
                                        "parameters": {"customer_account": acct}})])
    topn = int((re.search(r"top (\d+)", q, re.I) or [0, 10])[1]) if re.search(r"top (\d+)", q, re.I) else 10
    days = 90 if "90" in q else 0
    where = "t.txn_type='Invoice' AND t.closed=0"
    args = []
    if grp: where += " AND c.customer_group=?"; args.append(grp.group(1))
    if days: where += f" AND julianday('{EPOCH}') - julianday(t.due_date) > {days}"
    else: where += f" AND t.due_date < '{EPOCH}'"
    if acct and not grp: where += " AND t.account=?"; args.append(acct)
    rows = cx.execute(f"""SELECT c.name, t.account, ROUND(SUM(t.amount-t.settled),2) AS pd
                          FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account
                          WHERE {where} GROUP BY t.account ORDER BY pd DESC LIMIT {topn}""", args).fetchall()
    if not rows: return None
    return ({"top_customer_account": (rows[0][1], "contains"),
             "top_customer_past_due": (round(rows[0][2], 2), "number"),
             "customers_listed": (len(rows), "number")},
            [("data_find_entities_sql", {"sql": f"SELECT c.name, t.account, ROUND(SUM(t.amount-t.settled),2) AS past_due FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account WHERE {where.replace('?', repr(args[0]) if args else '?')} GROUP BY t.account ORDER BY past_due DESC LIMIT {topn}"})])

def h_payment_history(cx, acct, name, side, q):
    r = cx.execute("""SELECT voucher, trans_date, ROUND(-amount,2) FROM erp_cust_trans
                      WHERE account=? AND txn_type='Payment' ORDER BY -amount DESC LIMIT 1""", (acct,)).fetchone()
    if not r: return ({"largest_payment_amount": ("none", "string"), "largest_payment_voucher": ("none", "string")},
                      [("data_find_entities_sql", {"sql": f"SELECT voucher, trans_date, ROUND(-amount,2) AS paid FROM erp_cust_trans WHERE account='{acct}' AND txn_type='Payment'"})])
    return ({"largest_payment_amount": (r[2], "number"), "largest_payment_voucher": (r[0], "contains"),
             "largest_payment_date": (r[1], "contains")},
            [("data_find_entities_sql", {"sql": f"SELECT voucher, trans_date, ROUND(-amount,2) AS paid FROM erp_cust_trans WHERE account='{acct}' AND txn_type='Payment' ORDER BY paid DESC"})])

def h_invoicing_history(cx, acct, name, side, q):
    n = one(cx, "SELECT COUNT(*) FROM erp_cust_trans WHERE account=? AND txn_type='Invoice'", (acct,))
    t = round(one(cx, "SELECT SUM(amount) FROM erp_cust_trans WHERE account=? AND txn_type='Invoice'", (acct,)), 2)
    return ({"invoice_count": (n, "number"), "invoiced_total": (t, "number")},
            [("data_find_entities_sql", {"sql": f"SELECT COUNT(*) AS n, ROUND(SUM(amount),2) AS total FROM erp_cust_trans WHERE account='{acct}' AND txn_type='Invoice'"})],
            {"invoice_count": f"SELECT COUNT(*) FROM erp_cust_trans WHERE account='{acct}' AND txn_type='Invoice'",
             "invoiced_total": f"SELECT ROUND(SUM(amount),2) FROM erp_cust_trans WHERE account='{acct}' AND txn_type='Invoice'"})

def h_vendor_balance(cx, acct, name, side, q):
    cur = "EUR" if "eur" in q.lower() else ("USD" if "usd" in q.lower() else None)
    if cur:
        t = round(one(cx, "SELECT SUM(amount-settled) FROM erp_vend_trans WHERE currency=? AND txn_type='Invoice' AND closed=0", (cur,)), 2)
        return ({"ap_balance": (t, "number"), "currency": (cur, "contains")},
                [("data_find_entities_sql", {"sql": f"SELECT ROUND(SUM(amount-settled),2) AS ap_balance FROM erp_vend_trans WHERE currency='{cur}' AND txn_type='Invoice' AND closed=0"})])
    t = round(one(cx, "SELECT SUM(amount-settled) FROM erp_vend_trans WHERE account=? AND txn_type='Invoice' AND closed=0", (acct,)), 2)
    return ({"ap_balance": (t, "number"), "vendor_account": (acct, "contains")},
            [("data_find_entities_sql", {"sql": f"SELECT ROUND(SUM(amount-settled),2) AS ap_balance FROM erp_vend_trans WHERE account='{acct}' AND txn_type='Invoice' AND closed=0"})],
            {"ap_balance": f"SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_vend_trans WHERE account='{acct}' AND txn_type='Invoice' AND closed=0"})

def h_vendors_discount(cx, acct, name, side, q):
    code = cx.execute("SELECT cash_disc_code FROM erp_vendors WHERE account=?", (acct,)).fetchone()[0]
    if not code:
        return ({"offers_discount": ("no", "string"), "discount_code": ("none", "string")},
                [("data_find_entities", {"entity": "Vendors", "filters": {"account": acct}})])
    pct = one(cx, "SELECT percent FROM erp_cash_disc WHERE code=?", (code,))
    return ({"offers_discount": ("yes", "string"), "discount_code": (code, "contains"),
             "discount_percent": (pct, "number")},
            [("data_find_entities", {"entity": "Vendors", "filters": {"account": acct}}),
             ("data_find_entities", {"entity": "CashDiscounts", "filters": {"code": code}})])

def h_ap_invoices(cx, acct, name, side, q):
    n = one(cx, "SELECT COUNT(*) FROM erp_vend_trans WHERE account=? AND txn_type='Invoice' AND closed=0", (acct,))
    t = round(one(cx, "SELECT SUM(amount-settled) FROM erp_vend_trans WHERE account=? AND txn_type='Invoice' AND closed=0", (acct,)), 2)
    return ({"open_invoice_count": (n, "number"), "open_invoice_total": (t if n else "none", "number" if n else "string")},
            [("data_find_entities_sql", {"sql": f"SELECT invoice, due_date, ROUND(amount-settled,2) AS open FROM erp_vend_trans WHERE account='{acct}' AND txn_type='Invoice' AND closed=0"})])

def h_cash_discounts(cx, acct, name, side, q):
    n = one(cx, """SELECT COUNT(*) FROM erp_settlements s JOIN erp_cust_trans t ON t.id=s.invoice_id
                   WHERE s.account=? AND s.cash_disc_taken > 0""", (acct,))
    return ({"discount_payment_count": (n, "number")},
            [("data_find_entities_sql", {"sql": f"SELECT COUNT(*) AS n FROM erp_settlements WHERE account='{acct}' AND cash_disc_taken > 0"})])

def h_cash_collections(cx, acct, name, side, q):
    """Total cash collected from a customer in the current fiscal year (calendar FY here)."""
    t = round(one(cx, """SELECT SUM(-amount) FROM erp_cust_trans WHERE account=? AND txn_type='Payment'
                         AND trans_date >= ?""", (acct, EPOCH[:4] + "-01-01")), 2)
    n = one(cx, """SELECT COUNT(*) FROM erp_cust_trans WHERE account=? AND txn_type='Payment'
                   AND trans_date >= ?""", (acct, EPOCH[:4] + "-01-01"))
    return ({"total_collected_fy": (t if n else "none", "number" if n else "string"),
             "payment_count_fy": (n, "number")},
            [("data_find_entities_sql", {"sql": f"SELECT voucher, trans_date, ROUND(-amount,2) AS received FROM erp_cust_trans WHERE account='{acct}' AND txn_type='Payment' AND trans_date >= '{EPOCH[:4]}-01-01'"})])

def h_credit_notes(cx, acct, name, side, q):
    n = one(cx, "SELECT COUNT(*) FROM erp_cust_trans WHERE account=? AND txn_type='CreditNote' AND closed=0", (acct,))
    t = round(one(cx, "SELECT SUM(-amount) FROM erp_cust_trans WHERE account=? AND txn_type='CreditNote' AND closed=0", (acct,)), 2)
    return ({"unapplied_credit_note_count": (n, "number"),
             "unapplied_credit_total": (t if n else "none", "number" if n else "string")},
            [("data_find_entities_sql", {"sql": f"SELECT invoice, trans_date, ROUND(-amount,2) AS credit FROM erp_cust_trans WHERE account='{acct}' AND txn_type='CreditNote' AND closed=0"})])

def h_dispute(cx, acct, name, side, q):
    n = one(cx, "SELECT COUNT(*) FROM erp_cust_trans WHERE account=? AND disputed=1", (acct,))
    return ({"disputed_transaction_count": (n, "number")},
            [("data_find_entities_sql", {"sql": f"SELECT invoice, ROUND(amount,2) AS amount FROM erp_cust_trans WHERE account='{acct}' AND disputed=1"})],
            {"disputed_transaction_count": f"SELECT COUNT(*) FROM erp_cust_trans WHERE account='{acct}' AND disputed=1"})

def h_deductions(cx, acct, name, side, q):
    n = one(cx, "SELECT COUNT(*) FROM erp_cust_trans WHERE account=? AND deduction=1 AND closed=0", (acct,))
    t = round(one(cx, "SELECT SUM(-amount) FROM erp_cust_trans WHERE account=? AND deduction=1 AND closed=0", (acct,)), 2)
    return ({"open_deduction_count": (n, "number"),
             "open_deduction_total": (t if n else "none", "number" if n else "string")},
            [("data_find_entities_sql", {"sql": f"SELECT invoice, ROUND(-amount,2) AS deduction FROM erp_cust_trans WHERE account='{acct}' AND deduction=1 AND closed=0"})])

def h_collections_pool(cx, acct, name, side, q):
    assigned = one(cx, "SELECT COUNT(*) FROM erp_customer_pool")
    total = one(cx, "SELECT COUNT(*) FROM erp_customers")
    return ({"unassigned_customer_count": (total - assigned, "number")},
            [("data_find_entities_sql", {"sql": "SELECT COUNT(*) AS customers FROM erp_customers"}),
             ("data_find_entities_sql", {"sql": "SELECT COUNT(*) AS assigned FROM erp_customer_pool"})])

def h_collections_tasks(cx, acct, name, side, q):
    rows = cx.execute("SELECT activity_type, purpose, start_date FROM erp_activities WHERE account=? AND closed=0", (acct,)).fetchall()
    return ({"open_activity_count": (len(rows), "number"),
             "open_activity_purpose": (rows[0][1] if rows else "none", "contains" if rows else "string")},
            [("data_find_entities", {"entity": "Activities", "filters": {"account": acct}})])

def h_sales_orders(cx, acct, name, side, q):
    if "do not process" in q.lower():
        rows = cx.execute("SELECT sales_id, customer_name FROM erp_sales_orders WHERE hold_code='Do not process'").fetchall()
        return ({"order_count": (len(rows), "number"),
                 "sales_order_id": (rows[0][0] if rows else "none", "contains" if rows else "string")},
                [("data_find_entities", {"entity": "SalesOrders", "filters": {"hold_code": "Do not process"}})])
    rows = cx.execute("SELECT sales_id, status FROM erp_sales_orders WHERE account=?", (acct,)).fetchall()
    return ({"order_count": (len(rows), "number"),
             "sales_order_id": (rows[0][0] if rows else "none", "contains" if rows else "string")},
            [("data_find_entities", {"entity": "SalesOrders", "filters": {"account": acct}})])

def h_purchase_orders(cx, acct, name, side, q):
    rows = cx.execute("SELECT po_number, status FROM erp_purch_orders WHERE vendor=? AND status='Open'", (acct,)).fetchall()
    return ({"open_po_count": (len(rows), "number"),
             "purchase_order_number": (rows[0][0] if rows else "none", "contains" if rows else "string")},
            [("data_find_entities", {"entity": "PurchaseOrders", "filters": {"vendor": acct}})])

def h_ap_payments(cx, acct, name, side, q):
    rows = {m: a for m, a in cx.execute("SELECT method, payment_account FROM erp_methods_of_payment WHERE side='vend'")}
    if "payroll" in q.lower():
        return ({"payroll_ck_account": (rows.get("Payroll_CK", "none"), "contains"),
                 "check_account": (rows.get("CHECK", "none"), "contains")},
                [("data_find_entities", {"entity": "MethodsOfPayment", "filters": {"side": "vend"}})])
    return None

# A question only routes to a handler if its text really asks that question. FB's
# `scenario` label is coarse (e.g. "Aged Balance" also carries "coming due in 7 days"
# questions), and a mismatched route yields a task whose graded fields don't answer the
# prompt — prompt/verifier drift that field-name checks cannot see.
INTENT = {
    "Credit Limit": ["credit limit"],
    "Credit Rating": ["credit rating"],
    "Customer Setup": ["payment term", "terms are assigned", "terms assigned"],
    "Outstanding Balance": ["unpaid", "outstanding"],
    "Aged Balance": ["past due", "aged", "aging"],
    "Payment History": ["largest payment", "payment history", "payments made", "payment made"],
    "Cash Collections": ["collected", "collection"],
    "Invoicing History": ["invoices generated", "list of the invoices", "invoicing"],
    "Vendor Balance": ["vendor balance", "ap liability", "balance for transactions"],
    "Vendors": ["discount"],
    "AP Invoices": ["pending approval", "open invoices", "invoices are pending"],
    "Cash Disocunts": ["discount window", "within the discount"],
    "Credit Notes": ["credit note"],
    "Dispute": ["dispute"],
    "Discounts": ["deduction"],
    "Collections": ["pool", "unassigned"],
    "Collections Tasks": ["activit", "open task"],
    "Sales Orders": ["sales order"],
    "AP Purchase Orders": ["purchase order"],
    "AP Payments": ["method of payment", "methods of payment", "payment account"],
}

HANDLERS = {
    "Credit Limit": h_credit_limit, "Credit Rating": h_credit_rating,
    "Customer Setup": h_customer_setup, "Outstanding Balance": h_outstanding,
    "Aged Balance": h_aged_balance, "Payment History": h_payment_history,
    "Invoicing History": h_invoicing_history, "Vendor Balance": h_vendor_balance,
    "Vendors": h_vendors_discount, "AP Invoices": h_ap_invoices,
    "Cash Disocunts": h_cash_discounts, "Cash Collections": h_cash_collections,
    "Credit Notes": h_credit_notes, "Dispute": h_dispute, "Discounts": h_deductions,
    "Collections": h_collections_pool, "Collections Tasks": h_collections_tasks,
    "Sales Orders": h_sales_orders, "AP Purchase Orders": h_purchase_orders,
    "AP Payments": h_ap_payments,
}

def emit(out_dir, name, query, scenario, segment, fields, steps, sqls=None):
    sqls = sqls or {}
    d = out_dir / name
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "solution").mkdir(parents=True, exist_ok=True)
    walk = [{"server": "erp", "tool": t, "args": a} for t, a in steps]
    walk.append({"server": "harness", "tool": "submit_answer",
                 "args": {"answers": {k: v for k, (v, _) in fields.items()}}})
    (d / "solution/walk.json").write_text(json.dumps(walk, indent=1) + "\n")

    checks = {"answer_checks": [], "trace_checks": [
        {"type": "required_servers", "servers": ["erp"]}, {"type": "reads_before_submit"}],
        "state_checks": [{"type": "writes_only", "tables": ["answers"]}]}
    for k, (v, kind) in fields.items():
        if kind == "number":
            ac = {"field": k, "type": "number", "expect": v,
                  "tol_abs": 0.02 if isinstance(v, float) else 0}
            if k in sqls: ac["gt_sql"] = sqls[k]
            checks["answer_checks"].append(ac)
        elif kind == "contains":
            checks["answer_checks"].append({"field": k, "type": "contains_all", "expect": [str(v)]})
        else:
            checks["answer_checks"].append({"field": k, "type": "string", "expect": str(v)})
    (d / "tests/checks.json").write_text(json.dumps(checks, indent=1) + "\n")

    who = "Priya Shah · AP Manager" if segment == "AP" else "Casey Morgan · AR & Collections"
    lines = [f"**{who} · Teams**", "", query.strip(), "", "---", "",
             "Reply with `submit_answer`:", ""]
    for k, (v, kind) in fields.items():
        lines.append(f"- `{k}` ({'number' if kind == 'number' else 'text'})")
    lines.append("")
    (d / "instruction.md").write_text("\n".join(lines))

    (d / "task.toml").write_text(f'''schema_version = "1.4"

[task]
name = "{out_dir.name}/{name}"
version = "0.1.0"
description = "FinanceBenchmark erp_qa clone — {segment} / {scenario}."
authors = ["nario-ai"]
keywords = ["finance", "erp_qa", "financebenchmark-clone"]

[metadata]
family = "{out_dir.name}"
origin = "clone of microsoft/FinanceBenchmark erp_qa ({segment} / {scenario}); question verbatim, ground truth recomputed in-world (docs/AUDIT.md A3)"
difficulty = "medium"
acceptance_label = "pending_calibration"
walk_len = {len(walk)}

[verifier]
timeout_sec = 120
[agent]
timeout_sec = 600
[environment]
cpus = 1
memory_mb = 1024
''')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-scenario", type=int, default=4)
    ap.add_argument("--out", default="tasks/erp_qa_fb")
    a = ap.parse_args()
    import yaml
    data = yaml.safe_load(DATASET.read_text())
    erp = [t for t in data if t.get("plugin") == "erp_qa"]
    cx = sqlite3.connect(DB)
    out_dir = ROOT / a.out
    made, per, skipped, mismatched = 0, {}, {}, {}
    for t in erp:
        sc, seg, q = t.get("scenario"), t.get("segment"), t["query"]
        h = HANDLERS.get(sc)
        if not h: skipped[sc] = skipped.get(sc, 0) + 1; continue
        want = INTENT.get(sc, [])
        if want and not any(k in q.lower() for k in want):
            mismatched[sc] = mismatched.get(sc, 0) + 1; continue
        if per.get(sc, 0) >= a.per_scenario: continue
        acct, name, side = resolve(cx, q, seg)
        if not acct and sc not in ("Collections", "AP Payments", "Sales Orders", "Vendor Balance"):
            skipped[sc] = skipped.get(sc, 0) + 1; continue
        try: res = h(cx, acct, name, side, q)
        except Exception as e: skipped[sc] = skipped.get(sc, 0) + 1; continue
        if not res: skipped[sc] = skipped.get(sc, 0) + 1; continue
        fields, steps, sqls = (res + (None,))[:3] if len(res) < 3 else res
        per[sc] = per.get(sc, 0) + 1
        emit(out_dir, f"{slug(sc)}-{per[sc]}", q, sc, seg, fields, steps, sqls)
        made += 1
    print(f"generated {made} tasks into {a.out}")
    for k, v in sorted(per.items()): print(f"   {k}: {v}")
    if skipped: print("skipped (unresolvable/unsupported):", dict(sorted(skipped.items())))
    if mismatched: print("skipped (question intent != scenario label):", dict(sorted(mismatched.items())))

if __name__ == "__main__":
    main()
