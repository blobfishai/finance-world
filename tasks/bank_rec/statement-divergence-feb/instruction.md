You are assisting the controller at Contoso (USMF). Today is March 2, 2026.

Reconcile the **February operating-account bank statement** (the export is on the finance
shared drive) against the customer payments posted in the ERP for 2026-02-24 through
2026-02-28. Classify every line: matched · amount discrepancy · bank-only (on the
statement, not in the books) · books-only (posted, not on the statement).

Submit via harness `submit_answer`:

- `matched_count` (number of exactly-matched payments)
- `discrepancy_ref` (string — the payment reference whose amounts differ, or "none")
- `discrepancy_amount` (number — absolute difference in USD, or "none")
- `bank_only_ref` (string — statement line with no book entry, or "none")
- `books_only_ref` (string — posted payment absent from the statement, or "none")
