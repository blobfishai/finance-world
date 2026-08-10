You are assisting the AR analyst at Contoso Entertainment System USA. Today is March 2, 2026.

A colleague asks: **"Did we ever invoice Meadow Analytics for the February executive
workshop? What's outstanding from them?"** They warn you the client is brand new, so the
paperwork may not have made it into the ERP yet — check the shared mailbox and the team's
manual trackers on the shared drive too.

Ground the answer in tool calls, then submit via harness `submit_answer`:

- `found_in_erp` ("yes" or "no" — does the ERP have any record of this counterparty?)
- `invoice_number` (string, or "none")
- `outstanding_amount` (number, USD, or "none")
- `evidence_source` (string — where the invoice actually lives)
