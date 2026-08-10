You are assisting the AR analyst at Contoso Entertainment System USA (company USMF).

What is the outstanding receivables balance for the customer **Fourth Coffee East** as of
March 2, 2026? Be careful to pick the right customer — several accounts share similar names.

Outstanding balance means the open (unsettled) amount on posted customer transactions.

Ground every figure in ERP tool calls, then submit via harness `submit_answer` with fields:

- `customer_account` (string — the account id you resolved)
- `outstanding_balance` (number, USD)
- `open_invoice_count` (number of open invoices making up that balance)

If something does not exist, submit the string "none" for that field.
