# LedgerBench-100 v3.0.0 — release evidence

LedgerBench-100 is a first-party benchmark for realistic accounting and finance
work over an isolated enterprise sandbox. The release contains 100 high-level
employee requests, 100 task-specific causal workflows, Harbor 1.4 packs, a
Hugging Face dataset tree, deterministic verifiers, inspectable native evidence,
and measured trajectories.

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

Every task now has:

- one explicitly authored decision specification with a unique employee
  question, supported condition, decision code, causal analysis route, and
  rejected shortcut;
- 19–24 required context reads distributed across Dynamics 365 Finance,
  Gmail-shaped mail, governed documents, Microsoft Graph workbooks, the source
  finance systems, and task-specific operational records;
- a 30–132 call reference workflow, with 100 distinct raw tool-name sequences
  and 100 distinct semantic action graphs;
- a governed `FinanceCases` transition through the generic Dynamics data/action
  surface, followed by an exact state readback;
- a scoped completion email followed by reopening the exact sent thread;
- exact answer, final-state, evidence-reference, audit-row, read-before-write,
  successful-call, readback, ordering, and write-containment checks;
- three visible decision options: the supported branch plus two plausible but
  rejected alternatives;
- 28 agent-visible evidence assets that never contain the gold answer, verifier
  checks, or oracle recipe.

The ERP surface intentionally does not expose fake convenience tools such as
`approve_invoice`. The governed case transition is discovered through the same
generic entity metadata, entity query, action discovery, and action invocation
shape used by Dynamics-style integrations.

## Asset room

The release contains 2,800 generated task assets, all 2,800 with distinct SHA-256
content. Native parsing passed for every file.

| Format | Files |
|---|---:|
| Markdown | 800 |
| JSON | 600 |
| EML | 500 |
| CSV | 400 |
| PDF | 200 |
| XLSX | 200 |
| TXT | 100 |

The assets include current and superseded controls, five-message mail histories,
two real XLSX workbooks, controlled PDFs, master and transaction extracts,
approval records, source inventories, and lineage notes. Current records and
stale hypotheses are deliberately separated so an agent must establish identity,
effective revision, and source authority rather than match filenames or copy a
precomputed result.

Measured asset gates:

- 2,800/2,800 native assets parsed;
- 2,800/2,800 unique content digests;
- zero gold-answer or oracle-recipe leakage hits;
- exactly 28 assets for each of 100 tasks.

## Deterministic qualification

`benchmark/ledgerbench100/run_suite.py` executed 1,200 episodes against the
contents of the newly built packs.

| Gate | Executions | Result |
|---|---:|---:|
| Oracle replay | 100 | 100 passed |
| Exact deterministic replay | 100 | 100 byte-identical reports |
| No-op | 100 | 0 false accepts |
| Copied shortcut | 100 | 0 false accepts |
| State-only write | 100 | 0 false accepts |
| Missing required evidence read | 100 | 0 false accepts |
| Write before investigation | 100 | 0 false accepts |
| Missing post-write readback | 100 | 0 false accepts |
| Unauthorized off-task write | 100 | 0 false accepts |
| Wrong reported value | 100 | 0 false accepts |
| Unsupported decision branch | 100 | 0 false accepts |
| Wrong persisted evidence | 100 | 0 false accepts |

The incomplete-read control initially found one bad adversarial construction on
task 57: it removed the first occurrence of a discovery call that legitimately
appeared twice, leaving the investigation complete. The control now removes a
uniquely satisfying evidence request, has a regression test, and rejects all
100 tasks. The release was rebuilt from scratch and the full 1,200-run suite was
then rerun.

## Measured build results

| Measure | Result |
|---|---:|
| Tasks / families | 100 / 22 |
| Authored decision specifications | 100 |
| Raw reference sequences | 100 unique |
| Maximum raw sequence similarity | 0.956522 |
| Semantic action graphs | 100 unique |
| Maximum semantic graph similarity | 0.727273 |
| Prompt duplicates | 0 |
| Maximum prompt 5-shingle Jaccard | 0.635135 |
| Required evidence reads | 19 min / 21 median / 24 max |
| Reference calls | 30 min / 34 median / 132 max |
| Total reference calls | 4,334 |
| Deterministic checks | 2,055 |
| Answer / trace / state checks | 434 / 857 / 764 |
| Exact governed case transitions | 100 |
| Tasks with both post-write readbacks | 100 |
| MCP servers / tools | 8 / 66 |

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
manifest. `run_suite.py` performs the 1,200 executions. `hf_export.py` rebuilds
the public dataset records and assets, checks similarity and leakage, and seals a
content manifest. Self-replay bytecode caches are removed from the release tree
and excluded from the manifest.

## Publication and leaderboard honesty

The repository evidence above covers deterministic local qualification. Harbor
registry publication, Hugging Face upload, a full 100-task containerized Harbor
run, and full real-model leaderboard trials are separate release steps. They must
not appear as published links or leaderboard scores until their jobs complete
and their downloaded artifacts round-trip exactly. Partial historical runs are
not valid V3 leaderboard rows.

The generated `dist/` tree is intentionally gitignored. The committed generator,
catalog, decision specifications, tests, and measured reports are sufficient to
reproduce it. World data is synthetic except for frozen public SEC filing facts;
the verifier requires in-world evidence reads even when a public financial fact
might be present in model pretraining.
