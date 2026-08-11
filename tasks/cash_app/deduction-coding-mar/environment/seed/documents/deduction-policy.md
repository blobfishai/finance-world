# SOP-AR-06 — Coding and routing customer deductions

> Contoso Entertainment System USA · Accounts Receivable · effective 2026-01-01 · v3.0
> SIMULATION ONLY

A deduction is the difference between what was invoiced and what the customer paid. Every
deduction is coded to exactly one reason and routed to the owning team. The reason-code
taxonomy, each code's validity, owner and disposition live in the ERP entity
`DeductionReasons` — read it, do not memorise it.

## 1. Code from evidence, never from the remittance narrative

The reason a customer *states* is the least reliable input we have. It is written by their AP
clerk, often from a template, and it is frequently wrong even when the deduction itself is
justified. Code from what the documents show: the order, the contract, the delivery evidence.

Where the stated reason and the evidence disagree, the evidence governs, and the deduction is
coded to what actually happened.

## 2. Materiality

Deductions **below USD 250.00** are coded `write_off_immaterial` and written off without
investigation, **whatever reason is stated**. Chasing them costs more than they recover. This
test is applied first, before any evidential analysis.

## 3. Disposition

| Validity | Consequence |
|---|---|
| valid claim | concede — issue a credit memo for the deduction |
| not a valid claim | charge back to the customer and pursue through the owning team |

The two totals are reported separately: conceded amount and chargeback amount. They are
different lines in the AR bridge and must not be netted.

## 4. Absence of evidence

A deduction with no supporting documentation of any kind is not a claim we can assess. It is
coded `unauthorized` and charged back. The customer may supply evidence later and reopen it.
