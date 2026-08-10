# research/ — Stage 0 corpus

Question-driven, stored research (not one-shot). The ledger is the spine: every design
decision in `../THESIS.md` traces to a ✅/🟡 row here.

| File | What it answers | Ledger rows |
|---|---|---|
| `questions.md` | The question ledger itself (status per question, evidence links) | all |
| `reference-worlds.md` | House conventions from `~/dev/salesforce-grok`, `~/dev/lawfirm-qwen`, `~/dev/blobfish-0`; the world shape, VCode verifiers, triage-and-grow protocol | 15, 16 |
| `harbor-format.md` | True per-task Harbor spec (task.toml, reward contract, harbor 0.17.1 gotchas) + the two-dialect decision | 15 |
| `blobfish-api.md` | The world-factory API; import/release compatibility targets | 15 |
| `evals-and-benchmarks.md` | Benchmark landscape; **microsoft/FinanceBenchmark deep-dive** (251 tasks: 100 erp_qa / 126 finance_qa / 25 business_brief; grading; D365 MCP surface) | 5, 6, 7, 14 |
| `erp-domain.md` | D365 Finance AP/AR domain model (three-layer subledger, PaymTerm/CashDisc, collections state machine, dual aging truth), verified demo names, ERP MCP shapes, competitor-system briefs | 9, 10, 13 |
| `domain-workflows.md` | Seven personas + done-criteria, six workflows step-by-step (incl. 7-step dunning runbook), **12 sourced data-chaos patterns**, public-data stack (EDGAR endpoint map, finance MCPs) | 2, 3, 4, 10, 11, 12, 17 |
| `external/financebenchmark-extracts/` | 2.2 MB of the actual benchmark: dataset.yaml task/rubric definitions + USMF demo seed (SYNCUS/SYNVEN accounts, ~7k journal lines) | 6, 13 |

Cross-reference note: Birch Company's account number wasn't findable on the public web
(`erp-domain.md` marks it UNVERIFIED) but appears as **US-027** in the benchmark extracts —
when docs and shipped data disagree, the shipped data wins.
