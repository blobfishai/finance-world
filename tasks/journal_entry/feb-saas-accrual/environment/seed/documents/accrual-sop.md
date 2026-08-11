# SOP-GL-02 — Period-end expense accruals

> Contoso Entertainment System USA · Controllership · effective 2026-01-01 · v2.0
> SIMULATION ONLY

An accrual is raised when the entity has received a service in the period but no vendor
invoice has been posted against it by the close cut-off.

## 1. Before raising an accrual

Confirm no vendor invoice for the service is already posted in the period. Accruing on top
of a posted invoice double-counts the expense and will be reversed as an audit finding.

## 2. Measurement basis

Accruals are computed on a **365-day basis**:

```
accrual = annual contract value / 365 x days of service delivered in the period
```

rounded to the cent. Count the service days **inclusive of both the commencement date and
the period-end date**. Do not use a monthly convention (annual / 12) — the entity's
contracts commence mid-month too often for it to be defensible.

Always measure against the contract version **in effect on the service dates**. Superseded
versions stay in the document store for audit trail; check the effective date before using
one.

## 3. Coding

| Item | Account |
|---|---|
| Software & subscription expense | 600200 |
| Accrued liabilities (credit) | 210100 |

Accruals post to the period in which the service was delivered, where that period is open.

## 4. Authority

Journals are subject to the delegation-of-authority thresholds in the ERP
(`ApprovalPolicies`). A journal above the staff-accountant limit is **staged and submitted
for approval — it is not posted** until the named approver has approved it. Do not report an
accrual as booked until the ERP shows it posted.
