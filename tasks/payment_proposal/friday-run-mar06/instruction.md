You are the AP specialist at Contoso (USMF). Today is Monday, March 2, 2026.

Assemble the **payment proposal for Friday's run (payment date 2026-03-06)** following the
payment-run SOP in the docs library. In scope: the PPINV-prefixed invoice batch posted
last week. The SOP defines which invoices to include (due items and economically
favorable discounts) and which vendors must be excluded. You are proposing, not posting.

Submit via harness `submit_answer`:

- `proposal_invoices` (string — comma-separated invoice numbers to pay Friday)
- `excluded_invoice` (string — invoice left out despite being due, or "none")
- `exclusion_reason` (string)
- `discount_captured` (number, USD — total early-pay discount the proposal captures)
- `net_payment_total` (number, USD — total cash out after discounts)
