# Hard-layer design — the escalation contract

> Written 2026-08-11 after the first full-roster flake scan showed **sonnet passing 12/12
> calibrated tasks on every trial** (`traces/sonnet/`). Under the house triage rule that is
> `too_easy` across the board: the shipped world is calibrated below the frontier model's
> ceiling. This document is the contract for the layer that fixes that.
>
> Every mechanic below is **sourced** — from the wave-2 corpus (`research/erp-bench-deep-dive.md`,
> `research/odoo-domain.md`, `research/erp-mcp-tool-census.md`, `research/erp-workflow-automation.md`,
> `research/finben-and-agent-evals.md`) and the round-2 ledger (`research/questions-round2.md`).
> No invented realism. Each mechanic names the row it answers.

## The problem, stated precisely

| Evidence | Reading |
|---|---|
| sonnet: 12/12 tasks, 24/24 trials pass | the world does not measure the frontier |
| 37 of 58 tasks have walk depth ≤ 4 | the tool-graph is shallow |
| 58/58 tasks `acceptance_label = pending_calibration` | nothing was ever labelled |
| all 15 families are read-and-reconcile | the world tests *lookup*, not *operation* |

A world that a frontier model passes 100% of the time cannot rank models, cannot show
headroom, and cannot be sold as a measurement instrument. The fix is not "more tasks like
these" — it is **new mechanics that fail for structural reasons**.

## The seven hard mechanics

### M1 — Write-and-approve (round-2 Q19)
The largest structural gap. Every shipping ERP automation in the corpus is write-and-approve
gated by an explicit human confirmation step; all 15 of our families are read-only.

New families: `journal_entry` · `approval_queue` · `ap_invoice_entry` · `po_create` ·
`batch_job_ops` · `confirm_gate` · `anomaly_triage`.

Grading: τ-bench recipe (`research/external/repos/tau-bench`) — sha256 the post-episode DB,
replay the gold action set on a fresh DB, compare. **Any incidental write fails.** This is
strictly stronger than our current answer-only assertions.

### M2 — Unsatisfiable demand (round-2 Q26)
ERP-Bench tags **77 of 300** tasks `unsat_demand` and refuses to ship such a scenario unless
it contains *both* kept and rejected orders. The finance analogue is exact and instantly
familiar to a treasury buyer: **cash is short on Friday's payment run; the correct answer
names which obligations go unpaid and why.**

Verifier grades the **rejection set**, not just the payment set. Our existing empty-answer
traps test "no data"; this tests "the data says no" — a different failure mode.

### M3 — Objective non-collapse admission gate (round-2 Q22)
The strongest transferable idea in the corpus. ERP-Bench re-solves each blueprint for the
naive objective, then re-solves the real objective with the naive metric *pinned*, and
rejects the task unless the real objective still improves.

Our port, enforced at authoring time: **a task does not ship if the naive answer equals the
graded answer.** Naive baselines to beat, per family: largest invoice · earliest due date ·
alphabetical first · the single system's own total · the number printed on the summary tab.
This is an admission gate, not a post-hoc label — it kills trivial tasks before calibration
spends trials on them.

### M4 — Money re-derivation (round-2 Q40)
ERP-Bench never trusts the number the agent typed: it re-prices every line against the tier
table and flags any fallback. Our analogue: for every task where the agent writes or reports
an amount, the verifier **recomputes it from terms + base + rate** — cash-discount chains
(5D10%→10D5%→14D2%), installment splits, partial settlements, FX, withholding — rather than
reading the stored value back. An agent can otherwise write a self-consistent wrong number.

### M5 — Hidden constraints in unstructured text
Sourced twice: ERP-Bench seeds a hard limit that has **no field in the system of record**,
living only in an Internal Note; Odoo's installment model makes the header due date lie
(round-2 Q35 — `invoice_date_due` is only `max(date_maturity)`, so a "30% now, balance 60
days" invoice is 30% overdue on day 1 while its header reads 60 days out).

Both are ready-made traps that punish field-reading and reward document-reading.

### M6 — Adversarial tool behaviour (round-2 Q30, Q31)
Two sourced primitives our `mcp/lib/framework.py` does not model:
- **The lying tool** — 12 of 15 advertised browser-automation ERP actions are non-functional
  stubs returning `{status:'ok', data:null}`. An agent that checks `status === 'ok'` and moves
  on is wrong.
- **Documentation drift** — mcp-erp registers 79 tools while its README claims 44 and its
  manifest declares 34; ECOUNT logs 22 and registers 23; CData promises write on a
  SELECT-only server. **The roster the agent is told about should not match the roster it has.**

### M7 — Blast radius
ERP-Bench seeds ~150 decoy entities per task and fails the run if any are touched, with
opaque namespace tokens so relevance cannot be pattern-matched. Our analogue: decoy vendors,
near-duplicate invoices, and same-name counterparties in the adjacent legal entity — with a
state-diff veto on any write outside the task's intended set.

## Depth ladder

Current: 20 tasks at 2 hops, 5 at ≥7. Target for the hard layer: **10–20 hops**, built by
composing mechanics rather than by padding steps — each hop must be *load-bearing* (removing
it changes the answer). The walk-length field stays the honest reference for the turn budget
(`maxTurns = max(24, walk*3+6)`), never a capability cap.

## Admission rules for the hard layer (all must hold)

1. Oracle walk replays green through the task's own verifier (existing rule).
2. **Non-collapse (M3)**: the naive answer ≠ the graded answer, stated explicitly in `task.toml`.
3. **No ground-truth leak** (round-2 Q39): the seed spec, oracle plan, and expected values are
   unreachable from the agent's filesystem and from every MCP tool.
4. **One template context** (round-2 Q36): instruction, seed, oracle and verifier render from
   the same object; no number appears in `instruction.md` that is not traceable to it.
5. Every seeded inconsistency cites a sourced pattern (existing rule).

## What this buys the buyer

A world where a frontier model's score is *not* 100% — with the failure modes named, sourced,
and reproducible, and with a depth ladder that keeps producing headroom as models improve.
That is the difference between a benchmark and a demo.
