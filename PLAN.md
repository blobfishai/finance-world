# finance-world — build plan

World for a corporate-finance agent gym (buyer persona: finance team at a frontier AI lab).
Three workloads: ERP AP/AR question-answering over MCP tools · public-entity financial
research · business-brief synthesis. Packaging: Harbor. Method: the house world-creation
pipeline (salesforce-grok `docs/CREATION-PROTOCOL.md`, lawfirm-qwen
`docs/WORLD-CREATION-PLAYBOOK.md`), with research stored — not one-shot.

## Operating rules (non-negotiable)

- **Grounded research first.** Every design choice traces to `research/` (evals, domain docs,
  API surfaces, chaos scenarios). No invented realism.
- **Deterministic rewards.** VCode verifiers over state diffs; no LLM judge in the reward path.
  QA answers flow through a `submit_answer` tool so answers *are* state.
- **Ship-honest.** A task ships only if its oracle walk replays green through its own verifier.
- **Audit-before-blame.** A model "failure" counts only after the harness is exonerated
  (replay oracle in same config; check truncation/session-contamination/prompt-drift).
- **Fixed world epoch.** All aging/overdue math is stable relative to a frozen clock.
- **Calibration lives on the task.** `acceptance_label`: too_easy · in_band (flaky = the
  frontier, the gold) · too_hard · pending_calibration.

## Stages

### Stage 0 — Research (DONE 2026-08-10)
Question ledger: `research/questions.md`. Corpus: `research/*.md` + `research/external/`.
- [x] Reference-world conventions (`research/reference-worlds.md`)
- [x] Harbor packaging spec + dialect decision (`research/harbor-format.md`)
- [x] Blobfish factory API (`research/blobfish-api.md`)
- [x] Eval/benchmark/arena inventory incl. microsoft/FinanceBenchmark deep-dive
      (`research/evals-and-benchmarks.md` + `research/external/financebenchmark-extracts/`)
- [x] ERP domain model + API/MCP surfaces (`research/erp-domain.md`)
- [x] Real workflows, personas, done-criteria, chaos patterns
      (`research/domain-workflows.md`)
**Done when:** every `questions.md` row is ✅/🟡 with evidence, none 🔴. → Met, one
exception: Q8 (target model roster) stays 🔴 pending Sam/buyer input; doesn't block Stages 2–4.

### Stage 1 — Thesis (DRAFTED 2026-08-10 — pending Sam's review)
`THESIS.md`: the simulated company (name, size, fiscal calendar, epoch), personas, workloads,
which real systems are mimicked, the data-fragmentation story, task families, difficulty axes,
verification strategy. Feeds `world.json.thesis`.
**Done when:** thesis answers every questions.md row and names every system to be mocked.
→ Draft does both (7 mocked systems named; open decisions listed at bottom of THESIS.md).

### Stage 2 — Tool universe (WAVE-0 BUILT 2026-08-10)
Built: `mcp/lib/framework.py` (stdio MCP + tracing) + 7 per-tool servers in `mcp/servers/`
(erp discovery-first D365-shape, books QBO-shape, sheets, email, filings, docs, harness).
Remaining: seeded friction rates (lawfirm-calibrated), bank-export surface, form tools.

Census then mocks. For each tool: study the real product's MCP docs/API/GitHub usage
(`research/erp-domain.md`), then mock as a vendor Python module + per-vendor MCP server
(salesforce-grok pattern: one state, product-namespaced servers via `config/mcp-servers.json`).
Planned surface (confirm in Stage 1): D365-Finance-shaped ERP (AR/AP/ledger tools) · a second
ERP-ish system for a subsidiary (fragmentation) · spreadsheet tool over seeded XLSX/CSV
(shadow trackers) · document store (SOPs/policies/briefs, seeded like salesforce anchors) ·
filings/market-data tool over frozen public-company snapshots · email/comms read surface ·
eval-only harness server (verify/reset, off the business surface).
**Done when:** tool_schemas + deterministic behaviors + friction (rate limits, stale refs,
ambiguous acks at lawfirm-calibrated rates) exist for every censused tool, exercised by a
smoke test.

### Stage 3 — Tables & data chaos (CORE BUILT 2026-08-10; chaos is per-task by design)
Built: `world/schema.sql` (20 tables) + `world/etl/load_core.py` — 1,000 customers, 1,000
vendors, 3,459 AR + 3,428 AP posted lines from the FB raw journals; FIFO settlement engine;
aging snapshot 2026-03-01; epoch 2026-03-02. **Per-task seed layers carry the chaos**
(seed.sql / mcp_seed.json / documents/ / inputs/ in each task's environment/seed/).
Provenance note: FB's published GTs don't reconcile with their own shipped CSVs (group
assignments differ; "past due >90d" GT equals total open balance) — our GTs are recomputed
in-world and exact; FB scenarios are re-anchored, not copied blind.

SQLite schema (customers, vendors, invoices, open transactions, settlements, payment terms,
cash-discount codes, collection letters, aging config, GL summary, subsidiary tables,
spreadsheet mirrors, filings snapshots) seeded so that **sample-question ground truths are
computable exactly** (Birch receivables as of 2026-03-02; USMF overdue AP; Fourth Coffee East
discounts; Sparrow Retail collection level + recent payments). Chaos is *designed*: every
inconsistency (invoice only in spreadsheet, credit note in subsidiary system, stale tracker)
cites a sourced scenario from `research/domain-workflows.md`. Cross-system questions ("total
AR this week?") must have a single defensible answer the verifier computes.
**Done when:** seed builds reproducibly (`create_db` script, hash-pinned), oracle can compute
every planned ground truth, world clock frozen.

### Stage 4 — Task ladder (WAVE 1.5: 18 TASKS, 18/18 ORACLE-GREEN 2026-08-10)
Wave 1.5 added 6 workflow-anchored tasks from `research/workflow-mock-mapping.md`, all
zero-new-server, exact GTs: bank_rec (4-bucket statement-vs-books taxonomy), cash_app
(remittance emails + lockbox; no-remittance deposit must stay unapplied), cross_system/
intercompany-tieout (parent vs sub schedule delta decomposition), payment_proposal
(SOP-driven Friday run: discount capture + on-hold exclusion, exercises api_invoke_action),
pbc (approval only in email thread; second invoice = no-evidence finding), cash_forecast
(4-week direct method in separate legal entity CESP for exact arithmetic). 8 families now.
Parked pending schema: 3-way match (needs PO/receipt tables).
### (superseded) WAVE-0: 10 tasks
Wave 0 in `tasks/`: 6 erp_qa (incl. FB-verbatim credit limit, name-distractor balance,
company-wide AP aggregate, cash-discount capture, injected Sparrow collections story,
empty-answer trap) + 2 cross_system (subsidiary join w/ credit-memo trap; email-only
invoice) + 1 finance_qa + 1 business_brief (real-EDGAR frozen facts). Walks 3–8 tools.
Next waves: more FB scenario coverage (aged top-N, payment history, sales orders),
aging-snapshot divergence, collections_ops writes.

Start from researched tasks: FinanceBenchmark items first, then eval/arena/article-derived
scenarios. Each task: prompt (+ optional multi-turn `session`), `required_tools`, oracle
`walk` + args, VCode verifier (multi-probe, ALL-must-pass, anti-hack vetoes), difficulty
metadata. Families: erp_qa · public_research · business_brief · cross_system (chaos joins) ·
collections_ops (write actions: letters, holds) later.
**Done when:** every authored task passes the oracle admission rule.

### Stage 5 — Calibration loop (triage-and-grow) (IN PROGRESS 2026-08-10)
Status: wave-0 flake-scan running (haiku+sonnet, 2 trials, infra-aware resume after the
session-limit incident — docs/AUDIT.md A1). Real signal so far: haiku solidPass on
brief-caterpillar and total-ar-adventure-group → **escalated variants authored and
oracle-green** (brief-caterpillar-v2: per-year ratios + policy-band classification from a
seeded credit policy, walk 8→10; total-ar-adventure-group-v2: +side-log invoice
corroborated by email, +stale-summary distractor, walk 6→10). haiku real failures captured:
ap-overdue (pagination-truncation aggregation), email-invoice-meadow (guessed entity names,
asserted ERP absence without a successful query). Auto-escalator `sim/grow_tasks.py` still
TODO — variants are hand-grown for now (grounding beats generation).
`sim/run-flake-scan --trials 3` against target model(s):
- **Fail 3/3** → too_hard: park; log failure mode *after* audit-before-blame.
- **Mixed** → in_band flaky: the product. Study why pass vs fail; write failure-mode notes.
- **Pass 1st try** → too_easy: escalate via `sim/grow-tasks` (build it — spec-only in
  lawfirm): longer walks (3 → 10+ tools), ambiguity, distractor rows, conflicting docs,
  cross-system hops. Walk the sequence tree; grow depth until failure.
Budgets are reference-relative (`maxTurns = max(24, refWalk*3+6)`), never capability caps.
**Done when:** the shipped set is majority in_band/flaky at target depth, with failure-mode
reports per parked task.

### Stage 6 — Package & ship
Per-task true-Harbor export (`task.toml`/`instruction.md`/`environment/`/`solution/`/`tests/`,
reward.txt, oracle-verified at export, harbor CLI 0.17.1) + `world.json` (format_version 4)
kept blobfish-importable for hosted MCP / customer release. Dashboards from flake JSON.
**Done when:** `harbor run -p <task> -a oracle` passes for every shipped task; leaderboard run
on the model roster completes; handoff docs written.

## Repo layout (target)

```
research/            ← Stage 0 corpus (this exists first, by design)
THESIS.md            ← Stage 1
config/              ← world.config, model-roster, mcp-servers
world/packs/         ← authored content packs → assemble → world/build/world.json
world/runtime/       ← server.py, oracle.py, create_db, export_harbor.py
mcp/                 ← vendor MCP servers + bridge + harness server
sim/                 ← run-simulation, run-flake-scan, grow-tasks, leaderboard
data/                ← seeds, flake results, coverage
docs/                ← COVERAGE.md, AUDIT.md, anchors/ (all "> SIMULATION ONLY")
dist/harbor/         ← per-task export (gitignored)
```

Anti-goals (sibling warts): committed multi-hundred-MB world waves & screenshots; tasks with
null difficulty tiers or unmeasured solvability; template placeholders in prompts; partial-
credit rewards; single-probe verifiers; hand-edited result HTML.
