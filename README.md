# finance-world

A simulated corporate-finance environment + benchmark ("world") for evaluating and training
AI agents, built for a frontier-lab finance team. Harbor-packaged, deterministic verifiers,
no LLM judge in the reward path.

Task families — **20**, in two layers:

*Read-and-reconcile* (ask the world a question it will not answer in one place):
- **erp_qa** / **erp_qa_fb** — grounded AP/AR questions (balances, aged debt, open invoices,
  payment terms, cash discounts, collection letters) through MCP tools against a mocked ERP;
  `erp_qa_fb` replays microsoft/FinanceBenchmark questions verbatim with in-world ground truth.
- **finance_qa** / **finance_qa_fb** / **business_brief** / **business_brief_fb** —
  public-company figures, ratios, and structured counterparty profiles over a frozen SEC XBRL
  snapshot (38 registrants, 46,686 facts, annual and quarterly, every value carrying its
  accession). The `_fb` families replay FinanceBenchmark's own `finance_qa` and `business_brief`
  items, converted from its LLM judge to pinned per-field checks. Every brief also asks whether
  the subject is already a counterparty on our books — answerable only from the ERP, and for
  half the subjects the truthful answer is "no relationship".
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
- **erpbench** — procure-to-pay and make-or-buy planning against demand that on-hand stock
  cannot cover: which customer orders to accept, which to reject, what to buy from which
  vendor offer within its horizon-wide min/max, and what to manufacture on which workcentre.
  Ported from agentic-labs/erp-bench, whose 300 tasks each boot a real Odoo in Docker; here
  they run on an Odoo-shaped MCP surface (`mcp/servers/odoo_server.py`) and the same judgement
  is graded as deterministic SQL over the world the agent leaves behind.

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
  `email` · `filings` (frozen real-EDGAR facts) · `docs` · `odoo` (Odoo-19-shaped
  procurement/manufacturing: `search_read` over `[field, op, value]` domains, `create`,
  `write`, `action_confirm`) · `harness` (submit_answer only).
- `tasks/<family>/<slug>/` — **Harbor task dirs** (`task.toml`, `instruction.md`,
  `environment/` incl. per-task `seed/` layers, `solution/` oracle walk, `tests/` verifier).
  **1,534 tasks across 20 families.** Provenance is machine-readable and the three kinds are
  never summed: a *ported* clone of a real source item, a *generated* instance of a ported
  pattern over another entity (`generated = true` + `pattern`), and an *escalated variant* of a
  ported task (`variant_of`). Conflating them is what let the parity ledger report 689%
  coverage (`docs/AUDIT.md` A15).
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

## The prompt is a message; the contract is on the tool

An instruction is what a colleague would actually send — a request, its constraints, and the
war story behind them. It does **not** list the fields to be filled in:

```
**Marcus Bell · AP Controls · Teams 09:30**

Quarterly vendor hygiene review for the REVIEW group — can you work out which ones need
deactivating? Follow SOP-AP-11 to the letter on this, the definition is fussier than it
looks and last quarter's numbers had to be restated because two different findings got
counted in the same bucket.

Use today as the review date.
```

What must be filed lives on the reporting tool, where it lives in a real deployment: each task
seeds an `answer_schema`, and the harness server serves it through `reporting_fields`. The
agent discovers the contract by inspecting the system, and `submit_answer` reports what is
still outstanding.

This is a difficulty setting, not a cosmetic one. A prompt that asks for `overpayment_usd` and
`underpayment_usd` separately has already told the model there are two directions of error;
`duplicate_invoice` + `duplicate_of` has already told it a duplicate exists. `sim/validate.py`'s
S4 drift guard moved with the contract — a graded field must appear in the schema or the
instruction, so the invariant ("the agent is told, somewhere it can see, what it is graded on")
is repointed rather than relaxed.

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
