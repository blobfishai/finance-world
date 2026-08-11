# Ensuring Vendor Data Accuracy and Completeness: Governance, Hygiene and Controls

- **URL:** https://www.disbursementcontrols.com/vendor-data-accuracy/
- **Publisher:** DisbursementControls.com
- **Retrieved:** 2026-08-10
- **Topic:** vendor-master-bec-fraud

## Summary

A practitioner governance guide for the vendor master file. Where the FBI and state-auditor sources give the fraud rule, this one gives the surrounding data-governance machinery: field standards, re-validation currency periods, duplicate detection method, dormancy handling, audit-log requirements, and a measurable metric set.

### Completeness standards

Required fields are defined **conditionally by vendor type, payment method, or risk tier** rather than as one universal list. Stated examples: **ACH payments require different fields than check payments**, and **foreign vendors require W-8 documentation where domestic vendors require W-9**. The source does not publish an explicit field list.

### Onboarding validation steps

- **TIN matching** validation
- **Address verification**
- **Bank account verification checks**
- **Format consistency enforcement**

Tracked failure modes at onboarding are named as: **TIN mismatches, unverifiable addresses, and bank account rejections**.

### Data currency and re-validation cadence

The governing concept is a **"currency period"** — how long a validated data element stays valid before re-validation is required. Stated illustrations:

- **W-9 data collected five years ago** may no longer reflect the vendor's current legal name.
- **Banking information validated at onboarding three years ago is not indefinitely reliable.**

Cadence rules:

- Deduplication analyses should be performed **at least annually** (stated minimum).
- Re-validation should be **risk-tiered**: high-value, high-frequency vendors warrant more frequent review than low-activity relationships.

### Duplicate detection

- **Preventive:** system-enforced duplicate checks that flag potential matches when a new **vendor name, TIN, or banking record** is submitted.
- **Detective:** periodic deduplication analysis run against the **full vendor master**, using identity-resolution tools applying **probabilistic matching**.
- Method note: **exact-match rules miss near-duplicates**; **fuzzy matching algorithms** catch a substantially higher proportion. Matching fields named: **name, TIN, banking data, address**.

### Dormant vendor deactivation

- **Trigger:** vendors that have **not received a payment within a defined period — commonly 12 to 24 months** — should be reviewed for deactivation.
- **Process:** deactivation is **not automatic** but **systematic, documented, and subject to reactivation controls that require the same validation rigor as initial onboarding.** Reactivation is therefore a re-onboarding event, not a status toggle.

### Roles and segregation of duties

- A named **data steward** carries explicit responsibility for the **accuracy, completeness and currency** of the vendor master file. Duties: enforcing data-quality standards at onboarding and during record maintenance; reviewing and approving exceptions; managing the periodic re-validation schedule; monitoring data-quality metrics.
- **Segregation of duties:** prevent the same individual from **both maintaining vendor records and approving payments**.

### Audit trail requirement

Every change to a vendor record — **who made it, when, what changed, and who approved it** — must be captured in a **system-maintained audit log that cannot be altered by the user who made the change.** Immutability with respect to the maker is the stated bar.

### Metric set

The source names six measurable vendor-master data-quality metrics:

1. Proportion of active records with all required fields populated
2. Proportion with validated banking information **within the defined currency period**
3. Volume and rate of duplicate records
4. Records with no payment activity **within the defined inactivity threshold**
5. Validation failure rate at onboarding
6. **Volume of IRS CP-2100 notices received** (a downstream indicator of TIN data quality)

### Explicit gaps

This source does **not** provide: callback/out-of-band verification procedure for banking changes, two-person approval workflow mechanics, OFAC/sanctions screening cadence, a named audit-finding taxonomy, or numeric error-rate thresholds. Pair it with the IC3 and state-auditor sources for those.

## Eval-relevant hooks

- **Dormancy rule:** no payment activity for **12–24 months** triggers deactivation review; **reactivation must repeat full onboarding validation** — a strong pass/fail on a "reactivate this old vendor" task.
- **Duplicate-detection decision rule:** exact-match alone is insufficient; the correct answer specifies **fuzzy/probabilistic matching across name, TIN, banking data, and address**, run against the full master **at least annually**.
- **Audit-log assertion:** the log must record who/when/what/approver and must **not be alterable by the user who made the change** — checkable against a system-design answer.
- **Conditional-field logic:** required fields vary by payment method (ACH vs check) and by domestic (W-9) vs foreign (W-8) status — a good scenario for grading a vendor-setup completeness check.
- **Metric task:** build a vendor-master data-quality scorecard from the six named metrics, including **IRS CP-2100 notice volume** as the TIN-quality proxy.
- **Currency-period task:** given a vendor record whose banking detail was last validated 3 years ago and W-9 5 years ago, decide whether the record may be paid — the source's framing says stale validation is not indefinitely reliable.
