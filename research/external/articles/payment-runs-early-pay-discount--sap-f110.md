# Automatic Payment Program Run F110: SAP Tutorial

- **URL:** https://www.guru99.com/all-about-automatic-payment-run.html
- **Publisher:** Guru99
- **Retrieved:** 2026-08-10
- **Topic:** payment-runs-early-pay-discount

## Summary

The step sequence of the SAP automatic payment program — the reference implementation of "payment proposal → review → release" that most AP payment-run controls are modelled on.

### Run identity

Transaction code **F110**. Every payment run is uniquely identified by **two fields**: **Run date** and **Identification**. (This pairing is what makes a run re-runnable and auditable; the same run date can carry multiple identifications for different company codes or payment methods.)

### Parameters tab — the five questions

The parameters are framed as questions, each mapping to a named field:

- **What is to be paid** → **Docs. Entered Up to** (document entry cutoff date)
- **What payment methods will be used** → **Payment Methods**
- **When will the payments be made** → **Posting Date**
- **Which company codes will be considered** → **Company Codes**
- **How are they going to be paid** → **Payment Method Sequence** (determines priority — the order in which methods are attempted)

### Execution sequence (published order)

1. **Save Parameters** after entering all settings.
2. Press the **Proposal** button in the application toolbar.
3. Select **Start Immediately** in the dialog and continue.
4. **Proposal generation** creates the payment list from the parameters.
5. Review the **Proposal Log** for errors (Proposal Log button).
6. **Edit Proposal** (optional) to **block specific payments**.
7. Press the **Payment Run** button to release payments.
8. Select **Start Immediately** and continue.
9. Check the **Status** tab to monitor completion.

The control-relevant property: the **proposal is a reviewable, editable intermediate artifact**. Nothing posts until the payment run step, so the proposal is the natural approval gate — items can be blocked before any payment document or payment file is created.

### Outputs

The proposal shows the vendor list intended to receive payments; the payment run **posts the actual payment documents** and can generate **payment media or EDI output**.

### Explicit scope limits of this source

Noted so nothing is over-claimed: this article does **not** detail the **Free Selection**, **Additional Log**, or **Printout/data medium** tabs, does not give exception-handling mechanisms beyond reviewing the proposal log, and publishes **no numeric thresholds, approval limits, or cutoff times**.

## Eval-relevant hooks

- Sequence-integrity task: assert that Save Parameters precedes Proposal, and that Payment Run only follows proposal review — an agent that jumps straight to the payment run has skipped the approval gate.
- Gate-identification question: at which step can a disputed invoice still be excluded without reversing anything? Answer: **Edit Proposal**, before the payment run posts documents.
- Parameter-mapping task: map a business instruction ("pay all invoices entered through the 25th, from company codes 1000 and 2000, by ACH first then check, posting on the 28th") onto **Docs. Entered Up to**, **Company Codes**, **Payment Method Sequence**, and **Posting Date**.
- Run-identity check: two runs on the same date require distinct **Identification** values; a duplicate-payment scenario can hinge on this.
- Discount interaction: because the proposal is generated from due-date and terms data, a discount-eligible invoice omitted from the "Docs. Entered Up to" window will miss its discount deadline — a linkage task combining payment-run parameters with early-pay discount economics.
- Negative-knowledge check: this source specifies no approval thresholds or cutoff times; those must come from company policy, not from F110 defaults.
