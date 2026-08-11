# Matching Hold Detail Report — matching hold and release name taxonomy

- **URL:** https://docs.oracle.com/cd/A60725_05/html/comnls/us/ap/invoic10.htm
- **Publisher:** Oracle (Oracle Payables Help / User's Guide)
- **Retrieved:** 2026-08-10
- **Topic:** ap-3way-match

## Summary

The most complete published **match-exception taxonomy** available: every matching hold name Oracle Payables can apply, with its exact trigger condition, plus the release-status names. This is the vocabulary an AP exception queue is actually built from.

### Matching holds with HELD status (exact names and triggers)

- **Can't Close PO** — cannot close the PO before the shipment is fully delivered; applied if the Final Matching Payables option is enabled.
- **Currency Difference** — invoice currency differs from the purchase order currency.
- **Final Matching** — attempting to match to a PO permanently closed by final matching.
- **Matching Required** — the invoice is not matched to a PO although the supplier site requires matching.
- **Max Qty Ord** — quantity billed exceeds quantity ordered by the tolerance **amount**.
- **Max Qty Rec** — quantity billed exceeds quantity received by the tolerance **amount**.
- **Max Rate Amount** — exchange rate variance between PO and invoice exceeds the tolerance amount limit.
- **Max Ship Amount** — variance between invoice and shipment amount exceeds the tolerance amount limit.
- **Max Total Amount** — sum of invoice and exchange rate variances exceeds the tolerance amount limit.
- **PO Not Approved** — the PO is not approved (can occur if someone updates a PO *after* an invoice is matched).
- **Price** — invoice price exceeds PO price by more than the tolerance level allowed.
- **Qty Ord** — quantity billed exceeds quantity ordered by the tolerance **percentage**.
- **Qty Rec** — quantity billed exceeds quantity received by the tolerance **percentage**.
- **Quality** — quantity billed exceeds quantity **accepted** (the 4-way match condition).
- **Rec Exception** — Purchasing has enabled a receipt exception flag on the PO shipment being matched to.
- **Tax Difference** — invoice tax name differs from the PO tax name; also applies if the PO shipment is non-taxable but the matched invoice distribution carries tax.

**Critical naming pattern:** the `Max Qty Ord` / `Qty Ord` pair (and `Max Qty Rec` / `Qty Rec`) are *not* duplicates — the `Max` prefix denotes the **amount**-expressed tolerance and the bare name denotes the **percentage**-expressed tolerance. Both can fire on the same invoice.

### Release statuses (exact names)

- **Matched** — passed the matching condition during Approval.
- **Match Override** — a matching hold was manually released.
- **Invoice Quick Released** — all holds released from one or more invoices using a QuickRelease reason.
- **Holds Quick Release** — all holds released from a particular invoice using a QuickRelease reason.

### Release mechanics and roles

Holds are released through the **Invoice Approvals window** (where custom release reasons are defined), the **Invoice Holds window**, the **Invoice Actions window**, or by a **QuickRelease reason**. Prerequisites for the report: Purchasing installed and implemented, POs entered in Purchasing, invoices matched and approved, and access to the Submit Request window.

### Report parameters

Matching Hold Status (Hold / Release / Null), Supplier Name, Active Period Start and End Date, and an All Approvals checkbox.

## Eval-relevant hooks

- Exception-naming task: given a variance scenario, return the exact hold name — e.g. billed 105 against 100 ordered under a percentage tolerance → **Qty Ord**; under an amount tolerance → **Max Qty Ord**.
- 4-way match assertion: a billed quantity exceeding quantity *accepted* produces **Quality**, distinguishing 4-way from 3-way match.
- Root-cause reasoning: **PO Not Approved** arising after a post-match PO edit — the fix is in Purchasing, not AP.
- Multi-hold resolution: an invoice can carry several holds simultaneously; all must be released before payment, so a task can check the agent does not stop after clearing one.
- Release-path selection: distinguish **Match Override** (manual single-hold release) from **Holds Quick Release** / **Invoice Quick Released** (bulk QuickRelease reason) in an audit-trail question.
- Non-tolerance exceptions: **Currency Difference**, **Tax Difference**, **Matching Required**, and **Rec Exception** are not resolved by loosening tolerances — a good trap for agents that treat every hold as a tolerance problem.
