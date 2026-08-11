# SOP-GL-05 — Period close and reopening

> Contoso Entertainment System USA · Controllership · effective 2026-01-01 · v1.4
> SIMULATION ONLY

## 1. Period statuses

| Status | Meaning |
|---|---|
| `open` | postings accepted |
| `on_hold` | close in progress; only the close team's own adjusting entries, by exception |
| `closed` | hard locked; the ERP refuses postings and no exception exists |

Check `FiscalPeriods` before dating any journal. Do not infer a period's status from the
calendar — the close calendar and the calendar month diverge routinely.

## 2. Corrections to a closed period

A misstatement discovered after a period is closed is **never** forced back into that period.
Statutory reporting for a closed period has been filed; reopening it is a controller-level
decision requiring an audit memo, and is not available to staff accountants.

The correction is booked **in the earliest period that is currently `open`**, with the
originating period named in the journal description so the audit trail connects them. Skip
any period that is `on_hold` — an in-flight close is not a parking space for corrections.

## 3. Reclassifications

A coding correction moves the amount between expense accounts. It is a reclass, not a new
expense: the debit and credit are both expense lines and the entry nets to zero P&L impact.
Do not reverse and re-raise; book the reclass directly.

## 4. Authority

Reclasses below the staff-accountant delegation-of-authority threshold post directly. Above
it, they stage for approval like any other journal.
