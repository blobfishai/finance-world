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

### A4. `--max-turns` not strictly enforced by observed runs — WATCH
haiku's ap-overdue run recorded `num_turns=36` against `--max-turns 24`. Budget overruns
currently can't masquerade as passes (verification is answer-based), but turn accounting
must be understood before budget-based failure labels (`budget_exhausted`) are trusted.
UNRESOLVED — investigate whether the CLI counts turns differently than the flag.
