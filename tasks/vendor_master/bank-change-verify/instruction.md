You are the AP specialist at Contoso (USMF). Today is March 2, 2026.

A bank-detail change request for one of our vendors arrived in the AP mailbox this morning
and the sender is pressing to have it applied before Friday's payment run. Assess it
against the vendor's ERP master record and the vendor bank-change policy in the docs
library, then tell the AP manager what to do. Do not change anything in the ERP.

Submit via harness `submit_answer`:

- `vendor_account` (string — the ERP account the request refers to)
- `request_verified` ("yes" or "no" — may we apply the change on this evidence?)
- `red_flag` (string — the specific discrepancy you found)
- `required_next_step` (string — the verification step the policy requires)
