You are assisting the AP manager at Contoso Entertainment System USA (company USMF).

What is the **total overdue accounts payable balance** in USMF as of March 2, 2026?

Overdue means posted, unsettled vendor invoices whose due date is before March 2, 2026.
Ground the figure in ERP tool calls (the AP subledger has thousands of lines — aggregate,
don't sample). Submit via harness `submit_answer` with fields:

- `total_overdue_ap` (number, USD)
- `as_of_date` (string, YYYY-MM-DD)

If something does not exist, submit the string "none" for that field.
