You are the AP specialist at Contoso (USMF). Today is March 2, 2026.

Three vendor invoices (**TWINV-301, TWINV-302, TWINV-303**) are waiting in the match
queue. Run the 3-way match for each: compare the invoice against its purchase order and
the product receipts. Classify each as clean, price variance, or quantity variance, and
quantify the variances.

Submit via harness `submit_answer`:

- `clean_invoice` (string — the invoice that matches PO and receipt exactly)
- `price_variance_invoice` (string)
- `price_variance_amount` (number, USD — total over/under-billed due to unit price)
- `qty_variance_invoice` (string)
- `qty_over_billed_units` (number — units billed but not received)
