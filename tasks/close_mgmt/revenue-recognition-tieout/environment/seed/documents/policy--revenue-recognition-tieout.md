# RAP-04 — Revenue recognition tie-out

> Contoso Entertainment System USA · Revenue Accounting · effective 2026-01-01 · v2.1
> SIMULATION ONLY

Every contract in the FY26 contract register is tied out against its recognition schedule
before the register is released to the external auditors. The tie-out has **two independent
tests**. A contract passes only if it passes both.

## 1. System of record

The recognition schedule workbook is the system of record for recognised revenue. Recognised
revenue for a contract is the **sum of that contract's schedule lines** — recompute it.

The `Recognised USD (linked)` column on the contract register is a convenience formula that is
refreshed by hand and pasted as values before each distribution. It is **not authoritative**
and it is routinely stale. Compare `lastModifiedDateTime` on the two files before you rely on
anything the register has cached; where they disagree, the schedule governs.

## 2. Test A — amount

Compare recognised revenue to the contract value. The permitted variance is **the greater of
USD 100.00 or 0.1% of the contract value**. Variance inside that band is straight-line
rounding drift and is not an exception.

A contract whose variance falls outside the band is an **amount exception**.

## 3. Test B — term alignment

Run this test on **every** contract, including the ones that pass Test A. Total recognised
revenue can tie to the cent while the revenue lands in the wrong periods, and that is the error
the auditors ask about first.

The schedule aligns to the term when both hold:

- the **first** scheduled period is the calendar month of the contract start date, and
- the **last** scheduled period is the calendar month of the contract end date.

A schedule that begins before the start month, runs past the end month, or stops short of the
end month is a **timing exception** — even where the total ties exactly. Accelerating a full
contract value into a shortened window and trailing a period past the term end are both
recognition errors and are reported the same way.

## 4. Classification and reporting

Each contract appears in at most one exception class:

| Test A | Test B | Class |
|---|---|---|
| fail | any | amount exception |
| pass | fail | timing exception |
| pass | pass | clean — do not report |

Amount variances are reported **by direction and never netted**: over-recognised (schedule
exceeds contract value) and under-recognised (schedule falls short) are separate lines, because
over-recognition is a restatement risk and under-recognition is a cut-off risk. Timing
exceptions carry no amount variance by definition and are excluded from both totals.
