You are assisting the collections analyst at Contoso Entertainment System USA (company USMF).
Today is March 2, 2026.

Which collection letter level is customer **Sparrow Retail** currently at? And have they
paid us recently — if so, when and how much was the most recent payment, and what remains
open on their account?

The team's dunning runbook is in the internal docs library if you need the escalation
context. Ground everything in tool calls, then submit via harness `submit_answer`:

- `collection_letter_level` (string — the highest letter level issued, e.g. "1", "2", ...)
- `last_payment_date` (string, YYYY-MM-DD, or "none")
- `last_payment_amount` (number, USD, or "none")
- `open_balance` (number, USD — unsettled amount across their invoices)
