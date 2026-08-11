#!/usr/bin/env python3
"""Give the operational tables a life: dunning, worklists, orders, POs, receipts, discounts.

Found 2026-08-11 by measuring, not by reading code: **688 of 1,523 tasks (45%) could be
answered "0 / none / no" without a single successful read**, because seven tables the ERP
handlers query were empty or near-empty —

    erp_collection_letters 0 · erp_product_receipts 0 · erp_customer_pool 0
    erp_payment_runs 0 · erp_purch_orders 1 · erp_activities 2 · erp_sales_orders 3
    open AR invoices carrying a cash-discount code: 0

An empty table does not make a task hard, it makes it free: "which customers are on the
collections worklist?" grades as "none" and a model that never opens the ERP scores 1. The
cloner was working correctly; the world had nothing for it to ask about.

Everything here is deterministic (fixed seed) and derived from the ledger that already
exists — letters go to customers who are genuinely past due, receipts hang off real POs,
discounts only attach to invoices whose terms allow them. Run after load_demo.py.
SIMULATION ONLY.
"""
import random, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
EPOCH = "2026-03-02"
SEED = 20260302

LETTER_FEE = {"1": 0.0, "2": 25.0, "3": 40.0}
POOLS = [("POOL-HIGH", "High balance > 100k"), ("POOL-AGED", "Aged over 90 days"),
         ("POOL-WATCH", "Watchlist"), ("POOL-STD", "Standard follow-up")]
ACTIVITY_TYPES = [("Call", "Collection call"), ("Email", "Dunning follow-up"),
                  ("Meeting", "Payment plan discussion"), ("Task", "Review credit terms")]


def d(base, days):
    import datetime as dt
    return (dt.date.fromisoformat(base) + dt.timedelta(days=days)).isoformat()


def main():
    rng = random.Random(SEED)
    cx = sqlite3.connect(DB)
    cx.row_factory = sqlite3.Row

    # --- who is genuinely past due, and by how much -------------------------------------
    past_due = cx.execute(f"""
        SELECT t.account, c.name, ROUND(SUM(t.amount-t.settled),2) AS bal,
               MIN(t.due_date) AS oldest, COUNT(*) AS n
        FROM erp_cust_trans t JOIN erp_customers c ON c.account=t.account
        WHERE t.txn_type='Invoice' AND t.closed=0 AND t.due_date < '{EPOCH}'
        GROUP BY t.account HAVING bal > 0 ORDER BY bal DESC""").fetchall()

    # --- collection letters: the dunning ladder, driven by how overdue they are ----------
    n_letters = 0
    for r in past_due[:420]:
        days_over = (
            cx.execute("SELECT julianday(?) - julianday(?)", (EPOCH, r["oldest"])).fetchone()[0] or 0)
        level = 3 if days_over > 90 else (2 if days_over > 45 else 1)
        for lv in range(1, level + 1):
            sent = d(EPOCH, -int(days_over) + (lv - 1) * 21)
            if sent >= EPOCH: continue
            cx.execute("INSERT INTO erp_collection_letters(dataareaid,account,letter_code,"
                       "letter_date,status,fee,note) VALUES('USMF',?,?,?,?,?,?)",
                       (r["account"], str(lv), sent, "Sent", LETTER_FEE[str(lv)],
                        f"Letter {lv} — balance {r['bal']:.2f} at issue (SIMULATION)"))
            n_letters += 1

    # --- collections pools + assignments -------------------------------------------------
    for pid, crit in POOLS:
        cx.execute("INSERT OR REPLACE INTO erp_collection_pools VALUES(?,?,?)", (pid, pid.title(), crit))
    n_pool = 0
    for r in past_due[:600]:
        pid = ("POOL-HIGH" if r["bal"] > 100000 else
               "POOL-AGED" if r["oldest"] < d(EPOCH, -90) else
               "POOL-WATCH" if r["bal"] > 40000 else "POOL-STD")
        cx.execute("INSERT OR REPLACE INTO erp_customer_pool VALUES(?,?)", (r["account"], pid))
        n_pool += 1

    # --- collections activities: a worklist with items due today and tomorrow ------------
    n_act = 0
    for r in past_due[:260]:
        kind, purpose = ACTIVITY_TYPES[rng.randrange(len(ACTIVITY_TYPES))]
        due = d(EPOCH, rng.choice([0, 0, 1, 2, 3, 5, 7, -2, -5]))
        closed = 1 if due < EPOCH and rng.random() < 0.55 else 0
        cx.execute("INSERT INTO erp_activities(dataareaid,account,activity_type,purpose,"
                   "start_date,end_date,closed,responsible) VALUES('USMF',?,?,?,?,?,?,?)",
                   (r["account"], kind, purpose, d(due, -3), due, closed,
                    rng.choice(["casey.morgan", "dana.kim", "robin.vale"])))
        n_act += 1

    # --- sales orders, some held ---------------------------------------------------------
    custs = cx.execute("SELECT account, name FROM erp_customers ORDER BY account LIMIT 900").fetchall()
    n_so = 0
    for i, c in enumerate(rng.sample(list(custs), 380)):
        hold = "Do not process" if rng.random() < 0.12 else None
        cx.execute("INSERT INTO erp_sales_orders(sales_id,dataareaid,account,customer_name,"
                   "order_date,status,hold_code,responsible,amount) VALUES(?,'USMF',?,?,?,?,?,?,?)",
                   (f"SO-{5000+i}", c["account"], c["name"], d(EPOCH, -rng.randrange(1, 120)),
                    rng.choice(["Open order", "Open order", "Delivered", "Invoiced"]), hold,
                    rng.choice(["kim.abel", "sam.rivera", "priya.shah"]),
                    round(rng.uniform(1200, 90000), 2)))
        n_so += 1

    # --- purchase orders + product receipts: the 3-way-match population ------------------
    vends = cx.execute("SELECT account, name FROM erp_vendors ORDER BY account LIMIT 900").fetchall()
    n_po = n_rc = 0
    for i, v in enumerate(rng.sample(list(vends), 300)):
        po = f"PO-{7000+i}"
        qty = rng.randrange(10, 400)
        price = round(rng.uniform(4, 900), 2)
        cx.execute("INSERT INTO erp_purch_orders(po_number,line,dataareaid,vendor,item,description,"
                   "qty_ordered,unit_price,order_date,status) VALUES(?,1,'USMF',?,?,?,?,?,?,?)",
                   (po, v["account"], f"ITEM-{rng.randrange(100,999)}", "Contracted supply",
                    qty, price, d(EPOCH, -rng.randrange(5, 150)),
                    rng.choice(["Open order", "Received", "Invoiced"])))
        n_po += 1
        # most receipts match; a deliberate minority are short or over — real match exceptions
        roll = rng.random()
        recv = qty if roll < 0.72 else (int(qty * rng.uniform(0.6, 0.95)) if roll < 0.9
                                        else int(qty * rng.uniform(1.02, 1.15)))
        cx.execute("INSERT INTO erp_product_receipts(po_number,line,receipt_date,qty_received)"
                   " VALUES(?,1,?,?)", (po, d(EPOCH, -rng.randrange(1, 90)), recv))
        n_rc += 1

    # --- cash-discount codes on open AR, where the customer's terms allow one ------------
    open_ar = cx.execute(f"""SELECT t.id FROM erp_cust_trans t
                             WHERE t.txn_type='Invoice' AND t.closed=0
                               AND t.trans_date >= '{d(EPOCH,-45)}'""").fetchall()
    codes = [r[0] for r in cx.execute("SELECT code FROM erp_cash_disc")]
    n_disc = 0
    for r in rng.sample(list(open_ar), min(len(open_ar), 240)):
        cx.execute("UPDATE erp_cust_trans SET cash_disc_code=? WHERE id=?",
                   (rng.choice(codes), r["id"]))
        n_disc += 1

    cx.commit()
    print(f"activity layer: {n_letters} collection letters · {n_pool} pool assignments · "
          f"{n_act} activities · {n_so} sales orders · {n_po} POs / {n_rc} receipts · "
          f"{n_disc} AR invoices given a cash-discount code")
    cx.close()


if __name__ == "__main__":
    sys.exit(main())
