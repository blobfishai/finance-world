# Complete Guide to 2/10 Net 30 Early Payment Discounts

- **URL:** https://tipalti.com/resources/learn/210-net-30/
- **Publisher:** Tipalti
- **Retrieved:** 2026-08-10
- **Topic:** payment-runs-early-pay-discount

## Summary

The canonical early-payment-discount economics reference, with the annualization arithmetic worked end to end — which matters because the "right" answer depends on which convention is used.

### The worked calculation (exact as published)

Invoice **$500**, terms **2/10 net 30**:
1. Pay within 10 days at 98% → **$490**; savings **$10**.
2. Period rate over the 20 days of forgone credit: **($500 / $490) − 1 = 2.04%**.
3. Annualization factor: **360 ÷ 20 = 18** periods per year.
4. Effective annualized rate: **2.04% × 18 = 36.7%**.

Two convention choices drive the published figure. First, the period rate is computed on the **discounted amount ($490)** — the amount actually at risk — not on the gross invoice, which is why the numerator is 2.04% rather than 2.00%. Second, the year is taken as **360 days**, not 365. Using the gross base and a 365-day year gives ≈36.5%; using the net base and 365 days gives ≈37.2%. All three figures circulate in practice; **this source's published answer is 36.7%**.

The decision rule follows directly: taking the discount is correct when the company has sufficient internally generated cash flow, or access to financing at a cost **below 36.7%** — which effectively means below almost any commercial borrowing rate.

### Term variants listed

- **1/10 Net 30** — 1% discount if paid within 10 days; full payment due in 30 days.
- **3/10 Net 30** — 3% discount if paid within 10 days; full payment due in 30 days.
- **2/10 Net 45** — 2% discount if paid within 10 days; full payment due in 45 days.
- **3/20 Net 60** — 3% discount if paid within 20 days; full payment due in 60 days.

The source publishes **no annualized rates for these variants** — only for 2/10 net 30. Any variant rate must be derived, not cited.

### Accounting treatment

- **Net method** — record the invoice at the discounted amount ($490); a missed discount becomes an expense.
- **Gross method** — record at the full amount ($500) and adjust upon payment when the discount is taken.

## Eval-relevant hooks

- Formula-application task: compute the effective annualized rate for 1/10 net 30 and 3/20 net 60 using this source's stated convention (discounted base, 360-day year) — derivation required since the source does not publish them.
- Convention-sensitivity check: ask why 36.5%, 36.7%, and 37.2% all appear in the literature; a correct answer names the gross-vs-net base and the 360-vs-365 day count.
- Capital-allocation decision: given a revolver rate (say 9%) and a cash balance, decide whether to draw on the revolver to capture a 2/10 discount — the rule is take the discount whenever the cost of funds is below the effective rate.
- Days-of-credit trap: the annualization divisor is **20 days (day 10 → day 30)**, not 30 and not 10; an agent using 30 will materially understate the rate.
- Method selection: under the **net method**, a discount that lapses must be recognized as an expense rather than silently increasing the payable — a checkable journal-entry assertion.
- Payment-run scheduling: given a batch of invoices with mixed terms and discount deadlines, sequence the run so discount-eligible invoices are paid on the last qualifying day (day 10), not earlier — early payment beyond the deadline requirement is a free giveaway of float.
