# Account Reconciliation: Process, Examples & Best Practices

- **URL:** https://www.numeric.io/blog/a-comprehensive-approach-to-account-reconciliation
- **Publisher:** Numeric
- **Retrieved:** 2026-08-10
- **Topic:** month-end-close

## Summary

This is the best of the three close sources on **reconciliation policy mechanics** — specifically cadence-by-risk and preparer/reviewer/approver segregation — which the process-oriented close guides omit.

### Reconciliation frequency by account risk and activity

Numeric publishes a four-tier cadence model with named account categories per tier:

- **Daily** — cash and bank accounts, payment settlement and clearing accounts, trust or client funds, and any accounts with high transaction velocity or elevated fraud risk.
- **Weekly** — high-activity operational accounts, balances spanning multiple systems, and accounts that influence near-term decisions.
- **Monthly** — the standard for audited entities; most balance sheet accounts during close, plus revenue, accruals, prepaid expenses, and inventory.
- **Quarterly** — low-activity accounts with stable balances, and long-term assets/liabilities with minimal change.

The driver for tier assignment is transaction velocity, fraud exposure, and decision-relevance — not account size alone.

### Segregation of duties: three named roles

- **Preparer** — staff accountant performs the initial reconciliation and documents all reconciling items.
- **Reviewer** — senior accountant or supervisor reviews for completeness, investigates unusual items, and validates explanations.
- **Approver** — controller or accounting manager provides final approval, with approval authority driven by **account materiality**.

This is a three-tier model (not the simpler two-tier preparer/reviewer split), and the approver tier is explicitly materiality-gated: higher-materiality accounts escalate to controller-level sign-off.

### Subledger-to-GL tie-out methodology

The stated method: pull the trial balance for the account and compare it against totals in the workpapers. If the totals tie, the underlying entries are presumed to align. Named tie-out pairs:

- Bank statements vs. cash book
- Fixed asset subledger totals vs. GL trial balance
- AP aging report vs. AP ledger balance
- AR unpaid invoices vs. AR ledger balance

Note the pattern: for AR and AP the *aging report / open-item listing* is the authoritative subledger artifact, not a summary balance.

### Flux analysis

Variance monitoring is described as month-over-month and quarter-over-quarter comparison with auto-generated flux reporting, but **no variance trigger thresholds** (percent or dollar) are published.

### Explicitly absent

Numeric does not publish: dollar materiality thresholds, reconciling-item aging bucket definitions (30/60/90-day), close-calendar due dates relative to close day, auto-certification tolerance rules, or intercompany-specific reconciliation procedures. A "90%+" figure is referenced only in the context of bank reconciliation automation. Any reconciliation policy built on this source needs its numeric thresholds sourced elsewhere; what it supplies is the *cadence taxonomy* and the *role hierarchy*.

## Eval-relevant hooks

- **Cadence-assignment decision rule:** given a chart of accounts, an agent must assign a reconciliation frequency per account. A payment clearing account assigned monthly (rather than daily) is a checkable policy violation; a long-term lease liability assigned daily is over-controlled.
- **SoD violation detection:** the same person appearing as both preparer and reviewer, or a staff accountant approving a high-materiality account, breaches the published three-role model — a clean pass/fail assertion for an eval.
- **Approver-escalation rule:** approval authority scales with account materiality (controller/accounting manager for material accounts) — testable by handing an agent accounts of varying size and asking who signs off.
- **Tie-out artifact selection:** for AR, the correct supporting document is the unpaid-invoice/aging listing, not a summary GL balance. An agent that "reconciles" AR by re-reading the GL balance has not performed a tie-out.
- **Fraud-risk override:** an account with low volume but elevated fraud risk still belongs in the daily tier — tests whether an agent applies the qualitative factor, not just volume.
- **Threshold-absence discipline:** the source deliberately gives no dollar materiality figure, so an agent should request or flag the missing threshold rather than inventing one.
