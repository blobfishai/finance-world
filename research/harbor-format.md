# Harbor format — what finance-world must export

> Researched 2026-08-10. Sources at bottom. This is the packaging target for the world;
> the authoring repo itself follows the world-builder layout (see `reference-worlds.md`).

## What Harbor is

Harbor (laude-institute) is the harness behind Terminal-Bench 2.0: it runs arbitrary agents
(claude-code, openhands, codex, oracle) against containerized tasks, locally or on cloud
sandboxes (Daytona, Modal, E2B), and is also used to generate RL rollouts.

- Install: `uv tool install harbor`
- Run a local task: `harbor run -p <path/to/task> -a <agent> -m <model>`
- Sanity-check with oracle: `harbor run -p <path/to/task> -a oracle` (replays `solution/`)
- Scaffold: `harbor init --task "<org>/<name>"`
- blobfish-0 pins **harbor CLI 0.17.1** — pin the same until proven otherwise.

## Per-task directory spec (the true Harbor format)

```
<org>/<task-name>/
├── task.toml
├── instruction.md
├── environment/
│   └── Dockerfile            # or docker-compose.yaml, or docker_image in task.toml
├── solution/
│   └── solve.sh              # oracle solution (optional but required by our admission rule)
└── tests/
    └── test.sh               # verifier entrypoint
```

### task.toml (schema_version "1.4")

| Section | Fields | Notes |
|---|---|---|
| top | `schema_version` | e.g. `"1.4"` |
| `[task]` | `name, version, description, authors, keywords` | metadata |
| `[metadata]` | arbitrary | we put world_id, family, tier, difficulty, seed_db_sha256, tags here |
| `[verifier]` | `timeout_sec, network_mode, env, user`, `environment_mode = "separate"` opt | grading config |
| `[agent]` | `timeout_sec, network_mode, user` | agent phase |
| `[solution]` | `env` | oracle env vars |
| `[environment]` | `os, cpus, memory_mb, storage_mb, gpus, docker_image, network_mode, env` | container spec |

Gotcha (from blobfish-0 `scripts/export_harbor_agentic.py`): **omit `network_mode`
entirely** — harbor 0.17.1's local docker provider rejects `"no-network"` outright
(enforce-or-reject). Network isolation is instead achieved by simply not needing the network.

### Reward contract

The verifier (`tests/test.sh`) must write to `/logs/verifier/` (respect the
`VERIFIER_LOG_DIR` env override):

- `reward.txt` — single int/float, `1` pass / `0` fail (our default: binary), or
- `reward.json` — object of float metrics (harbor prefers this file if both exist).

```bash
LOGDIR="${VERIFIER_LOG_DIR:-/logs/verifier}"
python3 /tests/verify.py && echo 1 > "$LOGDIR/reward.txt" || echo 0 > "$LOGDIR/reward.txt"
```

Verifier modes: **shared** (default; runs in the agent's container, can inspect its state —
what we want for state-diff verification) vs **separate** (own image; must pre-bake `/tests/test.sh`).
Multi-step tasks exist (`[[steps]]` arrays) — useful later for dialogue/long-horizon families.

## The blobfish "agentic" export conventions (what we replicate)

blobfish-0's canonical per-task export (`scripts/export_harbor_agentic.py`) fills the spec like this:

- `environment/`: `Dockerfile`, `seed.db` (SQLite world state), `tools.py` (tool functions over
  `get_db()`), `tools_cli.py` (`list|call|replay`), `tool_schemas.json`. Baseline copy
  (`db_baseline.sqlite`) is made at setup for state-diff verification.
- `solution/`: `solve.sh` = `python3 /app/tools_cli.py replay "$SDIR/trace.json"`; `trace.json`
  is the teacher/oracle walk (ordered tool calls + args).
- `tests/`: `test.sh` + `verify.py` + `checks.json` — **multi-probe checks, ALL must pass**
  (single-probe verifiers were gamed; 468 tasks quarantined for it in blobfish-0).
- Instructions state: *"the database state is the answer; there is nothing to print or submit"*
  and **forbid raw SQL** (agent must use tools). For our QA-style tasks (answers, not writes),
  we need an answer-submission tool (e.g. `submit_answer`) so verification stays state-based.
- **Ship-honest admission rule**: a task ships ONLY if its teacher trace replays green through
  the verifier at export time; failures are gap-reported, never shipped. lawfirm-qwen enforced
  the same (231/231 reference walks pass).

## Two dialects — decision for finance-world

| | true Harbor (per-task dirs) | blobfish world-bundle dialect |
|---|---|---|
| Seen in | blobfish-0 `export_harbor_agentic.py`; harborframework.com spec | lawfirm-qwen `dist/harbor/` (`task.yaml` + `tasks/tasks.jsonl` + world image), website console jobs |
| Runs under `harbor run` | yes (verified 0.17.1) | no — needs the blobfish runtime |

**Decision: finance-world authors in the world-builder layout (packs → world.json → SQLite +
tool runtime) like lawfirm-qwen, but its exporter emits true per-task Harbor directories** so
`harbor run -p ... -a oracle` works out of the box. Do not copy the website-console
`task.yaml`/`verifiers/` dialect, partial-credit rewards, or committed `*.sqlite-wal/-shm` files.

## Sources

- https://harborframework.com/docs/tasks (task dir spec, task.toml fields, reward files, verifier modes)
- https://harborframework.com/docs/getting-started · https://harborframework.com/docs/core-concepts
- https://github.com/laude-institute/harbor (README; harness for Terminal-Bench 2.0)
- Local: `/Users/samuelchien/dev/blobfish-0/scripts/export_harbor_agentic.py` (canonical export, harbor 0.17.1 notes)
- Local: `/Users/samuelchien/dev/lawfirm-qwen/world/local/export_harbor.py` + `dist/harbor/` (bundle dialect)
