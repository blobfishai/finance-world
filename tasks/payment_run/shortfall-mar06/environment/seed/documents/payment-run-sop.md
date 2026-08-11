# SOP-AP-04 — Weekly vendor payment run

> Contoso Entertainment System USA · Treasury · effective 2026-01-01 · v3.1
> SIMULATION ONLY

Runs are built every Friday and funded from the operating account (USMF-OPER). Runs are
scoped to one vendor group at a time; an unscoped proposal is not reviewable and will be
rejected by the system.

## 1. Exclusions — applied before any funding decision

These are not funding decisions and are never deferred to a later run for cash reasons.
They are excluded outright, with the reason recorded on the line:

1. **Vendor on credit hold.** No obligation of a vendor whose master record carries a hold
   is paid, regardless of age or discount. Reason code `vendor_on_hold`.
2. **Disputed invoices.** An invoice under active dispute is excluded until the dispute is
   resolved and the resolution is documented. Disputes are raised by the business and are
   **not** flagged in the ERP — check the AP mailbox for the current week before building
   the run. Reason code `disputed`.

## 2. Funding priority — applied to everything that survives §1

Pay in this order, until available cash is exhausted:

1. **Discount capture first.** Any invoice whose cash-discount window closes *before the
   next scheduled run* is paid this week. Letting a discount lapse is a permanent loss;
   deferring a net-terms invoice by one week is not.
2. **Then past-due invoices**, oldest due date first.
3. **Then everything else** by due date.

## 3. What "done" means

Every eligible obligation is accounted for — each one is either paid or carries a rejection
reason. A short run is committed by **naming what goes unpaid and why**, never by quietly
dropping obligations from the proposal. Obligations deferred purely because cash ran out
take reason code `insufficient_cash` and are first in line next week.

The paid total may not exceed available cash. Overdrafts on USMF-OPER are not authorized.

## 4. Calendar

Runs are executed Fridays. The run following 2026-03-06 is **2026-03-13**.
