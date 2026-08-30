# LedgerBench-100 v3.3.0 — release evidence

LedgerBench-100 is a first-party benchmark for realistic accounting and finance
work over an isolated enterprise sandbox. The release contains 100 high-level
employee requests, 100 task-specific causal workflows, a graded control-date
decision model in every task, Harbor 1.4 packs, a Hugging Face dataset tree,
deterministic verifiers, inspectable native evidence, and measured trajectories.

- Harbor dataset: `blobfishai/ledgerbench-100`
- Task names: `blobfishai/lgr100-NNN-<slug>`
- Generated release: `dist/ledgerbench-100/`
- Committed release evidence: `benchmark/ledgerbench100/reports/`
- Data license: CC BY 4.0
- Code license: Apache-2.0

## Realism contract

V3 does not turn the employee request into a checklist. Each prompt asks for a
business outcome and gives the agent room to determine how to investigate it.
The hidden deterministic contract tests whether the agent actually established
the facts needed for that outcome.

V3.3 adds a graded reasoning chain to every task
(`benchmark/ledgerbench100/decision_model.py`). Each case now carries:

- a control requirement derived by summing the ERP's in-scope `FinanceCaseLines`
  documents — never read off a header (graded: `control_requirement_usd`);
- coverage reconciliation on the current evidence register with exclusions the
  counterparty's own message corroborates (graded: `observed_support_usd`,
  `excluded_support_usd`, `usable_support_usd`);
- the exception netted against the policy tolerance (graded: `exception_usd`,
  `exception_within_tolerance`);
- an external constraint from the counterparty's committed correction date and
  documented holding charge (graded: `external_constraint_date`);
- an internal constraint from the close calendar's posting window and lead times
  (graded: `posting_window_close_date`);
- three costed timing alternatives, each with an exact outcome date, an
  incremental cost, and an authority status — one recommended, one requiring a
  CFO exception beyond current authority, and one feasible-but-inferior or
  unsupported-by-current-evidence; every option outcome is graded as its own
  answer field;
- a recommendation compared with the requester's documented need-by date into a
  signed day variance and an honest timing status (graded: `business_need_date`,
  `outcome_vs_control_days`, `decision_timing_status`);
- an approved Dynamics approval request applied to the selected scope while the
  pending exception request must stay untouched (graded: `approval_request_id`
  with a look-alike forbid, `approval_authority_limit_usd`,
  `escalation_approval_required`, plus the `exception_request_untouched` state
  assertion);
- the selected option, outcome date and binding constraint persisted in the
  governed case rationale and graded again in the Controls completion email's
  body.

Every task also keeps the v3 contract: an explicitly authored decision
specification, 28–38 required context reads across the eight
provider surfaces, a governed `FinanceCases` transition with an exact state
readback, provider-native post-write readbacks, a scoped completion email with
thread reopening, and writes-only containment. A FY2025 look-alike case and a
pending exception approval are seeded as identity decoys; both are graded with
`forbid` lists.

## Measured build results

| Measure | Result |
|---|---:|
| Tasks / families | 100 / 22 |
| Authored decision specifications | 100 |
| Graded decision models | 100/100 |
| Fully qualified costed alternatives | 100/100 |
| Graded answer fields per task | 24 min / 27 median / 30 max |
| Graded numeric derivations per task | 9 min / 11 median / 16 max |
| Raw reference sequences | 100 unique |
| Maximum raw sequence similarity | 0.972222 |
| Semantic action graphs | 100 unique |
| Maximum semantic graph similarity | 0.777778 |
| Prompt duplicates | 0 |
| Maximum prompt 5-shingle Jaccard | 0.678571 |
| Required evidence reads | 28 min / 31 median / 38 max |
| Reference calls | 38 min / 42 median / 153 max |
| Total reference calls | 5,279 |
| Deterministic checks | 6,214 |
| Answer / trace / state checks | 2,634 / 2,616 / 964 |
| Public criteria per task | 82 min / 85 median / 89 max |
| Exact governed case transitions | 100 |
| Tasks with all contracted post-write readbacks | 100 |
| MCP servers / tools | 8 / 66 |

## Asset room

The release contains 3,000 generated task
assets (30 per task, exactly
14 marked
decision-material), all with distinct SHA-256 content; native parsing passed for
every file and zero gold-answer or oracle-recipe leakage hits were found.

| Format | Files |
|---|---:|
| MD | 900 |
| EML | 600 |
| JSON | 600 |
| CSV | 400 |
| PDF | 200 |
| XLSX | 200 |
| TXT | 100 |

## Deterministic qualification

`benchmark/ledgerbench100/run_suite.py` executed 1,400 episodes
against the contents of the newly built packs.

| Gate | Executions | Result |
|---|---:|---:|
| Oracle replay | 100 | 100 passed |
| Exact deterministic replay | 100 | 100 byte-identical reports |
| Missing required evidence read | 100 | 0 false accepts |
| Missing post-write readback | 100 | 0 false accepts |
| No-op | 100 | 0 false accepts |
| Rejected state-changing request | 100 | 0 false accepts |
| Copied shortcut | 100 | 0 false accepts |
| State-only write | 100 | 0 false accepts |
| Unauthorized off-task write | 100 | 0 false accepts |
| Write before investigation | 100 | 0 false accepts |
| Unsupported decision branch | 100 | 0 false accepts |
| Wrong persisted evidence | 100 | 0 false accepts |
| Unauthorized timing option executed | 100 | 0 false accepts |
| Wrong reported value | 100 | 0 false accepts |

The new `wrong_option` control executes the alternative that requires approval
beyond current authority — recording it on the case, in the Controls note and in
the reported recommendation — and must score 0 on every task.

## Reproduce locally

```bash
./world/build.sh
PYTHONPATH=benchmark/ledgerbench100 \
  python3 -m unittest benchmark.ledgerbench100.tests.test_realism -v
python3 benchmark/ledgerbench100/exporter.py
python3 benchmark/ledgerbench100/run_suite.py
python3 benchmark/ledgerbench100/hf_export.py
```

`exporter.py` self-replays every task before emitting the Harbor dataset
manifest. `run_suite.py` performs the 1,400 executions.
`hf_export.py` rebuilds the public dataset records and assets, checks similarity
and leakage, and seals a content manifest. Self-replay bytecode caches are
removed from the release tree and excluded from the manifest.

## Publication and leaderboard honesty

The repository evidence above covers deterministic local qualification. Harbor
registry publication, Hugging Face upload, a full 100-task containerized Harbor
run, and full real-model leaderboard trials are separate release steps. They must
not appear as published links or leaderboard scores until their jobs complete
and their downloaded artifacts round-trip exactly. Partial historical runs are
not valid V3.3 leaderboard rows.

The generated `dist/` tree is intentionally gitignored. The committed generator,
catalog, decision specifications, decision model, tests, and measured reports are
sufficient to reproduce it. World data is synthetic except for frozen public SEC
filing facts; the verifier requires in-world evidence reads even when a public
financial fact might be present in model pretraining.
