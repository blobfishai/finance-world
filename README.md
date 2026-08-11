# finance-world

A simulated corporate-finance environment + benchmark ("world") for evaluating and training
AI agents, built for a frontier-lab finance team. Harbor-packaged, deterministic verifiers,
no LLM judge in the reward path.

Task families — **17**, in two layers:

*Read-and-reconcile* (ask the world a question it will not answer in one place):
- **erp_qa** / **erp_qa_fb** — grounded AP/AR questions (balances, aged debt, open invoices,
  payment terms, cash discounts, collection letters) through MCP tools against a mocked ERP;
  `erp_qa_fb` replays microsoft/FinanceBenchmark questions verbatim with in-world ground truth.
- **finance_qa** / **business_brief** — public-company figures, ratios, and structured
  profiles synthesizing public filings with internal AR/AP.
- **cross_system** · **bank_rec** · **cash_app** · **cash_forecast** · **close_mgmt** ·
  **pbc** · **expense_audit** · **threeway_match** · **vendor_master** · **payment_proposal**
  — answers that require joining deliberately fragmented data (ERP + spreadsheets +
  subsidiary books + email).

*Write-and-approve* (the hard layer — `docs/HARD-LAYER-DESIGN.md`): the agent operates the
business, and the verifier grades **the world it leaves behind**, not the story it tells.
- **payment_run** — a Friday run that cannot be fully funded: exclusions first, then discount
  capture, then oldest past-due, committed as a *total and disjoint* paid/rejected partition.
  A short run is committed by naming what goes unpaid, never by dropping it.
- **journal_entry** — accruals computed from the governing contract on the SOP's day-count
  basis, staged and submitted for approval when they exceed the delegation-of-authority limit
  (so "posted" is the wrong answer).
- **anomaly_triage** — duplicate-disbursement screening, where the correct answer sits between
  paying a duplicate and rejecting a legitimate look-alike.
- **collections_ops** — dunning letters and credit holds as governed write actions.

Everything is simulation: all companies, balances, and documents in the world are synthetic
(`SIMULATION ONLY`), grounded in researched-but-fictionalized scenarios.

## Where things are

- `PLAN.md` — build stages, operating rules, current status.
- `research/` — Stage 0 corpus: question ledger, reference-world conventions, Harbor format,
  eval/benchmark inventory, ERP domain model, workflow & data-chaos research.
- `THESIS.md` — the world's framing (company, epoch 2026-03-02, personas, systems, chaos).
- `world/` — `schema.sql` + `etl/load_core.py`: builds `world/build/core.sqlite` from the
  FinanceBenchmark raw extracts (1,000 customers, 1,000 vendors, ~6,900 subledger lines).
- `mcp/` — **one MCP server per tool** over the task run's SQLite state:
  `erp` (D365-shaped, discovery-first) · `books` (QBO-shaped subsidiary) · `sheets` ·
  `email` · `filings` (frozen real-EDGAR facts) · `docs` · `harness` (submit_answer only).
- `tasks/<family>/<slug>/` — **Harbor task dirs** (`task.toml`, `instruction.md`,
  `environment/` incl. per-task `seed/` layers, `solution/` oracle walk, `tests/` verifier).
  Families: erp_qa, cross_system, finance_qa, business_brief.
- `verifiers/` — deterministic VCode engine (`vcode.py`): answer checks with tolerances,
  trace checks, state-diff anti-hack vetoes. No LLM in the reward path.
- `sim/` — `prepare.py` (core + task seed → run), `oracle.py` (admission gate),
  `validate.py` (**world-correctness gate**, 10 offline checks/task incl. negative
  controls), `run_task.py`, `run_batch.py` (flake-scan), `build_reports.py`, `scaffold.py`.

```bash
./world/build.sh           # the ONLY supported build: core -> cash -> demo, then validate
python3 sim/validate.py    # must print "VALIDATION PASSED" before any model run
python3 sim/refresh_gt.py  # re-derive gt_sql ground truths after a world rebuild (--apply)
python3 sim/reverify.py    # re-grade stored trials when the VERIFIER changed (--apply)
```

`load_core.py` drops and recreates the database, so running it alone silently discards the
cash and demo layers — always build through `world/build.sh` (`docs/AUDIT.md` A6).

## Honesty machinery (why the numbers can be trusted)

Every difficulty claim this repo makes has survived an audit-before-blame pass, and several
did not. `docs/AUDIT.md` is the ledger; the load-bearing entries:

| # | What we caught | Why it mattered |
|---|---|---|
| A5 | empty-answer traps graded by exact string equality | a correct answer that *explained itself* scored 0 — two "frontier" tasks were false-flaky |
| A6 | `load_core.py` run alone | zero payments loaded; every balance inflated ~2.5× |
| A7 | traces outliving the world they measured | a trial recorded `$81,262,127.02` graded **PASS** — correct against the pre-cash-layer world |
| A8 | the turn budget was a capability cap | models were cut off mid-task at 24 turns and scored as wrong answers |

The pattern: exact-match grading on natural-language fields and a tight clock were
manufacturing difficulty the world does not have. Fixes shipped as check types (`none_answer`,
`yes_no`), a `starved` trial class excluded from triage, and a rule that a trace is valid only
against the current world build.
- `traces/<model>/<family>/<slug>/trial-N.(pass|fail).json` — real model traces, failures included.
- `reports/` — `summary.json` + per-model failure reports.

## Per-task seeding (the core mechanic)

Every task carries its own seed layers in `environment/seed/`:
`seed.sql` (special core data — e.g. Sparrow Retail exists only in the collections task) ·
`mcp_seed.json` (special per-server data: email messages, sheet rows, subsidiary invoices,
filings facts) · `documents/` (seeded policy/SOP/template docs) · `inputs/` (input files
staged into the agent workdir). `sim/prepare.py` overlays them on the shared core.

## Is this Harbor format?

Yes. Each `tasks/<family>/<slug>/` is a Harbor task directory (schema_version 1.4:
`task.toml` + `instruction.md` + `environment/` + `solution/` + `tests/` with the
`reward.txt` contract in `tests/test.sh`). Per-task seeding is exactly what Harbor's
per-task environments want. Repo-level `mcp/`, `world/`, `verifiers/`, `sim/`, `traces/`,
`reports/` are the authoring/calibration workspace, outside Harbor's per-task contract; the
Stage-6 exporter bakes the runtime + materialized seed into each task's `environment/` so
`harbor run -p <task> -a oracle` works standalone.

Method: research-first world building per the house playbooks (see
`research/reference-worlds.md`), with triage-and-grow task calibration — flaky tasks are the
product. Admission rule: a task ships only if its oracle walk replays green (currently 10/10).
