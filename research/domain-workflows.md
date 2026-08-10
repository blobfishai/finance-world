# Finance-World Domain Research: How Real Corporate Finance Teams Work

Research date: 2026-08-10. Purpose: ground-truth for the `finance-world` Harbor world (agent answers AP/AR questions from a mocked ERP, researches public companies, writes business briefs). Buyer persona: finance team at a large AI company.

Claims are cited inline; anything without a source or based on general domain knowledge is marked **UNVERIFIED**. All URLs collected in the Sources section at the end.

---

## 1. Stakeholders & Roles

### 1.1 AP Clerk / AP Specialist
- **Recurring tasks**: Enter invoices into the ERP; run 3-way match (PO vs invoice vs goods receipt) on quantity and price before approving payment; route invoices through approval workflow; reconcile vendor statements; resolve discrepancies with purchasing/warehouse/receiving; respond to vendor payment-status inquiries; prepare payment runs; maintain vendor master data (Financial Professionals glossary; Ramp 3-way match guide; SignUp Software AP job description).
- **Questions they ask**: "Has invoice X been approved yet?" "Why doesn't this invoice match the PO?" "Did we already pay this?" "Which invoices are due this week / eligible for early-pay discount?" "Why is this vendor calling about an invoice we never received?"
- **Definition of done (per task)**:
  - Invoice processing: invoice matched (or exception resolved with documented reason), coded to correct GL account/cost center, approved per authorization matrix, scheduled for payment within terms. Best-in-class processes an invoice in 3.1 days vs 10.9-17.4 days average (Ardent Partners via Medius/Basware).
  - Vendor statement reconciliation: every line on the vendor's statement tied to an invoice/payment/credit note in the AP subledger; discrepancies (missing invoices, unrecorded credit notes) posted or disputed; vendor confirms corrected balance (Ramp, KlearStack vendor reconciliation guides).
- **KPIs**: cost per invoice ($2.78 best-in-class vs $10.89 average), invoice exception rate (9% best-in-class vs 22% average), straight-through processing rate (~35%+ best-in-class vs ~25% average) (Ardent Partners AP Metrics that Matter 2024/2025).

### 1.2 AR / Collections Analyst
- **Recurring tasks**: Issue invoices; process credit memos; apply cash daily (checks/lockbox, ACH, wires, credit cards); resolve unapplied cash; work the AR aging report and follow up on past-due balances; manage disputes, deductions, and chargebacks; escalate to collections (Financial Professionals AR job descriptions; Himalayas AR analyst guide).
- **Questions they ask**: "Who is >60 days past due and how much?" "Did customer Y's payment come in — and which invoices does it cover?" "Is this short-pay a dispute, a deduction, or an error?" "Which accounts need a call today?" "Why is there $40k of unapplied cash?"
- **Definition of done**:
  - Cash application: every receipt matched to specific open invoices same/next day; unapplied and on-account cash investigated and cleared; discrepancies (short pays) coded as dispute/deduction with owner (Emagia, HighRadius cash application guides).
  - Collections touch: contact logged, promise-to-pay date recorded, next action scheduled; dispute routed to the right internal owner. **UNVERIFIED** (synthesis of collections-software workflow descriptions).
- **KPIs**: DSO; Collection Effectiveness Index — CEI = (beginning AR + credit sales − ending AR) / (beginning AR + credit sales − ending *current* AR) × 100; >85% excellent, 70-84% good, <70% signals problems (Versapay, HighRadius, altLINE CEI guides); % AR current; unapplied cash aging (46% of finance teams cite unapplied cash sitting too long as a top challenge — Bill.com survey of 211 companies, via engini.ai).

### 1.3 Credit Manager
- **Recurring tasks**: Review new customer credit applications; set/approve credit limits; release or hold blocked orders; run periodic credit reviews (annual/biannual/quarterly per policy); monitor bankruptcy alerts and deteriorating payment patterns; prioritize a daily worklist (credit limit exceeded, blocked orders, new applications, expiring collateral, scheduled reviews) (HighRadius credit management workflows; Oracle Credit Management User Guide; Levelset credit manager role).
- **Questions they ask**: "Should we release this blocked order?" "What limit can we give this new customer?" "Has customer Z's financial position deteriorated since last review?" "Which public customers show leverage or liquidity red flags?"
- **Definition of done**: Credit decision documented (limit, terms, risk rating, rationale, review date); order released or hold justified; periodic review completed on schedule with updated financials and payment history (Oracle Credit Management User Guide).

### 1.4 Controller
- **Recurring tasks**: Own the month-end close calendar; review account reconciliations; approve journal entries; ensure subledger-to-GL ties; prepare monthly financial statements; enforce internal controls and compliance; oversee AP/AR teams day to day (CFI "FP&A vs Controller vs CFO"; Embat CFO/Treasurer/Controller comparison).
- **Questions they ask**: "Does the AP/AR subledger tie to the GL control account?" "What's unreconciled and who owns it?" "Are all accruals booked?" "Why did this account move vs last month?" "Are we on track to close by day 5?"
- **Definition of done**: All checklist tasks signed off; every balance-sheet account reconciled with support; variances explained; statements issued by the close deadline (FloQast month-end close checklist).

### 1.5 Treasury Analyst
- **Recurring tasks**: Daily cash positioning across bank accounts; short/medium-term cash forecasting; manage bank relationships and bank portals; oversee payment operations and approval workflows; debt covenant compliance; intercompany funding (Yardstick Treasury Analyst vs Financial Controller; Embat).
- **Questions they ask**: "What's our cash position today, by account and entity?" "Will this week's payment run plus payroll breach our minimum cash buffer?" "Which payments cleared the bank but aren't in the ERP yet?"
- **Definition of done**: Daily position report published before cutoff; funding moves executed; forecast variance within tolerance. **UNVERIFIED** (synthesis).

### 1.6 FP&A Analyst
- **Recurring tasks**: Budgeting and forecasting; variance analysis (actual vs budget/forecast); build financial models; consolidate inputs from departments; management reporting decks (CFI FP&A vs Controller; Nicolas Boucher).
- **Questions they ask**: "Why is opex 8% over budget in cloud spend?" "What is our vendor spend by category/vendor trend?" "What does DSO/DPO drift do to free cash flow?"
- **Definition of done**: Variance explained with driver-level commentary; forecast updated; deck delivered. **UNVERIFIED** (synthesis).

### 1.7 Procurement
- **Recurring tasks**: Raise and manage POs; onboard vendors (W-9, banking details, master data); negotiate terms (incl. early-pay discounts); resolve PO/receipt mismatches with AP; assess supplier financial health/viability for critical vendors (Kodiak Hub supplier financial risk assessment; Venminder).
- **Questions they ask**: "Is this vendor financially viable for a multi-year commitment?" (often answered with ratio analysis / Altman Z-score on public suppliers — Kodiak Hub, StableBread). "Which invoices failed match because receiving never posted?"
- **Definition of done**: PO issued before goods/services received (no maverick spend); vendor onboarded with verified bank details; supplier risk assessment documented for critical vendors. **UNVERIFIED** (synthesis).

---

## 2. Core Workflows & Scenarios (step by step)

### 2.1 Month-End Close: AP/AR Reconciliation
Canonical sequence (FloQast month-end close checklist; Numeric GL reconciliation guide; Tipalti month-end guide):
1. **Cutoff**: stop posting to the period; capture late invoices as accruals (goods/services received, no invoice = accrue; see GR/IR below).
2. **AP tie-out**: AP aging report → AP subledger → GL control account. All three must agree; investigate differences (journal entries posted directly to the GL control account, timing, unposted batches).
3. **AR tie-out**: AR aging → AR subledger → GL control account; verify revenue and receivable balances.
4. **Bank reconciliation**: bank statement vs cash GL; outstanding checks, deposits in transit, bank fees.
5. **GR/IR (goods-received-not-invoiced) analysis**: aged open items by PO line; <90 days = normal pipeline, 90 days-1 year = investigate with vendor/PO owner, >1 year = write-off candidate; SAP transactions F.13 (auto-clear) and F.19 (period-end regrouping) (Stampli GR/IR guide; SAP documentation; Basware GR/IR blog).
6. **Accruals & prepaids**: book recurring and estimated accruals; amortize prepaids.
7. **Review & sign-off**: controller reviews reconciliations, approves JEs, issues statements.
- Reconciling subledger vs GL surfaces: duplicate invoices, incorrect payment applications, unrecorded credit memos, unmatched customer payments (Solvexia; Numeric).
- **Data touched**: ERP subledgers + GL, aging reports, bank statements/portals, Excel reconciliation workpapers, close checklist (often Excel or FloQast-type tool).

### 2.2 Aged-Receivables Review & Collections Runbook (dunning escalation)
Aging buckets: current / 1-30 / 31-60 / 61-90 / 90+ days past due (CFI AR aging; HighRadius aging report guide).

Two documented escalation models to reproduce:
- **4-stage letter model**: friendly reminder (1-30 dpd) → firm follow-up (31-60) → urgent notice (61-90) → final demand (90+) (CreditPulse dunning letter guide; Finlens).
- **7-step operational runbook with owners** (CreditPulse dunning process guide):
  | Step | Days past due | Action | Owner |
  |---|---|---|---|
  | 1 | 1-3 | Soft email reminder | Credit analyst |
  | 2 | 7-10 | Follow-up email + dispute check | Credit analyst |
  | 3 | 14-17 | Phone call + email | Credit analyst |
  | 4 | 21-25 | Escalation notice; flag account; alert sales | Credit manager |
  | 5 | 30 | **Credit hold** placed; account review | Credit manager |
  | 6 | 45 | Formal demand letter | Credit director |
  | 7 | 60+ | Refer to collections agency / outside counsel | Credit director |
  Intervals are starting points, adjusted for invoice size and payment history (CreditPulse).
- First notice assumes oversight, not bad faith; tone escalates gradually; legal notice is last resort (Kolleno; Upflow).
- **Data touched**: AR aging from ERP, collections notes/CRM, email templates, dispute log (often a spreadsheet), credit-hold flag in order management.

### 2.3 Vendor Invoice → Approval → Payment Run (with cash-discount capture)
1. **Receipt**: invoices arrive by paper, email PDF, vendor portal, EDI — paper and email are the top two channels (PayStream via Edenred report); 68% of businesses manually key invoices into the ERP (DocuClipper AP statistics roundup).
2. **Capture & coding**: enter into ERP; code GL account/cost center; flag PO vs non-PO.
3. **Matching**: 3-way match invoice vs PO vs goods receipt on quantity and price; discrepancies go to exception handling with purchasing/receiving (Ramp; Docuware; Rillion).
4. **Approval**: route per authorization matrix (amount thresholds, department); often in ERP/AP tool, but in practice frequently via email outside the system of record (Ramp AP document management — approval delays build "because workflows exist outside the system of record").
5. **Payment proposal**: e.g., SAP F110 automatic payment program builds a proposal of open items due; AP reviews/edits/blocks items, checks the proposal log for errors before releasing (Guru99 F110 tutorial; SAP Community).
6. **Discount capture**: payment terms like 2/10 net 30; scheduler must run payment cycles after due-date analysis so discounted invoices are paid inside the discount window (Guru99; Doxis SAP AP guide).
7. **Execution & confirmation**: payment file to bank (ACH/wire/check/virtual card); confirmations reconciled; vendor remittance advice sent.
- **Data touched**: ERP (PO, GR, invoice, payment docs), approval emails, bank portal, vendor master file, payment-terms table.

### 2.4 Customer Credit Evaluation (incl. ratio analysis of public customers)
Process (HighRadius B2B credit management; Invevo; Bectran composite risk score):
1. Credit application + trade references + bureau data (D&B/Experian).
2. For public customers: pull financial statements (10-K/10-Q) and compute ratios.
3. Combine external data, internal payment history, and derived ratios into a score; auto-approve low-risk/small limits, route high-risk to approval workflow.
4. Set limit + terms + risk rating + next review date; monitor continuously (triggers: limit utilization, deteriorating payment patterns, unusual order volume, scheduled review) (HighRadius credit workflows).

**Ratios and thresholds actually used** (world tasks can test these):
- **Current ratio** (current assets / current liabilities): 1.5-3.0 commonly viewed as healthy; <1.0 = can't cover short-term obligations from current assets; retail runs structurally lower (insightsoftware benchmarking; CreditPulse credit risk scoring).
- **Debt-to-equity**: <1 generally healthy; >3:1 in most industries signals over-leverage (utilities tolerate more, tech less) (CreditPulse; insightsoftware).
- **Interest coverage / DSCR**: commercial credit standard; DSCR computed from 3-5 years of statements (Abrigo; CRI credit memo best practices).
- **Inventory turnover** (COGS / avg inventory): higher = efficient; low = overstocking/weak sales; interpret vs industry (insightsoftware; CFI ratio guide).
- **Operating margin** (operating income / revenue): profitability trend vs peers; creditors weight leverage ratios, but margin trend signals capacity (CFI; Allianz Trade).
- **Altman Z-score** for counterparty distress: >2.99 safe zone, 1.81-2.99 grey, <1.81 distress; used by procurement/credit on suppliers and customers (Wall Street Prep; StableBread; Sluamor).
- 5 Cs framework (Character, Capacity, Capital, Collateral, Conditions) as the qualitative wrapper (CFI 5 Cs; Abrigo).

### 2.5 Duplicate-Payment / Fraud Checks
- **Scale of problem**: top performers leak ~0.8% of annual disbursements as duplicate/erroneous payments; median 1.5% (on a $200M payables run, that's $3M) (Corpay duplicate payment detection).
- **Standard checks**:
  1. Exact-match rule in ERP: same vendor + invoice number + amount + date (this is all most ERPs check).
  2. Fuzzy matching: normalize invoice numbers before comparing — catches "INV-5521" vs "5521-OPS" from the same vendor for the same amount (Corpay); similar-amount/similar-date pairs; same invoice keyed under two vendor IDs (duplicate vendor master records). **UNVERIFIED** (last sub-pattern is standard audit practice but not in a fetched source).
  3. Behavioral monitoring: vendor payment frequency suddenly doubling; invoice amounts above vendor baseline (Corpay; Stampli).
- **Fraud red flags**: unauthorized changes to vendor bank details (the classic AP fraud vector — verify changes out-of-band), suspicious vendor/document patterns, round-dollar invoices, sequential invoice numbers from one vendor. First two: Stampli/Open.money; last two: **UNVERIFIED** (standard audit heuristics).
- **Defense in depth**: no single control suffices — layered stack across intake, matching, vendor master, and payment run (Stampli).

### 2.6 Business Brief / Credit Memo on a Counterparty (section structures)
Two authoritative templates to model brief-writing tasks on:

**A. Lending-style credit memo** (CRI credit memo best practices — 5 Cs structure):
1. **Character** — payment history, credit scores, past-due history, public records, deposit/overdraft behavior.
2. **Capacity** — DSCR (commercial) or DTI (consumer) from 3-5 years of financials; EBITDA-based cash flow.
3. **Capital** — liquid reserves, cash cushion.
4. **Collateral** — LTV/LTC where applicable.
5. **Conditions** — amount, maturity, rate structure, amortization, covenants, purpose (sources & uses).
Plus: risk rating, and the memo must let "someone other than the loan officer understand the nature of the credit" (CRI). Documented fields include origination amount, maturity date, rate (fixed/variable, index, spread, floor/ceiling), amortization, call code, risk rating (Abrigo).

**B. Equity-research-style company report** (CFI equity research report; Valuation Master Class; FE Training):
1. Company overview (products/services, leadership, markets, market cap).
2. Investment/business thesis.
3. Industry & competitive positioning.
4. Financial analysis (historical performance, key ratios: margins, ROE/ROA, D/E, revenue/earnings trends).
5. Valuation (DCF, comps) — optional for a finance-team brief.
6. Risk factors (operational, financial, regulatory, market).
7. Recent news/developments.

A finance-team "counterparty brief" for our world is a hybrid: overview → why we care (exposure: open AR/AP, contract size) → financial analysis with ratio table and trend → payment history with us → risks → recommendation (limit/terms/action). **UNVERIFIED** (synthesis of A + B + supplier-risk-assessment structure from Kodiak Hub/Venminder).

---

## 3. The Data-Chaos Map (patterns worth reproducing, each with a source)

Where data really lives in mid/large companies: ERP + Excel trackers + email + bank portals + BI dashboards + shared drives + vendor/customer portals. Documented patterns:

| # | Chaos pattern | Evidence / source | How to reproduce in world |
|---|---|---|---|
| 1 | **Excel is the real close system.** 94% of finance teams still use Excel during close (Ledge 2025 benchmarks via search); 89% say more than half of financial workflows run through Excel (Datarails Oct 2025 survey); 89% still rely on Excel despite owning planning software (Vena State of Strategic Finance 2025); 57% use spreadsheets for accruals, 54% for manual JEs, 53% for the close calendar (Resourceful Finance Pro survey). | Ledge; Datarails via The CFO/search results; Vena; Resourceful Finance Pro | Close checklist + accrual tracker live as spreadsheets, not in the ERP. Answers to "is task X done" exist only in the tracker. |
| 2 | **Some invoices exist only outside the ERP.** Paper + email are the top invoice-arrival channels; 68% manually key invoices into the ERP; ~37% of businesses still get paper invoices (PayStream/Edenred; DocuClipper). Un-keyed invoices = liabilities visible only in an inbox or scanned-PDF folder. | Edenred/PayStream report; DocuClipper; Stampli digital mailroom | A handful of invoices exist only as email attachments / a "to be entered" spreadsheet; AP balance in ERP is incomplete until found. |
| 3 | **Credit notes recorded in one place but not the other.** "Missing credit notes are one of the most common sources of balance discrepancies in vendor reconciliation — a vendor may issue a credit that never reaches the AP team" (invoicedataextraction.com); unrecorded credit notes distort reporting (KlearStack). | invoicedataextraction.com vendor statement guide; KlearStack | Vendor statement shows a credit memo the ERP lacks (or: credit notes live in a second system/CSV export the agent must join). |
| 4 | **Approvals happen in email, outside the system of record.** "Approval delays build because workflows exist outside the system of record"; "fragmentation happens when invoices, contracts, and payment records scatter across files, inboxes, and shared drives"; "matching errors persist because ERP and document systems aren't fully aligned"; "scattered audit trails" (Ramp AP document management). | Ramp | Approval status for some invoices is only determinable from an email thread dump, not an ERP field. |
| 5 | **Payment cleared at bank ≠ posted in ERP.** Timing differences between banking and ERP systems are a root cause of unapplied cash (Emagia); bank-ERP integration "remains fragmented and painful" (Apideck). | Emagia; Apideck | Bank portal export shows receipts/disbursements not yet in ERP; agent must reconcile across both. |
| 6 | **Remittance advice decoupled from payment.** Payments arrive without remittance detail (or remittance goes to a shared email inbox separately), creating unapplied cash; 46% of finance teams cite unapplied cash sitting too long as a top challenge (Bill.com survey via engini.ai); manual matching can consume ~50% of cash-application effort (kapittx). | engini.ai; Versapay; kapittx; Emagia | One customer pays 5 invoices in one wire with remittance in a separate email; another short-pays with no explanation. |
| 7 | **Subledger doesn't tie to GL.** Reconciliation surfaces duplicate invoices, incorrect payment applications, unrecorded credit memos, unmatched payments (Solvexia; Numeric). Causes include direct-to-GL journal entries bypassing the subledger. | Solvexia; Numeric | Seed a manual JE posted straight to the AP control account so subledger ≠ GL by a specific amount. |
| 8 | **GR/IR / GRNI limbo.** Goods received but never invoiced (or invoiced, never received) accumulate as aged open items nobody owns; monthly aging with 90-day/1-year action thresholds (Stampli; SAP F.13/F.19). | Stampli GR/IR; SAP docs; Basware | Aged GR/IR items: a PO received 8 months ago with no invoice — is it an accrual, a vendor error, or a duplicate under a different PO? |
| 9 | **Duplicate/near-duplicate records.** "INV-5521" vs "5521-OPS" same vendor+amount (Corpay); median 1.5% of disbursements are duplicate/erroneous (Corpay). | Corpay | Seed near-duplicate invoice pairs with normalized-number collisions; one true duplicate paid twice. |
| 10 | **Version drift in spreadsheets.** "Messy spreadsheets, version control issues, and manual data-entry mistakes" plague close (Airwallex/close-software content); 1 in 3 finance leaders don't trust their financial close data (The Fintech Times "Excel Trap"). | Airwallex; The Fintech Times | Two versions of the AR aging tracker on the shared drive with different totals; filename conventions like `AR_aging_FINAL_v3 (2).xlsx`. |
| 11 | **Fragmented systems generally.** Multiple specialized finance systems function independently → substantial fragmentation; invoices arrive from "email, PDFs, vendor portals" (Safebooks.ai; FCI-CCM; Fivetran data-silo explainers). | Safebooks.ai; FCI-CCM; Fivetran | The world's tools: ERP API + spreadsheet store + email archive + bank export + (optionally) a BI dashboard with stale numbers. |
| 12 | **BI dashboard disagrees with ERP.** Dashboards refresh on schedules and use their own semantic layer, so month-to-date numbers drift from the ERP until refresh. **UNVERIFIED** (widely reported practitioner pain; no single fetched source). | — | Dashboard shows yesterday's AR total; ERP shows today's; correct answer requires knowing refresh lag. |

Note on r/Accounting: Reddit blocks the search crawler (search attempts returned no reddit results; domain is inaccessible to the user agent), so no thread URLs are cited. The patterns above are corroborated by vendor/survey content instead; treat any specific "reddit says" anecdote as **UNVERIFIED**.

---

## 4. Public-Company Research Stack

### 4.1 SEC EDGAR APIs (free, no API key)
Official docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces (SEC.gov returns 403 to generic fetchers — a realistic quirk). Endpoint details corroborated by tldrfiling.com, dealcharts.org, edgarscout.com guides:

| Endpoint | URL pattern | Returns |
|---|---|---|
| Submissions | `https://data.sec.gov/submissions/CIK{10-digit-zero-padded}.json` | Filing history + metadata (name, SIC, state, tickers, accession numbers); older filings paginated in referenced files |
| Company Facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK{...}.json` | ALL XBRL facts ever filed, organized taxonomy → concept → unit → values (large JSON) |
| Company Concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK{...}/us-gaap/{Concept}.json` | One concept (e.g. `Revenues`, `NetIncomeLoss`, `Assets`) across all periods |
| Frames | `https://data.sec.gov/api/xbrl/frames/us-gaap/{Concept}/{Unit}/CY{Year}[Q{n}I].json` | One concept across ALL companies for a period (annual/quarterly/instantaneous) |
| Full-text search | `https://efts.sec.gov/LATEST/search-index?q=...&forms=...&startdt=...&enddt=...&ciks=...` | JSON hits (accession no., form, date, CIK, entity, URL, highlight snippets) over all filings since 2001; boolean AND/OR/NOT (tldrfiling FTS guide; edgarkit) |
| Ticker→CIK map | `https://www.sec.gov/files/company_tickers.json` | Bulk CIK/ticker/name mapping — download once, query locally |

- **Rate limit: 10 requests/second/IP**; exceeding → 429 + temporary block. **Required: User-Agent header** `"Name (email@example.com)"`; no key needed. Taxonomies: `us-gaap`, `dei`, `ifrs-full` (dealcharts; tldrfiling; sec-edgar-api readthedocs).
- CIKs must be zero-padded to 10 digits in URLs (tldrfiling).
- Best practices: ~100ms between requests; cache locally; bulk downloads for scale.
- These are the ideal template for the world's mocked "public data" tool: JSON shape is well documented, quirky (padding, giant companyfacts payloads, User-Agent), and free.

### 4.2 Free browsing sources
- **stockanalysis.com** — 130k+ stocks/funds; clean statements UI; free tier shows 5 years of financials (10+ paid); default data from S&P Global Market Intelligence; screener with ~299 metrics; financial-sources page discloses providers (stockanalysis.com/financial-sources; reviews by financialtechwiz, ryanoconnellfinance).
- **macrotrends.net** — long-run (30+ yr) charts of stock prices, revenue/margins/ratios, plus macro series (rates, commodities, FX); financial-statement pages per ticker, e.g. `/stocks/charts/AAPL/apple/financial-statements` (macrotrends.net; Find My Moat review). Scraper-hostile HTML but heavily used for quick ratio history.

### 4.3 Commercial financial data APIs
| API | Free tier | Strengths |
|---|---|---|
| **Alpha Vantage** | 25 requests/day | Stocks, FX, crypto, fundamentals (income statement/balance sheet/cash flow endpoints), 50+ technical indicators (AlphaLog guide; APIScout) |
| **Financial Modeling Prep (FMP)** | Limited free tier (250 req/day commonly cited — **UNVERIFIED** exact number) | Deepest fundamentals: statements, calculated ratios, DCF, transcripts; 30+ yrs history; sourced from SEC EDGAR (ksred/nb-data comparisons) |
| **Polygon.io** | 5 requests/minute | Best real-time/market data; paid from $199/mo; fundamentals exist but market data is the strength (ksred comparison) |
| **financialdatasets.ai** | API-key based; free-tier exists (**UNVERIFIED** limits) | Purpose-built "for AI agents"; statements + prices + news; has first-party MCP server (see below) |

### 4.4 Existing finance/SEC MCP servers (design references for our mocked tool)
- **stefanoamorelli/sec-edgar-mcp** (PyPI `sec-edgar-mcp`) — built on `edgartools`; tool families: company (CIK lookup, company info, facts), filings (10-K/10-Q/8-K retrieval **with section extraction**), financials (balance sheet / income statement / cash flow parsed from XBRL, "exact numeric precision"), insider trading (Forms 3/4/5); every response includes SEC source URLs for verification; requires `SEC_EDGAR_USER_AGENT` env var (GitHub README).
- **financial-datasets/mcp-server** — wraps Financial Datasets API; tools: `get_income_statements`, `get_balance_sheets`, `get_cash_flow_statements`, `get_company_news`, `get_current_stock_price`, `get_historical_stock_prices`, plus crypto equivalents; needs `FINANCIAL_DATASETS_API_KEY` (GitHub README).
- Others in the space: `cyanheads/secedgar-mcp-server` (XBRL + filings, STDIO/HTTP), `Taru0208/sec-edgar-mcp-server` (full-text search + 1000+ XBRL metrics, Apify standby), `flothjl/edgar-sec-mcp`, `leopoldodonnell/edgar-mcp`, `mcpwright/edgar-mcp` (Reg CF/Reg D focus) (GitHub search results).
- Design takeaways for our mock: (a) tool-per-statement + tool-per-lookup granularity is the norm; (b) include source URLs in responses (agents are expected to cite); (c) User-Agent/API-key friction and rate limits are authentic obstacles worth simulating; (d) section extraction from 10-K/10-Q (Item 1A Risk Factors, Item 7 MD&A) is a differentiating capability agents rely on for brief-writing.

---

## Open questions for world design
1. Which ERP dialect to mimic (SAP-flavored: F110 payment runs, GR/IR, credit holds — richest documented vocabulary; or generic NetSuite-like REST)?
2. How much of the dunning runbook is policy the agent must *read* (a policy doc in the world) vs. knowledge we expect it to have? Real teams codify intervals in policy docs — seeding one makes grading objective.
3. Do we grade discount capture in dollars (2/10 net 30 math) — easy objective metric?
4. For briefs: grade structure (sections present) + numeric fidelity to the mocked public-data tool?
5. Should the mocked public tool reproduce EDGAR's quirks (CIK padding, 10 rps limit, User-Agent requirement) as deliberate friction?

---

## Sources

### Roles & workflows
- https://www.financialprofessionals.org/glossary/accounts-payable
- https://www.signupsoftware.com/blog/accounts-payable-job-description-template/
- https://ramp.com/blog/accounts-payable/3-way-match
- https://start.docuware.com/blog/document-management/3-way-invoice-matching
- https://www.rillion.com/learn-ap/3-way-matching/
- https://quickbooks.intuit.com/r/enterprise/accounts-payable-workflow/
- https://www.financialprofessionals.org/training-resources/resources/articles/Details/accounts-receivable-job-descriptions
- https://himalayas.app/career-guides/accounts-receivable-analyst
- https://www.highradius.com/resources/Blog/accounts-receivable-aging-report/
- https://corporatefinanceinstitute.com/resources/accounting/accounts-receivable-aging/
- https://www.levelset.com/blog/credit-manager-role/
- https://www.highradius.com/software/order-to-cash/credit-management/credit-management-workflows/
- https://docs.oracle.com/cd/E18727_01/doc.121/e13502/T395686T395690.htm
- https://corporatefinanceinstitute.com/resources/career/fpa-vs-controller-vs-cfo
- https://www.embat.io/blog/cfo-vs-treasurer-vs-controller
- https://yardstick.team/compare-roles/treasury-analyst-vs-financial-controller-navigating-key-finance-roles
- https://nicolasboucher.online/fpa-vs-finance-controller-what-are-the-differences/

### Close & reconciliation
- https://www.floqast.com/blog/month-end-close-checklist
- https://tipalti.com/resources/learn/month-end-close-process/
- https://www.numeric.io/blog/general-ledger-reconciliation
- https://www.numeric.io/blog/month-end-reconciliation
- https://www.solvexia.com/blog/month-end-reconciliation
- https://www.stampli.com/resources/grir-reconciliation/
- https://help.sap.com/doc/8353d7531a4d424de10000000a174cb4/700_SFIN3E%20006/en-US/f47fd1538cdf4608e10000000a174cb4.html
- https://blog.basware.com/en/gr-ir-clearing-process-in-sap
- https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/gr-ir-gr-ir-regrouping-through-t-code-f-19/ba-p/13538883

### Collections & dunning
- https://www.creditpulse.com/blog/dunning-process-guide
- https://www.creditpulse.com/blog/how-to-write-a-dunning-letter
- https://www.kolleno.com/dunning-letter-guide-templates/
- https://upflow.io/blog/ar-collections/dunning-letter
- https://www.finlens.app/blogs/dunning-letter
- https://www.plooto.com/blog/dunning-letters-process-templates-automation

### Payment runs & discounts
- https://www.guru99.com/all-about-automatic-payment-run.html
- https://www.doxis.com/en/blog/sap-accounts-payable
- https://community.sap.com/t5/financial-management-blog-posts-by-members/payment-proposal-approval-configuration-using-workflow-in-sap-s4-hana-sap/ba-p/14053322

### Credit evaluation & ratios
- https://www.creditpulse.com/blog/credit-risk-scoring-guide
- https://www.highradius.com/glossary/b2b-credit-management/
- https://www.highradius.com/resources/Blog/how-to-check-the-creditworthiness-of-a-new-customer/
- https://invevo.com/blog/how-to-assess-the-creditworthiness-of-a-new-customer-step-by-step-guide
- https://www.bectran.com/post/composite-risk-score-b2b-credit
- https://www.wallstreetprep.com/knowledge/credit-risk-analysis/
- https://corporatefinanceinstitute.com/resources/commercial-lending/5-cs-of-credit/
- https://www.abrigo.com/blog/commercial-credit-analysis-101-back-to-basics/
- https://www.criadv.com/insight/credit-memo-best-practices/
- https://insightsoftware.com/blog/benchmarking-performance-financial-ratios/
- https://corporatefinanceinstitute.com/resources/accounting/financial-ratios/
- https://www.allianz-trade.com/en_US/insights/financial-ratios.html
- https://www.wallstreetprep.com/knowledge/altman-z-score/
- https://stablebread.com/altman-z-score/
- https://sluamor.com/blog/how-to-measure-the-financial-credibility-of-buyers-or-suppliers-using-z-score-models
- https://www.kodiakhub.com/blog/supplier-financial-risk-assessment
- https://www.venminder.com/products/vendiligence/financial-health-assessment

### Duplicate payments & fraud
- https://www.corpay.com/resources/blog/duplicate-payment-detection
- https://www.corpay.com/resources/blog/duplicate-payment
- https://www.stampli.com/resources/duplicate-detection-and-fraud-prevention-in-accounts-payable/
- https://open.money/blog/prevent-duplicate-invoice-fraud-ap/
- https://precoro.com/blog/what-are-duplicate-invoices/

### Briefs & research reports
- https://corporatefinanceinstitute.com/resources/valuation/equity-research-report/
- https://valuationmasterclass.com/equity-research-report/
- https://www.fe.training/free-resources/esg/equity-research-report/
- https://waveup.com/blog/tear-sheet-examples/

### Data chaos & benchmarks
- https://www.medius.com/resources/guides-reports/ardent-partners-accounts-payable-metrics-that-matter-in-2024/
- https://www.basware.com/en/resources/ardent-partners-accounts-payable-metrics-that-matter-in-2024
- https://ardentpartners.com/ap-metrics-that-matter-in-2025/
- https://www.bottomline.com/resources/blog/ardent-2024-epayables-study-automation-ai-earning-ap-a-seat-at-the-strategy-table
- https://www.docuclipper.com/blog/accounts-payable-statistics/
- https://edenredpay.com/wp-content/uploads/2023/06/white-paper-2018-paystream-advisors-report-1.pdf
- https://www.stampli.com/resources/paper-invoice-scanning-digital-mailroom/
- https://ramp.com/blog/accounts-payable/accounts-payable-document-management
- https://safebooks.ai/resources/financial-data-governance/overcoming-data-fragmentation-in-financial-data-governance/
- https://www.fci-ccm.com/blog/from-fragmentation-to-unification-overcoming-data-silos-and-integration-in-financial-data-management/
- https://www.fivetran.com/learn/data-silos-meaning
- https://www.apideck.com/blog/accounting-erp-integration-banks-use-cases
- https://www.venasolutions.com/resources/state-of-strategic-finance
- https://the-cfo.io/2024/11/21/spreadsheets-forever-58-of-finance-leaders-choose-excel-over-ai/
- https://thefintechtimes.com/the-excel-trap-why-1-in-3-cfos-still-dont-trust-their-financial-close-data/
- https://www.resourcefulfinancepro.com/news/survey-manual-spreadsheets
- https://www.airwallex.com/en-us/blog/best-automated-reconciliation-software-solutions
- https://coefficient.io/month-end-close/blackline-vs-floqast
- https://www.numeric.io/blog/floqast-what-it-is-how-it-works
- https://www.emagia.com/resources/glossary/risks-of-cash-application-process/
- https://www.emagia.com/blog/what-is-cash-application/
- https://www.highradius.com/resources/Blog/cash-application/
- https://engini.ai/blog/the-unapplied-cash-trap-how-automated-cash-application-software-solves-remittance-matching
- https://www.versapay.com/resources/how-to-solve-common-cash-application-challenges-with-automation
- https://www.versapay.com/resources/unlock-lockbox-processing-efficiency-automated-cash-application
- https://kapittx.com/automated-remittance-matching-how-to-eliminate-unapplied-cash/
- https://www.cashbook.com/problems-with-cash-application/
- https://klearstack.com/blogs/vendor-reconciliation-in-accounts-payable
- https://ramp.com/blog/vendor-reconciliation
- https://invoicedataextraction.com/blog/vendor-statement-reconciliation-guide
- https://www.versapay.com/resources/collection-effectiveness-index-cei
- https://www.highradius.com/resources/Blog/collections-effectiveness-index-how-to-act-on-it/
- https://altline.sobanco.com/collections-effectiveness-index-cei/

### Public data stack
- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://tldrfiling.com/blog/sec-edgar-api-guide/
- https://tldrfiling.com/blog/sec-edgar-full-text-search-api
- https://dealcharts.org/blog/sec-edgar-api-guide
- https://edgarscout.com/edgar-api/
- https://edgarkit.com/learn/edgar-full-text-search
- https://sec-edgar-api.readthedocs.io/
- https://www.sec.gov/files/company_tickers.json
- https://stockanalysis.com/financial-sources/
- https://stockanalysis.com/pro/
- https://www.macrotrends.net/
- https://www.macrotrends.net/stocks/charts/AAPL/apple/financial-statements
- https://www.findmymoat.com/tools/macrotrends
- https://www.financialtechwiz.com/post/stockanalysis-review/
- https://ryanoconnellfinance.com/stock-analysis-review/
- https://alphalog.ai/blog/alphavantage-api-complete-guide
- https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/
- https://www.nb-data.com/p/best-financial-data-apis-in-2026
- https://apiscout.dev/guides/best-stock-market-financial-apis-2026
- https://github.com/stefanoamorelli/sec-edgar-mcp
- https://pypi.org/project/sec-edgar-mcp/
- https://github.com/financial-datasets/mcp-server
- https://github.com/cyanheads/secedgar-mcp-server
- https://github.com/Taru0208/sec-edgar-mcp-server
- https://github.com/flothjl/edgar-sec-mcp
- https://github.com/leopoldodonnell/edgar-mcp
- https://github.com/mcpwright/edgar-mcp
