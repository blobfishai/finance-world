# Invoice Tolerances (Oracle Fusion Cloud Payables)

- **URL:** https://docs.oracle.com/en/cloud/saas/financials/26b/fappp/invoice-tolerances.html
- **Publisher:** Oracle (Using Payables Invoice to Pay, Oracle Fusion Cloud Financials)
- **Retrieved:** 2026-08-10
- **Topic:** ap-3way-match

## Summary

The authoritative list of **named tolerance fields** in Oracle Fusion Payables. Tolerances determine whether a **matching hold** is placed during the **invoice validation** process for a matched invoice. Two families exist — quantity-based and amount-based — and each tolerance is expressed as **either a percentage or an amount**.

### Quantity-based tolerances (published names)

| Tolerance | Variance measured | Expressed as |
|---|---|---|
| **Ordered Percentage** | Billed qty exceeds ordered quantity on the PO schedule line | Percentage |
| **Maximum Ordered** | Same variance, absolute cap | Amount |
| **Received Percentage** | Billed qty exceeds received quantity on the PO schedule line | Percentage |
| **Maximum Received** | Same variance, absolute cap | Amount |
| **Price Percentage** | Difference from unit price on the PO schedule line | Percentage |
| **Conversion Rate Amount** | Variance between invoice amount and PO schedule amount, compared in **ledger currency** (foreign-currency invoices) | Amount |
| **Schedule Amount** | Variance between all invoice amounts in **entered currency** and the PO schedule amount | Amount |
| **Total Amount** | Combined variance of Conversion Rate Amount **and** Schedule Amount (foreign-currency invoices) | Amount |
| **Consumed Percentage** | Billed qty exceeds consumed quantity on the **consumption advice** | Percentage |
| **Maximum Consumed** | Same variance, absolute cap | Amount |

Validation for the quantity family checks **billed vs. ordered/received/consumed quantity without considering price**.

### Amount-based tolerances (published names)

**Ordered Percentage**, **Maximum Ordered**, **Received Percentage**, **Maximum Received**, **Conversion Rate Amount**, **Total Amount** — same names, but the comparison is billed **amount** vs. ordered/received **amount** on the PO schedule line.

### Configuration semantics (the decision rules)

- A **zero percentage tolerance means no variance is allowed** (any deviation holds the invoice).
- **No active tolerance value means infinite variance is allowed** (the check is effectively disabled). Leaving a field blank is therefore *not* the conservative setting — this inversion is the most common configuration error.
- Tolerances are grouped into a tolerance definition and then **assigned to a supplier site** (not to the supplier header, and not globally).
- When invoice validation runs and billed amounts exceed the defined tolerances, a **matching hold is automatically placed** on the invoice, and the **invoice cannot be paid until holds are released**.

The page does not publish any recommended numeric values — tolerance percentages and amounts are customer-defined. Note that explicitly: there is no Oracle-published "standard" 5% or $100 tolerance.

## Eval-relevant hooks

- Configuration-inversion trap: assert that a blank tolerance = infinite variance allowed while 0% = zero variance allowed; ask an agent to harden a tolerance template and check it does not just clear fields.
- Field-selection task: given a foreign-currency invoice with both an FX-rate variance and a schedule-amount variance, identify **Total Amount** as the combined-variance tolerance (vs. Conversion Rate Amount or Schedule Amount individually).
- Quantity vs. amount family routing: for a services PO matched on amount, the agent must use the amount-based **Ordered Percentage / Maximum Received**, not the quantity family.
- Consignment scenario: a billed quantity exceeding the **consumption advice** maps to **Consumed Percentage / Maximum Consumed**, not Received.
- Assignment-level check: tolerances attach to the **supplier site**; an eval can present a fix applied at supplier level and require the agent to reject it.
- Payment-blocking assertion: an invoice with an unreleased matching hold cannot be selected for payment — a checkable precondition for any payment-run task.
