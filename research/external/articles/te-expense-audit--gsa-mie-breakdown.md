# M&IE Breakdown (GSA)

- **URL:** https://www.gsa.gov/travel/plan-book/per-diem-rates/mie-breakdown
- **Publisher:** U.S. General Services Administration (GSA)
- **Retrieved:** 2026-08-10
- **Topic:** te-expense-audit

## Summary

The GSA M&IE Breakdown page is the authoritative per-meal decomposition of the federal meals-and-incidental-expenses per diem. It is the reference an expense auditor uses to deduct a provided meal from a traveler's per diem and to compute the reduced first/last-day allowance — the two most common per-diem audit adjustments.

### The CONUS M&IE breakdown table

| M&IE Total | Breakfast | Lunch | Dinner | Incidentals | First & last day of travel |
|---|---|---|---|---|---|
| $68 | $16 | $19 | $28 | $5 | $51.00 |
| $74 | $18 | $20 | $31 | $5 | $55.50 |
| $80 | $20 | $22 | $33 | $5 | $60.00 |
| $86 | $22 | $23 | $36 | $5 | $64.50 |
| $92 | $23 | $26 | $38 | $5 | $69.00 |

### Structure of the tiers

There are **five CONUS M&IE tiers**, running from the standard **$68** rate to the highest designated locality rate of **$92**. Two structural facts are worth noting for rule-writing:

- **Incidental expenses are a flat $5 in every tier.** The incidental component does not scale with locality; only the three meal components do.
- **The three meal components plus $5 incidentals sum exactly to the M&IE total** in each row (e.g., $16 + $19 + $28 + $5 = $68; $23 + $26 + $38 + $5 = $92). This makes meal-deduction arithmetic exactly checkable.

### First and last day of travel

The final column is a reduced partial-day amount, equal to **75% of the full M&IE rate** for that tier. The published values confirm the arithmetic: 0.75 × $68 = **$51.00**; 0.75 × $74 = **$55.50**; 0.75 × $80 = **$60.00**; 0.75 × $86 = **$64.50**; 0.75 × $92 = **$69.00**. Note that $55.50 and $64.50 carry cents — a rounding trap for anyone assuming whole-dollar per diems.

### Provided meals

The page states that **meals provided by a common carrier, and complimentary meals provided by a hotel or motel, do not affect the per diem allowance**. So an airline meal or a hotel's complimentary breakfast is *not* a deductible provided meal, whereas a meal furnished by the host organization or included in a conference registration is handled under the deduction rules.

### What this page does not state

The retrieved page does **not** identify which fiscal year the table applies to, and it does not publish the separate incidental-expenses-only rate or the lodging rates. Those must be sourced from the GSA per diem rate lookup or the per-diem FAQ rather than from this table.

## Eval-relevant hooks

- Meal-deduction computation: given an M&IE tier and a list of provided meals, compute the reduced per diem (e.g., $68 tier with lunch provided → $68 − $19 = $49). Every subtraction is verifiable against the published table.
- Partial-day computation: first/last travel day pays 75% of the tier — $51.00, $55.50, $60.00, $64.50, $69.00 for the $68/$74/$80/$86/$92 tiers respectively; the .50 cases catch naive rounding.
- Checkable invariant: breakfast + lunch + dinner + $5 incidentals = M&IE total for every tier; incidentals are **always $5** regardless of locality.
- Exception rule: complimentary hotel breakfast and common-carrier meals do **not** reduce per diem — a frequent false-positive in automated expense audit rules.
- Combined-scenario task: a first travel day at the $80 tier with a provided dinner exercises both the 75% proration and the meal-deduction rule, and forces the agent to state the ordering it applied.
- Reconstruction task: infer the locality tier from a claimed per-diem amount and flag amounts that match no published tier.
