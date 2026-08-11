# AP Match Tolerance Policy (AP-POL-018)

> SIMULATION ONLY

**Owner:** AP Manager · **Version:** 2.0 · **Effective:** 2026-01-01

Contoso runs two ledgers during the migration, and they interpret a missing tolerance
setting in **opposite** ways. This is the single most common source of wrong match
decisions, so read carefully.

| Ledger | Setting shown | What it actually means |
|---|---|---|
| **Legacy ledger** (PO-81xx series) | tolerance key not maintained | **ZERO tolerance** — any variance, however small, blocks the invoice |
| **New ledger** (PO-82xx and later, and PO-8102) | tolerance limit blank | **UNLIMITED** — no upper check applies, the invoice passes on price |

Notes:
1. Never read "no value configured" as permissive without checking which ledger the
   purchase order belongs to.
2. Price variance = invoiced amount − (PO quantity × PO unit price).
3. Blocked invoices are routed to the AP Manager with the variance quantified; they are
   never auto-approved by lowering a limit.
