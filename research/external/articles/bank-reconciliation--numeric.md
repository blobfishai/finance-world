# Bank Reconciliations: Steps, Examples, Best Practices

- **URL:** https://www.numeric.io/blog/bank-reconciliation
- **Publisher:** Numeric
- **Retrieved:** 2026-08-10
- **Topic:** bank-reconciliation

## Summary

A close-management vendor's process guide. Its value over textbook treatments is that it attaches **aging thresholds and materiality bands** to reconciling items, and names the KPIs a controller would track.

### Five named steps

1. **Compare Balances** — align the bank account balance with the cash balance on the balance sheet.
2. **Review Bank Statement** — identify unrecorded transactions (fees, interest, wire charges).
3. **Review Account Trial Balance** — locate outstanding checks and deposits in transit.
4. **Adjust Balances** — modify GL and book balances for identified discrepancies.
5. **Record the Reconciliation** — document with preparer/reviewer sign-offs and supporting evidence.

The method is the **adjusted balance approach**: both the bank and book balances are adjusted to a common reconciled figure, then verified to match.

### Reconciling-item taxonomy (four buckets)

- **Timing differences** — outstanding checks, deposits in transit, in-process transactions.
- **Bank-only items** — service fees, interest earned, NSF charges (worked example uses a **$300** service fee and **$50** interest earned; these are illustrative example figures, not thresholds).
- **Book-only items** — unrecorded transactions, data entry errors.
- **True errors** — transposition errors, duplicate entries, misclassifications.

### Aging and variance thresholds (exact as published)

- **Outstanding checks older than 90 days** warrant investigation for stop payment and reissuance.
- **Deposits in transit uncleared for more than 3 business days** require investigation.
- Differences **under $100** may warrant investigation only if they **recur**.
- Variances **over $10,000** demand immediate explanation and resolution.
- Transactions above the materiality threshold require dual entry.

### Cadence, controls, retention

- Monthly reconciliation aligned to the standard close; optional **weekly or daily** cadence for high-volume or high-risk accounts.
- Segregation of duties stated as: never allow the same person to prepare and approve their own reconciliations; the preparer must also differ from transaction processors and check signers.
- Documentation retention **5–7 years** depending on regulatory requirements (**IRS: 7 years**; **SEC: 7 years** for public companies).

### Named KPIs

Average time to completion; number of reconciling items per period; aging of outstanding items; error frequency.

## Eval-relevant hooks

- Aging triage task: given a dated outstanding-check register, select the items over 90 days for stop-payment/reissue review and the deposits in transit over 3 business days for investigation.
- Materiality routing: a $62 unexplained variance appearing for the third consecutive month must be investigated (recurrence rule), while a one-off $62 need not be; a $14,000 variance requires immediate explanation.
- Control test: construct a reconciliation where the preparer is also a check signer, and require the agent to flag the segregation-of-duties failure (the rule covers preparer vs. approver *and* preparer vs. processor/check signer).
- Step-name fidelity: assert the five published step names in order, with "Record the Reconciliation" carrying the sign-off/evidence requirement.
- Bucket classification: sort items into timing difference / bank-only / book-only / true error — note that a transposition error is a *true error*, not a timing difference, and drives a correcting entry.
- Distractor check: the $300 fee and $50 interest are worked-example values, not policy thresholds; an eval can penalize treating them as limits.
