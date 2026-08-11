# SOP-PAY-04 — Semi-monthly payroll register review

**Owner:** FP&A / Payroll Control · **Applies to:** every semi-monthly payroll register returned
by the outsourced bureau (Ardent Payroll Services) before the pay file is released and before
the labour accrual is booked. SIMULATION ONLY — all names, rates and figures are synthetic.

## 1. Sources of record

| What | Who owns it | Where |
|---|---|---|
| Hours | HR timekeeping | the attendance export on the finance shared drive for the period |
| Rates | Comp & Benefits | the approved hourly rate schedule on the finance shared drive |
| Gross pay | Ardent Payroll Services | the register the bureau returns each period |

The rate column printed on the bureau's register is keyed by the bureau from its own master
file. It is **not** authoritative. Where the register and the approved rate schedule disagree,
the schedule governs and the difference is a variance against the bureau.

## 2. Payable hours

    payable hours = worked hours + paid-leave hours

Leave codes **PTO**, **SICK** and **HOL** are paid leave and are payable in the period they
fall in. **LWOP** (leave without pay) approved under the leave policy is recorded in the
attendance export for scheduling and headcount purposes only and is **not payable**.

Approved LWOP carries an approval reference of the form `LOA-YYYY-NNN` against the employee's
line in the attendance export. A register that pays fewer hours than the attendance export
records, solely because approved LWOP hours were excluded, is **correct** — do not raise it as
a variance, and do not fund a correction for it.

## 3. What counts as a discrepancy

A line is a discrepancy when

    gross pay on the register  ≠  payable hours × approved rate

Both legs matter, and they fail independently. An hours-only comparison will not surface a
rate mis-key, because the hours on such a line agree perfectly: the last two bureau errors we
caught in 2025 were both rate mis-keys on lines where hours tied, and both ran for two periods
before anyone noticed. Period totals are not a control either — a short-pay on one line and an
over-pay on another can leave the hours total and the gross total looking clean.

## 4. What to report

For each discrepancy line, report paid versus owed and the signed variance, stated as

    variance = gross paid − gross owed        (positive = we overpaid)

Net the period to a single figure for the accrual, but keep overpayments and underpayments
listed separately. Underpayments are made good on the next off-cycle run, so Payroll needs the
employee named; overpayments are recovered from the bureau under the service agreement and are
raised as a credit, never netted against the employee.
