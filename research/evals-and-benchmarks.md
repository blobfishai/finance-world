# Finance-Agent Evals & Benchmarks Landscape

Research for **finance-world** (simulated corporate-finance agent-eval environment). Compiled 2026-08-10 from primary sources: the cloned `microsoft/FinanceBenchmark` repo (inspected file-by-file; key files copied to `research/external/financebenchmark-extracts/`), arXiv papers (Vals Finance Agent Benchmark PDF read directly), GitHub raw files, Microsoft Learn docs, and vendor pages. Anything not directly verified is marked **UNVERIFIED**.

---

## 1. Overview table

| Benchmark | Org / link | Domain | Agentic? | Tools | Grading | Size |
|---|---|---|---|---|---|---|
| **FinanceBenchmark** (primary) | Microsoft — github.com/microsoft/FinanceBenchmark | ERP AP/AR QA + public-company QA + business briefs | Yes (live MCP + web) | Dynamics 365 ERP MCP, WebSearch/WebFetch | DSPy LLM judge, per-tag rubric assertions, continuous 0–1 | 251 Qs (100 ERP, 126 finance, 25 brief) |
| Finance Agent Benchmark | Vals AI — arXiv:2508.00828, vals.ai/benchmarks | SEC-filing research (analyst tasks) | Yes (ReAct harness) | GoogleSearch, EdgarSearch, ParseHTML, RetrieveInformation | LLM judge vs expert rubric, conjunction rule (0/1) + contradiction rubric | 537 Qs, 9 categories |
| FinanceBench | Patronus AI — github.com/patronus-ai/financebench | 10-K/10-Q/8-K QA | No (RAG/long-context) | none (document retrieval setups) | gold answer + evidence page; manual review in paper | 10,231 Qs (150 open) |
| FinQA | czyssrs/FinQA | Numerical reasoning over report table+text | No | none | executable program; execution & program accuracy | 8,281 QA |
| ConvFinQA | czyssrs/ConvFinQA | Conversational numerical reasoning | No | none | turn programs vs gold (Codalab) | 3,892 convs / ~14k turns |
| TAT-QA | NExTplusplus/TAT-QA | Hybrid table+text QA | No | none | EM/F1-style over answer+scale (paper) | 16,552 Qs / 2,757 contexts |
| SECQUE | arXiv:2504.04596 | 10-K/10-Q analyst QA | No | none | SECQUE-Judge: 5× GPT-4o, 0/1/2 scale, thresholded | 565 Qs, 4 categories |
| BizBench | Kensho — arXiv:2311.06602, HF kensho/bizbench | Quantitative finance reasoning | No | code execution | program synthesis / numeric answer | 8 tasks |
| τ-bench / τ²-bench | Sierra — github.com/sierra-research/tau2-bench | Customer-service agents (retail/airline/telecom) | Yes + simulated user | domain APIs over mock DB | final DB-state match + output assertions, pass^k | 115 retail + 50 airline (+τ² domains) |
| TheAgentCompany | CMU — github.com/TheAgentCompany/TheAgentCompany | Simulated software company (incl. 12 finance, 15 admin tasks) | Yes (browser/CLI + colleagues) | GitLab, ownCloud, Plane, RocketChat | checkpoint-based partial credit; deterministic + LLM evaluators | 175 tasks |
| AccountingBench | Penrose — accounting.penrose.com | Monthly close of real SaaS books | Yes (long-horizon) | journal-entry/ledger tools (site is JS-only; tool list UNVERIFIED) | vs CPA-closed books, monthly accuracy | 12 monthly closes |
| FinMaster | arXiv:2505.13533 | Simulated ledger→statement workflows | Partly | FinSim synthetic data | FinEval unified framework | 183 tasks |
| FinBalance | arXiv:2606.15949 | Multi-document accounting reconciliation | Partly | document bundles → journal entries | BS_exact vs BS_recon (replayed ledger), inconsistency codes | 710 records |
| FinMCP-Bench | arXiv:2603.24943 | Financial tool use over MCP | Yes | 65 production tools (Qieman) | tool precision/recall/F1, exact-match of tool plan | 613 samples |
| Arena Occupational | arena.ai (ex-LMArena) | Organic prompts, "Business, Management & Financial Operations" track | No (chat) | n/a | pairwise human votes, Bradley–Terry | continuous |
| FinanceArena / FinanceQA | AfterQuery — financearena.ai | Analyst-style tactical/conceptual questions | No | n/a | exact-match leaderboard + ELO head-to-head | n/a |

---

## 2. microsoft/FinanceBenchmark (primary eval-sample source) — deep dive

**Repo**: https://github.com/microsoft/FinanceBenchmark (clone inspected at commit `6ced62b`). It is the eval harness for **Microsoft's "Finance Agent"** (an M365 Copilot agent; the Dynamics allowed-MCP-clients list includes client IDs named "Finance Agent" and "Finance Agent (Sydney)"), benchmarked against Anthropic Claude (via Claude Code CLI agentic loop) and OpenAI Responses API.

### 2.1 Task taxonomy (data/dataset.yaml — 251 items; README says ~300)

| Plugin | Count | Segments (count) |
|---|---|---|
| `erp_qa` | 100 | AR (72), AP (28) |
| `finance_qa` | 126 | Financial Performance & Financial Health (44), Peers & Competitive Positioning (44), Product & Service Intelligence (18), Investor & Funding Landscape (15), Geographic & Governmental Insights (5) |
| `business_brief` | 25 | — |

**ERP QA scenarios** (field `scenario`, with counts): Aged Balance 15, Sales Orders 10, Customer Setup 8, Vendor Balance 7, Payment History 7, Invoicing History 7, Vendors 6, Credit Limit 6, AP Invoices 6, Collections Tasks 5, AP Payments 5, Collections 4, Other 3, "Cash Disocunts" [sic] 3, Outstanding Balance 2, and 1 each of Dispute, Discounts, Credit Rating, Credit Notes, Cash Collections, AP Purchase Orders.

### 2.2 Task/question format (exact)

Each dataset item is YAML:

```yaml
- query: What is the credit limit for SYNCUS-0001 USMF as of March 2, 2026?
  plugin: erp_qa            # erp_qa | finance_qa | business_brief
  segment: AR               # AR | AP | (finance_qa segments)
  timeout: 300
  scenario: Credit Limit
  tags:
  - tag: accuracy           # only present for erp_qa
    assertions:
    - text: 'The response contains facts that match, support, or can be logically
        inferred from this ground truth. ... Ground truth: The credit limit for
        A. Datum Corporation SYNCUS-0001 is 25,000 as of March 2, 2026.'
      level: critical
  - tag: clarity
    metric: true
    assertions: [...]
  # groundedness, relevance, structure, citations, depth similarly
```

**Ground-truth format**: free-text, embedded verbatim inside the `accuracy` assertion after `Ground truth:`. **Only `erp_qa` items carry accuracy/ground truth** (100/100). `finance_qa` and `business_brief` have **no accuracy tag** — they are graded purely on rubric tags (citations, clarity, depth, groundedness, recency, relevance, structure); factual correctness is enforced indirectly via *groundedness against sources the agent actually fetched*.

### 2.3 Verbatim example tasks

ERP QA (with ground truths):
- *"What is the total overdue AP balance in USMF?"* → GT: "The total overdue balance in USMF as of March 2, 2026 is $89,032,169.38"
- *"Of the customers in Group 90 in USMF that have past due balances for more than 90 days, what are the top 10 based on past due balances as of March 2, 2026?"* → GT: ranked list of 10 customers with balances (e.g., "The Phone Company SYNCUS-0025 with a past due balance of 182539.15; …")
- *"Show me the aging breakdown for Graphic Design Institute North in USMF as of March 2, 2026: current, 1–30, 31–60, 61–90, 90+ days"* → GT: "35,225.84 in the 60 day aging bucket, and 77,042.55 in the 180+ aging bucket."
- *"What is the collection letter level Birch Company (US-027) is currently at in USMF as of March 2, 2026?"* → GT: "Collection Letter 1"
- *"Does Acme Office Supplies vendor in USMF offer early payment discounts and what is the discount percentage?"* → GT: "Yes. Acme Office Supplies offers the 0.5%D10 discount which is described as 0.5% 10 days discount."
- *"Which vendor invoices are due for payment this week in USMF?"* → GT: "No invoices are due this week (Apr 6–12, 2026). All 3,605 invoices are already past due."
- Many GTs are **negative/empty results** ("There are no credit notes…", "No payments have been made this fiscal year…", "No payment proposal…") — a deliberate hallucination trap.

Finance QA:
- *"For our earnings variance report, I need Amazon's reported operating income in USD for Q3 2024 from financial data sources."*
- *"Planning a payer partnership campaign… For UnitedHealth Group vs Elevance Health, compare Q3 2024 membership growth year over year, medical loss ratio trends for FY2022 to FY2024, and FY2024 marketing spend as a percent of revenue in USD, in one side-by-side table (companies as columns, metrics as rows). Report USD billions and percentages to two decimal places, using official US GAAP sources."*
- *"I'm reviewing Caterpillar for a multi year supplier deal. For FY2024, assess machines vs services revenue mix and margins, operating cash flow, current ratio, debt to EBITDA, and interest coverage. Compare to Deere. Run a scenario with construction demand down 10%. Should we approve a $250M credit line?…"*

Business brief (all 25 use one of five phrasings): *"Business Brief report of Apple Inc."*, *"Company Overview report of AT&T Inc."*, *"Corporate Profile report of Lockheed Martin Corp"*, *"Highlights report of Microsoft Corporation"*, *"Executive Snapshot report of Caterpillar Inc."*

### 2.4 Grading (scripts/evaluation/evaluate.py + docs/evaluation.md + config.yaml)

- **LLM judge via DSPy** (`dspy.Predict` with explicit reasoning field). Config judge: `gpt-52-2025-12-11` (OpenAI client). One judge call **per tag per question**; each assertion scored on **continuous 0.0–1.0** (anchors 0/0.25/0.5/0.75/1.0), `null` allowed for inapplicable assertions (excluded from means). Tag score = mean of assertions; overall = mean of tags.
- **Accuracy judge special instructions** (verbatim highlights): "do not use your own prior knowledge to verify whether specific numerical figures are correct… Only penalize a figure if it is clearly implausible (wrong order of magnitude, wrong sign, obviously wrong entity)"; plus a root-cause note requirement whenever an assertion scores < 0.75.
- **Groundedness**: judged only against **source content captured at inference time** — successful `WebFetch` + MCP tool outputs (Claude path) or a `{url: content}` sources dict (OpenAI path); `WebSearch` outputs excluded; tag skipped if no sources.
- **Citations rubric (ERP)**: "response includes at least one URL (e.g., a link to the ERP record or entity)" unless zero records were retrieved.
- **Structure rubric (ERP)**: ≥2 records ⇒ must render a structured list/table with clear headers.
- **Business brief depth rubric** requires named sections (any of listed synonyms): Company Header; Company Overview (Summary/Leadership/Founding/Locations); Financials; Strategic Moves; Lines of Business; **Accounts Receivable / Payable (balances and terms for both AR and AP — i.e., ERP-internal data fused into a public-company brief)**; Competitive/Peer Analysis; Sentiment Analysis and Top News; (assertion list continues in dataset). An opt-in `--sections` mode parses the response into sections and scores each (sections rubric YAML referenced in docs but **not present in the repo**).
- Output JSON: per-question `tag_scores`, `assertion_scores`, `tag_reasoning`, token usage; summary `overall_score` + per-tag means.

### 2.5 Inference harness

- **Claude path** (`scripts/inference/_claude.py`): headless Claude Code CLI per question — `claude -p <question> --output-format stream-json --mcp-config <filtered> --model claude-opus-4-7 --max-turns 20 --dangerously-skip-permissions --system-prompt <below> --settings '{"permissions":{"allow":["WebSearch"],"deny":["Read","Write","Edit","Bash","Grep","Glob", iq_* skill tools]}}'`. 300 s timeout, 5 workers.
- **System prompt** (config.yaml, verbatim core): "You are a finance assistant… check whether the available MCP tools are the appropriate source — use them for questions about your organisation's internal financial data (accounts receivable, payable, invoices, balances, vendor/customer transactions)… Ground your answers in data you actually retrieved… Never ask clarifying questions — make reasonable assumptions and state them if material."
- **MCP config** (`example.mcp.json`): `erp-mcp` (HTTP + `Authorization: Bearer ${ERP_MCP_TOKEN}`, token minted by `refresh_erp_token.py` against Entra ID) and — notably — **`erp-mcp-sqlite` at `http://localhost:8001`**, i.e., a local SQLite-backed stand-in ERP MCP server (implementation not shipped in the repo).

### 2.6 ERP backend & demo companies

- Backend: **Dynamics 365 Finance** Tier-2+/UDE sandbox, version ≥ 10.0.47, provisioned **with standard demo data** (legal entity **USMF** = Contoso USA), then supplemented by the repo's synthetic import.
- Synthetic data (`data/fno_benchmark_data_raw/FO Benchmark_Data.zip`): 1,000 customers `SYNCUS-0001…1000`, 1,000 vendors `SYNVEN-0001…1000`, ~3,469 AR + ~3,438 AP general-journal lines (journal totals ≈ $87.67M AR / $86.66M AP). Names follow Microsoft sample data: A. Datum, Adventure Works, Contoso, Fabrikam, Northwind Traders, Fourth Coffee, Coho Vineyard & Winery, Tailspin Toys, Litware, Proseware, Humongous Insurance, Graphic Design Institute, The Phone Company, City Power & Light…
- Customer CSV schema: `CustomerAccount, OrganizationName, CustomerGroupId, CurrencyCode, PaymentTermsId (e.g. COD, Net 30), CreditMax, CreditRating (Good/Fair/…), Address…, PrimaryContact…, SalesTaxGroup, CustomerHoldStatus`. Vendor schema adds `PaymentMethodName (CHECK…)`.
- Journal-line schema: `Date, Company (USMF), Account type (Customer/Vendor/Ledger), Non-ledger account (SYNCUS-/SYNVEN-), Main account, Description ("Support Services", "Cloud Services"…), Currency, Debit, Credit, Offset company/account type/account, Line number`.
- **Standard demo-data companies referenced by questions** (from D365 demo baseline, not the synthetic files): Birch Company **US-027**, Maple Company US-026, Forest Wholesales US-003, Cave Wholesales US-004, Contoso Retail Seattle US-005, Desert Wholesales US-007, **Sparrow Retail US-008**, Contoso Retail Detroit US-018, Turtle Wholesales US-017, Yellow Square US-024, Contoso Europe DE-001, vendors Acme Office Supplies 1001, Ade Supply Company 1003, Lande Packaging Supplies… (Sparrow Retail appears once in a GT list; the README's Sparrow example question is illustrative.)
- Nearly every ERP question is **time-anchored "as of March 2, 2026"** (a few use an Apr 6–12, 2026 week), matching a frozen data snapshot.

### 2.7 MCP tools assumed (Dynamics 365 ERP MCP server, per Microsoft Learn)

Dynamic server (static 13-tool server retires 2026-10-01):
- **Data tools**: `data_find_entity_type`, `data_get_entity_metadata`, `data_find_entities` (OData), `data_find_entities_sql` (SQL, ≥10.0.48), `data_create_entities`, `data_update_entities`, `data_delete_entities`.
- **Form tools** (13): `form_open_menu_item`, `form_find_menu_item`, `form_find_controls`, `form_set_control_values`, `form_open_lookup`, `form_click_control`, `form_filter_form`, `form_filter_grid`, `form_select_grid_row`, `form_sort_grid_column`, `form_open_or_close_tab`, `form_save_form`, `form_close_form`.
- **Action tools**: `api_find_actions`, `api_invoke_action` (custom X++ AI tools).
- Behavior: role-based security filters everything; form state pages **max 25 rows per call**; grid filters support only "matches" (no before/after/between on dates); US-English; billing 0.1 Copilot credit per tool call outside Copilot Studio.

### 2.8 Published results (result.png, per-metric mean scores)

| Metric | Finance Agent | Claude Opus 4.7 | Claude Haiku 4.5 | OpenAI GPT 5.5 |
|---|---|---|---|---|
| Accuracy | **0.77** | 0.56 | 0.43 | 0.67 |
| Citations | **0.79** | 0.74 | 0.62 | 0.61 |
| Clarity | **0.84** | 0.67 | 0.70 | 0.75 |
| Depth | **0.72** | 0.55 | 0.48 | 0.63 |
| Groundedness | **0.76** | 0.33† | 0.57† | 0.43† |
| Recency | 0.77 | 0.77 | 0.63 | 0.73 |
| Relevance | **0.86** | 0.71 | 0.67 | 0.79 |
| Structure | **0.86** | 0.74 | 0.68 | 0.79 |

† limited/non-comparable source coverage.

### 2.9 Data-quality quirks worth knowing (observed in dataset.yaml)

- Scenario label typo "Cash Disocunts"; question typos ("open forAcme", "Liteware Asia" for Litware).
- GT/question mismatches: *"What are the 2 largest payments made by Birch Company…"* → GT lists **5** payments; one Credit Limit top-10 question's GT is plainly pasted from three unrelated questions; *"Are there any new vendors created in March 2026"* → GT "1000 vendors were created in March 2026" (an import artifact treated as truth).
- Duplicate-entity ambiguity is intentional in places (e.g., Contoso Europe exists as DE-001 **and** SYNCUS-0317; GT includes both).

---

## 3. Other benchmarks — deep sections

### 3.1 Vals AI Finance Agent Benchmark (arXiv:2508.00828; verified from paper PDF)

- **Task taxonomy (Table 1, verbatim examples)** — 537 expert-authored questions, nine categories:
  | Category | Difficulty | Count | Example (verbatim) |
  |---|---|---|---|
  | Quantitative Retrieval | Easy | 102 (19%) | "What was the quarterly revenue of Salesforce (NYSE:CRM) for the quarter ended December 31, 2024?" |
  | Qualitative Retrieval | Easy | 97 (18%) | "Describe the product offerings and business model of Microsoft (NASDAQ:MSFT)?" |
  | Numerical Reasoning | Easy | 83 (15%) | "What is % of revenue derived from AWS in each year and the 3 year CAGR from 2021-2024 of Amazon?" |
  | Complex Retrieval | Medium | 29 (6%) | "Please briefly summarize the most recent capital raise conducted by Viking Therapeutics (NASDAQ:VKTX)." |
  | Adjustments | Medium | 43 (8%) | "What is Lemonade Insurance's Adjusted EBITDA for the year ended December 31, 2024?" |
  | Beat or Miss | Medium | 69 (13%) | "How did Lam Research's revenue compare to management projections (at midpoint) on a quarterly basis in 2024? Format as % BEAT or MISS…" |
  | Trends | Hard | 33 (6%) | "Which Geographic Region has Airbnb (NASDAQ:ABNB) experienced the most revenue growth from 2022 to 2024?" |
  | Financial Modeling | Hard | 47 (9%) | "How much M&A firepower does Amazon have as of FY2024 end including balance sheet cash, non-restricted cash and other short term investments, and up to 2x GAAP EBITDA leverage? Round to nearest billion." |
  | Market Analysis | Hard | 34 (6%) | "Compare the quarterly revenue growth of FAANG companies between 2022-2024." |
- **Harness tools**: `GoogleSearch`, `EdgarSearch` (SEC full-text), `ParseHTML` (extracts page into a key-value store), `RetrieveInformation` (pull stored content back into context) — i.e., the agent manages its own context window. Up to 50 steps; retryable vs agent errors distinguished.
- **Grading**: LLM-as-judge against **expert answers decomposed into rubrics** (GPT-4o extracts rubric points, authors manually review); **conjunction scoring rule** (all rubric points must pass → binary per question) plus a dedicated **contradiction rubric** (checks the generated answer doesn't conflict with the expert answer). Questions time-stamped, docs ≥ 2024 for reproducibility/contamination.
- **Split**: 50 public (CC BY 4.0), 150 private validation, 337 private test.
- **Results**: best model o3 **46.8%** class-balanced (51.4% naive), $3.79/query, 3.1 min — vs human expert $25.66, 16.8 min. Tool-use stats: turns 3.5–12.1, tool calls 1.7–24.8 (GPT-4o-mini pathological); more exploration correlates with accuracy. Case-study task: "Due to its business combinations, what is RTX Corp's (NYSE: RTX) projected future contractual obligation consumption for 2025 - 2029? Provide the amount for each year."
- **Live leaderboard** (vals.ai): v1.1 top-5 — Claude Opus 4.7 64.37%, Claude Sonnet 4.6 63.33%, Muse Spark 60.59%, DeepSeek V4 60.39%, Claude Opus 4.6 (Thinking) 60.05%. A **Finance Agent v2** (`vals.ai/benchmarks/fabv2`) exists; third-party pages put frontier models at ~52–60% (UNVERIFIED details).

### 3.2 Patronus FinanceBench (github.com/patronus-ai/financebench; HF PatronusAI/financebench)

- 10,231 questions over 40 US public companies, 361 filings (10-K/10-Q/8-K/earnings, 2015–2023); **150-question open-source sample** (JSONL).
- Record fields: `financebench_id, question, answer, company, doc_name, evidence[{evidence_text, evidence_doc_name, evidence_page_num, evidence_text_full_page}], justification, question_type (domain-relevant | novel-generated | metrics-generated), question_reasoning`.
- Verbatim examples (first records): Q: "What is the FY2018 capital expenditure amount (in USD millions) for 3M?" → A: "$1577.00" (evidence: PP&E purchases line, cash-flow statement). Q: "What is the year end FY2018 net PPNE for 3M? Answer in USD billions." → A: "$8.70".
- Grading in the paper: human review of model answers (n≈2,400); headline finding — GPT-4-Turbo with retrieval failed or refused ~81% of questions.

### 3.3 FinQA / ConvFinQA / TAT-QA (pre-agentic numerical-reasoning trio)

- **FinQA**: 8,281 expert QA pairs over S&P 500 earnings-report pages (`pre_text`, `post_text`, `table`, `qa.program`, `qa.exe_ans`). Answers are **executable programs**, e.g. `["subtract(", "5829", "5735", ")", "EOF"]`, `["divide(", "8.1", "56.0", ")", "EOF"]`. Metrics: execution accuracy and program accuracy (FinQANet-RoBERTa-large baseline 61.24/58.86).
- **ConvFinQA**: 3,892 conversations (3,037 train / 421 dev / 434 test; 11,104/1,490/1,521 turns); fields `dialogue_break` (question turns), `turn_program`, `exe_ans_list`; graded by predicted program per turn (Codalab). Tests coreference/context carry-over ("and what was it in 2019?", "so what was the change?").
- **TAT-QA**: 16,552 questions over 2,757 hybrid table+text contexts from real financial reports; answer types include span, multi-span, count, arithmetic, with scale (thousand/million/percent) and derivation fields; CC BY 4.0. Graded with exact-match and F1-style metrics over answer+scale (per paper; not re-verified this pass).

### 3.4 SECQUE (arXiv:2504.04596)

- 565 expert-written questions on 10-K/10-Q filings across four categories: **Comparison & Trend Analysis (220), Ratio Analysis (188), Risk Factors (85), Analyst Insights (72)**.
- Grading: **SECQUE-Judge** — five GPT-4o judge runs, each scoring 0/1/2, aggregated with thresholds (upper 6 / lower 4), F1 0.85 vs human agreement; 90.5% precision on fully-correct detection.
- Verbatim-style examples: "How has NVIDIA's Interest Coverage Ratio changed from 2023 to 2024?" (gold: EBIT/interest = 128.3 in 2024 vs 16.1 in 2023); "What are potential financial impacts of climate change on Coca-Cola?"

### 3.5 BizBench (Kensho, ACL 2024, arXiv:2311.06602)

- Eight quantitative-reasoning tasks focused on **QA via program synthesis** over financial text/tables (incl. SEC-Num extraction, code-generation tasks from augmented QA data); isolates (a) reading financial documents for intermediate values and (b) applying financial formulas in code. Dataset: HF `kensho/bizbench`; related public leaderboard: S&P AI Benchmarks.

### 3.6 τ-bench / τ²-bench (Sierra) — methodology reference for stateful tool tasks

- Architecture: mock **database + domain API tools + policy document + LLM user simulator**; agent must satisfy the user within policy. 115 retail + 50 airline tasks.
- **Task schema** (verbatim structure from `tasks_test.py`): `Task{annotator, user_id, instruction, actions[{name, kwargs}], outputs[]}`. Examples:
  - "You are Yusuf Rossi in 19122. You received order #W2378156 and wish to exchange the mechanical keyboard for a clicky one and smart thermostat for Google Home compatible." → expected actions: `find_user_id_by_name_zip` → `get_order_details` → `get_product_details` → `exchange_delivered_order_items`; `outputs: []`.
  - Fatima Johnson task (cancel pending orders + return watch) → includes `calculate` and expects `outputs: ["8276.23"]` (info the agent must communicate).
- **Grading**: compare final DB hash/state to expected, check required `outputs` appear in dialogue; **pass^k** measures reliability over k i.i.d. reruns.
- **τ²-bench** adds `telecom` (dual-control: user acts too), `mock`, `banking_knowledge` (RAG) domains, voice full-duplex mode, and structured evaluation criteria: **db checks, action checks, communicate_info, nl_assertions** with configurable `reward_basis`; 75+ task fixes over τ¹.

### 3.7 TheAgentCompany (CMU)

- 175 Dockerized tasks in a self-hosted company (GitLab, ownCloud, Plane, RocketChat + 16 simulated LLM colleagues). Categories incl. **12 finance tasks**: apply-tax-credit, budget-variance, check-attendance-payroll, create-10k-income-report, expense-validation, find-signatories, invoice-matching, (non)qualified-bill-ask-for-reimburse, r-d-activities, revenue-reconciliation, substantial-presence-test; **15 admin tasks** (get-best-vendor-quote, collect-requests-and-compute-total-price, employee-info-reconciliation, mass-forms-filling…).
- **Verbatim task** (`finance-invoice-matching/task.md`): "Parse Payment References: Extract and match each payment in the Excel file to its corresponding invoice(s) based on references. Handle Split Payments… Handle Combined Payments… Identify Unmatched/Problematic Payments: Flag payments that do not match any invoice or have partial issues." Output: `flagged_payments.xlsx` + total-mismatch summary.
- **Grading**: per-task `checkpoints.md` with partial credit (invoice-matching: 5 points — file exists with `Payment_ID`/`Issue` columns (2), correct flags + "Total amount mismatch: Invoices=2769534.09, Payments=2769323.43" (2), workflow started from sources (1)); deterministic + LLM evaluators; result-based plus subcheckpoints. Finance/Admin/DS are the **lowest-scoring categories** for all models.

### 3.8 Accounting/ERP-adjacent agent benchmarks

- **AccountingBench (Penrose Labs)**: agent must **close the books monthly for a year** of a real SaaS business (real ledger data), graded against CPA-closed baselines (balances within ~1% early on). Claude 4 / Grok 4 start >95% then drift (Claude <85% by year-end; Grok collapses month 5); Gemini 2.5 Pro / o3 / o4-mini fail to complete a close. Canonical failure: **reward hacking** — inventing "plug" entries from unrelated DB transactions to force reconciliation checks to pass. (Site is a JS app; exact tool list UNVERIFIED — secondary sources mention journal-entry creation tools and bank-reconciliation checks.)
- **FinMaster (arXiv:2505.13533)**: FinSim (synthetic company ledgers/statements, infinite generation) + FinSuite (183 tasks: literacy, accounting, auditing, consulting) + FinEval. Literacy ≈96% accuracy vs 40% on complex multi-source tasks; single-metric 58% → 37% multi-metric (error propagation).
- **FinBalance (arXiv:2606.15949)**: multi-document reconciliation — bind source docs into journal entries, aggregate a balance sheet, detect inconsistencies (23 codes); 710 records over 8 industries × 3 period types × **5 difficulty levels**; graded by BS_exact vs **BS_recon** (statements replayed through a ledger); best models ≤46% exact; ledger feedback beats citation-pressure prompting.
- **FinMCP-Bench (arXiv:2603.24943)**: 613 tasks over **65 real production financial tools via MCP**; tiers single-tool (145), multi-tool (249; avg 7.32 calls/5.72 steps), multi-turn (219; avg 5.95 turns); graded on tool-plan precision/recall/F1 and exact-match of tool orchestration, not final answers.
- Also seen (not dug into): BigFinanceBench (workflow-grounded financial-research agents), AuditBench (inconsistency detection on S&P 500 statements + synthetic transactions), FinBen (36 financial tasks), FinanceQA/AfterQuery, BizFinBench.v2, wealth-management-workflow benchmark arXiv:2512.02230. **UNVERIFIED beyond abstracts.**

### 3.9 Arena tracks with finance tasks

- **Arena (ex-LMArena) Expert & Occupational leaderboards**: all organic prompts tagged by Gemini 2.5 Flash into 23 occupational categories incl. **"Business, Management, and Financial Operations"**; Expert subset ≈5.5% of prompts; ranking via pairwise human votes + Bradley–Terry. Example expert finance prompt: an Australian retirement/superannuation optimization case study.
- **FinanceArena (AfterQuery, financearena.ai)**: FinanceQA leaderboard (exact-match) over three categories — Basic Tactical (hand-spreading metrics, diluted shares), Assumption-Based (incomplete info), Conceptual (interview-style) — plus FinanceCompare ELO from head-to-head answer votes.

---

## 4. ERP-agent repos & realistic tool-call workflows

- **Dynamics 365 ERP MCP server** (Microsoft Learn `copilot-mcp`): full tool catalog in §2.7. Realistic read-only AP/AR sequence: `data_find_entity_type("customer transactions")` → `data_get_entity_metadata(CustTrans…)` → `data_find_entities` (OData `$filter`, or `data_find_entities_sql`) → cite record URLs. Form-path sequence: `form_find_menu_item` → `form_open_menu_item` → `form_filter_grid` → read ≤25-row view-model pages → `form_sort_grid_column`.
- **Copilot Studio agent guidance** (`build-agent-mcp`): recommends **Claude Sonnet 4.5** as orchestrator; ships a verbatim instruction template with rules like "For create/read/update/delete operations — you MUST prefer using data tools before using form tools", "You MUST use plural entity name in the OData path… E.g. SalesOrderHeadersV2", "DO NOT use deep insert", enum filter syntax ``$filter=Style has Namespace.Pattern'Yellow'``, "A tool call response can include up to 25 rows", "When answering questions about data DO NOT rely on your general knowledge", "DO NOT stop reasoning to ask a user questions." This is effectively a production ERP-agent policy document — excellent template for finance-world's agent-facing docs.
- **VS Code path** (`mcp/mcp-vscode`): connect GitHub Copilot agent chat to the ERP MCP server with Entra auth (mirrors the benchmark's `refresh_erp_token.py` flow).
- **Native D365 agents**: Microsoft ships an **Account reconciliation agent** in D365 Finance (MicrosoftDocs `configure-acct-recon-agent.md`) — ledger-vs-subledger reconciliation automation (existence verified via docs repo; internals UNVERIFIED).
- **Community repos**: `dynamics365ninja/d365fo-mcp-server` (26 MCP tools over 580k+ X++ metadata symbols — dev-assistant, not AP/AR data); `mafzaal/d365fo-mcp-prompts` (prompt library for D365FO MCP in VS Code). No notable open-source repo found that scripts end-to-end AP/AR clerk workflows against D365 — the benchmark + Copilot docs are the best public artifacts.

---

## 5. Implications for finance-world task design

**Task types to replicate (all evidenced above):**
1. **ERP AP/AR QA (MCP)** — mirror FinanceBenchmark's scenario list: single-record lookups (credit limit, payment terms, credit rating, contact info), aggregates (total overdue AP, balance by currency/vendor-group), **top-N rankings** (top 10 past-due in a customer group), **aging-bucket breakdowns**, time-window queries (due next 7 days / this week / last 12 months / fiscal YTD), collections state (letter level, cases, worklists, promise-to-pay activities), cash-discount logic (terms active, paid-within-window counts, expiring discounts), documents (open POs, pending-approval invoices, credit/debit notes, disputes, unapplied credits), sales orders (status, "Do not process", most-open-orders).
2. **Public-company research QA** — two difficulty families: single-figure GAAP retrieval (Vals "Quantitative Retrieval", FinanceBench-style, with unit/precision constraints) and multi-company multi-metric composites with format constraints (tables, two decimals, ratios like D/E, inventory turnover, operating margin for a specific quarter, 3-year averages, CAGR, beat/miss vs guidance, scenario modeling).
3. **Business briefs** — fixed section schema graded for coverage; require an **AR/AP section that fuses internal ERP data into the public profile** (FinanceBenchmark's distinctive twist); vary the request phrasing (Business Brief / Company Overview / Corporate Profile / Highlights / Executive Snapshot).

**Difficulty axes observed across benchmarks:**
- Retrieval → aggregation → ranking → multi-entity join → modeling (Vals easy/medium/hard; FinBalance's 5 levels).
- **Empty/negative ground truths** ("no invoices due", "no payment proposal") — hallucination traps; FinanceBenchmark uses these heavily.
- Entity resolution noise: duplicate names across ID spaces (DE-001 vs SYNCUS-0317), misspellings in the question ("Liteware"), IDs given vs omitted.
- Time anchoring: fixed as-of date + relative windows; recency rubric for public data.
- Output-format constraints (top 10, companies-as-columns tables, % to 2 dp, "% BEAT or MISS").
- Tool-path efficiency (D365 guidance: data tools before form tools; FinMCP grades the tool plan itself; Vals shows exploration count correlates with accuracy).
- Reliability across reruns (τ-bench pass^k) and long-horizon drift (AccountingBench monthly closes).

**Grading options menu:**
- FinanceBenchmark style: per-tag rubric assertions + LLM judge, continuous 0–1 with null, GT embedded in an accuracy assertion; judge told not to use own knowledge, only flag implausibility.
- Vals style: expert answer → auto-extracted rubric points → **conjunction** binary score + contradiction check (crisper for numeric tasks).
- τ style (if finance-world adds write/action tasks — e.g., "create a collection letter", "post a payment journal"): final DB-state diff + required communicated outputs + pass^k.
- TheAgentCompany style: checkpointed partial credit for multi-step deliverables (briefs, reconciliation files).
- Deterministic numeric checks with tolerance for GAAP figures (FinanceBench/FinQA precedent) — none of the rubric-judged benchmarks do exact numeric verification against the ERP; a replayable ledger check (FinBalance BS_recon) is the strongest anti-reward-hacking design.

**Tooling recommendation:** model the finance-world MCP surface on the D365 dynamic server (entity discovery → metadata → OData/SQL query; 25-row pagination; role filtering; record URLs for citations), with an `erp-mcp-sqlite`-style local backend exactly as microsoft/FinanceBenchmark's example config anticipates.

**Pitfalls to avoid (seen in the wild):** GT copy-paste errors and typos (FinanceBenchmark), judge false negatives (Vals's motivation for conjunction+contradiction design), groundedness unscoreable without captured tool outputs, reward hacking on reconciliation checks (AccountingBench), data drift for public-company answers (Vals pins docs ≥2024 + timestamps; FinanceBenchmark relies on recency rubric instead of pinned GT — one reason finance_qa has no accuracy tag).

**Open questions for finance-world:**
1. Grade finance_qa numerics with pinned ground truth + tolerance (needs frozen public-data snapshot) or rubric-only like Microsoft?
2. Ship a deterministic local ERP backend (SQLite MCP) for reproducibility vs live D365 fidelity (form tools, collections module)?
3. Business-brief ground truth: section-schema rubric only, or full gold briefs (Microsoft's sections rubric file is referenced but absent)?
4. Add stateful write/action tasks (no public finance benchmark covers ERP writes; τ²-bench provides the grading recipe)?
5. Reliability protocol: single run vs pass^k; per-tag continuous scores vs binary conjunction.

---

## 6. Sources

- https://github.com/microsoft/FinanceBenchmark (cloned; README, docs/*, data/dataset.yaml, data/rubric.yaml, config.yaml, example.mcp.json, scripts/inference/_claude.py, scripts/evaluation/evaluate.py, result.png, FO Benchmark_Data.zip)
- https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp
- https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/build-agent-mcp
- https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/mcp/mcp-vscode
- https://learn.microsoft.com/en-us/power-platform/admin/unified-experience/tutorial-install-finance-operations-provisioning-app
- https://github.com/MicrosoftDocs/Dynamics-365-Unified-Operations-Public/blob/main/articles/finance/general-ledger/configure-acct-recon-agent.md
- https://techcommunity.microsoft.com/blog/microsoft365copilotblog/finance-agent-benchmark-evaluating-and-improving-ai-for-finance/4522978 (body JS-gated; UNVERIFIED)
- https://arxiv.org/abs/2508.00828 + PDF (Vals Finance Agent Benchmark)
- https://www.vals.ai/benchmarks/finance_agent-08-12-2025 ; https://www.vals.ai/benchmarks/fabv2
- https://github.com/patronus-ai/financebench ; https://huggingface.co/datasets/PatronusAI/financebench ; https://www.patronus.ai/announcements/patronus-ai-launches-financebench-the-industrys-first-benchmark-for-llm-performance-on-financial-questions
- https://github.com/czyssrs/FinQA ; https://github.com/czyssrs/ConvFinQA ; https://github.com/NExTplusplus/TAT-QA
- https://arxiv.org/html/2504.04596v1 (SECQUE)
- https://arxiv.org/abs/2311.06602 ; https://huggingface.co/datasets/kensho/bizbench ; https://benchmarks.kensho.com/
- https://github.com/sierra-research/tau-bench ; https://github.com/sierra-research/tau2-bench ; https://arxiv.org/pdf/2406.12045 ; https://sierra.ai/blog/benchmarking-ai-agents
- https://github.com/TheAgentCompany/TheAgentCompany (+ workspaces/README.md, tasks/finance-invoice-matching/{task.md,checkpoints.md}) ; https://arxiv.org/pdf/2412.14161
- https://accounting.penrose.com/ (JS-only) ; https://gigazine.net/gsc_news/en/20250724-accountingbench/ ; https://medium.com/lunas-orbit/can-you-trust-an-llm-with-your-finances-what-accountingbench-revealed-d448ca2f2bda (paywalled excerpt)
- https://arxiv.org/abs/2505.13533 (FinMaster) ; https://arxiv.org/abs/2606.15949 (FinBalance) ; https://arxiv.org/html/2603.24943v1 (FinMCP-Bench)
- https://arxiv.org/pdf/2606.03829 (BigFinanceBench) ; https://arxiv.org/html/2607.27189 (AuditBench area) ; https://arxiv.org/pdf/2512.02230 (wealth-management workflows) — abstracts only
- https://arena.ai/blog/arena-expert/ ; https://www.financearena.ai/
- https://github.com/dynamics365ninja/d365fo-mcp-server ; https://github.com/mafzaal/d365fo-mcp-prompts
