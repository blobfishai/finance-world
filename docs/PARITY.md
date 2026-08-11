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

| corpus | ships | runs here | gap | note |
|---|---|---|---|---|
| microsoft/FinanceBenchmark `erp_qa` | 100 | **35** | 65 | cloner ceiling is 39; 50 questions rejected by the intent gate, 11 unresolvable |
| microsoft/FinanceBenchmark `finance_qa` | 126 | 0 | 126 | no cloner written; 6 hand-authored finance_qa tasks exist but are not clones |
| microsoft/FinanceBenchmark `business_brief` | 25 | 0 | 25 | no cloner written; 2 hand-authored briefs exist but are not clones |
| agentic-labs/erp-bench | 300 | 0 | 300 | Odoo procurement/manufacturing; needs an Odoo-shaped surface we do not have |
| TheAgentCompany (finance) | 12 | **4** | 8 | ported onto sheets/docs; originals need Docker + ownCloud + RocketChat |
| **agentic total** | **563** | **39** | **524** | **7%** |

Static-QA corpora are counted separately because porting them would change what they measure:

| corpus | ships | status |
|---|---|---|
| patronus/financebench | 150 | mechanism adopted (refusal/evidence-span design); not agent-tool tasks |
| FinQA / ConvFinQA / TAT-QA | 1,147 / 3,037 / 16,552 | mechanisms adopted (executable-program GT; `scale` as a graded field) |
| SECQUE | 565 | environment contract studied; no tools, hidden judge |
| vals-ai finance-agent v1/v2 | 50 / 27 | rubric design adopted (conjunction + contradiction, severity weights) |

Turning a static table-QA item into a tool-using task makes it a *retrieval* task, not a
finance-operations task. Those corpora were read for design, and that is defensible. **The
563 agentic tasks are not**, and 7% is the honest coverage.

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
