# Month-End Close Process: Steps, Checklist, and Best Practices

- **URL:** https://www.highradius.com/resources/Blog/what-is-month-end-close-process/
- **Publisher:** HighRadius
- **Retrieved:** 2026-08-10
- **Topic:** month-end-close

## Summary

HighRadius frames month-end close as a six-step sequence, then layers a nine-task operational checklist on top of it, plus automation benchmarks from its own record-to-report product.

### The six published process steps (in order)

1. **Collect all Financial Information** — pull transaction data from ERPs, bank portals, AR/AP, and other financial systems.
2. **Verify and Reconcile the Data** — match internal records against external sources, and tie sub-ledgers to the general ledger; investigate discrepancies.
3. **Post Adjusting Entries** — record accruals, prepayments, and depreciation belonging to the period.
4. **Review Balance Sheet and Variance Analysis** — confirm account balances and compare the current period against prior month, prior year, and budget.
5. **Prepare Financial Statements** — income statement, balance sheet, cash flow statement.
6. **Conduct a Final Review** — senior-level verification before close sign-off.

Note the ordering implication: reconciliation (step 2) precedes adjusting entries (step 3), and variance analysis (step 4) is positioned as a balance-sheet review activity that gates statement preparation.

### The nine-task close checklist

Record transactions → post journal entries → reconcile bank accounts and credit cards → reconcile sub-ledgers to GL → review balance sheet → prepare financial statements → conduct variance analysis → produce management reports → archive documentation.

This makes bank/credit-card reconciliation and subledger-to-GL reconciliation two *distinct* checklist items rather than one combined task, which matters for task-level close tracking.

### Timing benchmarks

- **Typical close duration: 5 to 10 days.**
- **"Fast close" target: under 5 days.**
- **Automation-driven improvement cited: 30% faster close.**

### Automation and accuracy metrics

- **Transaction auto-match rate: up to 90%.**
- **Anomaly resolution via auto-suggested actions: 80%.**
- **Anomaly detection accuracy: over 95%.**
- **Projected automation level by 2027: 90%.**

These are vendor-published product benchmarks, not independent survey data, and should be treated as aspirational targets rather than industry norms.

### What this source does *not* provide

Explicitly absent: materiality thresholds (dollar or percent), tolerance percentages for reconciliation sign-off, flux-analysis variance triggers, reconciling-item aging limits, a day-by-day close calendar (Day -1 / Day 0 / Day 1…), and named role or owner assignments per step. Preparer/reviewer segregation is not addressed beyond "senior-level verification" at final review. Anyone building a close policy from this source has the *sequence* and the *duration benchmarks* but must source thresholds and role assignments elsewhere.

## Eval-relevant hooks

- **Step-ordering assertion:** an agent asked to sequence close tasks should place subledger-to-GL reconciliation *before* posting adjusting entries and *before* financial statement preparation — an agent that prepares statements before reconciling subledgers has produced a checkable error.
- **Close-duration classification rule:** a close taking 5–10 days is "typical"; under 5 days qualifies as a "fast close." An eval can hand an agent a close calendar and ask it to classify performance against these published bands.
- **Checklist completeness check:** given a partial close checklist, the agent must identify which of the nine named tasks are missing — e.g. a checklist with bank reconciliation but no separate subledger-to-GL reconciliation task is incomplete.
- **Auto-match benchmark:** an environment reporting a transaction auto-match rate materially below 90% can trigger a task to diagnose the gap; the 90% figure is a concrete assertion target.
- **Negative/refusal hook:** because this source publishes *no* materiality threshold, an agent that cites a specific materiality percentage and attributes it to this source is hallucinating. Good test of source-grounded citation discipline.
- **Variance analysis scope:** step 4 compares current period against three baselines (prior month, prior year, budget) — an agent producing a flux analysis against only one baseline is under-delivering against the published step.
