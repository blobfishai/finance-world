# AUDIT — harness bugs & verdict-integrity findings

Lawfirm precedent: exonerate the harness before trusting any score. Every finding here was
caught by audit-before-blame, not by taking failures at face value.

## World-correctness gate (`python3 sim/validate.py`)

Standing evidence that the world executes correctly — run it before trusting any model
score, and after any tool/schema change. 10 offline checks per task:
structure · metadata (incl. `walk_len`, which drives the turn budget) · every walk tool
exists in a server registry · **prompt↔verifier field agreement** (the A5 drift class) ·
required servers reachable in the oracle walk · seed tables exist in schema ·
`prepare()` determinism · oracle scores 1 · **idle run scores 0** (task isn't free) ·
**walk-without-submit scores 0** (no answer leakage via side effects).

**Status 2026-08-10: PASSED — 21/21 tasks, 10/10 checks each.**

### A5. `walk_len` metadata drift (found by the validator on its first run) — FIXED
`business_brief/brief-caterpillar` (8 vs 9) and `erp_qa/cash-disc-fourthcoffee-east`
(5 vs 6) understated their reference walk length. Not cosmetic: `sim/run_task.py` sets
`maxTurns = max(24, walk_len*3+6)`, so an understated value under-budgets the agent and
manufactures capability verdicts out of harness caps — exactly what the reference-relative
budget rule exists to prevent. Both corrected; the check now guards it permanently.

### A6. Two realism bugs found by tracing tasks end-to-end (`sim/show_traces.py`) — FIXED
1. **Invented duplicate vendor identity.** `vendor_master/missing-po-inquiry` seeded
   "Wingtip Logistics" onto SYNVEN-0011 — an account the master already used for another
   company — producing two similar Wingtips and an ambiguous lookup. Fixed to use the
   existing SYNVEN-0027 Wingtip Toys, plus a state check that the agent actually mailed
   the address on the vendor master. **Rule: task seeds may add entities, never silently
   repurpose an existing account's identity.**
2. **Phrase-only search.** `docs.search_documents("dunning collection")` returned zero
   matches because it required the phrase as a contiguous substring; the oracle only
   recovered by knowing the doc_id. Real search tokenizes, so both `docs.search_documents`
   and `email.messages_list` now require all terms in any order (with an any-term
   fallback). Before the fix, a model that searched sensibly would have been failed by
   the harness — a false capability verdict.

### A7. Ground truths and oracle answers could go stale together — FIXED (S11)
The cash layer (`world/etl/load_cash.py`) changed the ledger, and validation still passed
with every task green — because the oracle walk *submits a hardcoded answer* and the checks
compare against that same constant. Both were stale relative to the world:
`erp_qa/ap-overdue-usmf` expected **$81,262,127.02** when the ERP now says **$30,616,554.46**.
S8 (oracle scores 1) is structurally blind to this: it only proves the walk agrees with the
checks, not that either agrees with reality.
**Fix:** answer checks may now carry `gt_sql`, and validator check **S11** recomputes it
against the prepared world, failing on any drift. Verified by deliberately corrupting an
expected value — S11 caught it. Every core-derived truth now carries `gt_sql`.
**Rule:** if a task's answer is computable from world state, it must ship with `gt_sql`.
Side effect worth noting: the cash layer paid Fourth Coffee East's account to zero, which
would have silently turned a balance-lookup task into a "the answer is nothing" task. It
now seeds its own open invoices, so task truth no longer depends on ledger regeneration.

## 2026-08-10 — wave-0 calibration

### A1. Session-limit contamination (harness/account, 33/40 runs) — FIXED
First flake-scan batch overlapped a Claude subscription session limit: 33 runs died in ~3s
with `agent_error`, 0 tool calls, final text "You've hit your session limit". Under naive
triage this read as `sonnet solidFail 10/10` — a completely false verdict.
**Fix:** `sim/run_task.py` now detects infra failures (limit/rate/auth markers + 0 calls),
retries once after 20s, and labels surviving ones `trial-N.infra.json`; `sim/run_batch.py`
excludes infra trials from classification and resumes only them. Existing traces retagged.
**Rule reaffirmed:** a model verdict requires at least one non-infra trial; `infra_only`
tasks are unmeasured, not failed.

### A2. Raw KeyError on unknown ERP entity (realism gap, verdict upheld) — PATCHED 2026-08-10
Applied after the wave-0 batch completed (wave kept internally consistent): unknown entity
→ `{"error", "available_entities", "hint"}`; framework marks error payloads `ok:false`;
all 12 oracle walks re-verified green post-patch. Model reruns of affected tasks are
DEFERRED under the benchmark freeze (Sam, 2026-08-10: no benchmark runs until world
correctness is proven).
haiku (cross_system/email-invoice-meadow) guessed entity names ("Customer", "Account")
instead of calling `data_find_entity_type`, received bare `KeyError('Customer')` exceptions,
never recovered, and asserted `found_in_erp=no` without a single successful ERP query.
- The **fail verdict stands**: claiming ERP absence without a successful ERP check is the
  exact hallucination-adjacent behavior the task exists to catch (FinanceBenchmark's own
  relevance rubric agrees: tool failure ⇒ the claim fails).
- The **harness realism gap is ours**: a real MCP server returns an informative error, not a
  raw exception. Patch (applied after the wave-0 batch completes, to keep the wave
  internally consistent): unknown entity → structured `{"error": ..., "available_entities":
  [...]}`; framework marks any `{"error": ...}` payload `ok=false` in the trace so
  `required_servers` still demands one *successful* call. Recovery from an informative
  error is part of the skill under test; recovery from a stack trace is not.

### A3. FinanceBenchmark ground truths don't reconcile with their shipped data — DESIGN DECISION
During ETL validation, FB's published erp_qa GTs disagree with their own CSVs/journals
(e.g. "Group 90 >90-days past due" list: the named customers aren't in group 90 in the
shipped master data, and the GT amounts equal each customer's *total open balance*, not the
>90-day slice). Cause unknown (their live D365 sandbox likely diverged from the repo dump).
**Decision:** we adopt FB's scenarios and demo world but recompute every ground truth
in-world (`world/etl/load_core.py` prints a validation block on each build). No GT is ever
copied from FB prose.

### A5. Empty-answer traps are graded by exact string equality — **HARNESS BUG, false fails**
Found 2026-08-11 during the first full-roster sonnet flake scan, by audit-before-blame on
three fails that looked like model errors and were not.

`verifiers/vcode.py:67` grades a `type:"string"` check as `norm(got) != norm(expect)` —
exact equality after normalization. Our empty-answer traps (the FinanceBenchmark
hallucination-trap mechanic) are all authored as `{"type":"string","expect":"none"}`. So an
answer that is **correct and well-justified** is scored wrong the moment the model explains
itself:

| task | field | model answered | verdict |
|---|---|---|---|
| `cash_app/remittance-batch-mar02` | `dep503_invoices` | `none — no remittance advice on file for dep-503; the $4,000…` | FAIL (should pass) |
| `business_brief/brief-caterpillar` | `internal_ar_relationship` | `no existing relationship. checked three internal systems…` | FAIL (should pass) |
| `business_brief/brief-caterpillar-v2` | `internal_relationship` | `none. caterpillar has no active account in either the erp cu…` | FAIL (should pass) |

The trap intends to catch **invented** invoices/relationships. It instead catches
**prose**. Both brief-caterpillar tasks were consequently mislabelled `flaky` when the
model's answers were right on the merits; `cash_app` was mislabelled `solidFail` on one of
its three trials for this reason (its other two trials failed for real reasons — a
`no_reads_before_submit` and a missing successful ERP call — so the task keeps genuine
signal).

**Fix (deferred until the in-flight scan completes, to keep the wave internally
consistent):** replace exact-match empty-answer traps with a dedicated `none_answer` check
that is both more forgiving *and* strictly stronger:
- PASS if the value's leading token is a negative (`none`/`no`/`n/a`/`nil`/`zero`/`not
  found`/`no …` ), allowing any trailing justification;
- FAIL if the value contains any token from an explicit `forbid` list (invoice-ID patterns,
  customer accounts, amounts) — i.e. the anti-hallucination half becomes an *assertion*
  rather than a side effect of string equality.

**Consequence for calibration:** every `too_hard`/`flaky` label derived from an
`expect:"none"` string check is provisional until the affected tasks are re-run under the
fixed verifier. Recorded here so the labels are not read as model verdicts.

**RESOLVED 2026-08-11.** `none_answer` implemented in `verifiers/vcode.py` (opens-with-a-
negative + an explicit `forbid` list that asserts no real record was named); all **14** tasks
carrying the old trap converted. The stored run directories were then re-verified — the runs
are unchanged, only the verifier is — and the corrected labels are *worse* for us, not better:

| task | old label | corrected | reading |
|---|---|---|---|
| `business_brief/brief-caterpillar` | flaky (0,1,1) | **1,1,1 too_easy** | the flakiness was entirely our bug |
| `business_brief/brief-caterpillar-v2` | flaky (0,1,0) | **1,1,1 too_easy** | the escalated v2 was never harder |
| `cash_app/remittance-batch-mar02` | too_hard (0,0,0) | **1,0,0 flaky** | genuine frontier task |

Two of the three tasks that looked like the frontier were false-flaky. The lesson is the
house rule stated backwards: audit-before-blame protects the *model* from our bugs, and
without it we would have shipped a difficulty claim that the data does not support. The one
task that survived (`cash_app`) is now the only confirmed in_band task in the world, and its
two real failures are both anti-hack vetoes firing correctly — a submit with no reads, and an
assertion of ERP absence without a successful ERP query.

### A6. Rebuilding the world with `load_core.py` alone silently destroys it — FIXED
Hit 2026-08-11 while adding the write-surface schema. `world/etl/load_core.py` drops and
recreates `core.sqlite`, and the world is built by **three** modules in a load-bearing order
(`load_core` → `load_cash` → `load_demo`; the cash layer's own docstring states it). Running
only the first left a ledger with **zero payments**, so nothing settled and every open
balance inflated ~2.4–2.7×:

| task | GT expects | broken build said |
|---|---|---|
| `erp_qa/ap-overdue-usmf` | 30,616,554.46 | 81,262,127.02 |
| `erp_qa/ar-balance-fourthcoffee-east` | 121,321.26 | 293,390.17 |

Two things worked exactly as designed and are worth keeping: `sim/validate.py`'s **S11
ground-truth freshness check** caught it immediately and named the drifted fields, and
`world/build/` is gitignored, so the broken artifact could never have been committed.

**Fix:** `world/build.sh` is now the only supported build entrypoint — it runs the three
stages in order and finishes by running the validation gate. Nothing calls `load_core.py`
directly any more. The cash layer is seeded (`random.Random(SEED)`), so the build is
reproducible and the ground truths re-derive exactly.

### A7. Calibration traces outlived the world they measured — INVALIDATED
Found 2026-08-11 while re-grading stored trials after the A5 verifier fix.

`traces/sonnet/erp_qa/ap-overdue-usmf/trial-1` (2026-08-10) records the model answering
**$81,262,127.02** and being graded **reward=1**. That figure is the *pre-cash-layer* AP
total: the run predates `world/etl/load_cash.py` (commit 828b13e), which added payments and
settlements and moved the same figure to ~$30.6M. The verdict was correct **against the
world of the day** and is meaningless against the world we ship.

Two mechanisms hid this:
1. `run_batch.py`'s resume rule re-runs a trial only when it has **no trace or an
   infra-tainted one** — a *stale* trace looks exactly like a good one, so a rescan
   preserves it forever.
2. Re-grading stored runs (`sim/reverify.py`) cannot fix it either: the run's own
   `world.sqlite` is the old world, so re-verification just re-measures the old answer
   against the new ground truth and reports a failure that never happened.

**Rule adopted:** a trace is valid only if it was recorded against the *current* world
build. Trials older than `world/build/core.sqlite` are archived, not re-graded — 191 of them
moved to `traces_archive/pre-2026-08-11-rebuild/` — and re-run from scratch.

`sim/reverify.py` remains the right tool for the narrower case it was written for (the
verifier changed, the world did not); it must never be used across a world rebuild.

**Consequence:** the "sonnet passes 12/12" reading recorded earlier in this session drew on
Aug-10 traces and does not stand. Difficulty claims wait for the fresh scan.

### A4. `--max-turns` not strictly enforced by observed runs — WATCH
haiku's ap-overdue run recorded `num_turns=36` against `--max-turns 24`. Budget overruns
currently can't masquerade as passes (verification is answer-based), but turn accounting
must be understood before budget-based failure labels (`budget_exhausted`) are trusted.
UNRESOLVED — investigate whether the CLI counts turns differently than the flag.
