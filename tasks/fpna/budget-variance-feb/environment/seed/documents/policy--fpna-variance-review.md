# FIN-FPA-04 — Opex budget variance review and exception reporting

> Contoso Entertainment System USA · Financial Planning & Analysis · effective 2026-01-01 · v4.1
> SIMULATION ONLY

This policy governs the monthly exception page that FP&A takes into the operating review. It
applies to operating expenditure only, at the department / category / month grain at which the
FY budget is approved.

## 1. Definitions

Variance is measured against the **approved budget for the same department, category and
period**:

```
Variance USD = Actual − Budget
Variance %   = Variance USD ÷ Budget
```

For opex a **positive** variance is **unfavourable** (we spent more than we planned). A
negative variance is favourable.

## 2. The flag test — both limbs, never one

An item is flagged as a significant variance only when **both** of the following hold:

1. the variance exceeds **10%** of the budgeted amount for the period, **and**
2. the variance exceeds **USD 5,000.00**.

Either limb alone is not a flag. This is deliberate and it is the most common mistake made on
this pack:

- a large *percentage* on a small base is noise — a category budgeted at a few thousand a
  month will swing double digits on a single invoice, and flagging it fills the exception page
  with items nobody can act on;
- a large *dollar* amount on a large base is within normal tolerance — payroll and other
  high-value lines move by more than five thousand dollars every month without anything
  having gone wrong.

## 3. Direction

Only **unfavourable** variances are flagged. Favourable variances (underspend) are covered in
the written commentary and in the reforecast, and are **not** put on the exception page —
however large. An underspend is a planning question, not an exception.

## 4. Contractually front-loaded categories (seasonality)

Some categories are budgeted evenly across the twelve months but are **not billed evenly**.
Testing those against the month they land in produces a guaranteed false flag in the billing
month and a guaranteed false favourable in every other month. FP&A therefore maintains a
short list of front-loaded categories, reviewed annually with the controller.

**The FY2026 front-loaded list contains exactly one category: `Facilities`.** Property
insurance, building services and site security for both occupied sites are invoiced by the
landlord as a **single annual instalment in January** under the master services agreement,
while the budget phases the same cost evenly over the year.

A front-loaded category is **excluded from the monthly test**. It is instead tested once, on a
cumulative basis:

```
Front-loaded variance = (sum of actuals for all closed months of the year)
                      − (sum of the approved budget for ALL TWELVE months of the year)
```

and the same two limbs of §2 are then applied to that figure. Note the denominator: the
**full-year** approved budget, summed from the monthly budget rows — the phasing is not flat
in every category, so it must be summed and not multiplied. In practice a front-loaded
category flags only when cumulative spend has already overrun the whole year's budget, which
is the only circumstance in which the front-loading is actually a problem.

Categories that are **not** on the front-loaded list are always tested month by month, whatever
shape their spend appears to have.

## 5. Exception identifiers

Every flagged item is reported as a single identifier in the form:

```
Department_Category_YYYYMM
```

using the department and category exactly as they appear in the budget workbook and the
calendar month of the variance (for a front-loaded category tested cumulatively, the latest
closed month). The exception page also carries the **count** of flagged items and the **total
unfavourable variance**, being the sum of the variance USD of the flagged items only.

## 6. Sources

The two workbooks on the finance shared drive are the sole sources: the approved FY budget
and the actuals extract for the closed months. Neither is restated during the review; if they
disagree with the ledger, that is a separate reconciliation and is not resolved on this page.
