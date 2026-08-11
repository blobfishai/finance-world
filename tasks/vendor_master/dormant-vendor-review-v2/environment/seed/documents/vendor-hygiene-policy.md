# SOP-AP-11 — Vendor master hygiene review

> Contoso Entertainment System USA · Accounts Payable Controls · effective 2026-01-01 · v2.1
> SIMULATION ONLY

Dormant vendor records are a standing fraud exposure: the account still carries banking
details, still passes a payment run's validity checks, and nobody is watching it. Compromise
of a dormant record is a documented business-email-compromise pattern, because the legitimate
counterparty is not in contact to notice.

## 1. Definition of dormant

A vendor is **dormant** when it satisfies all of:

1. it has **at least one posted transaction** in its history — a vendor that has never
   transacted is *not* dormant, it is **unused**, and is handled under §3; and
2. its **most recent** posted transaction is more than **12 months** before the review date; and
3. its master record is still **active** — a vendor already on hold has been actioned and is
   out of scope for this review.

Measure from the most recent transaction of any type, not from the most recent invoice: a
payment or credit note is contact with the counterparty.

## 2. Disposition of a dormant vendor

Flag for deactivation and bank-detail purge. Reactivation requires the full onboarding
control, including independent callback verification of banking details on the number of
record — never a number supplied in the reactivation request.

## 3. Unused vendors

A vendor with no transaction history was onboarded and never used. It is a **different**
finding with a different owner (Procurement, not AP Controls) and is reported separately.
Do not report it as dormant — the counts feed different control metrics and conflating them
has caused the quarterly numbers to be restated before.

## 4. Cadence

Reviewed quarterly against the vendor group under review. The review date is the world's
current date.
