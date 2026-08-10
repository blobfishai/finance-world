# THESIS — finance-world

> Stage 1 output, drafted 2026-08-10 from the Stage 0 corpus (`research/`). Every section
> cites its grounding. Everything below is SIMULATION ONLY: all balances, invoices, and
> documents are synthetic; public-company figures are frozen snapshots used as fixtures.

## The thesis in one paragraph

A frontier-lab finance team wants an agent it can trust with money questions. Trust means
grounded exactness: the right figure, for the right entity, as of the right date, in the right
currency, retrieved through tools — where "I found no overdue invoices" must be a first-class
answer, not a hallucination. Real finance data is fragmented (ERP + subsidiary books + Excel +
email), so finance-world's core mechanic is **fragmentation with a single defensible truth**:
every question has exactly one verifiable answer, but reaching it requires knowing which
system owns which slice of reality. We replicate microsoft/FinanceBenchmark's task surface as
the calibration anchor, then exceed it where it's weak: deterministic rewards instead of an
LLM judge, cross-system joins it doesn't attempt, write-workflows it doesn't test, and a
depth-escalation ladder that grows tasks until the target model breaks.

## The company & the clock

- **World**: Contoso Entertainment System USA — legal entity **USMF** — plus a small
  subsidiary, **CES Direct LLC**, whose books live outside the ERP. Adopting the
  FinanceBenchmark demo world (Contoso customers: Birch Company US-027, Sparrow Retail
  US-008, Forest/Cave/Desert Wholesales US-003/004/007; vendors incl. Fourth Coffee (East),
  Acme Office Supplies 1001, Fabrikam Electronics US-101; 1,000 synthetic SYNCUS/SYNVEN
  accounts, ~7k journal lines from the extracts) means the benchmark's 100 erp_qa tasks with
  verbatim ground truths replay in our world unchanged. (`research/erp-domain.md`,
  `research/external/financebenchmark-extracts/`)
- **Epoch**: frozen clock **2026-03-02T12:00:00Z** (proposed; confirm against extract dates
  during seeding). All aging, overdue, and discount-window math is relative to it.

## Personas (whose questions the tasks are)

AP specialist · AR/collections analyst · credit manager · controller · treasury analyst ·
FP&A analyst · procurement — each with documented recurring questions and done-criteria
(`research/domain-workflows.md` §1). Task prompts are written in these voices; done-criteria
become verifier assertions.

## Tool universe (Stage 2 census — all mocked over one SQLite state)

| MCP server | Shaped after | Owns |
|---|---|---|
| `erp` | Microsoft D365 ERP MCP (discovery-first: `data_find_entity_type` → `data_get_entity_metadata` → `data_find_entities`/`_sql`; form tools with 25-row pagination; `api_find_actions`/`api_invoke_action`) | USMF: three-layer AP/AR (posted `CustTrans`/`VendTrans` → open `CustTransOpen`/`VendTransOpen` with due dates → `CustSettlement` links incl. partials + discount-taken), `PaymTerm`, `CashDisc` chains, collection-letter state machine, credit limits/holds, aging snapshot (batch) **and** live open transactions |
| `books` | QuickBooks Online MCP (small subset of the 144-tool surface) | CES Direct subsidiary: its own customers (divergent IDs for shared counterparties), invoices, credit notes |
| `sheets` | Spreadsheet reader (Excel-as-shadow-system) | Collections tracker (stale vs ERP), manual invoice log (rows that exist nowhere else), close checklist |
| `email` | Read-only inbox | Invoices that only arrived by email, remittance advice, approval threads |
| `filings` | SEC EDGAR (submissions / companyfacts / companyconcept / full-text) | Frozen public-company snapshots: XOM, CAT, WMT, TSLA + brief subjects AAPL, T, LMT |
| `docs` | Document store (anchor pattern) | Policies the agent must *consult, not know*: 7-step dunning runbook, 2/10-net-30 discount policy, credit-review cadence, ratio thresholds, brief template |
| `harness` | eval-only (off the business surface) | verify / reset / submit_answer |

Friction defaults per lawfirm calibration (3% rate_limited/stale_reference, ambiguous write
acks); EDGAR-authentic friction (10 req/s, User-Agent, CIK padding) is an escalation lever,
off by default.

## The fragmentation story (every inconsistency cites a sourced pattern)

From the 12 patterns in `research/domain-workflows.md` §3, wave 1 seeds: (1) three CES Direct
customer invoices absent from USMF ERP (subsidiary books own them); (2) two invoices only in
the email inbox, one also hand-logged in `sheets` (68% manual keying); (3) a credit note in
`books` that the ERP-only answer would miss; (4) collections tracker in `sheets` one letter-
level stale vs ERP (version drift); (5) aging *snapshot* older than live open transactions
(dual-truth divergence); (6) one near-duplicate invoice pair ("INV-5521" / "5521-OPS"); (7) a
payment cleared in the bank export but unposted (timing gap). Cross-system questions ("total
AR exposure to Birch across all entities?") have exactly one defensible answer, which the
seed generator computes and pins.

## Task families

| Family | Wave-1 source | Count target | Verification |
|---|---|---|---|
| `erp_qa` | FinanceBenchmark's 100 (72 AR / 28 AP, 21 scenarios) replayed verbatim | 100 | exact GT via `submit_answer` (traps preserved: empty answers stay empty) |
| `finance_qa` | FB's 126, converted from LLM-judge to pinned numeric GT computed from frozen `filings` snapshots | ~60 wave 1 | value+tolerance+period+source assertions |
| `business_brief` | FB's 25 → structured submission (required sections incl. internal AR/AP fusion) | 10 wave 1 | per-field assertions + coverage checklist |
| `cross_system` | NEW — ours; chaos joins above | 20 wave 1 | pinned single-truth GT |
| `collections_ops` | NEW — writes (issue letter per dunning policy, place credit hold), τ²-bench recipe | wave 2 | state-diff + policy-compliance assertions |

Difficulty axes (ledger Q7): walk depth (2 → 10+ tools), as-of/currency/partial-settlement
reasoning, pagination forcing iteration, empty-answer traps, conflicting policy versions,
cross-system hops, format constraints.

## Verification strategy (the LLM-judge conversion)

House rule: deterministic VCode only. `submit_answer` writes the answer as state; verifiers
assert value (with per-class tolerance: exact for ERP sums and reported GAAP line items after
unit normalization; max(±0.01 absolute, ±1% relative) for derived ratios), currency, as-of
date, and — for briefs — required fields. Anti-hack vetoes throughout: reads-before-submit,
no raw SQL, no off-task writes, required-tool-family usage. Reliability is measured by
repeated trials (flake-scan), i.e. pass^k rather than single-run luck.

## Calibration plan (Stage 5)

Triage-and-grow per the house rule: 3 trials/task against the target model (roster TBD —
grok family expected, salesforce-grok's `config/model-roster.json` is the pattern). fail 3/3
→ park with failure-mode note (after audit-before-blame); mixed → **in_band flaky = the
product**; pass-first-try → escalate via `sim/grow-tasks` (to be built — lawfirm left it
spec-only): deepen walks, add ambiguity, add distractor rows, add cross-system hops.
Reference-relative budgets: `maxTurns = max(24, refWalk*3+6)`; FinanceBenchmark's own harness
capped at 20 turns, which their unmeasured-solvability warts trace to — we don't copy that.

## What finance-world adds beyond FinanceBenchmark

1. **Deterministic rewards** (their finance_qa/brief scoring is a DSPy LLM judge; ground
   truth exists only for erp_qa — we pin GT for everything shipped).
2. **Fragmentation** (their world is single-ERP; ours makes system-choice part of difficulty).
3. **Write tasks** (collections operations; they are read-only).
4. **Depth escalation + calibration labels** (their dataset has fixed difficulty; ours grows
   to the model's frontier and records `acceptance_label` per task).
5. **Harbor packaging** (per-task dirs, oracle-verified at export; theirs is a bespoke
   harness).

## Open decisions (need Sam / buyer input)

- **Model roster** for calibration (which grok + comparison models, API access) — ledger Q8.
- **Epoch confirmation** once extract dates are checked — ledger Q13.
- **EDGAR friction realism** on by default or escalation-only — ledger Q12.
- Whether wave 1 ships `collections_ops` or defers writes to wave 2 (proposed: defer).
