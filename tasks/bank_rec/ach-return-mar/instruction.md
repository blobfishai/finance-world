You are the AR analyst at Contoso (USMF). Today is March 2, 2026.

The March 1 bank file (shared drive) contains an **ACH return**. Work out what it undoes:
which customer payment came back, which invoice consequently goes back to open, and what
the customer's true open balance is once the return is recognised. The ERP has not yet
processed the return.

Submit via harness `submit_answer`:

- `returned_payment_ref` (string)
- `returned_amount` (number, USD)
- `reopened_invoice` (string — the invoice that becomes open again)
- `true_open_balance` (number, USD — the customer's open AR once the return is recognised)
