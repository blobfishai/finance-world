# External source repos — index

Shallow (`--depth 1 --single-branch`) checkouts of the repos that ground finance-world.
**`.git` removed from every clone** — this is source, not history. Cloned **2026-08-10**.
Total on disk: **362 MB** across 24 repos (budget ≤600 MB).

Four repos exceeded the ~150 MB clone cap but had a small, high-value subset; those were taken
as **partial clones** (`--filter=blob:none --sparse`, non-cone excludes). Each is flagged
`(sparse)` with the excluded paths named. Nothing else was modified.

> Licensing note for anyone lifting code (not facts) out of these: `erpnext` is **GPL-3.0** and
> `sec-edgar-mcp` is **AGPL-3.0**. Copying their *tool names, schemas and workflow semantics*
> into our mocks is fine (interfaces/facts); copying their source is not. Everything else here
> is MIT/Apache-2.0 except the unlicensed items noted in the table.

---

## 1. Evals & benchmarks

| Repo (dir) | URL | What it contains | Size | Why it matters to finance-world |
|---|---|---|---|---|
| `microsoft-FinanceBenchmark` | https://github.com/microsoft/FinanceBenchmark | The real harness + `data/dataset.yaml` = **251 tasks** (`query, plugin, segment, scenario, tags[{tag, assertions[{text, level}]}]`), `data/rubric.yaml` (judge rubric: clarity/groundedness/relevance/structure/citations/recency/depth), `FO Benchmark_Data.zip` = synthetic D365 ERP load (customer/vendor DMF CSVs + AP/AR journal XLSX). Plugins: erp_qa 100 (AR 72/AP 28), finance_qa 126, business_brief 25. | 2.4 MB | **Primary eval-sample source.** Our `erp_qa_fb` family is re-anchored from this; the scenario list is the coverage checklist for Stage 4. MIT. |
| `financebench` *(sparse)* | https://github.com/patronus-ai/financebench | `data/financebench_open_source.jsonl` (**150 rows**: question, gold answer, justification, page-level evidence), `financebench_document_information.jsonl` (**361 docs**: 10-K/10-Q/8-K/EARNINGS + GICS sector + URL), `results/` = **16 pre-computed model-run files** labelled Correct/Incorrect/**Refusal** across `closedBook / oracle / inContext / singleStore / sharedStore` conditions. | 4.0 MB | Gold Q/A + **evidence spans** for filings QA, and a rare public **refusal-rate** dataset for calibrating "no answer in the data" traps. `pdfs/` (705 MB) excluded — retrieval conditions are not runnable locally without re-downloading. No LICENSE file. |
| `FinQA` | https://github.com/czyssrs/FinQA | train 6,251 / dev 883 / test 1,147 / private_test 919. Each: `pre_text`, `post_text`, `table`, `filename` + `qa{question, answer, steps[{op,arg1,arg2,res}], program, gold_inds, exe_ans}`. Plus retriever/generator code. | 114 MB | The **executable-program annotation** pattern: every numeric answer carries the arithmetic that produced it. Directly reusable as the shape of our deterministic numeric ground truths. MIT. |
| `ConvFinQA` | https://github.com/czyssrs/ConvFinQA | `data.zip` (17 MB → 249 MB): 3,037 conversations / 11,104 turns; `annotation{dialogue_break, turn_program (with cross-turn refs `#0`), exe_ans_list}`. | 17 MB | The only public **multi-turn** financial-numeric decomposition set — the template for our multi-turn `session` tasks where turn *n* references turn *n−1*'s result. MIT. |
| `TAT-QA` | https://github.com/NExTplusplus/TAT-QA | 2,201/278/278 hybrid table+text contexts, 16,552 questions. Answer types span 5,722 / arithmetic 5,543 / multi-span 1,645 / count 305, each with `derivation` and a required **`scale`** label (thousand/million/billion/percent). | 35 MB | **Scale/unit correctness as a graded dimension** — a cheap, high-yield anti-sloppiness probe our verifiers don't yet apply. MIT. |
| `bizbench-benchmarks-pipeline` | https://github.com/kensho-technologies/benchmarks-pipeline | ⚠️ **Not BizBench data.** Kensho's S&P AI Benchmarks *demo runner*; `benchmark_questions.json` is gitignored (download from benchmarks.kensho.com). Has `prompts/` (11 few-shot JSONs), `python.py` (sandboxed `exec_python`), tasks: CodeTAT-QA, TAT-QA, CodeFinQA, FinKnow, FinCode, ConvFinQA. | 148 KB | The **`code` vs `cot` prompt-mode split** (emit a no-import Python snippet whose last expression *is* the answer) — a clean way to grade financial arithmetic without a judge. Kensho license header. |
| `SECQUE` | https://github.com/EnvCommons/SECQUE | ⚠️ **Env wrapper, no dataset** (parquet lives on OpenReward / HF `nogabenyoash/SecQue`). 9 files: `server.py`, 3 sample agents, Dockerfile. 565 single-turn tasks, `{question, context_markdown, ground_truth}`, **no tools**, hidden `@terminal` gpt-5-mini judge, binary reward. | 44 KB | A minimal, readable **OpenReward environment contract** (single-turn, message-ends-rollout, hidden grader tool) — useful packaging reference. No LICENSE file (README says MIT). |
| `vals-ai-finance-agent` | https://github.com/vals-ai/finance-agent | Agent harness + `data/public.csv` = **50-question public sample** with `Rubric` = JSON list of `{operator: correctness\|contradiction, criteria}`. Tools: `web_search`, `edgar_search`, `parse_html_page`, `retrieve_information`, `submit_final_result`. Expert time 15–30 min/q. | 516 KB | The **conjunction + contradiction** rubric design (crisper than a free-form judge) and a `submit_final_result` tool — the same "answers are state" pattern as our `submit_answer`. MIT. |
| `vals-ai-finance-agent-v2` | https://github.com/vals-ai/finance-agent-v2 | 27 rows, **gold `Answer` column removed**; severity-weighted `finance_agent_v2_operator` rubrics. Adds `calculator` + `price_history` (Tiingo, asset-class routed) tools. System prompt pins "current date is March 1, 2026", SEC-filing precedence, 2-dp precision, trailing `sources` dict. 9 types × 3 q, expert time 40–60 min. | 540 KB | Harder analyst tasks (Comparables, Precedents, Adjustments, Disclosure Analysis) + the **frozen-clock + citation-dict prompt contract**, which is nearly identical to our epoch design. MIT. |
| `accounting-bench-replication` | https://github.com/SakethKoona/accounting-bench | Replication of Penrose AccountingBench as a HUD env. `env.py` = 9 tools (`query_source_data`, `get_accounts`, `add/update/delete/post_journal_entry`, `get_journal_entries`, `submit_reconciliation_report`, `workspace_query`, `get_reconciliation_status`); `db/schema.sql` = Postgres `source_data` (mercury/ramp/stripe/rippling) + `general_ledger` + `workspace`; 5 tasks; CPA baseline balances in `data/synthetic/baselines/`. Grade = 80% balance accuracy `1−Σ|Ai−Pi|/(Σ|Ai|+Σ|Pi|)` + 20% reconciliation completeness, pass ≥0.95 **and** all recons passing. | 544 KB | The **only** public multi-turn month-end-close environment with a real ledger and CPA ground truth. Its `multi-month-close` scenario (deferred revenue, bonus accrual reversal, prepaid amortization) is a ready-made ladder for our `close_mgmt` family. Inner README is an unmodified HUD template — ignore it. No LICENSE. |
| `FinMCP-Bench` *(sparse)* | https://github.com/chentonghao/FinMCP-Bench | ⚠️ Third-party **2-sample demo**, not the full 613-task benchmark. Value is the row schema: `{scenery (3-level scenario taxonomy), diff_level{level, para_tool_call_number, tool_number, turns}, tool_list (gold tool sequences), question, messages (full gold trajectory)}` + `src/finmcp_agent/{metrics,tool_catalog,mcp_client}.py`. Chinese-language, consumer wealth/fund domain (Qieman MCP). | 548 KB | Confirms §3.8's previously-UNVERIFIED FinMCP-Bench: grading is **tool-plan precision/recall/F1 against a gold tool sequence**, with `para_tool_call_number` (expected *parallel* calls) as an explicit difficulty axis. A committed 405 MB `.venv` was excluded. No LICENSE. |

## 2. Agentic-benchmark methodology references

| Repo (dir) | URL | What it contains | Size | Why it matters to finance-world |
|---|---|---|---|---|
| `tau-bench` | https://github.com/sierra-research/tau-bench | Sierra's τ-bench (README marks it superseded by τ²). Domains retail (16 tools) + airline (14); DB is plain JSON reloaded per episode; each tool is a class with `invoke(data, **kwargs)` + `get_info()`; policy = `wiki.md` + `rules.py` as system prompt; `Task{user_id, instruction, actions, outputs}`; user simulator with `human\|llm\|react\|verify\|reflection` strategies ending on `###STOP###`. | 59 MB | The canonical recipe for **stateful write grading**: sha256 the post-episode DB, replay the gold actions on a fresh DB, compare hashes — **any incidental write fails**. Plus `pass^k`. Answers PLAN.md open question 4. MIT. |
| `tau2-bench` *(sparse)* | https://github.com/sierra-research/tau2-bench | τ²/τ³: pydantic-typed framework, pluggable domains (`data_model.py` + `tools.py` with `@is_tool` + `environment.py` + `db.json` + `policy.md` + `tasks.json`), half- and full-duplex orchestrators. Domains: airline 50, retail 114, telecom 2,285, mock 10, **`banking_knowledge` 97**. Excluded: `data/tau2/results/` (604 MB of published runs), `data/voice/`, `telecom/tasks_voice.json`, `retail/task_issues/`, `web/`, `figs/`. | 60 MB | Two things we should copy. (1) **Composable reward**: `reward_basis` multiplies any subset of `{DB, ENV_ASSERTION, COMMUNICATE, NL_ASSERTION, ACTION}` — `COMMUNICATE` requires the agent to actually *tell the user* specific facts, which our submit-answer design only half-covers. (2) The `banking_knowledge` domain (below). MIT. |
| `TheAgentCompany` | https://github.com/TheAgentCompany/TheAgentCompany | CMU's simulated-software-company benchmark: **175 tasks** (verified: `workspaces/tasks/`), each a Docker image with `task.md` + `checkpoints.md` + `evaluator.py` + `scenarios.json` (NPC personas), over self-hosted GitLab/ownCloud/Plane/RocketChat. Category split: sde 69, hr 29, pm 28, admin 15, ds 14, **finance 12**, research/qa/ml 2 each. | 12 MB | The **checkpointed partial-credit** grading style, the multi-system fragmentation our `cross_system` family imitates, and — unexpectedly — a real finance task suite (`finance-apply-tax-credit`, `finance-budget-variance`, `finance-revenue-reconciliation`, `finance-check-attendance-payroll`, `finance-invoice-matching`, `finance-expense-validation`, `finance-find-signatories`, `finance-substantial-presence-test`, `finance-r-d-activities`, `finance-create-10k-income-report`, ±2 reimbursement tasks). MIT. |

## 3. Real tool surfaces (for 1:1 mock fidelity)

| Repo (dir) | URL | What it contains | Size | Why it matters to finance-world |
|---|---|---|---|---|
| `sec-edgar-mcp` | https://github.com/stefanoamorelli/sec-edgar-mcp | Python FastMCP over `edgartools`. **21 tools** in 5 groups: company (`get_cik_by_ticker`, `get_company_info`, `search_companies`, `get_company_facts`), filings (`get_recent_filings`, `get_filing_content`, `analyze_8k`, `get_filing_sections`), financial (`get_financials`, `get_segment_data`, `get_key_metrics`, `compare_periods`, `discover_company_metrics`, `get_xbrl_concepts`, `discover_xbrl_concepts`), insider/Form-4 (`get_insider_transactions`, `get_insider_summary`, `get_form4_details`, `analyze_form4_transactions`, `analyze_insider_sentiment`), `get_recommended_tools`. Paging = **char offset + budget** (`offset`, `max_chars=50000`) and `days`/`limit` windows. Errors return `{"success": false, "error": ...}`. | 1.5 MB | The reference our `filings_server.py` is shaped against. Two things to steal: the **`_FINANCIAL_INSTRUCTIONS` block embedded in every docstring** (use only returned data, never round, always cite the filing URL + date + form type), and the insider/Form-4 surface we lack entirely. **AGPL-3.0 — do not copy code.** |
| `financial-datasets-mcp-server` | https://github.com/financial-datasets/mcp-server | 376-line single-file FastMCP, **11 tools**: `get_income_statements`, `get_balance_sheets`, `get_cash_flow_statements`, `get_current_stock_price`, `get_historical_stock_prices`, `get_company_news`, `get_sec_filings`, + 4 crypto. No pagination, no structured errors. | 68 KB | Minimal contrast case for our XBRL-first `filings_server` — and a caution: its README documents 10 tools while the code has 11. MIT. |
| `ramp_mcp` | https://github.com/ramp-public/ramp_mcp | Ramp's official server, **19 tools max**. Distinctive design: it does **not** return API rows — it loads Ramp data into an in-memory SQLite DB and hands the model SQL (`load_transactions`, `load_receipts`, `load_reimbursements`, `load_bills`, `load_vendors`, `load_spend_limits`, `load_spend_programs`, `load_entities`, `load_users`, … then `process_data` / `execute_query` / `clear_table`). Loader tools **register only if the matching OAuth scope was granted**. Pagination auto-followed and hidden, capped at `CLIENT_MAX_PAGES=100` → forces better filters. Amounts are **integer minor units** ("1000 = $10.00"). | 116 KB | **Our biggest tool-surface gap**: `expense_audit` runs through sheets/docs with no real T&E system. Also the two best friction ideas here: **scope-gated tool visibility** and the **cents-vs-dollars precision trap**. MIT. |
| `xero-mcp-server` | https://github.com/XeroAPI/xero-mcp-server | Xero's official TS server, **50 tools** (26 list / 11 create / 12 update / get / delete). Finance-relevant: `list-aged-payables-by-contact`, `list-aged-receivables-by-contact`, `list-trial-balance`, `list-report-balance-sheet`, `list-profit-and-loss`, `list-manual-journals`, `list-bank-transactions`, `list-credit-notes`, `list-tracking-categories`, plus a **payroll** block (`list-payroll-employees`, leave types/balances, `create-timesheet`, `approve-timesheet`, `revert-timesheet`). Pagination is **model-visible**: required `page`, size 10, and the tool description tells the model to ask the user before fetching page 2. | 756 KB | A second SMB-books dialect for the subsidiary fragmentation story, the only **payroll + timesheet approval** surface in the set, and the clearest example of pagination-as-agent-friction (a known failure mode for us — see the `ap-overdue` haiku truncation bug). MIT. |
| `quickbooks-online-mcp-server` | https://github.com/intuit/quickbooks-online-mcp-server | **Intuit's official** QBO server — **142 unique tools** (25 create / 26 update / 20 delete / 41 get / 30 search). Reports: `get_aged_payables`, `get_aged_receivables`, `get_trial_balance`, `get_general_ledger`, `get_profit_and_loss`, `get_balance_sheet`, `get_cash_flow`, `get_customer_balance`, `get_vendor_expenses`. Writes incl. `create_bill_payment`, `create_journal_entry`, `create_vendor_credit`, `create_transfer`, `create_deposit`, `create_purchase_order`. OAuth2 with **refresh-token rotation** + a token store; searches enforce per-entity allow-lists of filterable/sortable fields. | 2.4 MB | Ground truth for the surface our `books_server.py` (11 tools) imitates — a **13× fidelity gap**. Its **write-gating by name prefix** (`QUICKBOOKS_DISABLE_WRITE/UPDATE/DELETE`, READ never disabled) is a ready-made permission axis for read-only vs write task variants. Apache-2.0. |
| `modern-treasury-mcp-http` | https://github.com/agenticledger/modern-treasury-mcp-http | **Community** (not official) MT server, **65 tools**: `payment_order_create/list/get/update`, `return_create`, `incoming_payments_list`, `expected_payment_*`, `transactions_list`, `ledger_tx_create/reverse`, `ledger_entries_list`, `fx_quote_create`, `balance_reports_list`, `routing_number_validate`, counterparty/external/internal/virtual accounts, invoices, events. Native **cursor** pagination (`after_cursor`, `per_page`) passed straight through. | 172 KB | Modern Treasury ships **no official MCP server** — this is the only public MCP framing of payment rails. `expected_payment_*` vs `transactions_list` is the bank-matching problem expressed as tools. No LICENSE. |
| `modern-treasury-openapi` | https://github.com/Modern-Treasury/modern-treasury-openapi | The authoritative MT API spec: **177 operations** over payment_orders, expected_payments, returns, reversals, ledgers/ledger_accounts/ledger_transactions, balance monitors, counterparties, external/internal/virtual accounts, invoices, legal entities, holds, settlements. | 712 KB | The real vocabulary for **payment execution + bank matching**: `createExpectedPayment` vs `createTransaction` *is* the bank-rec problem, and `createReturn`/`createReversal` model ACH failures we don't simulate at all. |
| `mcp-grafana` | https://github.com/grafana/mcp-grafana | Grafana's official Go server — **104 unique tools** across dashboards, 11 datasource query languages, incidents, OnCall, Sift, alerting, admin/RBAC. Two independent auth layers (server→Grafana env/headers; caller→MCP `RequireBearerToken` with **constant-time** hash compare that strips the header before downstream calls). Tool gating by **named category** (`--enabled-tools`, `--disable-write`, 13 categories off by default). Server-clamped pagination (`limit<=0→50`, `>100→100`). Two-tier errors: `IsError:true` by default vs `HardError` for protocol-level. Plus `unmarshalWithTypeCoercion` (`"42"`→`42`) for LLM type slop. | 4.9 MB | Our density/quality reference. Concretely: it is the only server here with a **deliberate two-tier error model** and with **defensive coercion of model type errors** — both worth mirroring in `mcp/lib/framework.py`. Apache-2.0. |

## 4. ERP / finance workflow implementations

| Repo (dir) | URL | What it contains | Size | Why it matters to finance-world |
|---|---|---|---|---|
| `erpnext` *(sparse)* | https://github.com/frappe/erpnext | Full ERPNext source minus `erpnext/locale/` (107 MB of .po files). **192 doctypes under `accounts/`** and ~50 accounting reports, each doctype = JSON field schema + Python business logic + tests. Also `buying/` (purchase_order, supplier_scorecard) and `selling/` (customer_credit_limit, sales_order). | 43 MB | The single richest **open-source model of real AP/AR/GL mechanics** — field-level schemas and posting logic we can mine for realistic state and for task ideas (see §6). **GPL-3.0 — mine the schema, not the code.** |
| `d365-fasttrack-finance` *(sparse)* | https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets | Only `ERP/Finance/**` checked out (repo total is 751 MB). Content is thin: an **Invoice Capture** (OCR AP automation) guide incl. price-unit handling, and a customer-statement-printing optimization note. Excluded: a 96 MB installation-walkthrough MP4 and all non-Finance modules. | 2.1 MB | Marginal. Its one contribution is the **OCR invoice-capture → PO-match → price-unit mismatch** workflow, which is a real AP exception type. MIT. |

---

## 5. Skipped / not found

| Item | Verdict | Why |
|---|---|---|
| `patronus-ai/financebench` (full) | **Partial only** | HEAD tree 709 MB; `pdfs/` alone is 705 MB (INTEL 10-Ks are 25–38 MB each). Data + results taken, PDFs skipped. Re-fetch individual PDFs on demand from the URLs in `financebench_document_information.jsonl`. |
| `sierra-research/tau2-bench` (full) | **Partial only** | HEAD tree 815 MB. `data/tau2/results/` = 604 MB of published model runs, `telecom/tasks_voice.json` = 62 MB, plus voice audio. Framework + domains kept. |
| `frappe/erpnext` (full) | **Partial only** | HEAD tree 140 MB — just under the cap, but 107 MB of it is translation `.po` files with zero research value. Excluded them; kept 100% of the code. |
| `microsoft/Dynamics-365-FastTrack-Implementation-Assets` (full) | **Partial only** | HEAD tree 751 MB (Administration 459 MB, Customer Service 133 MB, ERP 131 MB) and mostly solution binaries/videos. Only `ERP/Finance` taken. |
| `chentonghao/FinMCP-Bench` (full) | **Partial only** | A 405 MB `.venv/` is committed to the repo. Excluded; the actual project is 0.5 MB. |
| `kensho-technologies/bizbench` | **Does not exist** | 404. BizBench (ACL 2024, arXiv:2311.06602) ships as a **HuggingFace dataset** (`kensho/bizbench`) with a held-out test set behind benchmarks.kensho.com. Cloned the official runner (`benchmarks-pipeline`) instead; get the data via `datasets`. |
| SECQUE official repo | **No code repo** | arXiv:2504.04596; data is HF `nogabenyoash/SecQue`. Cloned `EnvCommons/SECQUE`, an OpenReward env wrapper (no parquet). |
| Vals AI "FinanceAgentBenchmark" | **Named differently** | Lives at `vals-ai/finance-agent` and `vals-ai/finance-agent-v2` — both cloned. |
| AccountingBench (Penrose) | **Not open source** | accounting.penrose.com is a closed JS app. Cloned `SakethKoona/accounting-bench`, a faithful HUD-env replication with schema + CPA baselines. (`mkaburek-wu/AccountingBench` is 534 MB — over cap, and unaffiliated.) |
| **FinMaster** | **No repo found** | arXiv:2505.13533 (FinSim + FinSuite 183 tasks + FinEval). Exhaustive GitHub search returns nothing; paper ships no code link. Paper-only. |
| **FinBalance** | **No repo found** | arXiv:2606.15949 (multi-document accounting reconciliation, 710 records, 23 inconsistency codes, 5 difficulty levels, BS_exact vs BS_recon). No code/data released. Paper-only — but see §6, the design is reproducible from the abstract. |
| Official Intuit QuickBooks MCP | **Found & cloned** | `intuit/quickbooks-online-mcp-server` — official, Apache-2.0. |
| Official Modern Treasury MCP | **Does not exist** | The `Modern-Treasury` org publishes SDKs + `modern-treasury-openapi` only. Took the OpenAPI spec (authoritative) plus a community MCP wrapper. |
| `TheAgentCompany` | **Found & cloned** | Canonical repo is `TheAgentCompany/TheAgentCompany`. |

---

## 6. What these add that finance-world doesn't cover yet

Cross-referenced against the 15 task dirs in `tasks/`, the 7 servers in `mcp/servers/`, and
§5 of `research/evals-and-benchmarks.md`. Only genuinely *new* items are listed.

**New eval task types**

1. **Scale/unit as a graded field** (TAT-QA). 5,543 arithmetic questions each carry a required
   `scale` label; a right number with the wrong magnitude scores zero. Our verifiers compare
   values, not units — a one-line probe addition with real discriminative power.
2. **Tool-plan grading, incl. expected parallel calls** (FinMCP-Bench). Grade the *sequence* of
   tool calls against a gold plan (precision/recall/F1) rather than only the final state, with
   `para_tool_call_number` as an explicit difficulty axis. Our oracle walks already encode the
   gold plan — this is nearly free signal about *how* the agent got there.
3. **Refusal as a first-class label** (financebench `results/`). Its 16 run files score
   Correct / Incorrect / **Refusal** separately. We have empty-answer traps but score them
   binary; splitting "wrongly refused" from "wrongly answered" would sharpen the too_hard call.
4. **Multi-month drift** (accounting-bench `multi-month-close`). One task, three sequential
   months, where month 2's errors compound into month 3 — deferred revenue on annual contracts,
   a December bonus accrual that must be *reversed*, and AWS prepaid capitalization with monthly
   amortization. Our `close_mgmt` is single-period.
5. **Multi-document reconciliation with inconsistency codes** (FinBalance, paper-only but
   reproducible): from a bundle of OCR'd source docs — deliberately mixed *posting*, *support*,
   and **distractor** documents — emit **cited** journal entries, a balance sheet, and a code
   from a fixed taxonomy for each inconsistency found. Grading via **BS_recon** (replay the
   statements back through a ledger) is the strongest anti-plug-entry design published, and it
   answers the reward-hacking failure mode AccountingBench documents.
6. **Conversational decomposition with cross-turn references** (ConvFinQA). 11,104 turns where
   turn *n*'s program references turn *n−1*'s *result* (`#0`). Our multi-turn `session` support
   exists but no task currently requires carrying a computed value across turns.

**New workflow scenarios (mostly from ERPNext's 192 accounting doctypes + the MT spec)**

7. **Payment reconciliation / un-reconciliation** (`payment_reconciliation`,
   `process_payment_reconciliation`, `unreconcile_payment`): match unapplied payments and
   customer advances against open invoices with a partial-allocation queue — and, harder,
   *undo* a mis-application and re-apply it. Our `cash_app` applies cash; it never corrects it.
8. **Withholding tax with thresholds** (`tax_withholding_category` → `tax_deduction_basis`,
   `cumulative_threshold`, `transaction_threshold`, `tax_on_excess_amount`): compute 1099/TDS
   withholding on a vendor payment where the rate applies only to the excess over a
   *cumulative year-to-date* threshold. Pure arithmetic on ledger state — exactly verifiable.
9. **Dunning with interest and fees** (`dunning`: `rate_of_interest`, `dunning_fee`,
   `total_interest`, `overdue_payments` child table): our `collections_ops` escalates a letter
   *level*; ERPNext computes the interest and fee that go on the dunning notice.
10. **FX revaluation at period end** (`exchange_rate_revaluation` → `make_jv_entries`,
    unrealized gain/loss account, `pegged_currencies`): revalue open foreign-currency AR/AP and
    post the unrealized gain/loss JE. We have multi-currency data and no revaluation task.
11. **Period close and lock** (`accounting_period`, `period_closing_voucher`,
    `repost_accounting_ledger`): attempt a backdated posting into a closed period, then either
    refuse correctly or reopen/repost. A clean "does the agent respect controls?" probe.
12. **Rule-based bank auto-match + internal transfers** (`bank_transaction_rule`,
    `auto_reconcile_vouchers`, `create_internal_transfer`, `search_for_transfer_transaction`,
    report `cheques_and_deposits_incorrectly_cleared`): our `bank_rec` classifies into four
    buckets; the real trap is a **transfer between two of the company's own bank accounts**
    appearing as an unmatched debit *and* credit, which a naive agent books twice.
13. **ACH returns and payment reversals** (MT `createReturn`, `createReversal`,
    `createExpectedPayment`): a payment that settles, then bounces back days later (R01
    insufficient funds), must be un-applied and the invoice re-opened. Nothing in the world
    currently models a payment *failing after the fact*.
14. **Deferred revenue / prepaid amortization schedules** (`process_deferred_accounting`,
    `deferred_revenue_and_expense`, `subscription`): recognize one month of a 12-month contract.
15. **Supplier scorecard** (`supplier_scorecard` + criteria/period/variables): score a vendor
    from delivery and invoice-accuracy history — a natural escalation of `vendor_master`.
16. **Statement-of-account run** (`process_statement_of_accounts`, `psoa_*`): generate and send
    per-customer statements for a filtered set — a bulk, multi-entity write task.
17. **Ledger integrity bisect** (`bisect_accounting_statements`, `ledger_health_monitor`,
    report `invalid_ledger_entries`): given "the trial balance stopped balancing sometime this
    quarter", *find the date and the entry*. A genuinely agentic search task with an exact answer.
18. **OCR invoice capture → PO match with unit mismatch** (D365 FastTrack): the vendor invoices
    per-case while the PO is per-each; the price-unit mismatch is the exception. A concrete
    third exception type for the parked `threeway_match` family.

**New scenarios from TheAgentCompany's `finance/` suite** (12 tasks, none previously mined)

19. **Ask a colleague for a blocking input.** In `finance-apply-tax-credit` and
    `finance-find-signatories` the agent *must* message an NPC (finance director / sales
    director) on chat to get a folder path or resolve an ambiguity — the information exists
    nowhere else. Our world's `email_server` is read-only, so no task can require obtaining a
    missing fact from a person. This is the largest structural gap the survey found.
20. **Fill a real regulatory form.** `finance-apply-tax-credit`: complete **IRS Form 6765
    Section B (Alternative Simplified Credit)** from a wages CSV + a financials CSV, consulting
    the instructions PDF, and save the filled PDF. A form-filling deliverable, not a text answer.
21. **Budget-vs-actual variance with a compound flag rule.** `finance-budget-variance`: flag a
    department/category/month only when the variance exceeds **both 10% and $5,000**, after a
    seasonality adjustment; deliver the flagged keys as `Department_Category_YYYYMM`. Pairs with
    ERPNext's `budget_variance_report` / `monthly_distribution` (seasonal budget spreading).
22. **Signatory / delegation-of-authority extraction.** `finance-find-signatories`: pull
    name/title/company/date of every signature out of filing PDFs into a CSV, then report the
    count back to a named person. Authority-matrix questions ("who can approve this?") are a
    natural fit for our `pbc` and `payment_proposal` families.
23. **Payroll ↔ attendance reconciliation** (`finance-check-attendance-payroll`) and
    **expense-policy qualification** (`finance-expense-validation`, qualified vs non-qualified
    reimbursement) — a payroll subledger and a policy-driven expense decision, neither modelled.

**New environment / grading mechanics**

24. **Knowledge-retrieval as a difficulty axis** (τ² `banking_knowledge`): 97 tasks share a
    **698-document knowledge base**, and `--retrieval-config` swaps the agent's access to it —
    `no_knowledge`, `full_kb` (everything in context), `golden_retrieval`, `grep_only`, `bm25`,
    `openai_embeddings`, `qwen_embeddings`, `terminal_use` (a real shell), `alltools` — with
    `_reranker` and `_grep` suffixes composing. Same task, seven difficulty settings, no
    re-authoring. Our `docs_server` holds SOPs and policies and exposes exactly one retrieval
    mode; this is the cheapest available lever for growing tasks that came back `too_easy`.
25. **Discoverable / unlockable tools** (τ² `banking_knowledge`:
    `list_discoverable_agent_tools`, `unlock_discoverable_agent_tool`,
    `call_discoverable_agent_tool`, `give_discoverable_user_tool`): the tool surface is not
    fixed at t=0 — capabilities are revealed or handed over mid-conversation. A clean way to
    force genuine exploration instead of a memorized walk.
26. **Composable reward bases** (τ² `reward_basis`): the score is the *product* of any subset of
    DB-equality, environment assertions, communicated-info checks, NL assertions, and
    action-trajectory matching; unlisted components still run as diagnostics. That last part is
    exactly what we want for flake triage — measure more than you grade.
27. **Permission variants as difficulty** (Ramp scope-gating, QuickBooks
    `DISABLE_WRITE/UPDATE/DELETE` by name prefix, Grafana `--disable-write`): ship the same task
    against a read-only vs read-write tool surface and see whether the agent finds the legal
    path. All three production servers do this; our `erp_server` has role filtering but no
    task-level variant that exercises it.
28. **SQL-over-loaded-data as a tool idiom** (Ramp): load once into SQLite, then let the model
    query. Combined with Ramp's **integer minor units** convention ("1000 = $10.00"), this is a
    realistic and nasty precision trap — a correct SQL aggregate reported 100× too large.
29. **Contamination-resistant graders** (TheAgentCompany): evaluators ship **Fernet-encrypted**
    (`evaluator.py.enc`, key via env) so a browsing agent can't read its own rubric. Worth
    considering before any public release of finance-world tasks.

**Tool-surface gaps worth closing**

- No **T&E / corporate-card** system (`ramp_mcp`) despite an `expense_audit` family.
- No **payment-rails / bank** surface (`modern-treasury-openapi`) — payments are executed
  inside the ERP mock, so returns, reversals and expected-payment matching are unreachable.
- No **second books dialect** (`xero-mcp-server`) for the subsidiary fragmentation story.
