# Credit Analysis — Financial Ratios + Lending Process

- **URL:** https://www.wallstreetprep.com/knowledge/credit-risk-analysis/
- **Publisher:** Wall Street Prep
- **Retrieved:** 2026-08-10
- **Topic:** credit-ratio-analysis

## Summary

This page is the leveraged-lending view of ratio analysis: the metrics a credit analyst actually underwrites and covenants against, expressed as multiples of EBITDA rather than as textbook liquidity ratios.

### Leverage ratios

| Metric | Formula |
| --- | --- |
| Total Leverage | Total Debt ÷ EBITDA |
| Net Leverage | Net Debt ÷ EBITDA |
| Senior Debt Leverage | Senior Debt ÷ EBITDA |

Net Debt nets cash against gross debt; senior leverage isolates the claim sitting ahead of subordinated tranches, which is why lenders covenant on it separately from total leverage.

### Coverage ratios

| Metric | Formula |
| --- | --- |
| EBIT Coverage | EBIT ÷ Interest Expense |
| EBITDA Interest Coverage | EBITDA ÷ Interest Expense |
| Capex-Adjusted Coverage | (EBITDA – Capex) ÷ Interest Expense |
| Cash Interest Coverage | EBITDA ÷ Cash Interest Expense |
| Fixed Charge Coverage (FCCR) | (EBITDA – Capex – Cash Taxes) ÷ (Cash Interest + Mandatory Repayment) |

The progression matters: EBITDA/Interest is the loosest, and each successive variant strips out another mandatory cash outflow. **Cash Interest Coverage** excludes non-cash (e.g., PIK) interest; **FCCR** is the strictest because it charges the borrower for capex, cash taxes, and mandatory amortization before measuring capacity.

### Covenant thresholds
The page gives maintenance-covenant examples — presented as illustrative, not universal, with the explicit caveat that actual levels vary by lender, industry, and transaction structure:

- **Total Leverage cannot exceed 6.0x EBITDA**
- **Senior Leverage cannot exceed 3.0x EBITDA**
- **EBITDA Coverage cannot fall below 2.0x**
- **Fixed Charge Coverage Ratio cannot fall below 1.0x**

Note the direction of each test: leverage covenants are ceilings ("cannot exceed"), coverage covenants are floors ("cannot fall below"). Getting the inequality direction backwards is the most common mechanical error in covenant work.

### Working capital / cash conversion metrics

- **A/R Days = (A/R ÷ Revenue) × 90**
- **A/P Days = (A/P ÷ COGS) × 90**
- **Inventory Days = (Inventory ÷ COGS) × 90**
- **Cash Conversion Cycle = A/R Days + Inventory Days – A/P Days**

The **90** is a quarterly-period convention; the same formulas take 365 for an annual period, so a model must state which period it is using. Note the denominators differ deliberately: receivables scale with **Revenue**, while payables and inventory scale with **COGS**. Inventory Days is the reciprocal-style expression of inventory turnover (turnover = COGS ÷ Inventory), so DIO and inventory turnover are recoverable from each other.

The page does not present the "5 Cs of Credit," and it publishes no default-rate or accuracy statistics.

## Eval-relevant hooks

- Covenant-compliance task: given EBITDA, total debt, senior debt, capex, cash taxes, cash interest, and mandatory amortization, compute all four covenant tests and return pass/fail per covenant with the correct inequality direction (leverage = ceiling, coverage = floor).
- Headroom task: solve for the EBITDA decline that would breach the **6.0x total leverage** or the **2.0x EBITDA coverage** covenant first — a classic credit-analyst deliverable and exactly gradeable.
- Metric-selection trap: asked "can the borrower service its debt," the strongest answer uses **FCCR**, not EBITDA/Interest, because only FCCR charges capex, cash taxes, and mandatory repayment.
- PIK trap: with PIK interest present, **Cash Interest Coverage** and **EBITDA Interest Coverage** diverge; an agent that treats them as interchangeable is wrong.
- Period-convention check: the working-capital formulas use **×90** (quarterly). An agent applying them to annual figures without switching to 365 produces a 4x error.
- Denominator check: **A/R Days uses Revenue; A/P Days and Inventory Days use COGS** — a frequently botched detail that is trivially checkable.
