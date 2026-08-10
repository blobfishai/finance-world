#!/usr/bin/env python3
"""Build world/build/core.sqlite from the FinanceBenchmark raw extracts.

Master data: D365 customer/vendor DMF CSVs (1,000 each).
Transactions: AR/AP GL journal workbooks (data starts row 11; header row 10).
AR: debit on a Customer row = invoice; credit = customer payment.
AP: credit on a Vendor row = vendor invoice (payable); debit = payment to vendor.
Settlement: FIFO per account by transaction date. Aging snapshot: as of 2026-03-01.
Validated against the benchmark's own aged-balance ground truths (see __main__).
"""
import csv, sqlite3, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research/external/financebenchmark-extracts/data/fno_benchmark_data_raw/FO Benchmark_Data"
BUILD = ROOT / "world/build"
EPOCH = "2026-03-02"
SNAP_AS_OF = "2026-03-01"
TERM_DAYS = {"COD": 0, "Net10": 10, "Net15": 15, "Net30": 30, "Net45": 45, "Net60": 60}

def term_days(code): return TERM_DAYS.get(code, 30)

def d(x):
    if isinstance(x, dt.datetime): return x.date().isoformat()
    if isinstance(x, dt.date): return x.isoformat()
    m, day, y = str(x).split("/")
    return f"{y}-{int(m):02d}-{int(day):02d}"

def load_masters(cx):
    with open(RAW / "Master Data/D365_Customers_DMF_Final.csv", newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cx.execute("INSERT INTO erp_customers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                r["CustomerAccount"], "USMF", r["OrganizationName"], r["CustomerGroupId"],
                r["CurrencyCode"], r["PaymentTermsId"], None, float(r["CreditMax"] or 0),
                r["CreditRating"], r["CustomerHoldStatus"], r["AddressCity"], r["AddressState"],
                r["PrimaryContactPersonFirstName"], r["PrimaryContactEmail"], r["PrimaryContactPhone"]))
    with open(RAW / "Master Data/D365_Vendors_DMF_Final.csv", newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cx.execute("INSERT INTO erp_vendors VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                r["VendorAccountNumber"], "USMF", r["VendorOrganizationName"], r["VendorGroupId"],
                r["CurrencyCode"], r["PaymentTermsId"], None, r["PaymentMethodName"],
                r["VendorHoldStatus"], r["AddressCity"], r["AddressState"],
                r["PrimaryContactPersonFirstName"], r["PrimaryContactEmail"], r["PrimaryContactPhone"]))

def load_journal(cx, path, side):
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True)["Sheet1"]
    table, acct_type = ("erp_cust_trans", "Customer") if side == "cust" else ("erp_vend_trans", "Vendor")
    terms = dict(cx.execute(f"SELECT account, payment_term FROM {'erp_customers' if side=='cust' else 'erp_vendors'}"))
    inv_n = pay_n = 0
    for row in ws.iter_rows(min_row=11, values_only=True):
        date, company, atype, account, _main, desc, cur, debit, credit = row[:9]
        off_type, off_account = row[10], row[11]
        debit, credit = float(debit or 0), float(credit or 0)
        if atype == acct_type and account:            # direct subledger row
            pass
        elif off_type == acct_type and off_account:   # ledger row, party in offset (AP pattern)
            account = off_account
            # offset takes the opposite sign of the primary ledger amounts
            debit, credit = credit, debit
        else:
            continue
        tdate = d(date)
        if side == "cust": inv_amt, pay_amt = debit, credit      # AR: debit=invoice, credit=payment
        else:              inv_amt, pay_amt = credit, debit      # AP: credit=invoice, debit=payment
        if inv_amt > 0:
            inv_n += 1
            due = (dt.date.fromisoformat(tdate) + dt.timedelta(days=term_days(terms.get(account)))).isoformat()
            pre = "CIV" if side == "cust" else "VINV"
            cx.execute(f"INSERT INTO {table}(dataareaid,account,voucher,invoice,txn_type,description,trans_date,due_date,currency,amount) VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (company, account, f"{pre}V-{inv_n:06d}", f"{pre}-{inv_n:06d}", "Invoice", desc, tdate, due, cur, round(inv_amt, 2)))
        elif pay_amt > 0:
            pay_n += 1
            pre = "CPAY" if side == "cust" else "VPAY"
            cx.execute(f"INSERT INTO {table}(dataareaid,account,voucher,invoice,txn_type,description,trans_date,due_date,currency,amount) VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (company, account, f"{pre}V-{pay_n:06d}", f"{pre}-{pay_n:06d}", "Payment", desc or "Payment", tdate, tdate, cur, round(-pay_amt, 2)))
    return inv_n, pay_n

def settle_fifo(cx, table, side):
    accounts = [a for (a,) in cx.execute(f"SELECT DISTINCT account FROM {table}")]
    for acct in accounts:
        invs = cx.execute(f"SELECT id, amount FROM {table} WHERE account=? AND txn_type='Invoice' ORDER BY trans_date, id", (acct,)).fetchall()
        pays = cx.execute(f"SELECT id, amount, trans_date FROM {table} WHERE account=? AND txn_type IN ('Payment','CreditNote') ORDER BY trans_date, id", (acct,)).fetchall()
        i, open_inv = 0, [[iid, amt, 0.0] for iid, amt in invs]
        for pid, pamt, pdate in pays:
            remain = round(-pamt, 2)
            while remain > 0.004 and i < len(open_inv):
                iid, iamt, isett = open_inv[i]
                take = min(remain, round(iamt - isett, 2))
                if take > 0:
                    cx.execute("INSERT INTO erp_settlements(side,dataareaid,account,payment_id,invoice_id,amount,settle_date) VALUES(?,?,?,?,?,?,?)",
                               (side, "USMF", acct, pid, iid, round(take, 2), pdate))
                    open_inv[i][2] = round(isett + take, 2)
                    remain = round(remain - take, 2)
                if open_inv[i][2] >= open_inv[i][1] - 0.004: i += 1
            cx.execute(f"UPDATE {table} SET settled=?, closed=1 WHERE id=?", (round(pamt, 2), pid))
        for iid, iamt, isett in open_inv:
            cx.execute(f"UPDATE {table} SET settled=?, closed=? WHERE id=?", (isett, 1 if isett >= iamt - 0.004 else 0, iid))

def build_aging(cx):
    as_of = dt.date.fromisoformat(SNAP_AS_OF)
    rows = cx.execute("""SELECT t.account, c.name, t.due_date, t.amount - t.settled
                         FROM erp_cust_trans t JOIN erp_customers c ON c.account = t.account
                         WHERE t.txn_type='Invoice' AND t.closed=0""").fetchall()
    agg = {}
    for acct, name, due, open_amt in rows:
        b = agg.setdefault(acct, [name, 0, 0, 0, 0, 0])
        days = (as_of - dt.date.fromisoformat(due)).days
        idx = 1 if days <= 0 else 2 if days <= 30 else 3 if days <= 60 else 4 if days <= 90 else 5
        b[idx] = round(b[idx] + open_amt, 2)
    for acct, (name, nd, b1, b2, b3, b4) in agg.items():
        cx.execute("INSERT INTO erp_aging_snapshot VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (f"AGE-{SNAP_AS_OF}", SNAP_AS_OF, "USMF", acct, name, nd, b1, b2, b3, b4,
                    round(b1 + b2 + b3 + b4, 2)))

def refdata(cx):
    cx.execute("INSERT INTO erp_companies VALUES('USMF','Contoso Entertainment System USA (SIMULATED)')")
    for code, days, desc in [("COD",0,"Cash on delivery"),("Net10",10,"Net 10 days"),("Net15",15,"Net 15 days"),
                             ("Net30",30,"Net 30 days"),("Net45",45,"Net 45 days"),("Net60",60,"Net 60 days")]:
        cx.execute("INSERT INTO erp_payment_terms VALUES(?,?,?)", (code, days, desc))
    for code, pct, days, nxt, desc in [("2%10N30",2.0,10,None,"2% if paid within 10 days, net 30"),
                                       ("1%15N45",1.0,15,None,"1% if paid within 15 days, net 45"),
                                       ("5D10",10.0,5,"10D5","10% if paid within 5 days"),
                                       ("10D5",5.0,10,"14D2","5% if paid within 10 days"),
                                       ("14D2",2.0,14,None,"2% if paid within 14 days")]:
        cx.execute("INSERT INTO erp_cash_disc VALUES(?,?,?,?,?)", (code, pct, days, nxt, desc))
    cx.execute("INSERT INTO meta VALUES('WORLD_NOW', ?)", (EPOCH + "T12:00:00Z",))
    cx.execute("INSERT INTO meta VALUES('WORLD_NAME','finance-world core (SIMULATION ONLY)')")

def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    db = BUILD / "core.sqlite"
    if db.exists(): db.unlink()
    cx = sqlite3.connect(db)
    cx.executescript((ROOT / "world/schema.sql").read_text())
    refdata(cx); load_masters(cx)
    ar = load_journal(cx, RAW / "Transactional Data/AR_Journal_Import_Updated.xlsx", "cust")
    ap = load_journal(cx, RAW / "Transactional Data/AP_Journal_Import_Updated.xlsx", "vend")
    settle_fifo(cx, "erp_cust_trans", "AR"); settle_fifo(cx, "erp_vend_trans", "AP")
    build_aging(cx)
    cx.commit()
    print(f"AR invoices/payments: {ar}  AP invoices/payments: {ap}")
    print("--- validation vs FinanceBenchmark GT (Group 90, >90d past due, as of 2026-03-02, top 5) ---")
    for name, acct, amt in cx.execute("""
        SELECT c.name, t.account, ROUND(SUM(t.amount - t.settled),2) AS past_due
        FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account
        WHERE c.customer_group='90' AND t.txn_type='Invoice' AND t.closed=0
          AND julianday(?) - julianday(t.due_date) > 90
        GROUP BY t.account ORDER BY past_due DESC LIMIT 5""", (EPOCH,)):
        print(f"  {name} {acct}: {amt}")
    print("GT expects: The Phone Company SYNCUS-0025 182539.15; Northwind Traders Europe SYNCUS-0327 173961.25; Fourth Coffee Pro SYNCUS-0629 171810.59")
    cx.close()

if __name__ == "__main__":
    main()
