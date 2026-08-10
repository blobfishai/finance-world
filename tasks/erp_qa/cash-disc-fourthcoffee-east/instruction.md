You are assisting the AP specialist at Contoso Entertainment System USA (company USMF).
Today is March 2, 2026.

Does our **vendor Fourth Coffee East** have any cash discount terms active on current
invoices? If yes: which open invoices still qualify for the discount as of today, and how
many dollars of discount would we capture if we paid those qualifying invoices today?

Context you may need: the vendor's February statement arrived in the AP mailbox, and the
company's discount-capture policy is in the internal docs library. A cash discount window
runs from the invoice date for the number of days on the discount code.

Ground everything in tool calls, then submit via harness `submit_answer`:

- `has_active_discount` ("yes" or "no")
- `qualifying_invoices` (string — comma-separated invoice numbers, or "none")
- `potential_discount_usd` (number — total discount if qualifying invoices are paid today)
