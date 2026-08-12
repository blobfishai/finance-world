# Parity ledger — what the source corpora ship vs what runs here

> Opened 2026-08-11 in response to a fair challenge: *why didn't we download all the eval and
> workflow repos and build the world by reaching parity first?*
>
> The honest answer is that we did **mechanism extraction**, not **corpus replication**. We
> mined each repo for its ideas — unsat demand, objective non-collapse, scale-as-a-field,
> τ-bench state hashing, delegation-of-authority gating — and authored our own tasks around
> them. That produces a differentiated world and it is **not** parity. Goal 2 says *tasks*.
>
> This file makes the gap a number instead of a feeling, and it is regenerated, not asserted.

## The number

**Generated, not asserted** — `python3 ingest/run.py` reads the corpora, binds each item to
the live world, and prints this. Re-run it; do not edit it.

```
world capability: 47 tables · 708 named parties · 7 servers · 68 filing companies

microsoft/FinanceBenchmark — 251 items
   class      : verbatim_gt 100 · not_agentic 98 · recomputable 28 · judgement_port 25
   addressable: 153      binding: bound 152 · absent_entity 1       ported: 97  (63%)
   instances  : 1026 generated over 27 patterns (breadth; excluded from the rate)
TheAgentCompany — 12 items
   class      : judgement_port 12
   addressable: 12       binding: bound 12                          ported: 9   (75%)
   variants   : 4 escalated from ported tasks (depth; excluded from the rate)
agentic-labs/erp-bench — 300 items
   class      : needs_surface 300
   addressable: 0                                                   ported: 0
──────────────────────────────────────────────────────────────────────────
TOTAL  items 563 · addressable 165 · ported 107  (65% of addressable)
       + 1026 generated instances (breadth) · 4 escalated variants (depth)
```

**Three buckets, never summed.** *Ported* = a real clone of a real source item, and the only
thing the parity rate counts. *Instances* = the same pattern re-asked over another entity.
*Variants* = a ported task made harder to retrieve, same ground truth. Summing them is not a
rounding error, it is a category error: it claims coverage of source items that were never
covered. This ledger reported **689% of addressable** until 2026-08-11 because 1,026 generated
instances carried byte-identical provenance to real clones (`docs/AUDIT.md` A15).

**The denominator matters more than the numerator.** The crude "7% of 563" was itself
misleading: 300 of those items need an Odoo surface, and 90 of FinanceBenchmark's
`finance_qa` are open analytical prompts whose only grader is an LLM judge over 2,394 style
assertions — which this repo bans from the reward path. Counting them as a gap would imply we
intend to close them, and we do not; counting them as "done" would be a lie. They are a
**class**, with a reason.

Addressable = `verbatim_gt` + `recomputable` + `judgement_port`. Against that, coverage is
**107 of 165 (65%)**, and every one of the remaining 58 has a named blocker:

| blocker | items | what unblocks it |
|---|---|---|
| ~~FB `erp_qa` questions not yet emitted by the cloner~~ | ~~65~~ **3** | **NEARLY CLOSED** — the ten rejected intent classes got handlers; 97 of 100 now emit. The last 3 are the genuinely degenerate ones (a year before the ledger begins; a typo'd question FB itself ships) and should ship as documented exclusions, not silent zeros |
| ~~FB items naming companies absent from the shared world~~ | ~~31~~ **0** | **CLOSED** — `world/etl/fetch_filings.py` freezes real SEC XBRL facts; 68 filing companies in-world |
| FB `finance_qa` single-figure (`recomputable`) | 28 | a filings-snapshot cloner; the frozen `filings` surface already serves this shape |
| FB `business_brief` | 25 | a brief emitter grading required fields per-section |
| ~~TAC finance remaining~~ | ~~4~~ **3** | 9 of 12 done; the porting pattern is proven |

The 31 unbindable items were a *useful* failure: filings had been seeded per task, so the
binder correctly reported those companies absent from the shared world and named exactly
which snapshot to build. That build is done — **152 of 153 addressable FB items bind**, the
one `absent_entity` being a question about a company the world deliberately does not hold,
which is an empty-answer trap rather than a gap. The pipeline working as intended: the ledger
produced a build list, the build closed it, and re-running the ledger proved it.

## Why the gap exists, without excuses

Three of the reasons are real, one is not.

**Real.** ERP-Bench is Odoo procurement and manufacturing — a different business surface from
this world's AP/AR/close/treasury. Porting its 300 needs an Odoo-shaped mock, which is a
build, not a transcription.

**Real.** FinanceBenchmark's own ground truths do not reconcile with its shipped data
(`docs/AUDIT.md` A3), so blind replication imports its bugs. Every clone here recomputes truth
in-world — which is slower than copying and is the right call.

**Real.** TheAgentCompany grades written `.xlsx` artefacts inside a Docker/ownCloud/RocketChat
estate. The judgement ports; the plumbing cannot.

**Not real, and the actual answer to the question.** Sequencing. Parity is mechanical,
parallelisable and gives breadth fast; the hard layer is the differentiator you add *after*
you can claim it. I did the interesting work first. "This world runs all 100 of
FinanceBenchmark's ERP tasks" is a checkable claim a buyer can verify in a minute; "we
extracted the mechanisms" is not.

## What actually blocks the biggest slice

The FB `erp_qa` gap is **not** a world-capability gap. The cloner routes a question to a
handler only if the question's wording matches its scenario label, because FB's labels are
coarse and a mis-route produces a task whose graded fields do not answer its own prompt. 50
of the 100 questions fail that gate — and reading them, most are answerable from data this
world already has:

| rejected under | asks for | this world has it |
|---|---|---|
| Aged Balance (7) | "coming due in the next 7 days", "180+ days", overdue breakdown | yes — due-window and bucket queries |
| Customer Setup (7) | phone numbers, contact details | yes — `erp_customers.phone/contact_*` |
| Invoicing History (6) | largest invoice, highest-invoiced customer | yes — ranking over `erp_cust_trans` |
| Vendor Balance (5) | total overdue AP, AP by vendor group | yes — an existing task computes this |
| Vendors (5) | payment terms, vendors on hold, new vendors | yes — vendor master |
| AP Payments (4) | payment proposal contents, 7-day obligation | yes — payment-run surface |
| AP Invoices (4) | due this week, posted on a date, 3-way match status | yes — incl. the PO/receipt tables |
| Collections (3) | current letter level, last letter sent | yes — `erp_collection_letters` |
| Collections Tasks (3) | today's worklist, open cases | yes — `erp_activities` |
| Cash Discounts (2) | discount expiring in N days | yes — `erp_cash_disc` chains |

A minority are genuinely degenerate and should ship as empty-answer traps or be excluded with
a stated reason — e.g. *"How many payments did Birch Company make in 2017"* (before this
ledger begins) and *"top 10 largest payments … in yyyy"* (a literal typo in FB's dataset,
which is documented as carrying typos).

**So the biggest parity slice is ~10 new handlers plus intent entries, not new world
capability.** That is the next push.

## Order of work

1. **FB `erp_qa` to ceiling** — handlers for the ten rejected classes above. Highest yield per
   unit of effort: +~50 tasks against existing world data.
2. **TAC finance, remaining 8** — the porting pattern is proven; four are done.
3. **FB `finance_qa` (126)** — needs a filings-snapshot cloner; each item is a public-company
   figure or ratio, and the frozen `filings` surface already serves that shape.
4. **FB `business_brief` (25)** — the section schema is known; graded per-field.
5. **ERP-Bench (300)** — decide explicitly: build an Odoo-shaped surface, or record it as
   deliberately out of scope with the reason. Do not leave it silently at zero.

Parity is not the ceiling of this world — the hard layer is what makes it worth running. But
parity is the claim a buyer can check, and it should have come first.

## Generated instances vs ported tasks — counted separately, deliberately

`world/etl/sweep_erp_qa.py` generates additional **instances** of the ERP question patterns
the cloner already verifies, over other entities in the ledger, with ground truth recomputed
in-world. They live in `tasks/erp_qa_gen/` and are **excluded from every parity number above**,
which counts only real clones of real benchmark questions.

The distinction matters and is easy to abuse: 1,320 instances of 33 patterns is breadth, not
diversity. ERP-Bench does the same (300 tasks from 29 patterns) and it is defensible — a
benchmark needs instances so a model cannot pass by memorising one — but the count must be
reported as **patterns x instances**, never as if each task were a distinct kind of problem.

| | count |
|---|---|
| distinct task patterns (hand-authored + ported + cloner routes) | ~70 |
| generated instances of those patterns | 1,320 |
| escalated variants (same ground truth, harder retrieval) | 54 |
