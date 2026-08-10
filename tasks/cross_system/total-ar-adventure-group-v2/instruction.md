You are assisting the controller of the Contoso group. Today is March 2, 2026.

The treasury committee needs our **total group AR exposure to Adventure Works Cycles** —
and the number has to survive scrutiny. Their business with us spans the USMF ERP and our
subsidiary **CES Direct LLC** (separate accounting system), and finance ops warns that
during the CES migration some paperwork was kept in side records on the shared drive and
mailbox rather than either system. They also warn that not every summary file on the drive
is current — verify anything you use.

Net unapplied credit memos against the subsidiary balance. Count a side-record invoice
only if it is not recorded in either system (no double counting).

Submit via harness `submit_answer`:

- `erp_open_balance` (number, USD — open AR in USMF)
- `subsidiary_net_balance` (number, USD — CES Direct open invoices minus unapplied credit memos)
- `offbook_invoice_amount` (number, USD — valid side-record invoices counted, or "none")
- `combined_exposure` (number, USD — the defensible group total)
