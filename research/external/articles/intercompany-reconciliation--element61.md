# Next-Generation Intercompany Reconciliation within S/4HANA Group Reporting (ICMR)

- **URL:** https://www.element61.be/en/resource/next-generation-intercompany-reconciliation-within-s4-hana-group-reporting
- **Publisher:** element61 (EPM/analytics consultancy)
- **Retrieved:** 2026-08-10
- **Topic:** intercompany-reconciliation

## Summary

A practitioner walkthrough of SAP's **Intercompany Matching and Reconciliation (ICMR)** capability in S/4HANA Group Reporting. Useful as the non-Oracle counterpart to the ERP-vendor docs: it names the apps a reconciliation team actually works in, the shape of the close-cycle process, and — most valuably for eval design — the **reason-code taxonomy** used to classify unmatched intercompany items.

### The named apps and what each is for

- **Reconciliation Status Overview** — a single view to evaluate and reconcile data in **aggregate form at the company level**. This is the "am I in balance with each trading partner" screen.
- **Reconciliation Balances** — displays balances at the **account level**, with the option to view in **transaction currency** or **group presentation currency**. The currency toggle is the practical control for separating a genuine economic difference from an FX-translation difference.
- **Manage Assignments** — transaction-level work: matching and grouping document line items under **assignment numbers**. An assignment number is the unit that binds the two sides of a matched intercompany pair together.

### Status and difference handling

Transactions are given a **matching** status when the two sides reconcile. Where a difference exists, ICMR can be configured to detect that difference and **flag the transaction with a specific status**, which is what drives the exception queue.

The source names **pre-built reason codes** that guide accountants on unmatched trades, citing as examples:

- **open items longer than 30 days**
- **goods in transit**

These are exactly the operational exception categories a controller would expect: an aging-based reason code (stale unmatched item) and an in-transit inventory/shipment timing reason code. The platform also supports **automatic adjustment logic**, defined so that specific classes of difference are resolved automatically "in a controlled and traceable manner" — i.e., auto-posting is scoped by reason code rather than applied blanket.

### Where reconciliation sits in the group close

The described integration into the group close runs in this order:

1. **Data collection**
2. **Document matching**
3. **Adjustment postings**
4. **Currency conversion**
5. **Reconciliation results review**

Note the sequence: adjustment postings occur *before* currency conversion, so an adjustment is booked in transaction terms and then translated, rather than being plugged post-translation. The architectural claim behind the speed is that matching runs directly on the S/4HANA data (no ETL), letting reconciliation move from company close into corporate close continuously rather than as an end-of-period batch.

### Explicit limits of this source

The page does **not** publish tolerance percentages or amounts, does **not** enumerate the full set of matching rule subtypes (e.g., exact / suggested / exceptional match patterns), and does **not** define role assignments or named reconciliation-status values beyond "matching" and the generic notion of a difference flag. Any numeric tolerance for this platform must come from a different source; nothing here should be treated as a published threshold other than the 30-day open-item reason code.

## Eval-relevant hooks

- Exception-taxonomy hook: "open items longer than 30 days" and "goods in transit" are published reason codes — an agent classifying unmatched intercompany items can be scored against a reason-code taxonomy that includes an aging bucket and an in-transit bucket.
- Aging rule: an unmatched intercompany item open more than **30 days** is a flagged exception, a directly checkable decision rule.
- Tool-selection task: given a question ("which trading partner am I out of balance with?" vs "which account?" vs "which document pair?"), pick Reconciliation Status Overview vs Reconciliation Balances vs Manage Assignments.
- FX-versus-real-difference task: the Reconciliation Balances currency toggle (transaction currency vs group presentation currency) is the correct first diagnostic when a difference appears only after translation.
- Sequence assertion: adjustment postings precede currency conversion in the close flow; an agent proposing a post-translation plug contradicts the published order.
- Control hook: automatic adjustment logic is scoped to specific difference types and must be traceable — a task can require an agent to justify which differences may be auto-cleared versus routed to a human.
