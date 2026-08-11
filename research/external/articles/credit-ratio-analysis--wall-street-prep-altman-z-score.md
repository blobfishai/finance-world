# Altman Z-Score — Formula + Calculator

- **URL:** https://www.wallstreetprep.com/knowledge/altman-z-score/
- **Publisher:** Wall Street Prep
- **Retrieved:** 2026-08-10
- **Topic:** credit-ratio-analysis

## Summary

The Altman Z-Score is a multivariate discriminant model for bankruptcy risk, developed by NYU Stern professor Edward Altman. This page sets out the original model, two variants, and the zone cutoffs used to classify a borrower.

### Original model — public manufacturing companies

**Z = (1.2 × X1) + (1.4 × X2) + (3.3 × X3) + (0.6 × X4) + (0.99 × X5)**

| Variable | Definition | What it proxies |
| --- | --- | --- |
| X1 | Working Capital ÷ Total Assets | short-term liquidity |
| X2 | Retained Earnings ÷ Total Assets | reliance on debt financing / cumulative profitability |
| X3 | EBIT ÷ Total Assets | operating profitability |
| X4 | Market Capitalization ÷ Total Liabilities | market view of solvency |
| X5 | Sales ÷ Total Assets | asset efficiency |

Note on the X5 coefficient: this page prints **0.99**. Other publications state the original coefficient as **0.999**; the difference is immaterial to classification but matters if an eval demands an exact reproduction, so the source's own figure is recorded here.

**Zones (public manufacturing):**
- **Z > 2.99** → Safe Zone (low bankruptcy risk)
- **1.81 ≤ Z ≤ 2.99** → Grey Zone (moderate risk)
- **Z < 1.81** → Distress Zone (high bankruptcy risk)

### Z' — private manufacturing companies

**Z' = (0.717 × X1) + (0.847 × X2) + (3.107 × X3) + (0.42 × X4) + (0.998 × X5)**

The re-estimation exists because a private company has no market capitalization; note that the page does not restate the X4 definition for this variant, so treat X4's book-value substitution as *not documented here*.

### Z'' — non-manufacturing / emerging markets

**Z'' = 3.25 + (6.56 × X1) + (3.26 × X2) + (6.72 × X3) + (1.05 × X4)**

This four-variable model **drops X5 (Sales ÷ Total Assets)** — the asset-turnover term whose industry sensitivity makes cross-sector comparison unreliable — and adds a **constant of 3.25**.

**Zones (private non-manufacturing):**
- **Z'' > 2.60** → Safe Zone
- **1.10 ≤ Z'' ≤ 2.60** → Grey Zone
- **Z'' < 1.10** → Distress Zone

### Worked example
For a hypothetical public manufacturer with X1 = 0.13, X2 = 0.05, X3 = 0.13, X4 = 0.67, X5 = 0.38, the computed **Z = 1.40**, which falls in the **Distress Zone** (below 1.81). This is a good regression test: the weighted sum must reproduce 1.40 and the classification must be *distress*, not *grey*.

**Accuracy:** this page publishes **no classification-accuracy percentages** from Altman's original study. Any "the Z-Score is X% accurate one year prior to bankruptcy" claim cannot be sourced here.

## Eval-relevant hooks

- Computation task: from a balance sheet and income statement, derive all five ratios, apply the exact coefficients, and return both the score and the zone label — three-way classification is gradeable exactly.
- Model-selection decision rule: public manufacturer → **Z**; private manufacturer → **Z'**; non-manufacturer / emerging market → **Z''** (which has no X5 and carries a **+3.25** constant). Picking the wrong variant is a clean failure mode.
- Cutoff-boundary tests: scores of exactly 1.81, 2.60, 2.99 sit on documented boundaries; also test that **Z'' uses 2.60/1.10**, not the 2.99/1.81 cutoffs.
- Trap: applying the Z (public) model to a private company with no market cap — the correct move is to switch models, not to substitute book equity silently.
- Regression fixture: X1 0.13 / X2 0.05 / X3 0.13 / X4 0.67 / X5 0.38 → **Z = 1.40, Distress**.
- Grounding assertion: no accuracy percentage is published on this page; a fabricated accuracy claim is a detectable hallucination.
