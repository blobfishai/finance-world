# SOP-AP-09 — Withholding on vendor payments

> Contoso Entertainment System USA · Accounts Payable / Tax · effective 2026-01-01 · v1.3
> SIMULATION ONLY

Withholding is applied **at payment**, by the payment run, and is remitted to the authority
separately. The vendor is paid net; the withheld amount is still a discharge of the debt.

## 1. What decides the rate

Two facts, in this order:

1. the vendor's **tax category** on `VendorTaxProfile`; and
2. whether a **valid, unexpired certificate** is on file as at the **pay date**.

A valid certificate buys the declared treatment. For a treaty claim that means a **reduced**
rate — not exemption. Without a valid certificate the punitive default applies: the
non-resident rate for a foreign payee, backup withholding for a domestic one.

**A certificate that has lapsed is not a certificate.** The record still shows one on file,
and the vendor will often still claim the treaty rate in correspondence. Neither changes the
position: check the expiry against the pay date, every run.

## 2. Rates

Read them from the `WithholdingTax` entity — rate, threshold and statutory reference are
maintained there. Do not hard-code rates into a payment proposal.

## 3. Vendor correspondence

A vendor asserting a treaty rate in an email has not thereby filed a certificate.
Documentation reaches us on the form or it has not reached us.
