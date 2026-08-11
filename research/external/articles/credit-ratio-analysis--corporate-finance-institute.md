# Coverage Ratio — Guide to Understanding All the Coverage Ratios

- **URL:** https://corporatefinanceinstitute.com/resources/accounting/coverage-ratio-overview/
- **Publisher:** Corporate Finance Institute (CFI)
- **Retrieved:** 2026-08-10
- **Topic:** credit-ratio-analysis

## Summary

CFI's coverage-ratio guide supplies the four coverage formulas a credit analyst uses to test whether operating performance and asset backing can service debt, each with an explicit numerator/denominator and a worked example. Unlike CFI's broader "Credit Analysis Ratios" page — which lists ratio *names* without formulas and was rejected as a source for that reason — this page states the arithmetic and gives benchmark values.

### 1. Interest Coverage Ratio (Times Interest Earned)
**Interest coverage ratio = Operating income ÷ Interest expense**
- **Benchmark: an interest coverage ratio of 1.5 is considered the minimum acceptable ratio.**
- Worked example: $500,000 operating income ÷ $60,000 interest expense = **8.3x**.

Note the numerator is **operating income**, not EBITDA — a materially different (more conservative) measure than the EBITDA/Interest convention used in leveraged lending, because depreciation and amortization remain deducted. "Times interest earned" is used here as a synonym.

### 2. Debt Service Coverage Ratio (DSCR)
**Debt service coverage ratio = Operating income ÷ Total debt service**
- **Benchmark: an ideal debt service coverage ratio is 2 or higher.**
- Worked example: $500,000 operating income ÷ ($100,000 interest + $150,000 principal) = **2.0x**.

The key structural point is that **total debt service includes principal, not just interest** — which is why DSCR is always lower than the interest coverage ratio for the same borrower and why an amortizing facility can fail DSCR while passing interest coverage.

### 3. Cash Coverage Ratio
**Cash coverage ratio = Total cash ÷ Total interest expense**
- Worked example: $50 million cash ÷ $2.5 million interest expense = **20.0x**.

This is a balance-sheet (stock) test rather than an earnings (flow) test: it asks how many years of interest the existing cash pile covers, independent of operating performance.

### 4. Asset Coverage Ratio (ACR)
**Asset coverage ratio = ((Total assets – Intangible assets) – (Current liabilities – Short-term debt)) ÷ Total debt obligations**
- Interpretation: an **ACR of 1** means the company could just barely pay its debts by selling all its assets; **above 1** indicates capacity to cover debt without liquidating everything.
- Worked example: (($170M – $30M) – ($30M – $20M)) ÷ $100M = **1.3x**.

Two deductions inside the formula carry the analytic content: **intangibles are removed** because they realize little in liquidation, and **short-term debt is added back** to current liabilities (i.e., excluded from the deduction) so that debt is not double-counted against the asset base.

Across all four ratios the general rule stated is that a **higher coverage ratio indicates greater ability to meet financial obligations**. The page does not cover leverage ratios (debt-to-equity), liquidity ratios (current, quick), or turnover metrics (inventory turnover, DIO) — those formulas are not available from this source.

## Eval-relevant hooks

- Threshold decision rules: **ICR minimum acceptable = 1.5x**; **ideal DSCR = 2 or higher**; **ACR = 1.0** is the break-even liquidation line. These are three directly checkable pass/fail rules for a credit memo task.
- Numerator-definition trap: this source computes ICR and DSCR from **operating income**, while leveraged-finance sources use **EBITDA**. An eval can require the agent to state which convention it used and flag the divergence rather than silently mixing them.
- DSCR construction task: include **principal repayments** in total debt service; an agent that computes DSCR using interest only will produce 5.0x instead of the correct 2.0x on the worked example.
- ACR construction task: reproduce the exact adjustment sequence — subtract intangibles from total assets, subtract (current liabilities – short-term debt), divide by total debt obligations — to get **1.3x** from the given figures.
- Flow-vs-stock reasoning: cash coverage (20.0x) can look strong while earnings-based coverage is weak; a good eval pairs a cash-rich, loss-making borrower to test whether the agent notices.
- Regression fixtures: 500,000/60,000 → **8.3x**; 500,000/250,000 → **2.0x**; 50M/2.5M → **20.0x**; ((170−30)−(30−20))/100 → **1.3x**.
