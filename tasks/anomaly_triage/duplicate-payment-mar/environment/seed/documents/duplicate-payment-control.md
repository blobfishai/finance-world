# SOP-AP-07 — Duplicate disbursement control

> Contoso Entertainment System USA · Accounts Payable · effective 2026-01-01 · v1.2
> SIMULATION ONLY

Duplicate payments are the most common avoidable loss in disbursements. Recovery after the
fact depends on the vendor's goodwill, so the control is preventive: **no payment run is
committed until its lines have been screened against already-settled history.**

## 1. What counts as a suspected duplicate

An open obligation is a suspected duplicate when it matches an **already-settled** obligation
from the same vendor on **both**:

- the same purchase-order reference, **and**
- the same gross amount.

Invoice numbers are not a reliable key. Vendors re-issue paper copies under a different
number, and AP re-keys them; "OSINV-5521" and "5521-OPS" are the same debt.

## 2. What does NOT count

Matching on amount alone is not a duplicate finding. Vendors legitimately bill the same
amount twice — recurring services, split deliveries, standard rate cards. **A different PO
reference means a different obligation, however similar the amount.** Rejecting a valid
invoice damages the vendor relationship and is treated as a control failure in its own right.

Corroborate before rejecting: the vendor's own statement in the AP mailbox shows what they
believe they are owed.

## 3. Disposition

A confirmed duplicate is rejected on the run with reason code `duplicate` and referred to the
AP supervisor for credit. It is **not** deferred — deferring leaves it to be paid next week.

## 4. Scope

This screen runs on every payment proposal, whether or not cash is constrained. A fully
fundable run is not a safe run.
