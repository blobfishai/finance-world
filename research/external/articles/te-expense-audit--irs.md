# Publication 463 — Travel, Gift, and Car Expenses

- **URL:** https://www.irs.gov/publications/p463
- **Publisher:** Internal Revenue Service (IRS)
- **Retrieved:** 2026-08-10
- **Topic:** te-expense-audit

## Summary

Publication 463 is the IRS's taxpayer-facing statement of the substantiation and reimbursement rules that a corporate T&E policy has to mirror. It supplies the day counts, per-mile and per-day rates, and the record elements an expense audit tests against.

### Accountable plan requirements and the "reasonable period of time" safe harbors

The publication states the three accountable-plan elements: a **bona fide business purpose** for the travel (business connection under IRC §162(a)), **adequate accounting** to the employer, and **return of excess reimbursements** within a reasonable period of time.

The safe-harbor day counts given for "reasonable period":

- **60 days** to substantiate an expense after it is paid or incurred
- **120 days** to return any excess amount
- **30 days'** notice requirement for repayment
- A **fixed-date method** may be keyed to calendar month-end or pay-period-end

### Standard mileage rate

**70 cents per mile** for business use of a personal vehicle (2025 rate as presented).

### Per diem / standard meal allowance (M&IE)

Rates are published by location on GSA.gov and are organized by **federal fiscal year, October 1 – September 30**. Special transportation-industry rates are stated as **$80 per day** for travel within the continental U.S. and **$86 per day** for travel outside the continental U.S.

**First and last day of travel:** the taxpayer may claim **three-fourths (3/4) of the standard meal allowance**, or use any method consistently applied and in accordance with reasonable business practice. This is the 75% partial-day rule stated in fractional form.

### 50% meal limit

Generally only **50%** of the unreimbursed cost of business meals is deductible. Named exceptions to the 50% limit include amounts under an accountable plan, employee reimbursements, recreational expenses for employees, and meals made available as advertising/promotion.

### Business gifts

**$25 per person per year** is the deduction limit for business gifts. **Incidental costs** — wrapping, delivery — do not count toward the $25 limit.

### Record elements

Documentation must establish, for travel, meals and gifts: (1) **time**, (2) **place** of the business destination, (3) **business purpose**, (4) **amount**, and (5) **business relationship** (for gifts and entertainment). The publication requires **timely kept records** — contemporaneous, not reconstructed after the fact — and states that a **canceled check alone is insufficient**.

### Lavish or extravagant

Meal expenses are **not** disallowed merely because they exceed a fixed dollar amount or because the meal takes place at a deluxe restaurant, hotel, or resort. This matters for policy design: a corporate cap is a policy control, not a tax rule.

### Explicit limits of what this retrieval surfaced

Two items that practitioners commonly attribute to Pub. 463 did **not** appear in the text returned by this fetch and should not be sourced to this file:

- The **$75 de minimis documentary-evidence threshold** did not appear in the retrieved recordkeeping text. What the retrieved text does say is that "adequate records" means an account book, diary, log, statement of expense, trip sheets, or receipts, and that **lodging must be substantiated with an actual receipt** with no dollar-amount exception noted.
- The **wage/Form W-2 and withholding consequences** of unsubstantiated amounts were not detailed here; the publication emphasizes that adequate records are needed to prove expenses on examination. (For the codified W-2/withholding treatment see the companion file on 26 CFR §1.62-2.)
- The **high-low substantiation method** is referenced by name only, without operational specifics in the retrieved text.

## Eval-relevant hooks

- Day-count decision rule: an expense report submitted more than **60 days** after the expense, or an unreturned advance older than **120 days**, falls outside the accountable-plan safe harbor — directly checkable against submission dates in an expense dataset.
- Mileage recomputation task: verify a reimbursement at **$0.70/mile** and flag over- or under-payment.
- Partial-day proration task: apply **3/4 of the standard meal allowance** on the first and last travel days and detect full-day claims on travel days.
- Transportation-industry rate check: **$80/day** CONUS vs **$86/day** OCONUS.
- Gift-limit test: aggregate gifts per recipient per year against the **$25** cap, excluding incidental wrapping/delivery costs.
- Record-completeness audit: score an expense line against the five required elements (time, place, business purpose, amount, business relationship) and reject on any missing element; a canceled check alone is not sufficient support.
- Policy-vs-tax distinction: an expensive restaurant is not automatically "lavish or extravagant" under the publication — an agent that disallows on price alone is applying policy, not the tax rule, and should say so.
