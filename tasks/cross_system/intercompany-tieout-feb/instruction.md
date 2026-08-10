You are supporting the month-end close at Contoso (USMF). Today is March 2, 2026.

Tie out the **intercompany balance with CES Direct LLC**: what does USMF's AR show as
owed by the subsidiary (customer account IC-001), what does the subsidiary's own
intercompany schedule on the shared drive show, and what exactly explains any difference?
Check the mailbox — the subsidiary's accountant usually flags in-transit items.

Submit via harness `submit_answer`:

- `parent_ar_balance` (number, USD — USMF open AR to IC-001)
- `sub_recorded_balance` (number, USD — per the subsidiary's schedule)
- `difference` (number, USD)
- `difference_cause` (string — name the specific item(s) explaining the difference)
