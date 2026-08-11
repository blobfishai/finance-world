# AS 1105: Audit Evidence

- **URL:** https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105
- **Publisher:** PCAOB (Public Company Accounting Oversight Board)
- **Retrieved:** 2026-08-10
- **Topic:** audit-pbc-evidence

## Summary

AS 1105 is the standard that defines what counts as audit evidence and how an auditor judges whether a piece of client-provided support is good enough. For a PBC/evidence world it supplies the grading rubric: why one artifact is accepted and a superficially similar one is rejected.

### Definition, sufficiency, appropriateness

Paragraph .02 defines audit evidence as all the information, whether obtained from audit procedures or other sources, used by the auditor in reaching the conclusions on which the opinion is based — explicitly including information that **contradicts** management's assertions, not just information that supports them.

- **Sufficiency** (.04–.05) is the measure of the **quantity** of evidence. It is driven by the assessed risk of material misstatement (higher risk → more evidence needed) and by the quality of the evidence obtained (higher quality → less corroboration needed).
- **Appropriateness** (.06) is the measure of **quality** — specifically **relevance** and **reliability**.

### Reliability factors (.08) — the acceptance/rejection rubric

Reliability depends on nature, source, and circumstances. The enumerated factors:

- Evidence from **independent external sources** is more reliable than evidence from sources internal to the company.
- Company-generated information is more reliable when the company's **internal control, including IT general controls, is effective**.
- Evidence obtained **directly by the auditor** is more reliable than evidence obtained indirectly or by inference.
- **Original documents** are more reliable than photocopies, digitized versions, or otherwise converted formats; for converted documents, reliability depends on the controls over the conversion and over subsequent maintenance.
- Third-party evidence carrying **restrictions** requires the auditor to evaluate the effect of those limitations.

This is the direct source of the everyday PBC rejection reasons: a screenshot instead of a system-generated report, a re-keyed spreadsheet instead of the original, a customer-supplied copy instead of a direct confirmation.

### Information produced by the company (.10)

When the auditor uses information produced by the company, the standard requires the auditor to (a) **test the accuracy and completeness** of the information, or test the controls over its accuracy and completeness (including relevant IT controls), and (b) evaluate whether the information is **sufficiently precise and detailed** for the auditor's purpose. This is the technical basis for the tie-out expectation on every client schedule: the schedule must be shown to agree to the ledger/source system and to be complete.

### The seven audit procedures (.13–.21)

1. **Inspection** (.15) — examining records or documents (paper or electronic), or physically examining an asset.
2. **Observation** (.16) — watching a process or procedure performed by others; limited because it is evidence only at the point in time observed.
3. **Inquiry** (.17) — seeking information from knowledgeable persons inside or outside the company.
4. **Confirmation** (.18) — a direct written response from an external party.
5. **Recalculation** (.19) — checking mathematical accuracy.
6. **Reperformance** (.20) — independently executing a control originally performed by the company.
7. **Analytical procedures** (.21) — evaluating relationships among financial and non-financial data.

### Selecting items for testing (.22–.28)

Three means of selection are recognized:

- **Selecting all items** (.24) — 100% examination, appropriate for small populations, for significant risks, or where the procedure can be automated.
- **Selecting specific items** (.25–.26) — items with specified characteristics: key items, items **exceeding a threshold amount**, or suspicious/unusual items. Critically, paragraph .27 states results from specific-item selection **cannot be projected to the population**.
- **Audit sampling** (.28) — testing less than 100% to draw a conclusion about the whole balance or class of transactions.

### Conflicting evidence (.29)

If evidence from one source is inconsistent with evidence from another, or if the auditor has doubt about the reliability of information, the auditor **must perform the procedures necessary to resolve the matter** and determine the effect on other aspects of the audit.

## Eval-relevant hooks

- Evidence-grading task: rank candidate artifacts for the same assertion (bank confirmation vs. bank statement PDF vs. screenshot of online banking vs. client spreadsheet) using the .08 reliability hierarchy — external/independent > direct auditor knowledge > original over copy.
- Checkable rule: any schedule produced by the client must have its **accuracy and completeness** tested (or the controls over them tested) before it can support a conclusion — this is the codified "tie it to the GL" requirement.
- Rejection-reason generator: converted/digitized documents are only as reliable as the controls over conversion and maintenance — a defensible basis for re-requesting an original.
- Sampling-scope trap: a "targeted" selection of all items above a threshold produces conclusions that may **not** be projected to the population (.27); an agent that extrapolates from a specific-item selection is wrong.
- Procedure-matching task: map an assertion to the correct procedure among the seven named types (e.g., existence of cash → confirmation; control operating effectiveness → reperformance; arithmetic of a schedule → recalculation).
- Conflict-handling rule: inconsistent evidence obliges additional procedures and an assessment of knock-on effects — not a silent choice of the more convenient item.
