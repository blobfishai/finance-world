#!/usr/bin/env python3
"""Seed the Contoso demo-entity layer into core.sqlite.

microsoft/FinanceBenchmark runs against a D365 environment that is *demo data (Contoso
companies) + their synthetic SYNCUS/SYNVEN overlay*. Our ETL loads the shipped synthetic
overlay; this module adds the demo layer the eval's questions actually name (Birch
Company US-027, Cave Wholesales US-004, Acme Office Supplies 1001, Contoso Europe DE-001,
…) plus the D365 concepts those questions touch: sales orders, collections pools and
activities, methods of payment / payment accounts, disputes and deductions.

Balances are authored (small, hand-checkable) so every cloned question has an exact,
in-world ground truth. Run after load_core.py. SIMULATION ONLY.
"""
import sqlite3, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
EPOCH = "2026-03-02"

CUSTOMERS = [
    # account, name, group, terms, credit_max, rating, hold, city, state, contact, email
    ("US-003", "Forest Wholesales",       "30", "Net30",  250000, "Good",      "Open", "Chicago",   "IL", "Ana",   "ana@forest-sim.example"),
    ("US-004", "Cave Wholesales",         "30", "Net30",  150000, "Fair",      "Open", "Phoenix",   "AZ", "Bo",    "bo@cave-sim.example"),
    ("US-007", "Desert Wholesales",       "30", "Net45",  200000, "Good",      "Open", "Las Vegas", "NV", "Cy",    "cy@desert-sim.example"),
    ("US-018", "Contoso Retail Detroit",  "10", "Net30",  300000, "Excellent", "Open", "Detroit",   "MI", "Dee",   "dee@contoso-sim.example"),
    ("US-023", "Northwind Traders",       "20", "Net30",  180000, "Good",      "Open", "Boston",    "MA", "Eli",   "eli@northwind-sim.example"),
    ("US-027", "Birch Company",           "10", "Net30",  120000, "Good",      "Open", "Portland",  "OR", "Fay",   "fay@birch-sim.example"),
    ("DE-001", "Contoso Europe",          "40", "Net45",  500000, "Excellent", "Open", "Munich",    "BY", "Gus",   "gus@contoso-eu-sim.example"),
]
VENDORS = [
    ("1001",   "Acme Office Supplies",      "40", "Net30",  "0.5%D10", "CHECK",      "No"),
    ("1002",   "Lande Packaging Supplies",  "30", "Net30",  None,      "ELECTRONIC", "No"),
    ("US-101", "Fabrikam Electronics",      "20", "Net45",  None,      "CHECK",      "No"),
]
# Birch Company open invoices — the eval's "unpaid invoices for Birch Company" question.
BIRCH = [("000105", "2025-11-14", 353.29), ("000110", "2025-12-05", 361.79),
         ("000115", "2026-01-09", 369.03), ("000120", "2026-02-06", 376.41)]

def main():
    cx = sqlite3.connect(DB)
    def ex(sql, args=()): cx.execute(sql, args)

    for a, n, g, t, cm, cr, h, city, st, cn, em in CUSTOMERS:
        ex("""INSERT OR REPLACE INTO erp_customers
              (account,dataareaid,name,customer_group,currency,payment_term,cash_disc_code,
               credit_max,credit_rating,on_hold,city,state,contact_name,contact_email,phone)
              VALUES(?,'USMF',?,?,?,?,NULL,?,?,?,?,?,?,?,?)""",
           (a, n, g, "EUR" if a.startswith("DE") else "USD", t, cm, cr, h, city, st, cn, em, "555-0100"))
    for a, n, g, t, cd, pm, h in VENDORS:
        ex("""INSERT OR REPLACE INTO erp_vendors
              (account,dataareaid,name,vendor_group,currency,payment_term,cash_disc_code,
               payment_method,on_hold,city,state,contact_name,contact_email,phone)
              VALUES(?,'USMF',?,?,'USD',?,?,?,?,?,?,?,?,?)""",
           (a, n, g, t, cd, pm, h, "Seattle", "WA", "Sam", f"ap@{n.split()[0].lower()}-sim.example", "555-0111"))

    ex("INSERT OR REPLACE INTO erp_cash_disc VALUES('0.5%D10',0.5,10,NULL,'0.5% 10 days discount')")

    # --- transactions -----------------------------------------------------
    for inv, d_, amt in BIRCH:
        due = (dt.date.fromisoformat(d_) + dt.timedelta(days=30)).isoformat()
        ex("""INSERT INTO erp_cust_trans(dataareaid,account,voucher,invoice,txn_type,description,
              trans_date,due_date,currency,amount,settled,closed)
              VALUES('USMF','US-027',?,?,'Invoice','Retail supply order',?,?,'USD',?,0,0)""",
           (f"BIRV-{inv}", inv, d_, due, amt))
    # Contoso Retail Detroit payment history (largest payment question)
    for v, d_, amt in [("ARPM000080", "2025-04-28", 187707.98), ("ARPM000112", "2025-09-15", 54210.00)]:
        ex("""INSERT INTO erp_cust_trans(dataareaid,account,voucher,invoice,txn_type,description,
              trans_date,due_date,currency,amount,settled,closed,payment_method)
              VALUES('USMF','US-018',?,?,'Payment','Customer payment',?,?,'USD',?,?,1,'CHECK')""",
           (v, v, d_, d_, -amt, -amt))
    # Contoso Europe invoicing history (EUR — also the EUR vendor-balance neighbourhood)
    for i, (d_, amt) in enumerate([("2025-10-02", 382761.50), ("2025-11-02", 191380.75),
                                   ("2025-12-02", 95690.25)], start=667):
        due = (dt.date.fromisoformat(d_) + dt.timedelta(days=45)).isoformat()
        ex("""INSERT INTO erp_cust_trans(dataareaid,account,voucher,invoice,txn_type,description,
              trans_date,due_date,currency,amount,settled,closed)
              VALUES('USMF','DE-001',?,?,'Invoice','European distribution',?,?,'EUR',?,0,0)""",
           (f"CIVV-{i:06d}", f"CIV-{i:06d}", d_, due, amt))
    # Cave Wholesales: one disputed transaction + one open deduction (dispute/deduction scenarios)
    ex("""INSERT INTO erp_cust_trans(dataareaid,account,voucher,invoice,txn_type,description,
          trans_date,due_date,currency,amount,settled,closed,disputed)
          VALUES('USMF','US-004','CAVV-01','CAV-001','Invoice','Bulk order Q1','2026-01-12','2026-02-11','USD',18400.00,0,0,1)""")
    ex("""INSERT INTO erp_cust_trans(dataareaid,account,voucher,invoice,txn_type,description,
          trans_date,due_date,currency,amount,settled,closed,deduction)
          VALUES('USMF','US-004','CAVV-02','CAV-DED-01','CreditNote','Short-pay deduction: damaged pallet','2026-02-02','2026-02-02','USD',-1250.00,0,0,1)""")
    # Forest Wholesales unapplied credit note
    ex("""INSERT INTO erp_cust_trans(dataareaid,account,voucher,invoice,txn_type,description,
          trans_date,due_date,currency,amount,settled,closed)
          VALUES('USMF','US-003','FORV-CN1','FOR-CN-001','CreditNote','Returned goods credit','2026-02-18','2026-02-18','USD',-3400.00,0,0)""")
    # AP: Acme open invoices + an open purchase order; Lande has nothing pending (empty-answer)
    for inv, d_, amt in [("ACM-9001", "2026-02-05", 4820.00), ("ACM-9002", "2026-02-19", 2615.50)]:
        due = (dt.date.fromisoformat(d_) + dt.timedelta(days=30)).isoformat()
        ex("""INSERT INTO erp_vend_trans(dataareaid,account,voucher,invoice,txn_type,description,
              trans_date,due_date,currency,amount,settled,closed,cash_disc_code)
              VALUES('USMF','1001',?,?,'Invoice','Office supplies',?,?,'USD',?,0,0,'0.5%D10')""",
           (f"ACMV-{inv}", inv, d_, due, amt))
    ex("""INSERT INTO erp_vend_trans(dataareaid,account,voucher,invoice,txn_type,description,
          trans_date,due_date,currency,amount,settled,closed)
          VALUES('USMF','US-101','FABV-01','FAB-7781','Invoice','Components shipment','2026-01-30','2026-03-01','EUR',294.72,0,0)""")
    ex("""INSERT INTO erp_purch_orders VALUES('39',1,'USMF','1001','PAPER-A4','Copy paper cases',
          200,24.10,'2026-02-10','Open')""")

    # --- D365 concepts the eval's questions touch -------------------------
    ex("""INSERT OR REPLACE INTO erp_sales_orders VALUES
          ('724','USMF','US-027','Birch Company','2026-02-18','Open order','Do not process','Karl Bystrom',15400.00)""")
    ex("""INSERT OR REPLACE INTO erp_sales_orders VALUES
          ('725','USMF','US-004','Cave Wholesales','2026-02-20','Open order',NULL,'Karl Bystrom',8200.00)""")
    ex("""INSERT OR REPLACE INTO erp_sales_orders VALUES
          ('726','USMF','US-018','Contoso Retail Detroit','2026-02-24','Delivered',NULL,'Tricia Miller',22750.00)""")
    ex("""INSERT OR REPLACE INTO erp_activities VALUES
          ('ACT-1001','USMF','US-004','Task','Follow up on Promise to pay broken','2026-02-19','2026-02-20',0,'Casey Morgan')""")
    ex("""INSERT OR REPLACE INTO erp_activities VALUES
          ('ACT-1002','USMF','US-027','Phone call','Payment plan discussion','2026-02-10','2026-02-10',1,'Casey Morgan')""")
    ex("INSERT OR REPLACE INTO erp_collection_pools VALUES('POOL-PASTDUE','Past due over 30 days','Aging bucket 31+')")
    for m, side, desc, acct in [("CHECK", "vend", "Check", "USMF OPER"),
                                ("Payroll_CK", "vend", "Payroll check", "USMF PAYRL"),
                                ("ELECTRONIC", "vend", "Electronic payment", "USMF OPER"),
                                ("CHECK", "cust", "Customer check", "USMF OPER")]:
        ex("INSERT OR REPLACE INTO erp_methods_of_payment VALUES(?,?,'USMF',?,?)", (m, side, desc, acct))

    cx.commit()
    n = lambda q: cx.execute(q).fetchone()[0]
    print(f"demo layer: {n('SELECT COUNT(*) FROM erp_customers')} customers, "
          f"{n('SELECT COUNT(*) FROM erp_vendors')} vendors, "
          f"{n('SELECT COUNT(*) FROM erp_sales_orders')} sales orders, "
          f"{n('SELECT COUNT(*) FROM erp_activities')} activities, "
          f"{n('SELECT COUNT(*) FROM erp_methods_of_payment')} payment methods")
    print("Birch open total:", n("SELECT ROUND(SUM(amount-settled),2) FROM erp_cust_trans WHERE account='US-027' AND closed=0"))
    cx.close()

if __name__ == "__main__":
    main()
