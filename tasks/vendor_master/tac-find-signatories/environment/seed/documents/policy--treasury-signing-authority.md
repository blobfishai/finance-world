# SOP-TR-02 — Signing authority and bank mandate maintenance

> Contoso Entertainment System USA · Treasury · effective 2026-01-01 · v4.1
> SIMULATION ONLY

Applies to every bank mandate held in the name of the USMF entity, including the operating
account (USMF-OPER) and the payroll account (USMF-PAYR).

## 1. Authority bands

A mandate row appoints one named individual, in one capacity, at one band. The band sets the
ceiling; the row states the individual's own single-signature limit, which may be lower.

| Band | May release, single signature, up to |
|---|---|
| A | the limit stated on the row, to a maximum of USD 1,000,000 |
| B | USD 250,000 |
| C | USD 50,000 |

A payment above a signatory's single-signature limit is not theirs to release. It is escalated
to a signatory whose limit covers it — in practice, to Band A.

## 2. What makes an authority valid today

An authority is valid on a given day only if **all** of the following hold on that day. Any one
of them failing voids the authority immediately; there is no grace period and no partial
authority.

1. **The individual is an active employee.** Signing authority is a property of employment.
   It lapses on the individual's last working day, automatically, whether or not anyone tells
   the bank and whether or not the offboarding checklist has been closed. The current HR
   personnel extract is the record of employment status; the mandate register is not.
2. **The delegation is within its dates.** The row must have taken effect on or before today.
   Where the row states an expiry date, the authority is void from the day after that date.
   A time-limited delegation is never extended by silence, by the delegate remaining employed,
   or by the register still showing the row — an extension requires a fresh written delegation
   from the CFO.
3. **The row is on the current register** for the account being certified.

## 3. The register status column is not evidence

The `Register status` column is maintained by hand by Treasury Operations and is updated when
the change is noticed, not when it happens. It routinely shows `Active` against authorities
that have already fallen away under section 2. Never certify a mandate, revoke access, or
release a payment on the strength of that column. Test each row against section 2.

## 4. One individual, one signature

An individual may hold more than one mandate row — a substantive role and a cover arrangement,
or two capacities in different processes. **Two rows held by the same person are one
signatory.** When certifying to the bank, count individuals, not rows: the bank holds one
specimen signature per person. For the same reason, two rows in one person's name can never
satisfy a requirement for two signatures.

## 5. Removal

Every row failing section 2 is struck from the mandate at the next refresh, the bank is
notified in the certification, and the individual's payment-release access in the ERP is
revoked on the same day. Rows are struck, never left in place "pending tidy-up".

## 6. Certification

The refresh certificate states the individuals authorised to sign, each one's single-signature
limit, and the rows being struck with the reason. Treasury Management signs the certificate;
the administrator who maintains the register does not certify it.
