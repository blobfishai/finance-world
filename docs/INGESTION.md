# Ingestion — turning a GitHub repo into runnable world content

> Written 2026-08-11 after porting three corpora by hand (FinanceBenchmark clones,
> TheAgentCompany finance, plus mechanism extraction from ERP-Bench/τ-bench/TAT-QA) and
> measuring the result: **39 of 563 agentic source tasks run here** (`docs/PARITY.md`).
>
> One-off porting does not compose. This is the repeatable pipeline, and it is designed
> around the failure modes the hand ports actually produced — every stage below exists
> because something went wrong without it.

## The five porting classes

A corpus is not "portable" or "not". Classifying it correctly is the first decision, because
each class needs a different pipeline and a different honesty claim.

| class | means | example | what we emit |
|---|---|---|---|
| `verbatim_gt` | source ships question **and** checkable ground truth | FinanceBenchmark `erp_qa` (100) | question verbatim, GT **recomputed in-world** |
| `recomputable` | question is factual; GT derivable from data we can hold | FB `finance_qa` single-figure items | GT computed from a frozen filings snapshot |
| `judgement_port` | the judgement ports; the artefacts/plumbing do not | TheAgentCompany finance (12) | re-authored onto our surface, source cited |
| `needs_surface` | requires a tool surface the world lacks | ERP-Bench (300, Odoo) | blocked, with the named surface |
| `not_agentic` | static text/table QA, no tools | FinQA, ConvFinQA, TAT-QA, SECQUE | **mechanisms only** — porting would change what it measures |

Rule: a corpus is never silently skipped. It is classified, and the class is the reason.

## The pipeline

```
repo ──▶ 1 survey ──▶ 2 classify ──▶ 3 extract ──▶ 4 bind ──▶ 5 emit ──▶ 6 gate ──▶ 7 ledger
                                      (TaskSpec)   (world)    (Harbor)   (admit)   (parity)
```

### 1 · Survey
Count what the repo actually ships (items, splits, licence), not what its README claims.
Documentation drift is real and sourced: `mcp-erp` registers 79 tools while its README says 44
(`research/erp-mcp-tool-census.md`).

### 2 · Classify
Assign one of the five classes per **item**, not per repo — FB's own `finance_qa` mixes
single-figure questions (`recomputable`) with open analytical prompts that only an LLM judge
can score (`not_agentic` for our purposes).

### 3 · Extract → TaskSpec
One normalised record per source item (`ingest/ir.py`). Adapters are the only per-corpus code;
everything downstream is shared. A TaskSpec carries:

- `source` — repo, path, item id, licence *(provenance is not optional)*
- `question` — verbatim where the corpus is the eval
- `entities` — every named entity the question depends on
- `capabilities` — servers/tables the answer requires
- `ground_truth` — per field: type, `gt_sql` or derivation, tolerance, `forbid`
- `naive_baseline` — the shortcut a practitioner runs, and what it yields
- `dropped` — what the port deliberately does not carry, and why

### 4 · Bind — **strict**
Resolve every `entities` and `capabilities` reference against the live world
(`ingest/capability.py` reads the built DB, the server registries and the seeded filings).

Binding has exactly three outcomes, and **fuzzy rebinding is not one of them**:

| outcome | when | action |
|---|---|---|
| `bound` | entity and capability exist | proceed |
| `absent_entity` | question names something the world does not have | emit as an **empty-answer trap**, or reject — never rebind |
| `missing_capability` | needs a table/tool we lack | reject to the capability backlog, naming what to build |

*This stage exists because of `docs/AUDIT.md` A10.3*: the FB cloner fuzzy-matched a question
about "Contoso Retail San Diego" — absent from the world — onto "Contoso Retail" and pinned
ground truth to the wrong account. A model that answered "none" was scored wrong. Strict
binding makes that outcome impossible to reach silently.

### 5 · Emit — one template context
`instruction.md`, `environment/seed/*`, `solution/walk.json` and `tests/checks.json` all render
from the **same** TaskSpec object. No number may appear in an instruction that is not traceable
to it. *(ERP-Bench's anti-drift mechanism, `research/erp-bench-deep-dive.md`; round-2 ledger
row 36.)*

### 6 · Gate — admission, all must hold
| gate | catches | origin |
|---|---|---|
| oracle replays green | the task is unsolvable as authored | existing rule |
| every `gt_sql` re-derives from the built world | ground truth that drifted from the ledger | A7 / S11 |
| naive ≠ graded | tasks solvable by the shortcut | S12, ERP-Bench objective certification |
| **prompt/verifier type agreement** | instruction says *(text)* while the check grades polarity | **A10.2 — S4 checks only that a field is mentioned** |
| no ground-truth leak | the answer readable off disk or via a tool | round-2 row 39 |
| nop scores 0 | task passable by doing nothing | export gate |

### 7 · Ledger
`docs/PARITY.md` is **generated**, never asserted: per corpus, emitted / rejected-with-reason /
blocked-on-capability. A blocked item names the capability, so the backlog is a build list
rather than a shrug.

## What this fixes that hand-porting did not

| hand-port failure | stage that prevents it |
|---|---|
| question rebound to a near-neighbour entity (A10.3) | 4 · strict bind |
| grader changed without re-reading the instruction (A10.2) | 6 · type-agreement gate |
| ground truth copied from source prose (A3) | 3 · GT is `gt_sql`/derivation, never a literal from the source |
| a stated figure that does not re-derive (TAC port, 726.30 vs 725.90) | 5 · one template context |
| corpora silently at zero | 2 · classify — every item ends in a class with a reason |

## Adding a corpus

1. Write `ingest/adapters/<corpus>.py` emitting TaskSpecs. That is the only new code.
2. Run the survey; read the classification split before writing any task.
3. Fix what binding rejects — usually a capability, occasionally the adapter.
4. Emit, gate, and let the ledger move.

The adapter is the contract. If a corpus cannot be expressed as TaskSpecs, that is the finding,
and it belongs in the ledger as a class — not as silence.
