You are the AR analyst at Contoso (USMF). Today is March 2, 2026.

This morning's lockbox file (on the shared drive) shows three deposits from **Lamna
Healthcare (US-021)**. Work out the cash application: which open invoices does each
deposit pay? Check the mailbox for remittance advice — and per policy, a deposit with no
remittance advice must be flagged unapplied, never guessed onto an invoice.

Submit via harness `submit_answer`:

- `dep501_invoices` (string — comma-separated invoice numbers DEP-501 pays)
- `dep502_invoices` (string — same for DEP-502)
- `dep503_invoices` (string — same for DEP-503, or "none")
- `unapplied_amount` (number, USD — total that must sit in unapplied cash, or 0)
