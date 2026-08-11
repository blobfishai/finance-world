# What Is Positive Pay? A Finance Leader's Guide to Check and ACH Fraud Defense

- **URL:** https://www.corpay.com/resources/blog/positive-pay
- **Publisher:** Corpay
- **Retrieved:** 2026-08-10
- **Topic:** payment-runs-early-pay-discount

## Summary

Positive pay is the control that sits immediately downstream of the payment run: once a payment batch is approved and issued, the issue file is what the bank matches against. This source gives the workflow, the matching fields, the product variants, and — most usefully for evals — the **decision cutoff windows**.

### Four-step workflow (published)

1. **Issue file submission** — treasury transmits the issued-checks file to the bank, usually **nightly or in batches throughout the day**.
2. **Presentment** — a check or ACH debit is presented for payment.
3. **Match** — the bank compares the presented item against the issue file.
4. **Exception or clear** — matched items clear normally; unmatched items **hold as exceptions**, and the bank notifies the business for a **pay / no-pay decision before the cutoff**.

### Matching fields

Required issue-file fields: **account number, check number, issue date, amount** — plus **payee name** for payee positive pay. Standard check positive pay matches **check number and amount only**; payee positive pay adds **payee-name verification**.

### Product variants

| Variant | Coverage | Key difference |
|---|---|---|
| **Check positive pay** | Counterfeit / altered checks | Matches number + amount only |
| **Payee positive pay** | Adds altered-payee fraud | Includes payee-name matching |
| **Reverse positive pay** | Similar coverage | **Bank sends the list; the business reviews daily** |
| **ACH positive pay** | Inbound ACH debit fraud | Matches debits against an authorized list |
| **ACH debit block** | Blocks all ACH debits | Flat block on the account |
| **ACH debit filters** | Allowlist-based | Only specified company IDs permitted |

The check/payee distinction is the operational one: a check with a valid number and amount but a **substituted payee name clears under standard positive pay** and is caught only by payee positive pay.

### Exception decision window (exact)

Decisions must be made before the bank's cutoff, **commonly 11 a.m. or 2 p.m. local time depending on the bank**. Default behaviour on a missed exception varies by bank: **some default to pay, others default to return** — so the default setting is itself a control decision that must be documented.

### Fraud statistics as published (2024–2025)

- **79%** of organizations experienced attempted or actual payments fraud in 2024.
- **63%** experienced **check fraud** specifically.
- Only **22%** of organizations recovered **more than 75%** of funds lost to payments fraud in 2024.
- **91%** of organizations still use checks; **34%** report that **more than a quarter** of their payments are still by check.

## Eval-relevant hooks

- Cutoff-clock task: an exception notified at 9:30 a.m. against an 11 a.m. cutoff leaves 90 minutes; assert escalation when the reviewer is unavailable, and identify the bank's default (pay vs. return) as the outcome if the window lapses.
- Variant-selection task: given a fraud scenario where the payee name was altered but check number and amount are genuine, the correct control is **payee positive pay** — standard check positive pay would clear it.
- Issue-file completeness check: validate a file for account number, check number, issue date, amount (and payee name if payee positive pay); a manual check cut outside the payment run and never added to the issue file will present as an exception.
- Control-configuration decision: choose between **ACH debit block** and **ACH debit filters** for an account that must accept debits from two known trading partners only.
- Reverse positive pay contrast: the review burden shifts to the business daily, with no issue file transmitted — a good question about which party bears detection responsibility.
- Recovery-expectation reasoning: with only 22% recovering more than 75% of losses, prevention controls dominate recovery efforts — usable as a justification-quality assertion.
