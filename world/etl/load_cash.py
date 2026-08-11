#!/usr/bin/env python3
"""Give the ledger a cash life: payments, settlements, partials, discounts, disputes.

The benchmark's shipped journals are invoice-only, which left the world with 3,467 customer
invoices and 2 payments — no settlements, nothing ever closed by cash, no payment history,
and "did they pay in the discount window?" trivially zero. This module generates the
missing half of a subledger, deterministically (fixed seed), with behaviour that varies by
counterparty rather than uniformly:

  credit rating -> how they pay          | Excellent: 4 days early, almost always
                                         | Good:      ~3 days late, usually
                                         | Fair:      ~15 days late, often
                                         | Poor:      ~35 days late, sometimes not at all
  ~7% of customers carry 2/10 net 30 terms; some of those genuinely pay inside the window
  and take the discount (cash_disc_taken on the settlement).
  ~6% of payments are partial (short-pays), leaving the invoice open with settled > 0.
  A few invoices are disputed or carry credit notes.

Run after load_core.py and before load_demo.py. SIMULATION ONLY.
"""
import random, sqlite3, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
EPOCH = dt.date(2026, 3, 2)
SEED = 20260302

BEHAVIOUR = {   # rating: (days late mean, days late sd, probability of having paid)
    "Excellent": (-4, 3, 0.95),
    "Good":      (3, 6, 0.86),
    "Fair":      (15, 10, 0.70),
    "Poor":      (35, 18, 0.45),
}

def main():
    rng = random.Random(SEED)
    cx = sqlite3.connect(DB)
    cx.row_factory = sqlite3.Row

    # a slice of customers get early-payment terms, so discount questions have real answers
    custs = [dict(r) for r in cx.execute("SELECT account, credit_rating FROM erp_customers ORDER BY account")]
    disc_accounts = {c["account"] for c in custs if rng.random() < 0.07}
    for a in sorted(disc_accounts):
        cx.execute("UPDATE erp_customers SET cash_disc_code='2%10N30' WHERE account=?", (a,))
    rating = {c["account"]: (c["credit_rating"] or "Good") for c in custs}

    pay_seq = 0
    stats = dict(paid=0, partial=0, disc=0, disputed=0, credit_notes=0)
    invoices = cx.execute("""SELECT id, account, invoice, trans_date, due_date, amount, currency
                             FROM erp_cust_trans WHERE txn_type='Invoice' AND settled=0
                             ORDER BY account, trans_date, id""").fetchall()
    for inv in invoices:
        acct = inv["account"]
        late_mu, late_sd, p_paid = BEHAVIOUR.get(rating.get(acct, "Good"), BEHAVIOUR["Good"])
        due = dt.date.fromisoformat(inv["due_date"])
        if rng.random() > p_paid:
            continue                                    # still outstanding
        takes_discount = acct in disc_accounts and rng.random() < 0.55
        if takes_discount:
            pay_date = dt.date.fromisoformat(inv["trans_date"]) + dt.timedelta(days=rng.randint(3, 9))
        else:
            pay_date = due + dt.timedelta(days=max(-9, int(rng.gauss(late_mu, late_sd))))
        if pay_date >= EPOCH:                           # would settle after the world clock
            continue
        gross = round(inv["amount"], 2)
        disc = round(gross * 0.02, 2) if takes_discount else 0.0
        partial = (not takes_discount) and rng.random() < 0.06
        applied = round(gross * rng.uniform(0.35, 0.8), 2) if partial else round(gross - disc, 2)

        pay_seq += 1
        cx.execute("""INSERT INTO erp_cust_trans(dataareaid, account, voucher, invoice, txn_type,
                      description, trans_date, due_date, currency, amount, settled, closed, payment_method)
                      VALUES('USMF',?,?,?,'Payment',?,?,?,?,?,?,1,?)""",
                   (acct, f"ARPM{pay_seq:06d}", f"ARPM{pay_seq:06d}",
                    "Customer payment" + (" (discount taken)" if takes_discount else ""),
                    pay_date.isoformat(), pay_date.isoformat(), inv["currency"],
                    -applied, -applied, "CHECK" if rng.random() < 0.4 else "ELECTRONIC"))
        pid = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        settled_total = round(applied + disc, 2)
        closed = 1 if settled_total >= gross - 0.005 else 0
        cx.execute("UPDATE erp_cust_trans SET settled=?, closed=? WHERE id=?",
                   (settled_total, closed, inv["id"]))
        cx.execute("""INSERT INTO erp_settlements(side, dataareaid, account, payment_id, invoice_id,
                      amount, cash_disc_taken, settle_date) VALUES('AR','USMF',?,?,?,?,?,?)""",
                   (acct, pid, inv["id"], applied, disc, pay_date.isoformat()))
        stats["paid"] += 1
        stats["partial"] += 1 if partial else 0
        stats["disc"] += 1 if takes_discount else 0

    # a realistic sprinkle of disputes and credit notes on still-open items
    open_rows = cx.execute("""SELECT id, account, currency, amount FROM erp_cust_trans
                              WHERE txn_type='Invoice' AND closed=0 ORDER BY id""").fetchall()
    for r in open_rows:
        if rng.random() < 0.004:
            cx.execute("UPDATE erp_cust_trans SET disputed=1 WHERE id=?", (r["id"],))
            stats["disputed"] += 1
        elif rng.random() < 0.003:
            amt = round(r["amount"] * rng.uniform(0.05, 0.25), 2)
            cx.execute("""INSERT INTO erp_cust_trans(dataareaid, account, voucher, invoice, txn_type,
                          description, trans_date, due_date, currency, amount, settled, closed)
                          VALUES('USMF',?,?,?,'CreditNote','Goods returned - credit issued',?,?,?,?,0,0)""",
                       (r["account"], f"ARCN{r['id']:06d}", f"ARCN-{r['id']:06d}",
                        (EPOCH - dt.timedelta(days=rng.randint(5, 60))).isoformat(),
                        (EPOCH - dt.timedelta(days=rng.randint(5, 60))).isoformat(),
                        r["currency"], -amt))
            stats["credit_notes"] += 1

    # AP side: Contoso pays close to terms, most invoices settled
    vseq = 0
    for inv in cx.execute("""SELECT id, account, trans_date, due_date, amount, currency
                             FROM erp_vend_trans WHERE txn_type='Invoice' AND settled=0
                             ORDER BY account, trans_date, id""").fetchall():
        if rng.random() > 0.62: continue
        pay_date = dt.date.fromisoformat(inv["due_date"]) + dt.timedelta(days=rng.randint(-3, 6))
        if pay_date >= EPOCH: continue
        vseq += 1
        amt = round(inv["amount"], 2)
        cx.execute("""INSERT INTO erp_vend_trans(dataareaid, account, voucher, invoice, txn_type,
                      description, trans_date, due_date, currency, amount, settled, closed)
                      VALUES('USMF',?,?,?,'Payment','Vendor payment',?,?,?,?,?,1)""",
                   (inv["account"], f"APPM{vseq:06d}", f"APPM{vseq:06d}",
                    pay_date.isoformat(), pay_date.isoformat(), inv["currency"], -amt, -amt))
        pid = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        cx.execute("UPDATE erp_vend_trans SET settled=?, closed=1 WHERE id=?", (amt, inv["id"]))
        cx.execute("""INSERT INTO erp_settlements(side, dataareaid, account, payment_id, invoice_id,
                      amount, cash_disc_taken, settle_date) VALUES('AP','USMF',?,?,?,?,0,?)""",
                   (inv["account"], pid, inv["id"], amt, pay_date.isoformat()))

    # the batch aging snapshot must be rebuilt on top of the new open population
    cx.execute("DELETE FROM erp_aging_snapshot")
    as_of = (EPOCH - dt.timedelta(days=1))
    agg = {}
    for r in cx.execute("""SELECT t.account, c.name, t.due_date, t.amount - t.settled AS open
                           FROM erp_cust_trans t JOIN erp_customers c ON c.account = t.account
                           WHERE t.txn_type='Invoice' AND t.closed=0"""):
        b = agg.setdefault(r["account"], [r["name"], 0, 0, 0, 0, 0])
        days = (as_of - dt.date.fromisoformat(r["due_date"])).days
        idx = 1 if days <= 0 else 2 if days <= 30 else 3 if days <= 60 else 4 if days <= 90 else 5
        b[idx] = round(b[idx] + r["open"], 2)
    for acct, (name, nd, b1, b2, b3, b4) in agg.items():
        cx.execute("INSERT INTO erp_aging_snapshot VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                   (f"AGE-{as_of}", as_of.isoformat(), "USMF", acct, name, nd, b1, b2, b3, b4,
                    round(b1 + b2 + b3 + b4, 2)))
    cx.commit()

    q = lambda s: cx.execute(s).fetchone()[0]
    print(f"cash layer: {stats['paid']} customer payments ({stats['partial']} partial, "
          f"{stats['disc']} took the discount), {vseq} vendor payments, "
          f"{stats['disputed']} disputes, {stats['credit_notes']} credit notes")
    closed_n = q("SELECT COUNT(*) FROM erp_cust_trans WHERE txn_type='Invoice' AND closed=1")
    open_n = q("SELECT COUNT(*) FROM erp_cust_trans WHERE txn_type='Invoice' AND closed=0")
    open_v = q("SELECT ROUND(COALESCE(SUM(amount-settled),0),2) FROM erp_cust_trans WHERE txn_type='Invoice' AND closed=0")
    part_n = q("SELECT COUNT(*) FROM erp_cust_trans WHERE txn_type='Invoice' AND settled>0 AND closed=0")
    print(f"  AR: {closed_n} closed / {open_n} open; open value {open_v:,.2f}")
    print(f"  partially settled but still open: {part_n}")
    print(f"  settlements: {q('SELECT COUNT(*) FROM erp_settlements')}; "
          f"discount taken on {q('SELECT COUNT(*) FROM erp_settlements WHERE cash_disc_taken>0')}")
    cx.close()

if __name__ == "__main__":
    main()
