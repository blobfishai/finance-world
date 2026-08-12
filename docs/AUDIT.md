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

### A8. The turn budget was a capability cap after all — FIXED
Found 2026-08-11 auditing the first clean scan. Several "failures" showed the model making
44–84 successful tool calls and then submitting **nothing** — verdicts like
`answer:*:missing` plus `trace:no_reads_before_submit`. That is not a model that got the
finance wrong; it is a model that ran out of clock.

| task | budget | turns used | submitted |
|---|---|---|---|
| `cash_app/remittance-batch-mar02` | 27 | 28 | no |
| `collections_ops/escalate-sparrow-letter3` | 24 | 25 | no |
| `erp_qa/collections-sparrow` | 24 | 24 | no |
| `erp_qa/ap-overdue-usmf` | 24 | 25 | no |

Root cause: `budget = max(24, walk_len*3+6)` derives the allowance from the **oracle's** walk,
and the oracle cheats — it goes straight to the right `data_find_entities_sql`. A model doing
the same work honestly spends turns on discovery and on 25-row pagination (`ap-overdue-usmf`
aggregates 3,428 AP rows = 137 pages if paged). A 3-step oracle walk is legitimately a
30-turn agent run, so PLAN.md's own rule — "budgets are reference-relative, never capability
caps" — was being violated by the formula meant to implement it.

**Fix:** `budget = max(40, walk_len*8+12)`, sized off observed *successful* runs (40–45 turns
at walk 5–6) with headroom. Runs that still end without submitting at the cap are now written
as `trial-N.starved.json`, carry `budget_exhausted: true`, are excluded from triage exactly
like infra runs, and are re-run by the resume rule. A model failure has to be a *finance*
failure, not a clock failure.

### A9. The OpenAI-path runner ended episodes on an empty assistant turn — FIXED
Found 2026-08-11 auditing the first DeepSeek sweep, before reading any of it as a result.

`sim/agent_openai.py` treated any assistant message with no tool calls as the end of the
episode. Models on this transport routinely emit an empty or purely narrative turn mid-task,
so the loop exited while the model was still working — and the run was then graded as a wrong
answer:

| task | turns / budget | successful tool calls | submitted |
|---|---|---|---|
| `erp_qa_fb/aged-balance-1` | 5 / 40 | 5 | no |
| `erp_qa/due-next-week-adventure` | 6 / 40 | 5 | no |
| `erp_qa_fb/aged-balance-2` | 10 / 40 | 14 | no |
| `erp_qa/ap-overdue-usmf` | 35 / 40 | 46 | no |

**4 of 23 apparent failures were this bug** (2 more at 40/40 were genuine budget starvation,
already labelled). Reading that sweep at face value would have overstated the world's
difficulty by ~17% of its failures — the same error as A5 and A8, in a new transport.

**Fix:** an assistant turn with no tool call ends the episode only if `submit_answer` has
already succeeded; otherwise the runner appends one reminder that the task is not complete
and continues, capped at 3 nudges. This enforces the output contract that `claude -p`
enforces by running to completion, and supplies no task content — the nudge says "you have
not submitted", never anything about the finance. Affected trials were discarded, not
re-graded (the run itself was truncated, so there is nothing to re-grade), and re-run.

### A10. Three graders were wrong, found in the deepseek "too_hard" bucket — 2 FIXED, 1 OPEN
Found 2026-08-11 auditing the 17 tasks deepseek-v4-pro failed 3/3, before labelling any of
them `too_hard`.

**A10.1 — we failed a model for using our own spelling. FIXED.**
`finance_qa/xom-cat-liquidity-compare` demanded `larger_company` contain `"ExxonMobil"`. The
company our own seed calls **"Exxon Mobil Corporation"**. The model read our data, echoed our
name, and got every other field exactly right (91,990,000,000 / 45,682,000,000 /
46,308,000,000). Now accepts `Exxon`, and — since the check was doing no real work — also
`forbid`s `Caterpillar`, so it grades naming the *wrong* company instead of grading spacing.

**A10.2 — my own yes/no conversion introduced prompt/verifier drift. FIXED.**
`expense_audit/threshold-shaving-h1` asks for `detector_triggered` **(text)** in its
instruction. When I swept 8 tasks onto the new `yes_no` check type earlier the same day, I
changed the grader without reading each instruction, so the prompt asked for text and the
verifier graded polarity. The model answered `"Threshold shaving"` — the detector's name,
which is what the prompt invites — with all three other fields correct. Instruction now states
the yes/no contract. **Validator gap worth noting:** S4 checks that an answer field is
*mentioned* in the instruction, not that the stated type matches the check type. A conversion
sweep can therefore pass validation while breaking the contract.

**A10.3 — the FB cloner silently rebinds a question to a different entity. OPEN.**
`erp_qa_fb/credit-limit-3` asks *"What is the credit limit for **Contoso Retail San Diego**"*.
No such customer exists in this world. `resolve()` fuzzy-matched it to **Contoso Retail**
(SYNCUS-0485) and pinned ground truth to that account's 100,000. The model answered `none`,
which for the entity actually named is defensible, and we scored it 0.

This is the A6 class one level up: *task seeds may add entities, never silently repurpose an
existing account's identity* — here the **question's** entity is repurposed. A benchmark
question naming an entity the world does not have should either be excluded with a stated
reason or shipped deliberately as an empty-answer trap, never rebound to a near neighbour.

Deferred only because `world/etl/clone_fb_erp.py` is being edited concurrently by the parity
push; the fix is a strictness flag on `resolve()` plus a re-run. **Until it lands, every
FB-cloned task whose question names an entity absent from the ledger is suspect.**

### A11. Nearly half the task tree was answerable without reading anything — FIXED
Found 2026-08-11 by measuring the shipped checks, not by reading code. Immediately after
scaling the tree to 1,523 tasks:

**688 of 1,523 (45%) could be answered "0 / none / no" with no successful tool call.**

Cause: seven tables the ERP handlers query were empty or near-empty —
`erp_collection_letters` 0 · `erp_product_receipts` 0 · `erp_customer_pool` 0 ·
`erp_payment_runs` 0 · `erp_purch_orders` 1 · `erp_activities` 2 · `erp_sales_orders` 3 ·
open AR invoices carrying a cash-discount code 0. An empty table does not make a task hard,
it makes it **free**: "which customers are on the collections worklist?" grades as "none",
and a model that never opens the ERP scores 1. The cloner was working correctly; the world
had nothing for it to ask about. The entity sweep then multiplied the defect 1,320-fold.

**Fix, in two parts.**
1. `world/etl/load_activity.py` (build stage 4) gives the operational tables a life,
   deterministically and derived from the ledger that already exists: 1,147 collection
   letters on customers who are genuinely past due, 600 pool assignments, 260 worklist
   activities, 380 sales orders (12% on hold), 300 POs with 300 receipts (28% deliberately
   short or over — real match exceptions), and cash-discount codes on 240 open AR invoices.
2. The sweep now judges **the emitted checks**, not its own field dict, and drops any
   instance where every graded check is satisfied by "0/none/no". The two disagreed on
   list-valued answers; the gate that matters is the one a model actually faces.

**Result: 45% → 3%**, and 0 of 1,026 generated instances are null-answerable. The gate
rejected 3,728 candidates to get there — the drop rate is the point, not a cost.

**Lesson worth keeping:** the 10x looked like progress and was partly defect multiplication.
Counting tasks measured nothing; measuring what a *null-answering* model would score measured
the thing that matters. Any future generator ships with this check or it does not ship.

### A12. Scaling the task tree filled the disk — FIXED
2026-08-11. `sim/prepare.py` copies the whole built world (~3 MB) into a per-task run
directory. That is fine at 60 tasks and fatal at 1,200: `sim/refresh_gt.py` prepares every
task once (~3.6 GB) and `sim/validate.py` prepares every task **three** times (a, b, oracle
— ~11 GB), on top of `.runs/<model>/` from every scan. It exhausted a 42 GB disk mid-refresh,
and the tooling then could not run at all.

**Fix:** both now delete each task's run directory as soon as they are done reading it. The
copies are scratch the moment their `gt_sql` has been evaluated or their oracle has replayed.
`.runs/` was already gitignored, so nothing was lost — but "gitignored" is not "free".

**The pattern, again:** a mechanism that is correct at small N and unaffordable at large N.
The 10x multiplied the per-task cost as faithfully as it multiplied the tasks. Anything that
scales with the tree now has to state its cost per task before it runs.

### A13. `refresh_gt` treated "query returns nothing" as "the answer is zero" — FIXED
2026-08-11, caught within seconds of starting it because the edit landed in a task I knew the
answer to.

`sim/refresh_gt.py` re-derives every `gt_sql`-backed truth from the built world and rewrites
any that drifted. It read the result as `fetchone()[0] or 0`. For a **write** task the graded
value does not exist before the agent acts — `anomaly_triage/duplicate-payment-mar` grades
`total_paid` off `erp_payment_run_lines`, which is empty until the run is committed — so the
query returned NULL, `or 0` turned that into `0`, and the tool **rewrote a correct 34,450.00
to 0.00** in both `checks.json` and the gold walk.

One task was corrupted before the kill; `git checkout` restored it, and the oracle replays
green again. The blast radius was one because the run was watched, not because anything
stopped it.

**Fix:** a NULL re-derivation now means *this truth is not derivable from the world as the
agent finds it* — it is reported and skipped, never rewritten. `sim/validate.py`'s S11 check
carried the identical `or 0` coercion and is fixed the same way. 41 answer checks fall into
this class; their post-episode values are graded by `state_checks`, which run after the
episode and are the right place for them.

**The deeper lesson:** `gt_sql` on an *answer* check silently assumes the truth exists in the
pre-episode world. That holds for every read task and for none of the write tasks. A repair
tool that trusts its own inputs is a corruption tool with good intentions — and this one was
built earlier the same day to fix a different integrity bug.

### A14. Generated world data collided with hand-authored task ids — FIXED
2026-08-11, one command after A13. `world/etl/load_activity.py` mints purchase orders
`PO-7000..PO-7299`; `threeway_match/ppinv-exceptions-mar` seeds `PO-7001..PO-7003` by hand.
`prepare()` runs the task seed on top of the built world, hit a UNIQUE constraint on
`erp_purch_orders(po_number, line)`, and **every task in the tree became unpreparable** — the
refresh crashed on the first one it reached.

Generated identifiers now live in a reserved range (`PO-6xxxxx`, `SO-5xxxxx`) recorded as
`ID_RANGES` in the loader, so a hand-authored id and a generated one cannot occupy the same
namespace.

Same family as A6 (task seeds may not repurpose an existing account's identity) and A10.3 (a
question may not be rebound to a near neighbour), now from the other direction: **the world
generator may not squat on identifiers a task already owns.** Three variants of one rule, all
found the hard way, all cheap to prevent once stated.

### A15. The parity ledger counted generated instances as benchmark coverage — FIXED
`python3 ingest/run.py` reported **1,123 FinanceBenchmark items running here against 153
addressable — 734%**, and a grand total of **689% of addressable**. A coverage number above
100% is not a small error; it is the document disproving itself in its own headline, and
`docs/PARITY.md` is precisely the artefact a buyer checks first.

Cause: `world/etl/sweep_erp_qa.py` generates additional *instances* of an FB question pattern
over other entities, and emits them through the cloner's `emit()`. That writer stamped one
provenance for both products, so a generated instance was byte-identical in metadata to a real
clone — `origin = "clone of microsoft/FinanceBenchmark erp_qa (...); question verbatim"` — on a
task whose question is **not** verbatim and whose entity FB never asked about. `shipped()`
matched on that string, so all 1,026 instances counted as ported benchmark items.

The intent was already correct and written down twice. The sweep's own docstring says
instances "go to their own family so they never inflate the FinanceBenchmark parity number",
and PARITY.md said they were "excluded from every parity number above". Both were false in
code. **A stated invariant that nothing enforces is a comment, not a control** — the same
lesson as A11, where the property "a task must require reading" was believed rather than
checked.

Fixed in three places, so the invariant now holds by construction:
- `emit(..., instance_of=)` writes distinct provenance and stamps `generated = true` +
  `pattern = "<scenario>|<handler>"`.
- `grow_tasks.py` stamps `variant_of` on escalated variants — the same bug in miniature, which
  had TheAgentCompany reporting **13 ported against 12 addressable (108%)**.
- `ingest/run.py` counts three buckets and never sums them: ported (the only thing the rate
  counts), instances (breadth), variants (depth).

Backfilled onto 1,026 instances and 30 variants without touching a ground truth, a check or an
instruction — each instance's pattern key recovered by re-running the cloner's router over its
question, so backfilled labels share the vocabulary of fresh output (1,026/1,026 routed).

True number after the fix: **107 of 165 addressable (65%)** — FB 97/153, TAC 9/12 — plus 1,026
instances over 27 patterns and 4 variants. The honest number was *better* than the 25% the doc
had been claiming from a stale hand-edit; the bug was hiding real progress as well as
manufacturing fake progress.

### A16. Three defects in the filings surface, found by asking it 28 real questions — FIXED
Building the `finance_qa` cloner meant binding FinanceBenchmark's 28 single-figure questions
against the frozen SEC snapshot. Only **9 bound**. The other 19 were not hard questions; they
were three bugs wearing a trenchcoat.

**1. Tag selection preferred presence over coverage.** `LINE_ITEMS` lists fallback XBRL tags per
concept, and the fetcher took `next(c for c in candidates if c in gaap)` — the first tag the
filer uses *at all*. Microsoft tags `Revenues` for FY2010 only and has reported everything since
under the ASC-606 contract-with-customer tag, so Microsoft held 12 revenue facts, all from 2010,
and every modern revenue question rejected as `fact_absent` against a world that had the data
under another name. Candidates are now merged across the whole history and resolved **per
period** in priority order, which is what the 2018 ASC-606 transition actually requires.

**2. Quarterly facts did not exist, and questions about quarters matched annual rows anyway.**
`if r.get("form") != "10-K": continue` dropped every 10-Q, so all 10,005 rows were `fp='FY'`.
The probe then "successfully" bound *"Apple's Q4 FY2024 diluted EPS"* to the **full-year** EPS —
a wrong ground truth that looks perfectly bound, which is the A10.3 failure mode exactly. 10-Q
rows are now stored with their real `fp` and duration-filtered, so a Q3 row is one quarter and
never a nine-month cumulative. The snapshot went from 10,005 annual facts to **42,737** across
FY/Q1/Q2/Q3.

**3. Re-seeding silently doubled every fact.** `load_into_world` uses `INSERT OR REPLACE`, but
`filings_facts` carries no unique constraint, so there is nothing to replace — running it twice
appends. A duplicated fact does not read downstream as "duplicate"; it reads as **"two
period_ends equidistant from the date you asked for"**, so nine legitimate questions became
unanswerable through ambiguity. Same shape as A6: an ETL step that is only correct against an
empty database. The loader now clears both tables first and creates
`UNIQUE(cik, concept, period_end, fp)` so it cannot recur.

A fourth was in the cloner, not the world: company matching used `\bexxon\b`, which cannot match
"ExxonMobil" — there is no word boundary before the M — so two items rejected as `absent_entity`
against a world that holds the company. Matching is now prefix-anchored.

Result: **9 → 21 of 28 bound**, and the 7 that remain are named individually in `docs/PARITY.md`
with 4 of them structurally unanswerable from us-gaap XBRL (GHG emissions, analyst consensus, a
non-SEC registrant, a footnote line item). Existing ground truths were re-checked against the
rebuilt snapshot and are unchanged — XOM current assets still 91,990,000,000, Walmart's average
inventory still 55,663,500,000.

The lesson is the one this repo keeps relearning: **a capability is only real once something
asks it a question.** The filings surface had passed every gate it had, because no gate had
ever asked it for a quarter.

### A17. Three ways to grade a procurement plan against the wrong number — CAUGHT BY THE GATE
Porting ERP-Bench meant grading "did the agent plan this well?", and the plan's own JSON offers
several plausible cost figures that mean subtly different things. All three mistakes below were
caught by the oracle admission rule rather than shipped, which is the rule earning its keep: an
oracle walk that cannot pass its own checks is a task that cannot be solved.

**1. The oracle walk was invalid, not merely suboptimal.** The first walk bought every unit from
the single cheapest vendor offer. That ignores the offer's `max_qty`, which is a horizon-wide
cap — so the walk "beat" the optimal plan on cost by proposing a purchase no vendor would
accept. All 70 tasks in the first slice failed the spend check. The walk is now built from the
plan's own `purchase_orders` array, which names the vendor, quantity and unit cost of every line
it intends. **A cheaper answer that violates a constraint is not a better answer**, and a spend
check with no validity check would have rewarded exactly that.

**2. `variable_cost` is not purchase spend.** Grading committed PO value against the sum of
per-allocation `variable_cost` demanded purchasing the plan never intended, because that figure
also carries the cost of on-hand stock consumed.

**3. `optimal_new_spend` is not purchase spend either.** It additionally carries the workcentre
assembly cost, so it over-demanded purchasing on every make-or-buy scenario — the buy-only
tasks passed and the manufacturing ones failed by exactly the assembly total, which is what
made the cause legible. PO lines are now graded against the plan's own `purchase_orders`
totals, and assembly cost is graded as its own answer field.

Two design rules came out of it, both already house rules applied in a new place:
- The `assembly_cost` field is declared on **every** ERP-Bench task, 0 where nothing is
  manufactured. A field that appeared only on make-or-buy scenarios would tell the model the
  answer before it read the product's routes — the same leak as the `business_brief`
  `internal_open_ar_usd` field (A16's sibling, fixed in the same session).
- Scenarios whose stated invoicing/downpayment policy cannot yet be expressed as a scalar
  assertion are **rejected, not shipped** (15 of 300). Shipping them would put a policy in the
  prompt that the checks do not grade — A10.2 exactly.

### A18. Naturalising the prompts truncated 286 of them — FIXED, and found only by being asked
The answer contract used to be stapled to the end of every instruction ("Reply with
`submit_answer`: - `dormant_count` (number) ..."). No colleague types that, and worse, it hands
over the decomposition: being told to file `overpayment_usd` AND `underpayment_usd` separately
reveals there are two directions of error before the model has looked at anything. It moved to
the reporting tool — `answer_schema`, served by the harness `reporting_fields` tool — and 1,534
instruction files were rewritten by script.

The script matched the WHOLE LINE containing the lead-in phrase and deleted it. Where the
lead-in sat alone on its line, correct — 1,249 tasks. Where a task put real instruction on the
same line, the instruction went with it:

| lost text | tasks |
|---|---|
| `Work in the \`odoo\` ERP. When the plan is committed,` | **284** |
| `When the run is committed,` | 1 |
| `...rounded to two decimals.` | 1 |

So every ERP-Bench task silently lost the sentence naming **which of the eight MCP servers to
work in**, and one prompt ended mid-sentence at "rounded to".

**Nothing in the gate would have caught this.** The oracle does not read instructions — it
replays a fixed walk — so all 284 still scored 1. `sim/validate.py` checks that graded fields
are declared, not that the prose still parses as English. A prompt can lose a sentence and
every automated check stays green, because no check reads the prompt *as a prompt*.

It was found because Sam asked to see the tasks and spot-check what they prompt. The fix that
mattered was not the regex: it was diffing every instruction against its committed version and
listing each removed line that was not part of the answer block. That took one command and
should have run before the refactor was reported as done — six oracle spot-checks were run
instead, and none of the six happened to be an ERP-Bench task.

Standing rule from this: **a bulk rewrite of authored text is not verified by its outputs
passing; it is verified by diffing what it removed.** The parser now preserves any prose before
the lead-in, the 284 were re-emitted from the corrected emitter, and the other two are restored.

A second, sharper cost: a validation gate was running while the tasks were being edited under
it. Whatever it printed would have described a tree that no longer existed. It was killed
rather than reported. **A gate that ran against a moving tree is not evidence**, and the honest
move is to throw the run away, not to quote it.

### A12b. Validator cleanup is best-effort, not guaranteed — OPEN, known cost
The A12 fix added `shutil.rmtree(...)` at the end of `sim/validate.py`'s per-task loop. It
runs only when the task reaches the end of the body, and several paths `continue` before it,
so a full run over 1,205 tasks still left ~300 directories behind and consumed ~12 GB of
transient disk (it had to be reclaimed mid-run to let the gate finish).

The correct shape is a `try/finally` around the per-task body, which needs the loop body
re-indented — deliberately **not** attempted while the tree was green and unvalidated changes
were the larger risk. Until it lands:

    python3 sim/validate.py    # needs ~12 GB free at 1.2k tasks; clean .runs afterwards

Worth stating because it is the shape of the whole day: the fix that is 90% right is the one
that bites next, and "it worked when I ran it" is not the same as "it cannot leak".

### A4. `--max-turns` not strictly enforced by observed runs — WATCH
haiku's ap-overdue run recorded `num_turns=36` against `--max-turns 24`. Budget overruns
currently can't masquerade as passes (verification is answer-based), but turn accounting
must be understood before budget-based failure labels (`budget_exhausted`) are trusted.
UNRESOLVED — investigate whether the CLI counts turns differently than the flag.
