# Audit Rules to Identify Anomalies in the Expense Report (Oracle Fusion Cloud Expenses)

- **URL:** https://docs.oracle.com/en/cloud/saas/financials/25d/faiex/audit-rules-to-identify-anomalies-in-the-expense-report.html
- **Publisher:** Oracle (Fusion Cloud Financials — Expenses, Implementing guide, release 25D)
- **Retrieved:** 2026-08-10
- **Topic:** te-expense-audit

## Summary

This is a rule-by-rule specification of the automated audit selection rules an enterprise expense system uses to decide **which** expense reports go to a human auditor. It is unusually concrete about the parameters each rule exposes, which makes it directly usable as a policy-configuration and rule-evaluation reference.

### The seven published audit rules

**1. Audit expense reports of top spenders.** Triggers when the report owner is identified as a top spender in a specified period. Parameters: number of months in the period, number of top spenders to identify. Oracle's examples: *10 top spenders of past 6 months*; *20 top spenders of past 10 months*.

**2. Audit expense reports of top policy violators.** Triggers when the report owner is identified as a top policy violator in a specified period. Parameters: number of months, number of top policy violators. Examples: *10 top policy violators of past 6 months*; *20 top policy violators of past 10 months*.

**3. Audit expense reports with same policy violation for more than specified times.** Triggers when the owner violates the **same** policy more than a defined threshold within a period. Parameters: number of months, number of permitted violations. Examples: *Airfare class of ticket* violation allowed **5 times in 1 month**, with the next report audited if exceeded; *Corporate Card Required* violation allowed **10 times in 2 months**.

**4. Audit expense reports with public sectors attendees.** Triggers when the report includes any expense with attendees from the public sector. No configurable parameters. This is the anti-bribery/government-official control.

**5. Audit expense reports for duplicate expense.** Triggers when an expense item is identified as a duplicate. The published matching attributes are **Amount, Date, Currency, Expense Type, and Merchant**. Requires the **Detection of Duplicate Expenses** feature to be enabled.

**6. Audit expense reports with same attendees for the same day.** Triggers when attendees (employee or non-employee) on the report are also detected on other submitted expense reports with the same expense item type and the same date or date range. This is the control against two employees each expensing the same shared meal.

**7. Audit expense reports with expense amount below specific threshold of missing receipt policy.** Triggers when an expense amount sits **just below** the receipt threshold and the behavior recurs more often than allowed. Parameters: percentage of threshold (the permissible band below the threshold amount), number of incidents allowed, number of months in the period. Oracle's worked example: **10% of the threshold amount, occurring more than 5 times in the last 6 months** — so with a receipt threshold of **USD 500**, amounts in the **USD 450–499** band occurring **5+ times in 6 months** cause subsequent reports to be audited. This is the published detector for deliberate threshold-shaving.

### Dependencies

Rules 1, 2 and 3 all depend on a scheduled process named **Generate Summary Metrics for Expenses**, which refreshes the top-spender and policy-violator data the rules read. If that process is not scheduled, the behavior-history rules will not fire — a real operational failure mode, not a data problem.

### Structure worth noting for rule design

The seven rules split into three families: **behavioral/history-based** (top spenders, top violators, repeat same-violation — all parameterized by a lookback in months and a count), **transaction-pattern-based** (duplicate expense, same attendees same day, below-threshold shaving), and **categorical** (public sector attendees, always audited, no parameters). Only the categorical rule is unconditional; every other rule is a count-over-a-window test.

The page documents selection rules only; it does not publish a random-sampling percentage, expense report workflow statuses, or auditor role definitions.

## Eval-relevant hooks

- Rule-firing evaluation: given an expense dataset and a configured rule set, determine which reports are selected for audit — e.g., does an employee with 6 *Airfare class of ticket* violations in 1 month exceed a threshold of 5?
- Threshold-shaving detector: with a USD 500 receipt threshold and a 10% band, flag expenses in the USD 450–499 range and count occurrences against the "more than 5 times in 6 months" rule. Fully computable.
- Duplicate-detection specification: duplicates are matched on **Amount, Date, Currency, Expense Type, Merchant** — an agent proposing a duplicate match on amount alone, or missing Currency, is under-specifying the rule.
- Shared-expense control: "same attendees for the same day" with the same expense item type is the check for two employees claiming one meal — a distinct rule from duplicate detection.
- Configuration-dependency trap: the three history-based rules silently produce no results unless **Generate Summary Metrics for Expenses** is scheduled; a "zero flagged reports" result should be diagnosed as a missing process before being reported as clean.
- Policy-design task: classify a proposed control into the correct rule family (behavioral count-over-window vs transaction-pattern vs unconditional categorical) and specify its required parameters (months, count, percentage).
- Compliance hook: expenses involving **public sector attendees** are audited unconditionally with no parameters — a rule an agent should never propose thresholding.
