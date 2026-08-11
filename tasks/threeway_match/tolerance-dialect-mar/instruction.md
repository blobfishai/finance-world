You are the AP specialist at Contoso (USMF). Today is March 2, 2026.

Two invoices are sitting in the match queue with price variances against their purchase
orders: **TDINV-401** (legacy ledger) and **TDINV-402** (new ledger). Both ledgers report
"no tolerance value configured" for the relevant key — but the two systems mean opposite
things by that. The AP tolerance policy in the docs library spells out which is which.

Decide which invoice is blocked and which may proceed, and quantify both variances.

Submit via harness `submit_answer`:

- `blocked_invoice` (string)
- `blocked_variance` (number, USD)
- `passing_invoice` (string)
- `passing_variance` (number, USD)
- `blocking_rule` (string — why the blocked one blocks)
