# Bank Reconciliation (procedure and reconciling-item treatment)

- **URL:** https://www.accountingtools.com/articles/bank-reconciliation
- **Publisher:** AccountingTools
- **Retrieved:** 2026-08-10
- **Topic:** bank-reconciliation

## Summary

A practitioner reference for the mechanical procedure and, most usefully, for **which side of the reconciliation each item adjusts** — the single rule agents most often get backwards.

### Six-step procedure as published

1. Enter the bank reconciliation software module to view uncleared items.
2. Check off all **checks** listed on the bank statement as having cleared.
3. Check off all **deposits** listed on the bank statement as having cleared.
4. Enter as **expenses** all bank charges appearing on the bank statement that have not already been recorded.
5. Enter the ending bank statement balance and compare it to the book balance.
6. If the two do not agree, investigate for additional reconciling items; otherwise post the changes and close the reconciliation.

### Which side each item adjusts (the load-bearing rule)

**Adjustments to the BANK balance** (timing differences — the bank does not know yet, so no journal entry):
- **Deposits in transit** → *add* to the bank balance.
- **Outstanding checks** → *subtract* from the bank balance.

**Adjustments to the BOOK balance** (bank-originated items — the company does not know yet, so each *requires a journal entry*):
- **Bank service fees** → *deduct* from the book balance.
- **NSF checks and associated penalties** → *deduct* from the book balance.
- **Interest earned** → *add* to the book balance.

### Adjusted balance method

The completion test is stated directly: the **adjusted bank balance should equal the company's ending adjusted cash balance**. Both columns are adjusted to a common figure rather than one side being forced to the other. The journal-entry population is exactly the book-side column — bank charges, NSF items, interest — plus any book errors; the bank-side column (deposits in transit, outstanding checks) generates no entries because those transactions are already on the books.

### Frequency

Month-end reconciliation is treated as the minimum cadence; the source describes **daily** reconciliation as "even better" but does not mandate it.

### Explicit gaps in this source

Stated plainly so nothing is invented: this article gives **no stale-dated check day count** (no 6-month/180-day rule), **no variance or materiality thresholds**, no check-kiting detection procedure, and no named preparer/reviewer roles. It also gives no procedural detail for book-vs-bank errors beyond noting they exist.

## Eval-relevant hooks

- Sidedness classification task: given a mixed list of reconciling items (deposit in transit, outstanding check, wire fee, NSF return, interest credit, transposed book entry), assert for each whether it adjusts the bank column or the book column, and its sign.
- Journal-entry scoping: assert that exactly the book-side items generate journal entries and that deposits in transit / outstanding checks generate none — a common agent error is booking an accrual for outstanding checks.
- Adjusted-balance completion assertion: adjusted bank balance must equal adjusted book balance; an eval can present a reconciliation that ties only because an item was placed on the wrong side.
- Step-order check: bank charges are recorded as expenses (step 4) *before* the balance comparison (step 5), so an agent that compares balances first and never records fees will report a false out-of-balance.
- Negative-knowledge check: this source supplies no stale-check threshold — an agent citing "180 days per AccountingTools' bank reconciliation article" would be fabricating.
