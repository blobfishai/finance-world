# Collection Effectiveness Index (CEI): What Is It & Why Is It Important?

- **URL:** https://www.quadient.com/en-us/blog/what-collection-effectiveness-index
- **Publisher:** Quadient
- **Retrieved:** 2026-08-10
- **Topic:** ar-collections-dunning

## Summary

This source publishes the full Collection Effectiveness Index formula with every term named, plus a worked example with dollar figures — the piece that the DSO-focused sources omit.

### The CEI formula as published

**Numerator:** (Beginning receivables + Monthly credit sales) − Ending total receivables

**Denominator:** (Beginning receivables + Monthly credit sales) − Ending current receivables

**Result:** (Numerator ÷ Denominator) × 100

The four required inputs are therefore: beginning receivables, monthly credit sales, ending **total** receivables, and ending **current** receivables. The only difference between numerator and denominator is *total* vs. *current* ending receivables — the numerator measures what was actually collected, the denominator measures what was collectible. Because ending current receivables (not yet due) are excluded from the denominator, CEI does not penalize a company for invoices that simply have not come due.

### Worked example with published figures

- Beginning receivables: **$25M**
- Monthly credit sales: **$40M**
- Ending total receivables: **$35M**
- Ending current receivables: **$20M**

Calculation: ($25M + $40M − $35M) ÷ ($25M + $40M − $20M) × 100 = **57% CEI**

Working it through: numerator = $30M, denominator = $45M, ratio = 0.5666… → 57%.

### Benchmark

**A CEI of 85% or higher is considered good.** Values below that indicate collections processes needing improvement. (Note this differs from the commonly cited 80% threshold — this source's published bar is 85%.)

### Cadence

CEI can be calculated for a period of any duration, and is **typically calculated monthly**. The formula as published uses "monthly credit sales," so applying it to a different period requires substituting the credit sales for that period.

### CEI versus DSO

The stated distinction: CEI measures the collections department's **effectiveness at recovering receivables** (did the money get collected at all, out of what was collectible), while DSO tracks **how many days elapse before payment arrives**. The source recommends using both together for a complete cash-flow picture — CEI answers a quality question, DSO answers a timing question.

### Not covered

This source does not publish formulas for Average Days Delinquent, Best Possible DSO, aging-bucket definitions, dunning step timings, or role assignments. It is a single-metric deep dive.

## Eval-relevant hooks

- **Exact-arithmetic assertion:** the worked example is fully specified, so an agent computing CEI from ($25M, $40M, $35M, $20M) must return 57%. Any other answer is a hard fail.
- **Formula-construction trap:** the most common CEI error is using ending *total* receivables in both numerator and denominator (which forces 100%) or swapping total and current. An eval can supply the four inputs and check the agent placed *current* receivables in the denominator only.
- **Benchmark classification rule:** a computed CEI of 57% falls well below the published 85% "good" bar — an agent should flag the collections process as needing improvement rather than reporting the number without judgment.
- **Metric-selection reasoning:** asked "are our collectors effective, or are our terms just long?", the correct decomposition is CEI for effectiveness and DSO for timing. Tests whether the agent distinguishes quality from timing.
- **Input-sourcing task:** the agent must pull four specific balances (beginning AR, period credit sales, ending total AR, ending current AR) from an AR aging and a sales ledger — a realistic multi-source data-extraction step before the calculation.
- **Period substitution:** applying CEI to a quarter requires substituting quarterly credit sales for monthly; an agent that keeps monthly sales while using quarter-end balances produces an invalid ratio.
