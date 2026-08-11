# Frequently Asked Questions, Per Diem (GSA)

- **URL:** https://www.gsa.gov/travel/plan-a-trip/per-diem-rates/faqs
- **Publisher:** U.S. General Services Administration (GSA)
- **Retrieved:** 2026-08-10
- **Topic:** te-expense-audit

## Summary

GSA's per diem FAQ supplies the rules that determine *which* rate applies and *when* a partial rate applies — the locality-determination rule, the 75% partial-day rule, the one-day-travel threshold, and how the rates themselves are set and revised. It complements the M&IE Breakdown table, which supplies the amounts.

### First and last day of travel — 75%

On the first and last travel day, federal employees are eligible for only **75 percent of the total M&IE rate** for their temporary duty travel location. The rule is stated without an hour-of-departure qualifier for those days.

### One-day travel — the 12-hour threshold

For one-day travel away from the official station, the traveler is entitled to **75% of the prescribed meals and incidental expenses if the travel is longer than 12 hours**. This is the FAQ's explicit duration threshold: the 12-hour mark is what converts a same-day trip into a per-diem-eligible trip at the reduced 75% rate.

### Which locality's rate applies

Reimbursement is based on **the location of the work activities, not the location of the accommodations** — unless lodging is not available at the work activity location, in which case the agency may authorize the rate for the location where lodging is obtained. This is the operative tie-breaker when a traveler works in a high-rate city and sleeps in a cheaper suburb: the work location governs by default, and using the lodging location requires an availability-based authorization.

### What "incidental expenses" covers

The FAQ defines incidental expenses as **fees and tips given to porters, baggage carriers, hotel staff, and staff on ships**. That is the whole definition — a narrow list, useful for rejecting items miscoded as "incidentals."

### How rates are set and challenged

Rates are set based on **contractor-provided average daily rate (ADR) data of local lodging properties**. **Non-standard areas receive annual reviews**, and **special reviews occur if requested by December 31**. That December 31 deadline is the published cut-off for an agency to get a locality rate re-examined outside the normal annual cycle.

### What this page does not state

The retrieved FAQ does **not** publish the current fiscal-year lodging or M&IE dollar amounts (it directs users to the per diem lookup tool, referencing rate coverage between 10/1/2023 and 09/30/2026), does **not** itemize the breakfast/lunch/dinner/incidentals split (it points to the M&IE breakdown page for the first-and-last-day table), does **not** address a 50-mile rule, and does **not** contain provided-meal deduction language. Those must be sourced elsewhere; the M&IE Breakdown page carries the amounts and the provided-meal exceptions.

## Eval-relevant hooks

- Eligibility gate: one-day travel qualifies for M&IE only if it exceeds **12 hours**, and then only at **75%** — a two-part rule an agent can be scored on precisely.
- Locality-selection task: given a work city and a different lodging city, apply the work-location default and require an availability-based justification before using the lodging-location rate. A strong source of "wrong rate applied" exceptions.
- Partial-day rule: first and last travel days pay **75%** of the destination's M&IE, independent of departure or arrival hour — so an agent should not prorate further by hours on those days.
- Coding check: an expense claimed as "incidentals" that is not a tip to a porter, baggage carrier, hotel staff or ship staff falls outside the published definition and should be reclassified.
- Rate-governance task: a request for a special (off-cycle) rate review must be made **by December 31**; non-standard areas are otherwise reviewed annually. Rates trace to contractor-supplied **ADR** lodging data.
- Negative-knowledge hook: this page does not establish a 50-mile rule or provided-meal deductions — an agent citing the FAQ for either is over-claiming its authority.
