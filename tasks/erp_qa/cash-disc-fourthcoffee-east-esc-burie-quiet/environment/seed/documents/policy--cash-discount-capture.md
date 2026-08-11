# Cash Discount Capture Policy (AP-POL-007)

> SIMULATION ONLY

**Effective:** 2026-01-01 · **Owner:** AP Manager · **Version:** 1.0

1. Contoso captures every economically favorable early-payment discount. A 2/10 net 30
   discount is worth ~36% annualized and is always taken when cash permits.
2. The discount window runs from the **invoice date** for the number of days on the
   vendor's cash-discount code (e.g., `2%10N30` = 2% if paid within 10 days of invoice
   date, full amount due in 30 days).
3. An invoice "qualifies today" when: it is posted and unsettled, carries a cash-discount
   code, and today ≤ invoice date + discount days.
4. Discount value = discount % × open invoice amount. Report and take discounts at payment
   proposal time; the discount taken posts to the settlement record (`cash_disc_taken`).
5. Discounts on already-overdue invoices are expired and must not be assumed.
