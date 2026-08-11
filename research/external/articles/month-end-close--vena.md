# Month End Close Steps, Process, Checklist and Best Practices

- **URL:** https://www.venasolutions.com/blog/month-end-close-process-checklist
- **Publisher:** Vena Solutions
- **Retrieved:** 2026-08-10
- **Topic:** month-end-close

## Summary

Vena's guide is the strongest of the three close sources on *sequence granularity*: it splits the close into three phases and enumerates fifteen named tasks across them, which maps cleanly onto a close-calendar structure even though Vena does not assign explicit day numbers.

### Pre-close phase

1. Verify ERP, payroll, and other systems are fully synced.
2. Send reminders to department heads for pending expenses and approvals.
3. Distribute the month-end close schedule with clear task ownership.

The pre-close phase is where ownership is assigned — task ownership is distributed *before* the period ends, not during execution.

### Close execution phase

4. Record all revenue and flag missing invoices.
5. Collect and accrue unbilled expenses.
6. Reconcile bank and credit card accounts.
7. **Reconcile AP and AR subledgers with the general ledger.**
8. Review and post journal entries.
9. Validate payroll and benefit entries.
10. Review fixed asset activity and record depreciation and disposals.
11. **Hold a mid-close sync to review blockers.**
12. Upload backup documentation for material entries.

Two items here are operationally distinctive. Step 11 institutionalizes a *mid-close checkpoint* — a standing meeting inside the close window to surface blockers rather than discovering them at sign-off. Step 12 conditions documentation upload on materiality ("material entries"), implying a threshold exists in policy even though Vena does not publish one.

### Post-close phase

13. Update final actuals in reporting and planning tools.
14. **Review key variances and write commentary.**
15. Document recurring issues and lessons learned.

Flux commentary (step 14) is placed *after* close, in the reporting layer, rather than as a gate on closing the books. Step 15 creates a continuous-improvement loop feeding the next cycle.

### Benchmarks published

- **Target close: 3–5 business days** (described as aspirational).
- **50% of teams actually take six days or more.**
- **High performers: 5–7 business days.**
- **Mid-sized companies: 8–10 business days.**
- **94% of teams still use Excel for month-end close** (attributed to Ledge 2025 data).

Note the internal tension worth flagging: the "aspirational" 3–5 day target sits below the stated high-performer band of 5–7 days.

### Roles

Vena names functional owners without mapping them to individual steps: Accounting (reconciliations, journal entries), FP&A (variance analysis, forecasting), department heads (expense submission, budget review), and Payroll, HR, and Procurement as data feeds. There is no preparer/reviewer segregation model and no approver hierarchy.

### Explicit gaps

No numeric materiality thresholds, no cutoff rules, no variance-analysis trigger percentages, no reconciling-item aging buckets, and no APQC benchmark citations. The value here is the fifteen-step named sequence and the four close-duration bands.

## Eval-relevant hooks

- **Phase-assignment task:** give an agent an unordered list of the fifteen tasks and require correct assignment to pre-close / close / post-close. Misplacing "distribute the close schedule" into the execution phase is a checkable error.
- **Close-duration benchmarking rule:** an 8-day close is at the top of the "mid-sized company" band (8–10 days) and outside the high-performer band (5–7 days). An agent can be asked to grade a close calendar against these four published bands.
- **Mid-close sync as a control:** a close plan with no blocker-review checkpoint between start and sign-off is missing Vena step 11 — a specific, assertable omission.
- **Documentation gate:** backup documentation is required for *material* entries, so an eval can test whether an agent asks for the materiality threshold rather than assuming one (Vena publishes none).
- **Ownership timing:** task ownership must be distributed during pre-close; an agent that assigns owners after the period closes violates the published sequence.
- **Flux placement:** variance commentary is a post-close activity in this model, not a prerequisite to closing — useful for testing whether an agent can distinguish "close the books" from "report on the books."
