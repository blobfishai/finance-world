You are assisting the controller of the Contoso group. Today is March 2, 2026.

What is our **total group AR exposure to Adventure Works Cycles** — across both the USMF
ERP and our subsidiary **CES Direct LLC**, whose books are kept in a separate accounting
system? The subsidiary trades with the same counterparty under its own customer record.
Net any unapplied credit memos against the subsidiary balance.

Ground every number in tool calls, then submit via harness `submit_answer`:

- `erp_open_balance` (number, USD — open AR in USMF)
- `subsidiary_net_balance` (number, USD — CES Direct open invoices minus unapplied credit memos)
- `combined_exposure` (number, USD — the group total)

If something does not exist, submit the string "none" for that field.
