# Are these real prompts? — provenance and realism assessment

## What the tasks are actually based on (82 tasks)

| n | Basis | Research anchor |
|---|---|---|
| 47 | **Verbatim questions from microsoft/FinanceBenchmark** `erp_qa` | `research/external/financebenchmark-extracts/data/dataset.yaml` — Microsoft's own eval, written to represent real ERP QA against D365. Question text unchanged; ground truth recomputed in-world (AUDIT A3). |
| 11 | **Researched workflows** | `research/finance-agent-workflows.md` — 12 workflows step-mapped from vendor runbooks and practitioner sources, plus teardowns of shipping finance agents. |
| 7 | **FinanceBenchmark scenarios re-anchored** (`finance_qa`, briefs) | `research/evals-and-benchmarks.md` segments; figures are real XBRL facts from data.sec.gov. |
| 4 | **The buyer's own brief examples** | The engagement brief: Birch receivables, USMF overdue AP, Fourth Coffee East discounts, Sparrow Retail collections. |
| 3 | **Practitioner-article findings** | `research/external/articles/` (49 sources) — tolerance-dialect inversion, threshold-shaving detector, PCAOB AS 2315 projection. |
| 3 | **Repo-sweep findings** | `research/external/repos/` (24 repos) — interactive counterparty (TheAgentCompany), ACH return, grounded refusal (FinanceBench). |
| 3 | **Sourced chaos patterns** (novel scenarios) | `research/domain-workflows.md` §3 — 94% close in Excel, 68% of invoices keyed from email, 46% unapplied cash. |
| 2 | Grown variants | escalations of tasks that passed too easily. |
| 2 | External eval classes | ConvFinQA multi-turn, AccountingBench multi-period. |

**71% of tasks carry wording from an external eval or the buyer's own brief.** The questions
were not invented here.

## Where realism was failing: the framing, not the questions

Before this pass every prompt was a briefing memo I had written around the question:

> You are the AR analyst at Contoso Entertainment System USA (company USMF). Today is
> March 2, 2026. What is the outstanding receivables balance for the customer **Fourth
> Coffee East**…? Be careful to pick the right customer — several accounts share similar
> names. Outstanding balance means the open (unsettled) amount on posted customer
> transactions. Ground every figure in ERP tool calls, then submit…

Four things there are not how the ask arrives in real life:
1. **Role-play preamble** — the analyst knows who they are.
2. **Method spelled out** ("outstanding means the open unsettled amount", "net the credit
   memos", "use average inventory") — deciding the method *is* the work.
3. **Location hints** ("check the mailbox and the trackers too") — knowing where to look is
   the skill the fragmented world exists to test.
4. **Difficulty telegraphed** ("several accounts share similar names") — real life does not
   warn you about the distractor.

## After: how the ask actually arrives

```
**Casey Morgan · AR & Collections · Teams 09:14**

Fourth Coffee East just called about their account. What are we carrying on them right now?

---

Reply with `submit_answer`:

- `customer_account` (text)
- `outstanding_balance` (number)
- `open_invoice_count` (number)
```

A named colleague, a channel and a time, one or two sentences, no method, no hints, no
warning about the seven other Fourth Coffees. The only artificial element left is the reply
contract — kept deliberately, because deterministic grading needs a schema and real teams
do have reporting conventions.

All 82 were rewritten this way; the 47 benchmark clones keep Microsoft's question verbatim
and simply lose my wrapper, arriving as a Teams ping from the AP or AR lead.

## A defect the rewrite exposed: question ↔ graded-field mismatch

Reading the rewritten prompts side by side with their checks surfaced a generator bug that
no automated check could see. The cloner dispatched on FinanceBenchmark's `scenario`
label, which is coarse: "Aged Balance" also carries *"which transactions are coming due in
the next 7 days?"* and *"show me the aging breakdown for X"*. Those routed to the top-N
past-due handler, producing tasks whose graded fields **did not answer the question asked**
— prompt/verifier drift that field-name checking (S4) can never catch, because the
contract block is generated from the checks themselves.

Fixes: an intent gate (a question only routes to a handler if its text really asks that
question — 45 questions were dropped rather than mis-graded), a per-customer aging branch
that returns buckets instead of a ranking, and a real cash-collections handler. The clone
count fell from 47 to 33, which is the honest number: **fewer tasks, all of which actually
ask what they grade.**

## Residual realism gaps (honest list)

1. **Task truth is now task-owned where it can be.** Entity-specific tasks seed (and where
   needed clear) their own counterparty rows, so regenerating the shared ledger cannot
   silently gut a task — the failure mode that turned Fourth Coffee East's balance to zero.
   World-wide questions (total overdue AP) can't do this and are protected by `gt_sql`/S11
   instead.
2. **Field names still carry structure.** `subsidiary_net_balance` tells the agent a
   subsidiary exists; `tracker_cached_total` hints the tracker is stale. A harder variant
   would ask for one number and grade the reasoning trace instead.
3. ~~The core ledger has almost no cash~~ — **FIXED** by `world/etl/load_cash.py`: the
   ledger now carries 2,182 invoices closed by cash against 1,277 open, 146 partially
   settled short-pays, 4,337 settlements, 107 with the discount taken, and payment
   behaviour that varies by credit rating.
4. ~~Signal-to-noise is too high~~ — **IMPROVED**: the six-month expense extract is 66 rows
   (the six banded claims must be found by aggregation, not by eye), the bank statement 21,
   the lockbox 15, the AR watchlist 10. Real extracts are larger still, but the findings no
   longer sit in a hand-sized list.
5. **Most clone tasks are ≤4 tool calls** — authentic questions, but lookup-shaped work. The
   realistic *work* lives in the ~15 hand-authored workflow tasks.
6. **Everything happens on one frozen day, in one sitting**, and the scripted counterparty
   always replies immediately and helpfully.
