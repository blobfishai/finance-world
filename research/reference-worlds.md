# Reference worlds — conventions finance-world inherits

> Distilled 2026-08-10 from `~/dev/salesforce-grok`, `~/dev/lawfirm-qwen`, `~/dev/blobfish-0`
> (plus `~/dev/hillclimb`, `~/dev/eval-gen`). File paths below are in those repos.

## The house pattern (common to all three)

A "world" repo is a **world-builder**, not a task-dir collection:

1. **Research-first**: domain census → benchmark/eval inventory → anchor documents (SOPs,
   policies) → coverage matrix with Covered/Partial/Gap verdicts.
2. **One simulated company** with a SQLite state (`seed.db` → copy-on-write `state.db`
   sessions), a Python HTTP runtime (`server.py`) exposing `/mcp` (JSON-RPC, `Mcp-Session-Id`),
   `/sessions`, `/tool-call`, `/verify/{task_id}`, `/reset`.
3. **Tools as per-vendor Python modules**, namespaced through MCP config so the agent sees
   *separate product servers* (e.g. `salesforce.list_lead`) over one shared state.
4. **Tasks as JSONL rows** (prompt, goal, `required_tools`, `walk` = reference tool path,
   `expected_state_changes`, `acceptance_label`, `difficulty_tier`, optional `session`
   multi-turn nudges).
5. **Verifiers as deterministic Python "VCode"** — `def verify(initial_state, final_state,
   trace)` doing state-diff assertions + anti-hack vetoes. **No LLM judge in the reward path.**
6. **Oracle admission rule**: a task ships only if its reference walk replays green through its
   own verifier (lawfirm: 231/231; blobfish-0 calls it "ship-honest").
7. **Flake-scan triage** (both playbooks, same rule): run model N trials/task —
   fail 3/3 → too hard, park it (log failure mode; first audit-before-blame: replay the
   reference walk to rule out harness bugs) · mixed pass/fail → **flaky = the frontier, keep
   and study** · pass 1st try → too easy → escalate (longer walks, ambiguity, distractors).

## salesforce-grok (closest analog: built for grok/xAI)

- Layout: `config/ data/ docs/ mcp/ scripts/ sim/ world/ dashboard/ test/ external/`. Node ESM
  driver scripts, zero npm deps; world runtime is Python.
- Canonical wave-6 package `world/blobfish-wave6/package/sbx_*/`: **214 tables, 205 tools,
  25 tasks, 8,138 seeded rows**; `world.json` (format_version 4) embeds tables/tools/tasks/
  verifiers + a `harbor` block; `tools/{salesforce,stripe,email,slack,calendar,erp,jira,github,
  notion,pagerduty,core}.py`; 11 vendor MCP servers via `config/mcp-servers.json` +
  `mcp/vendor-server.mjs`; eval-only `mcp/harness-server.mjs` (verify/reset off the agent's
  business surface).
- `docs/CREATION-PROTOCOL.md` = methodology (research → THESIS → tool universe → data chaos →
  task ladder, with the §5 triage rule). `docs/COVERAGE.md`: 171-item census × world inventory.
  `docs/anchors/`: 48 SOP/policy markdown docs, each prefixed `> SIMULATION ONLY`, seeded into
  an in-world `agent_documents` table (`scripts/seed-wave6-documents.mjs`).
- Difficulty = **tool-graph walk length** (wave-6 bimodal at 2 and 9–13 hops). Escalators:
  `scripts/escalate-local.mjs` (obscure refs + distractor rows, verifiers unchanged),
  `scripts/harden-wave5.mjs` (conflicting SOP versions, conditional rules, decoy docs).
- Flake protocol: `sim/run-flake-scan.mjs --all --trials N` → `data/flake/<label>.json`
  (`solidPass/flaky/solidFail`, `depthCurve` buckets, `failedConditions` histogram) →
  generated `dashboard/*.html`. Model roster: `config/model-roster.json` (8 models, grok focus).
- Golden details to copy: **reference-relative turn budgets** (`maxTurns = max(24, refWalk*3+6)`
  — caps must never masquerade as capability verdicts); audit-before-blame; immutable seed +
  copy-on-write sessions; `(SIMULATED)` disclaimers everywhere.
- Warts to avoid: 231 MB committed world waves + 54 MB screenshots; **no `research/` dir**
  (its own protocol says to adopt one — we are); no CI; `difficulty_tier` null on 16/25 tasks;
  `solvability.measured: false` on most tasks; template placeholders leaking into prompts;
  near-duplicate wave packages instead of diffs.

## lawfirm-qwen (newest; adds Harbor export + research discipline)

- Same skeleton + `world/expansion/packs/` (9 authored content packs → `assemble.mjs` compiles
  packs into tasks + generated VCode, append-only) and `world/local/export_harbor.py` →
  `dist/harbor/` (world-bundle dialect: `task.yaml` + `tasks/tasks.jsonl` + one image; see
  `harbor-format.md` for why our exporter targets per-task true-Harbor dirs instead).
- Scale: 231 tasks, 102 tools, 74 tables (~1,000 rows), 211 seeded documents; 21 proven-flaky.
- `docs/WORLD-CREATION-PLAYBOOK.md` = 6-stage canonical pipeline (Stage 0 question-driven
  research → thesis → tool census/multi-system mocking → tables → eval-anchored seeding →
  triage-and-grow), annotated with what's implemented vs gap. `data/research/` holds
  `legal-eval-inventory.md` (29 benchmarks) and `domain-registry.json` (101 items with
  `what_agents_must_do`/`task_families`/`world_requirements`) — the model for our `research/`.
- Task rows carry `acceptance_label` (too_easy 105 / pending_calibration 75 / in_band 36 /
  too_hard 5) — calibration state lives *on the task*.
- Seeded friction: 3% `rate_limited`/`stale_reference` tool errors, 15% ambiguous write-acks,
  per-session write caps, **fixed world clock** (`2026-08-09T12:00:00Z`) — determinism rule:
  the world has an epoch, tasks say "as of" dates.
- `docs/AUDIT.md`: three harness bugs found *before trusting scores* (4096-token truncation,
  shared-seed contamination flipping 202 verdicts, prompt/verifier drift → task quarantined).
  Finance-world should budget for the same audit pass.
- Known gap we must build: the automatic too-easy → variants spawner (`sim/grow-tasks.mjs`)
  is spec-only there.
- `mcp/systems.json` splits 102 tools into 8 product-namespace MCP servers over one state, and
  explicitly notes true multi-storage fragmentation is the *next* world's mechanic — **that
  mechanic (data split across ERP + spreadsheets + second system) is ours to build.**

## blobfish-0 (the factory monorepo; source of the true-Harbor exporter)

- 33 GB product monorepo (`packages/world-factory` stages `s01_ingestion…s13_realism`), not a
  world repo. Useful to us mainly for: `scripts/export_harbor_agentic.py` (per-task Harbor
  export, harbor 0.17.1-verified; see `harbor-format.md`), the multi-probe verifier lesson
  (468 tasks quarantined for single-probe gameability → `checks.json` ALL-must-pass), and
  `research/` (paper notes, `ideas/hill-climb.md`, `realism-gap-rubric.md`).
- Dataset card: 1,189 tasks / 217 worlds; families hard/deep/ultra/dialogue.
- Avoid copying: website-console harbor dialect (`task.yaml` + `verifiers/`), partial-credit
  rewards, committed `*.sqlite-wal/-shm`, repo-root log litter.

## Adjacent tooling

- `~/dev/hillclimb` — **prompt-regression CI**, not difficulty calibration: FastAPI mock of the
  Composio v3 REST surface (10 toolkits, 60+ tools, SQLite, `/seed`, `/reset`,
  `/api/v3/tools/{slug}/execute`) + YAML tasks with llm_judge assertions + baseline/revision
  compare loop. Relevant only if we later want Composio-style vendor shims.
- `~/dev/eval-gen` — MCP-eval generator SaaS (generates evals from tool schemas / session
  logs / workflows via `claude -p`). Could seed extra task variants later; not on the critical
  path.

## Bottom line for finance-world

Author like lawfirm-qwen (packs → assemble → world.json → SQLite + server.py + vendor MCP
split), run the salesforce-grok flake/triage/dashboard loop, export true per-task Harbor dirs
per blobfish-0's exporter, and add the two things the siblings lack: a real `research/` corpus
(this directory) and genuine multi-system data fragmentation as the core world mechanic.
