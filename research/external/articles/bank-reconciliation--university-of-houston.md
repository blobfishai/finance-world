# Bank Account Reconciliation (MAPP 05.04.06)

- **URL:** https://uh.edu/policies/mapps/05-finance-and-accounting/050406/
- **Publisher:** University of Houston (Manual of Administrative Policies and Procedures)
- **Retrieved:** 2026-08-10
- **Topic:** bank-reconciliation

## Summary

An institutional bank reconciliation policy with unusually explicit day counts and named role owners — the kind of source that turns "reconcile promptly" into a testable rule.

### Timeliness thresholds (exact)

- Bank accounts must be reconciled **within 30 working days** of the *later* of two trigger events: (a) receipt by the **Manager of Bank Reconciliation** of the bank statement from the Treasurer's Office or the online banking systems, or (b) the **final accounting close of the fiscal month**. The "later of" construction matters: the clock does not start at statement date alone.
- **Bank discrepancies** (items the bank got wrong) must be communicated to **Treasury** for resolution with the bank **within 20 working days of reconciliation**.
- **Posting discrepancies** (items the books got wrong) must be communicated to the **Office of General Accounting** for inclusion or correction in the accounting system **within 20 working days of reconciliation**.
- Treasury must forward electronic bank data **within three business days after the end of the month** — an upstream SLA that feeds the 30-working-day reconciliation window.
- Escalation: the **Director** notifies the **Controller** of items **not resolved within 30 days** of being referred to another area.

### Roles and sign-off chain

- Preparation/review sits with an **account analyst** and the **Manager of Bank Reconciliation**; **both sign the reconciliation summary**.
- The signatures certify two distinct assertions: that current procedures were followed, *and* that the reconciliation accurately presents the status of the account both **at the bank** and **on the books** — i.e. the two-sided adjusted-balance assertion.
- The **Director of Accounting Services** receives a monthly summary **by the last working day of the month**.
- The **Associate Vice President for Finance** has access to the reconciliation files on request.

### Segregation of duties

The controlling sentence: staff responsible for the bank account reconciliation **will not initiate corrections** either at the bank or in the accounting system. Reconcilers detect and refer; other functions (Treasury, General Accounting) execute the correction. This is a cleaner separation than the more common "preparer ≠ reviewer" rule, because it separates *detection* from *remediation* rather than just preparation from approval.

### What this source does NOT contain

Explicitly noted so it is not over-claimed: the policy states **no dollar variance thresholds**, no materiality cut-off for unreconciled differences, and **no stale-dated check or escheatment provisions**. Those must be sourced elsewhere.

## Eval-relevant hooks

- Deadline arithmetic task: given a statement receipt date and a fiscal close date, compute the reconciliation due date as 30 *working* days after the later of the two — a trap for agents that use calendar days or the earlier trigger.
- Routing task: classify each open reconciling item as a bank discrepancy (→ Treasury) or a posting discrepancy (→ Office of General Accounting), then assert the 20-working-day communication deadline for each.
- Control-violation detection: flag a scenario where the account analyst who prepared the reconciliation also posts the correcting journal entry — a direct breach of the "will not initiate corrections" rule.
- Sign-off completeness check: a reconciliation package missing either the account analyst or the Manager of Bank Reconciliation signature fails; assert both signatures plus the two certification assertions.
- Escalation trigger: an item referred to another department 31+ days ago and still open must be escalated by the Director to the Controller.
- Negative-knowledge check: ask for the policy's dollar variance threshold — the correct answer is that the policy specifies none.
