# Price variance vs. quantity variance on an invoice, and how each should be resolved

- **URL:** https://www.stampli.com/resources/invoice-match-exceptions-price-quantity/
- **Publisher:** Stampli
- **Retrieved:** 2026-08-10
- **Topic:** ap-3way-match

## Summary

Where the ERP docs give field names, this source gives the **ownership rules** — who is allowed to resolve which match exception, and why AP must not resolve some of them at all.

### Definitions

- **Price variance** — the invoice charges a **different unit price than the PO**.
- **Quantity variance** — the invoice **bills more (or less) than was ordered or received**.

Both are surfaced during automated **line-level** matching against PO and receipt records; the system's job is to surface the discrepancy for human judgment, not to reconcile it silently.

### How tolerance is expressed

Tolerance is defined as the variance accepted without intervention, expressed as **a percentage, an absolute amount, or both** — the published illustrative example being **2% up to $100** (a percentage capped by an absolute ceiling; this is the "lesser-of" pattern in practice). The source is explicit that this figure is **illustrative only** and prescribes no mandatory percentage.

Threshold-setting inputs, as published: the **historical variance distribution**, the **cost of investigation labor (typically $25–$50 per investigation)**, and risk appetite. The implied decision rule is that a tolerance band below the cost of investigating is uneconomic to enforce.

### Resolution ownership (the control rule)

- **Price variances → procurement owns commercial resolution.** The exception routes to procurement/the vendor to determine whether a price change was agreed (in which case the **PO is updated**) or the vendor erred (in which case a **revised invoice or credit memo** is required).
- **AP must not silently edit prices on the invoice** to force a match — the source frames this as converting a control into a bypass. This is the single most checkable rule in the article.
- **Quantity variances → receiving records answer the question.** Resolution runs through receiving discipline and documentation, not through AP adjustment.

### Workflow states

An invoice awaiting a receipt enters a visible **"awaiting receipt"** state. AP detects and routes exceptions. Items **within tolerance are auto-accepted**; genuine exceptions land in a **match-exception queue** with full context before approval and payment.

### Cadence

**Quarterly variance analysis by vendor and by cause** is recommended to identify chronic offenders warranting supplier-management intervention (as opposed to case-by-case firefighting).

## Eval-relevant hooks

- Ownership-routing task: route a $340 unit-price discrepancy to procurement and a 12-unit over-billing to receiving; penalize routing either to AP for direct correction.
- Control-bypass detection: an agent that "resolves" a price variance by editing the invoice unit price to match the PO must be scored as failing — the legitimate outcomes are PO update, revised invoice, or credit memo.
- Tolerance-expression task: implement a combined rule ("2% up to $100") and evaluate boundary cases — e.g. a $9,000 line with a $150 variance is 1.67% but exceeds the $100 absolute cap, so it is an exception.
- Economic-threshold reasoning: given a $25–$50 investigation cost, argue whether a $12 tolerance band is justified.
- Queue-state assertion: an invoice matched to a PO with no receipt posted should sit in "awaiting receipt", not be rejected outright.
- Trend task: from a quarter of exception data, identify the vendor generating recurring price variances and recommend supplier-management escalation rather than per-invoice resolution.
