# research/ — Stage 0 corpus

Question-driven, stored research (not one-shot). The ledger is the spine: every design
decision in `../THESIS.md` traces to a ✅/🟡 row here.

| File | What it answers | Ledger rows |
|---|---|---|
| `questions.md` | The round-1 question ledger (rows 1–17, frozen 2026-08-10) | all |
| `questions-round2.md` | The **round-2 ledger** (rows 18–42), opened after the wave-2 research: what we now know we don't know, with a stated plan on every 🔴 | 18–42 |
| `reference-worlds.md` | House conventions from `~/dev/salesforce-grok`, `~/dev/lawfirm-qwen`, `~/dev/blobfish-0`; the world shape, VCode verifiers, triage-and-grow protocol | 15, 16 |
| `harbor-format.md` | True per-task Harbor spec (task.toml, reward contract, harbor 0.17.1 gotchas) + the two-dialect decision | 15 |
| `blobfish-api.md` | The world-factory API; import/release compatibility targets | 15 |
| `evals-and-benchmarks.md` | Benchmark landscape; **microsoft/FinanceBenchmark deep-dive** (251 tasks: 100 erp_qa / 126 finance_qa / 25 business_brief; grading; D365 MCP surface) | 5, 6, 7, 14 |
| `erp-domain.md` | D365 Finance AP/AR domain model (three-layer subledger, PaymTerm/CashDisc, collections state machine, dual aging truth), verified demo names, ERP MCP shapes, competitor-system briefs | 9, 10, 13 |
| `domain-workflows.md` | Seven personas + done-criteria, six workflows step-by-step (incl. 7-step dunning runbook), **12 sourced data-chaos patterns**, public-data stack (EDGAR endpoint map, finance MCPs) | 2, 3, 4, 10, 11, 12, 17 |
| `finance-tool-landscape.md` | Vendor/market survey of the tools a real finance team runs (ERPs, AP, AR, close, treasury, FP&A, expense, data providers, shipping AI agents) | 2, 3, 17 |
| `finance-mcp-landscape.md` | **Master tool inventory**: full parse of the BlockRunAI curated MCP list (49 servers + 7 skills), verified tool surfaces from the cloned finance MCPs, four tool-surface archetypes, cross-reference to our 7 mocked servers, unmocked classes, and the census-tested new-server shortlist (result: zero) | 2, 9, 17, 32 |
| `erp-bench-deep-dive.md` | **ERP-Bench / the Anchor method**: 300 Odoo-19 tasks in true Harbor format, one solved spec → four artifacts (the anti-drift mechanism), the admission gates (CP-SAT OPTIMAL, objective non-collapse, unsat-demand shape), the 3-dimension weighted verifier, and the seeded chaos layer | 22, 23, 26, 36, 37, 38, 39, 40, 41 |
| `odoo-domain.md` | **Second ERP data model** (Odoo 19.0, LGPL fact-source): polymorphic `account_move` vs the D365 subledger split, per-installment open items (the lying header due date), early-payment discount on the term, the per-line 2-way/3-way bill-control rule, the five bill-matching verdicts | 18, 20, 34, 35 |
| `erp-mcp-tool-census.md` | **Six real ERP MCP servers**, four access patterns (generic CRUD · curated verbs · SQL passthrough · discovery-first), verbatim NetSuite `ns_*` ladder, ERPNext↔D365 model mapping, tiered rate limits, and the documentation-drift catalogue | 18, 29, 30, 33 |
| `erp-workflow-automation.md` | **How agents actually drive ERPs**: a production Odoo agent's LangGraph decomposition and confirmation gate, SAP Fiori's 9-step login, the lying tool (12/15 stubs), retry-induced duplicate writes, and the nine uncovered write-and-approve families | 19, 21, 31, 42 |
| `finben-and-agent-evals.md` | **FinBen correction** (the checked-out harness has zero finance tasks), the deterministic metric bank + DROP numeric grader, the shipped Vals rubric row schema (v1 conjunction → v2 severity/must_pass), and a multi-agent write-path architecture | 23, 24, 25, 27, 28 |
| `external/financebenchmark-extracts/` | 2.2 MB of the actual benchmark: dataset.yaml task/rubric definitions + USMF demo seed (SYNCUS/SYNVEN accounts, ~7k journal lines) | 6, 13 |
| `external/repos/INDEX.md` | Index of the **40 vendored source repos** (838 MB) — evals, methodology, real tool surfaces, ERP-vendor axis, skipped-and-why, and what they add that the world doesn't cover | all |

Cross-reference note: Birch Company's account number wasn't findable on the public web
(`erp-domain.md` marks it UNVERIFIED) but appears as **US-027** in the benchmark extracts —
when docs and shipped data disagree, the shipped data wins.

Wave-2 corrections to earlier notes, per the same rule: `evals-and-benchmarks.md` §3.8 listed
"FinBen (36 financial tasks)" as pending — the checked-out `financial-evaluation` tree contains
**zero** finance tasks (`finben-and-agent-evals.md` §1); and §3.1's "binary conjunction" rubric
rule is superseded by Vals v2's severity-weighted `must_pass` scheme (same note, §3).
