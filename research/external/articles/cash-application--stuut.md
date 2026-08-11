# Cash Application Exception Handling: Short Pays and Deductions

- **URL:** https://www.stuut.ai/blog/cash-application-exception-handling-short-pays-and-deductions
- **Publisher:** Stuut
- **Retrieved:** 2026-08-10
- **Topic:** cash-application

## Summary

The only source found that publishes both a **named deduction reason-code list** and **routing rules mapping each exception type to a resolving function** — the two pieces most useful for modelling an exception queue with real ownership.

### Exception taxonomy: two primary categories

- **Short pays** — defined as any partial payment of an invoice. Named causes: clerical errors, cash flow constraints, and missing purchase orders.
- **Deductions** — defined as an intentional reduction where the customer pays less than the full invoice amount.

The distinction is intent: a short pay may be accidental or circumstantial; a deduction is deliberate and carries a claimed reason.

### Seven standardized deduction reason codes

1. Damaged goods
2. Short shipment
3. Pricing error
4. Early payment discount
5. Return chargeback
6. Promotional allowance
7. Freight dispute

### Routing and ownership rules

Resolution ownership is assigned by reason category, not by dollar value:

- **Pricing errors** → sales representative
- **Damaged goods / short shipments** → operations or shipping team
- **Unauthorized discounts** → AR analyst (who requests repayment directly from the customer)
- **General triage and evidence gathering** → AR analysts

This produces a two-tier model: AR analysts own triage and evidence collection for everything, then hand the substantive resolution to the function that owns the underlying commercial fact (sales owns price, operations owns delivery).

### Write-off threshold

Balances below the materiality threshold should be written off using a **"de minimis" reason code**, and the source instructs teams to **document the write-off threshold in their collections policy**. Critically, **no dollar or percentage figure is published** — the threshold is treated as a company-specific policy parameter. Any specific number attributed to this source would be fabricated.

### Aging guidance

The single explicit aging rule published: **exceptions approaching 60+ days need immediate action.** No other SLA or resolution timeframe is given.

### Match rate

**95%+ automated cash application match rate** is cited for AI-driven automation across the full payment portfolio.

### Four-step resolution workflow

1. Find unapplied cash
2. Prioritize by value, aging, and customer tier
3. Uncover short-pay reasons
4. Reconcile deductions

Note that prioritization (step 2) is explicitly three-dimensional — value **and** aging **and** customer tier — rather than a simple aging queue.

### Gaps

No exception-rate percentages (what share of payments become exceptions), no on-account cash handling specifics, and no numeric write-off threshold.

## Eval-relevant hooks

- **Reason-code classification:** given a short-pay narrative ("customer deducted $1,200 citing a promotional allowance from Q2"), the agent must select the correct code from the seven published options. Clean multiple-choice assertion with a fixed vocabulary.
- **Routing assertion:** a deduction coded "pricing error" routed to the operations team is a routing violation — it belongs with the sales representative. Damaged goods routed to sales is the mirror-image error.
- **Intent distinction:** classifying an accidental partial payment as a deduction (rather than a short pay) is a taxonomy error, testable with ambiguous cases.
- **60-day aging trigger:** an exception at 58 days is approaching the published immediate-action threshold; one at 65 days has breached it. Directly checkable against a queue snapshot.
- **Threshold-absence discipline:** the write-off threshold is explicitly a policy parameter with no published value, so the correct agent behavior is to look it up in the company's collections policy or request it — not to assume a figure. Strong hallucination test.
- **Three-dimensional prioritization:** asked to work an exception queue, an agent sorting only by aging has ignored value and customer tier, both named in step 2 of the published workflow.
