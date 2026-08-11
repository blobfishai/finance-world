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
    write_surface_refdata(cx)

def write_surface_refdata(cx):
    """Reference data for the write-and-approve surface (docs/HARD-LAYER-DESIGN.md M1/M2/M4).

    Task-specific rows (approval requests, payment runs, journals) live in per-task seeds;
    only world-level reference data belongs here. account_type vocabulary is Odoo's
    (research/odoo-domain.md); DoA rules follow ERPNext's Authorization Rule shape
    (transaction/based_on/value/approving_role), company-scoped rules shadowing global ones.
    """
    # Chart of accounts — the minimum that makes a balanced accrual/reclass journal postable.
    for code, name, atype, recon in [
            ("110100", "Bank — operating (USD)",        "asset_cash",        1),
            ("130100", "Accounts receivable",           "asset_receivable",  1),
            ("140100", "Prepaid expenses",              "asset_current",     0),
            ("150100", "Inventory",                     "asset_current",     0),
            ("200100", "Accounts payable",              "liability_payable", 1),
            ("210100", "Accrued liabilities",           "liability_current", 0),
            ("215100", "Accrued payroll & bonus",       "liability_current", 0),
            ("230100", "Deferred revenue",              "liability_current", 0),
            ("300100", "Retained earnings",             "equity",            0),
            ("400100", "Revenue — product",             "income",            0),
            ("400200", "Revenue — services",            "income",            0),
            ("500100", "Cost of goods sold",            "expense",           0),
            ("600100", "Professional fees",             "expense",           0),
            ("600200", "Software & subscriptions",      "expense",           0),
            ("600300", "Travel & entertainment",        "expense",           0),
            ("610100", "Rent expense",                  "expense",           0),
            ("690100", "FX gain / (loss)",              "expense",           0),
            ("999999", "Suspense — do not post",        "off_balance",       0)]:
        cx.execute("INSERT INTO erp_main_accounts(account_code,dataareaid,name,account_type,"
                   "currency,blocked,reconcilable,requires_dimension) VALUES(?,?,?,?,?,?,?,?)",
                   (code, "USMF", name, atype, "USD", 1 if code == "999999" else 0, recon,
                    "dept" if atype == "expense" else None))
    # Fiscal periods around the epoch: Jan closed, Feb on_hold (the close in flight), Mar open.
    for pid, s, e, st in [("2025-12", "2025-12-01", "2025-12-31", "closed"),
                          ("2026-01", "2026-01-01", "2026-01-31", "closed"),
                          ("2026-02", "2026-02-01", "2026-02-28", "on_hold"),
                          ("2026-03", "2026-03-01", "2026-03-31", "open")]:
        cx.execute("INSERT INTO erp_fiscal_periods VALUES(?,?,?,?,?)", (pid, "USMF", s, e, st))
    # Cash position: the constraint that makes the unsat-demand mechanic (M2) bite.
    for acct, name, bal, od in [("USMF-OPER", "Operating — First National", 1_250_000.00, 0.0),
                                ("USMF-PAYR", "Payroll — First National",     480_000.00, 0.0),
                                ("CESP-OPER", "CES Direct operating",          95_000.00, 25_000.00)]:
        cx.execute("INSERT INTO erp_bank_accounts VALUES(?,?,?,?,?,?,?)",
                   (acct, "USMF" if acct.startswith("USMF") else "CESP", name, "USD", bal,
                    EPOCH + "T08:00:00Z", od))
    # Delegation of authority. Thresholds are the amount ABOVE which the approving role is
    # required; the company-scoped USMF rule shadows the global one for vendor payments.
    for pid, doc, thr, applies, approving in [
            ("DOA-JE-01",  "Journal Entry",  25_000.00,  "Finance analyst",     "Controller"),
            ("DOA-JE-02",  "Journal Entry", 250_000.00,  "Controller",          "CFO"),
            ("DOA-PAY-01", "Payment Run",    50_000.00,  "Finance analyst",     "Controller"),
            ("DOA-PAY-02", "Payment Run",   500_000.00,  "Controller",          "CFO"),
            ("DOA-VEND-01","Vendor Bank Change", 0.00,   "AP specialist",       "Controller")]:
        cx.execute("INSERT INTO erp_approval_policies(policy_id,dataareaid,doc_type,based_on,"
                   "threshold_amount,currency,applies_to_role,approving_role,approving_user,"
                   "escalation_policy_id,active) VALUES(?,?,?,?,?,?,?,?,?,?,1)",
                   (pid, "USMF", doc, "Grand Total", thr, "USD", applies, approving, None,
                    "DOA-JE-02" if pid == "DOA-JE-01" else
                    "DOA-PAY-02" if pid == "DOA-PAY-01" else None))
    # Withholding-tax categories. Rates are the standard US statutory ones so the
    # arithmetic is checkable against a public reference rather than invented.
    for cat, desc, rate, thresh, ref in [
            ("backup_withholding", "Backup withholding - payee TIN missing or not certified", 24.0, 600.0, "IRC 3406 / Form W-9"),
            ("foreign_contractor",  "Non-US person, US-source services, no treaty claim",      30.0,   0.0, "IRC 1441 / Form W-8BEN"),
            ("foreign_treaty",      "Non-US person with a valid treaty claim on file",         15.0,   0.0, "Treaty article; Form W-8BEN Part II"),
            ("none",                "No withholding applies",                                   0.0,   0.0, "-"),
    ]:
        cx.execute("INSERT INTO erp_withholding_tax VALUES(?,?,?,?,?)", (cat, desc, rate, thresh, ref))

    # Deduction reason codes: the taxonomy an AR analyst codes a short-pay against.
    for code, desc, valid, owner, disp in [
            ("pricing_variance",     "Customer paid at a price different from the invoiced price", 0, "Sales", "verify against the order; concede only with Sales approval"),
            ("shortage_damage",      "Goods short-shipped or damaged in transit",                  1, "Logistics", "issue credit memo once the delivery evidence supports it"),
            ("promotional_allowance","Contracted promotional or volume allowance taken at payment",1, "Sales", "issue credit memo; allowance is contractual"),
            ("unauthorized",         "No contractual or evidential basis for the deduction",       0, "Collections", "charge back to the customer and pursue"),
            ("write_off_immaterial", "Below the materiality threshold for investigation",          1, "AR", "write off without investigation"),
            ("duplicate_payment",    "Customer deducted a prior overpayment",                      1, "AR", "offset against the identified overpayment"),
    ]:
        cx.execute("INSERT INTO erp_deduction_reasons VALUES(?,?,?,?,?)", (code, desc, valid, owner, disp))
    # FX rates — without a rate table M4 cannot re-derive any cross-currency amount.
    for f, t, rate in [("EUR", "USD", 1.0842), ("GBP", "USD", 1.2715), ("CAD", "USD", 0.7218),
                       ("USD", "EUR", 0.9223), ("USD", "GBP", 0.7865), ("USD", "CAD", 1.3854)]:
        cx.execute("INSERT INTO erp_fx_rates VALUES(?,?,?,?)", (f, t, EPOCH, rate))

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
