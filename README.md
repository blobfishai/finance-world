# finance-world

A simulated corporate-finance environment + benchmark ("world") for evaluating and training
AI agents, built for a frontier-lab finance team. Harbor-packaged, deterministic verifiers,
no LLM judge in the reward path.

Task families:
- **erp_qa** — grounded AP/AR questions (balances, aged debt, open invoices, payment terms,
  cash discounts, collection letters) answered through MCP tools against a mocked ERP.
- **public_research** — public-company financial figures and ratios with context.
- **business_brief** — structured company profiles synthesizing public + internal data.
- **cross_system** — questions whose answer requires joining deliberately fragmented data
  (ERP + spreadsheets + subsidiary systems).

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
  `run_task.py`, `run_batch.py` (flake-scan), `build_reports.py`, `scaffold.py`.
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
