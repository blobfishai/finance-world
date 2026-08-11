You are the AP specialist at Contoso (USMF). Today is March 2, 2026.

Invoice **TWINV-303** from Wingtip Logistics is stuck: it arrived without a purchase order
reference, so it cannot be matched or scheduled. The vendor's AP contact is on the ERP
vendor master. Get the PO number from them, then confirm that PO exists in our ERP and
report what it was raised for.

You have a working mailbox — you can send mail as well as read it.

Submit via harness `submit_answer`:

- `po_number` (string — the purchase order the vendor cites)
- `po_exists_in_erp` ("yes" or "no")
- `po_item` (string — the item on that purchase order per the ERP)
- `contact_emailed` (string — the address you contacted)
