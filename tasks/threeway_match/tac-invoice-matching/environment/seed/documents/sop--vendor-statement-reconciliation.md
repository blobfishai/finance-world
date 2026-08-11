# SOP-AP-11 — Vendor statement reconciliation

**Owner:** Accounts Payable · **Applies to:** every statement of account a vendor sends us,
before any balance on it is agreed, paid or accrued at period end. SIMULATION ONLY — all
vendors, invoices and figures referenced by this procedure are synthetic.

## 1. The two sources

| What | Whose record it is | Where |
|---|---|---|
| What the vendor says it billed us | the vendor | the statement of account they sent, on the finance shared drive |
| What we actually disbursed | us | the payment register extract for that vendor and period, on the finance shared drive |

Neither file's own footer total is evidence. Each is prepared by the party that owns the file
and each is complete only in its own terms — the statement cannot see a payment we made
against an invoice it did not list, and the register cannot see an invoice we never paid.
**Agreeing two footers is not a reconciliation.**

## 2. Remittance reference conventions

The disbursements team keys one reference per payment line, in one of three forms:

| Form | Example | Means |
|---|---|---|
| a single invoice number | `HF-2201` | this payment settles that one invoice |
| invoice numbers separated by commas | `HF-2205,HF-2206` | one remittance covering every invoice named; the remittance is applied to each named invoice for that invoice's full statement amount |
| an invoice number followed by `(partial n of m)` | `HF-2210 (partial 1 of 2)` | one invoice settled in instalments across separate payment runs |

Instalment and combined references are **payment structure, not discrepancy**. A run that was
split over two Fridays, or a remittance that cleared four invoices at once, is a normal
disbursement and is not an exception.

## 3. Reconcile at invoice level

Reconciliation is performed **per invoice on the statement**, never per payment line:

    applied to invoice = sum of every payment, or part of a payment, whose reference names it
    variance on invoice = applied to invoice - statement amount of that invoice

Aggregate the instalments of a split invoice, and attribute each invoice named in a combined
remittance, **before** comparing anything. Comparing a payment line to the first invoice its
reference happens to name manufactures exceptions against instalments and combined remittances
that are perfectly in order, and — because it never looks at an invoice that no payment
mentions — it cannot see an invoice we simply never paid, nor an invoice paid twice in full.
Both of those are the failures this procedure exists to catch.

## 4. Scope

A remittance reference naming an invoice that is **not on the statement** is outside this
statement's scope: it belongs to an earlier statement, to a credit the vendor has not carried
forward, or to a keying error. Report the payment separately so the vendor can identify it.
Do **not** count it in the amount applied to this statement, and do **not** net it against the
statement variance — doing so silently reduces a balance we owe by a payment that was never
against it.

## 5. What to report

1. **Exception invoices** — every invoice on the statement whose applied amount differs from
   its statement amount, in either direction. An invoice with no payment against it at all is
   an exception; so is an invoice whose applied amount exceeds it.
2. **Gross overpayment** and **gross underpayment**, stated separately as positive amounts.
   Netting them reports neither: an overpayment is cash to recover from the vendor and an
   underpayment is a balance we owe, and the two are actioned by different people.
3. **Net position** — the statement total less the amount applied to invoices on the
   statement. Positive means we are behind; negative means we are ahead.
4. Any payment whose reference falls outside the statement's scope, per section 4.

Amounts are stated in USD to the cent. Round only at the point of reporting.
