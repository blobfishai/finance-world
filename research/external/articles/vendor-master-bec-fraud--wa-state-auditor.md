# Protect Your Vendor Master File from Fraudsters

- **URL:** https://sao.wa.gov/the-audit-connection-blog/protect-your-vendor-master-file-fraudsters
- **Publisher:** Office of the Washington State Auditor (SAO) — The Audit Connection blog
- **Retrieved:** 2026-08-10
- **Topic:** vendor-master-bec-fraud

## Summary

A state-audit-office control advisory aimed at government entities, written from actual reported loss experience. It is short but states the core vendor-master control rules in unambiguous, auditable language.

### Reported loss experience

- **Since 2021, governments have reported $6.8 million in vendor-related payment losses to SAO**, although some funds were later recovered.
- SAO cites the industry benchmark that **an organization's duplicate payments can range from 0.8% to 2% of total payments**.

### The bank-detail change rule

The advisory's central instruction: **independently verify any request to change vendor information directly with the vendor, by phone, using contact information that is known, reliable, and already on file.** The decisive qualifier is *already on file* — contact details supplied in or alongside the change request are not acceptable verification sources. Note that this source does not further specify a callback script, a required number of attempts, or a documentation template; it states the principle only.

### Segregation of duties

- **Accounts payable clerks should not be able to add new vendors or change vendor information in the vendor master file.** The person who maintains the vendor record must not be the person who processes the payment.
- SAO points to page **22** of its *Segregation of Duties Guide* for the detailed role matrix, and notes that **Appendix A** of that guide contains alternatives for small governments that lack the staffing to segregate duties fully (i.e., compensating controls such as independent review of vendor-master change reports).

### New vendor vetting steps

Referencing page **5** of SAO's *Accounts Payable Guide*, the recommended onboarding due-diligence set is:

1. Obtain a **W-9** form from the vendor.
2. Validate the information through the **IRS Taxpayer Identification Number (TIN) Matching** service.
3. Check **state licensure / registration** status.
4. Run **credit reports**.
5. Conduct **internet research** on the entity.

### Vendor master file hygiene cadence

**At least once per year**, evaluate the cleanliness of the vendor master file, including:

- **Removing duplicate vendor records**, and
- **Inactivating vendors that are not being used.**

This is the source's only stated cadence: an annual minimum. It does not define a dormancy day-count (e.g., 12 or 24 months of no payment activity) — that threshold has to come from another source.

### Why the file is the attack surface

The implicit model in the advisory is that the vendor master file is the single point where a fraudster's bank account can be inserted into an otherwise legitimate payment stream. Once a fraudulent account number sits on a real vendor record, every downstream control (three-way match, invoice approval, payment run approval) can pass while the money still leaves for the wrong destination. That is why the advisory concentrates on (a) who may touch the record, (b) how a change is independently verified, and (c) how stale and duplicate records are purged.

## Eval-relevant hooks

- **Hard decision rule (highly checkable):** verification of a vendor bank-detail change must use a phone number **already on file**, not one contained in the change request or email signature. An agent that calls the number in the email fails.
- **Segregation-of-duties assertion:** an AP clerk with the ability to both add/modify vendor records and process payments is a control failure — usable as a pass/fail on a role-permission review task.
- **Onboarding checklist task:** W-9 → IRS TIN Matching → state licensure/registration check → credit report → internet research, as a five-item completeness check on a new-vendor packet.
- **Cadence assertion:** vendor master file cleanliness review is required **at least annually**, covering duplicate removal and inactivation of unused vendors.
- **Quantitative hook:** duplicate payments run **0.8%–2% of total payments**; a task can ask an agent to size expected duplicate-payment exposure from a total disbursement figure.
- **Small-entity compensating-control hook:** where duties cannot be segregated, the correct answer is documented compensating controls (per Appendix A of the SoD guide), not waiving the control.
