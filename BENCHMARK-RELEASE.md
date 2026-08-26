# LedgerBench-100 — release notes

First-party Blobfish benchmark release built from this repository's finance world, to
CounselBench-100 parity (Harbor 1.4 packs + Harbor dataset manifest + Hugging Face tree +
executed qualification suite). Built on branch `bench/ledgerbench-100-release`.

- Benchmark: **LedgerBench-100** v1.0.0
- Harbor dataset: `blobfishai/ledgerbench-100` (100 tasks, `blobfishai/lgr100-NNN-<slug>`)
- Release tree: `dist/ledgerbench-100/` (generated output, gitignored like every `dist/`;
  the committed evidence lives in `benchmark/ledgerbench100/reports/` and the whole tree
  reproduces deterministically from the commands below)

## What was built

1. **Curation** (`benchmark/ledgerbench100/curate.py`, committed `catalog.json`)
   - Pool: the 478 ported/hand-authored + 30 escalated-variant tasks. The 1,026
     `erp_qa_gen` template instances are excluded wholesale (the repo's own PARITY
     discipline).
   - Every one of the 508 candidates was **oracle-replayed at HEAD** in this session
     (prepare → in-process MCP replay → vcode verify): **508/508 reward 1**.
   - Selection: all 18 operational families in full (80 tasks after dropping the two
     multi-step tasks `close_mgmt/two-period-close-cesq` and
     `finance_qa/xom-current-assets-followup`, excluded to keep a uniform single-step
     contract), plus a deterministic hand-picked slice of the four corpus-port families
     (erpbench 10, erp_qa_fb 5, business_brief_fb 3, finance_qa_fb 2) preferring
     write-layer grading, harder difficulty, longer walks. 22 families covered.

2. **Harbor packs** (`benchmark/ledgerbench100/exporter.py` + `runtime/server.py`)
   - Self-contained schema-1.4 packs: prepared per-task `world.sqlite` (core world +
     task seed layers, gzipped with mtime pinned to 0), the 8 MCP servers + framework +
     `vcode.py` verifier baked into a **separate `world` container** on the digest-pinned
     public base `python:3.12-slim@sha256:7a8b4750…` (the exact digest CounselBench-100
     proved pullable). No private registry anywhere.
   - The world container serves the 8 servers over per-server **Streamable HTTP**
     (`http://world:8974/mcp/<server>`), declared as 8 `[[environment.mcp_servers]]`
     entries, plus `GET /health` and a **token-gated `POST /verify`**:
     `verification_token(task_id) = sha256("LedgerBench-100 verifier capability::" + task_id)`;
     the world image holds only the token's sha256 digest; the agent container never sees
     the token (it exists only in `tests/test.sh`, which Harbor copies in after the agent
     finishes). Answer keys (`checks.json`, `walk.json`) live only in the world image /
     solution dir — never in the agent container.
   - `solution/solve.py` replays the exact oracle walk **over the live MCP surface**;
     `tests/test.sh` POSTs `/verify` and writes `$VERIFIER_LOG_DIR` (or
     `$HARBOR_LOGS/verifier`) `report.json`, `reward.json`, `reward.txt`, and prints
     `{"passed": …, "reward": …}`.
   - **Export gate** (kept from `sim/export_harbor.py`): every pack must replay its own
     oracle from its own contents and score reward 1 before it ships — **100/100 passed**.
   - **Release hardening**: the 10 erpbench packs' authoring checks carried no
     `writes_only` veto; the exporter adds one (allowed = `answers` + the 13-table
     `erpb_*` Odoo surface) so the off-task-write control is sound on every task. No
     other check was touched.
   - `harbor/dataset/dataset.toml`: 100 `[[tasks]]` entries with sha256 content digests
     computed by the exact harbor-0.21 `Packager.compute_content_hash` algorithm.

3. **Hugging Face tree** (`benchmark/ledgerbench100/hf_export.py`) —
   `dist/ledgerbench-100/huggingface/`: `data/tasks.jsonl` (apex-accounting-compatible
   fields incl. `rubric` = the graded checks, `gold_output` = submit_answer payload +
   expected state assertions, `metadata.grading = "deterministic"`,
   `metadata.llm_judge = false`), per-task JSON, `task_files/` context documents,
   `world/` source (framework, 8 servers, verifier, HTTP bridge, full SQL schema),
   `trajectories/` (one normalized oracle JSONL per task), `reports/`, measured README
   dataset card, LICENSE-CODE (Apache-2.0), LICENSE-DATA (CC BY 4.0), and a sealed
   `release-manifest.json` (sha256 per file).

## Measured results (all executed in this session)

**Qualification suite** (`benchmark/ledgerbench100/run_suite.py`, 600 executions against
pack contents only — committed at `benchmark/ledgerbench100/reports/qualification.json`):

| Gate | Result |
|---|---:|
| Oracle replay (per pack) | **100/100 reward 1.0** |
| Determinism (second replay, byte-identical verifier report) | **100/100 exact matches** |
| Negative: `noop` (pristine world, zero calls) | 0/100 false accepts |
| Negative: `no_submit` (walk minus every submit_answer) | 0/100 false accepts |
| Negative: `wrong_submit` (every submitted value corrupted) | 0/100 false accepts |
| Negative: `off_task_write` (full walk + one off-task table write) | 0/100 false accepts (writes_only veto) |

**Dockerized Harbor probes** (harbor CLI 0.21.0, run from `~/.cache/bf-audit/ledgerbench/`,
results committed under `benchmark/ledgerbench100/reports/harbor-probes/`):

- `lgr100-001-duplicate-payment-mar` (QA-style task): `harbor run -a oracle` → 1 trial,
  0 exceptions, **reward 1.0**; verifier `report.json`/`reward.json`/`reward.txt` written.
- `lgr100-051-2147-hard-15-parallel-subassemblies-branch-assigned` (erpbench write task,
  99-step walk, augmented veto): 1 trial, 0 exceptions, **reward 1.0**.
- `lgr100-034-cash-disc-fourthcoffee-east` (inputs bind-mount compose variant): 1 trial,
  0 exceptions, **reward 1.0**.
- Five more stratified probes — `lgr100-003` (buried-decoy variant), `lgr100-008`
  (business brief), `lgr100-021` (cross-system tieout), `lgr100-063` (SEC filings
  surface), `lgr100-080` (payment-run commit) — each 1 trial, 0 exceptions,
  **reward 1.0**. Total: **8/8 Dockerized oracle trials passed**.

**Reproducibility**: re-exporting a pack produces a byte-identical content digest
(verified on `lgr100-001`: `f2e5df84…` before and after). World build is fully offline
(`fetch_filings.py --load` reads committed EDGAR snapshots).

**Build stats** (`reports/build.json`, all measured): 100 tasks / 22 families; oracle
walks min 3 / median 6 / max 104 MCP calls (1,515 total); 434 answer + 257 trace + 264
state = 955 graded checks; 8 MCP servers / 66 tools; 59 seeded context files across 47
tasks; release tree 208 MB.

## Reproduce

```bash
git checkout bench/ledgerbench-100-release
./world/build.sh                                   # offline; committed snapshots only
python3 sim/validate.py                            # full 10-check world gate (slow)
python3 benchmark/ledgerbench100/curate.py <scan.json>   # optional: re-derive catalog.json
python3 benchmark/ledgerbench100/exporter.py       # 100 gated packs + dataset.toml
python3 benchmark/ledgerbench100/run_suite.py      # 600 executions; writes qualification.json
python3 benchmark/ledgerbench100/hf_export.py      # HF tree + README + release manifest

# Dockerized probe (run from a $HOME-mounted dir; /private/tmp is empty under Colima)
mkdir -p ~/.cache/bf-audit/ledgerbench && cp -R dist/ledgerbench-100/harbor/tasks/lgr100-001-* ~/.cache/bf-audit/ledgerbench/
cd ~/.cache/bf-audit/ledgerbench && harbor run -p lgr100-001-duplicate-payment-mar -a oracle
```

`curate.py`'s scan input is produced by replaying all 508 candidates (the session used a
scratch script equivalent to validate.py's S8 step); `catalog.json` is committed, so the
scan is only needed to re-derive the selection.

## Honest caveats

- **`dist/` is generated, not committed** (repo-wide `dist/` gitignore, same policy as
  the CounselBench-100 reference, whose release files are intentionally git-ignored).
  What IS committed: the full generator, `catalog.json`, and the evidence set
  (`dataset.toml` with all 100 digests, `qualification.json`, `build.json`,
  `release-manifest.json`, harbor probe results) under `benchmark/ledgerbench100/`.
- **Docker was probed on 8 of 100 packs, 8/8 reward 1.0** (covering every
  container-topology variant — plain, erpbench/augmented-veto, inputs bind-mount — and
  every surface family style: QA, buried-decoy variant, cross-system, filings, brief,
  ERP write, Odoo write). The other 92 were verified in-process
  from pack contents (6 executions each), not inside containers. A 100/100 Dockerized
  sweep (CounselBench's bar) was not run — ~100 × 1 min of docker builds on a
  disk-constrained machine.
- **No real-model trials in this session.** CounselBench-100 shipped 10 stratified model
  trials; LedgerBench-100 has none yet. Historical model evidence (deepseek-v4-pro over
  83 authoring tasks, 77% pass) is from the authoring repo's earlier calibration, not
  from these packs, and is not claimed for this release.
- **25 prompt texts appear twice by design**: the `doc_mode="buried"` escalated variants
  reuse their base task's persona message against a harder world (decoy documents; same
  ground truth, different required search). Documented in the dataset card. If you want
  100 distinct prompts, filter `provenance = "variant"`.
- **erpbench veto is an export-time augmentation**, not authored upstream: the 10
  erpbench packs' `writes_only` (answers + `erpb_*`) exists only in the packed
  `checks.json`. The authoring repo remains unchanged.
- **Two multi-step tasks were excluded** rather than packaged (uniform single-step
  release); Harbor `[[steps]]` support in this pack format is untested.
- **The `filings` surface serves real SEC XBRL facts** (38 registrants, frozen
  snapshots) — real public-domain data inside an otherwise synthetic world; flagged in
  the dataset card. Financial questions on TSLA/WMT/XOM etc. could in principle be
  answered from a model's pretraining rather than tool use, but trace checks still
  require successful in-world server reads before submission.
- **Nothing was published**: no `harbor publish`, no HF upload, no push. The dataset.toml
  digests use harbor 0.21's algorithm but have not been round-tripped against the live
  registry. The `[[environment.mcp_servers]]` entries parse under harbor 0.21 and the
  oracle probes pass with them, but no MCP-native agent (e.g. claude-code) has been run
  against the live declarations.
- `submit_answer` stamps a wall-clock `submitted_at` into the answers table; it is never
  read by the verifier (reports are byte-identical across replays), but the post-run DB
  is not bit-identical between runs.
- The full `sim/validate.py` world gate at HEAD was re-run in this session and PASSED:
  **1,534 tasks, 10/10 checks each** (structure, metadata, tool existence, contract
  drift, seeds, prepare determinism, oracle green, idle-run negative, no-submit
  negative, ground-truth freshness). Two earlier attempts died of disk-full conditions:
  the first from a scratch-dir leak in validate.py itself (fixed on this branch), the
  second from transient disk pressure caused by concurrent sessions on this machine.
