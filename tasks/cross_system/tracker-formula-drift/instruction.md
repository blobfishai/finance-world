You are assisting the controller at Contoso (USMF). Today is March 2, 2026.

The CFO quotes a number from the **AR watchlist tracker** on the shared drive and the AR
analyst says it "feels low." Audit the tracker: does its TOTAL cell agree with its own
rows? Do the row balances agree with the live ERP? Give the number the CFO should
actually use.

Submit via harness `submit_answer`:

- `tracker_cached_total` (number, USD — what the TOTAL cell currently shows)
- `tracker_rows_sum` (number, USD — what the tracker's rows actually add to)
- `erp_live_total` (number, USD — the same watchlist customers' true open AR from the ERP)
- `stale_customers` (string — which watchlist customers' tracker rows are out of date, or "none")
