# AUDIT — harness bugs & verdict-integrity findings

Lawfirm precedent: exonerate the harness before trusting any score. Every finding here was
caught by audit-before-blame, not by taking failures at face value.

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

### A2. Raw KeyError on unknown ERP entity (realism gap, verdict upheld) — PATCH QUEUED
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
