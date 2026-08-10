# Finance Tool Landscape — Competitor/Adjacent Tools a Real Finance Team Runs

Research date: 2026-08-10. Purpose: ground finance-world's tool census and future chaos
mechanics in the real product landscape around our mocked stack (D365-shaped ERP MCP,
QBO-shaped subsidiary books, Excel shadow drive, shared mailbox, EDGAR snapshot, policy
library). Per product: what finance does in it, API style, MCP existence, adoption
evidence. Claims not confirmed against a primary source are marked **UNVERIFIED**.

Method note: multi-round web search (Aug 2026); MCP claims checked against GitHub/vendor
pages where possible. Search-result summaries are second-hand for some adoption numbers —
treat all market-share figures as directional.

---

## 1. ERPs (competitors to D365 F&O)

Market context: ERP market ~$73B in 2025, ~70% cloud deployments; Oracle, SAP, Microsoft
together control >70% of market share by revenue. SAP and Oracle roughly tied at ~$8.6–8.7B
annual ERP revenue each; Microsoft #3 at ~$5.4B (2024).

- **SAP S/4HANA** — The enterprise incumbent (141k+ ERP customers; 24k+ RISE cloud
  customers). Finance lives in FI/CO: GL, AP (MIRO invoice verification), AR, asset
  accounting, credit management, period close. API style: OData/REST via SAP Business
  Accelerator Hub + BAPIs/IDocs legacy. MCP/agents: SAP + Anthropic announced Claude in
  SAP Business AI/Joule using MCP to coordinate agents across S/4HANA, SuccessFactors,
  Ariba (https://erp.today/sap-anthropic-claude-joule-mcp/). "Autonomous Finance" is a
  named Joule pillar. Partner ecosystems (e.g., Mindset Consulting) already run 11 MCP
  servers / 157 tools against S/4HANA, including a Credit Management Agent and a 3-way-match
  Invoice Discrepancy Reconciler.
- **Oracle Fusion Cloud ERP** — ~14k large-enterprise customers (~100k Oracle ERP customers
  incl. NetSuite). Finance uses GL/Payables/Receivables/Cash Mgmt modules on Redwood UI.
  API style: extensive REST APIs (docs.oracle.com). Agents: Release 26B ships four GA native
  finance agents — Ledger, Payables, Expenses, Payments — free with the apps
  (https://blogs.oracle.com/fusioninsider/agentic-ai-in-erp-four-agents-you-can-use-today).
  Payables Agent does multi-channel invoice ingest → extract → PO match → accounting →
  approval routing. No public Oracle Fusion MCP server found — **UNVERIFIED** whether one
  is planned.
- **NetSuite** — 41k+ customers, growing ~25%/yr; the default mid-market cloud ERP.
  Finance does full GL-to-close plus billing. API style: SuiteTalk REST/SOAP, SuiteQL,
  SuiteScript. MCP: **official** — "NetSuite AI Connector Service" (MCP-native) with an
  MCP Standard Tools SuiteApp plus custom MCP tools buildable in SDF/SuiteScript
  (https://www.netsuite.com/portal/products/artificial-intelligence-ai/mcp-server.shtml).
  NetSuite 2026.1 adds native AI Close, cash management, and reconciliation agents.
- **Workday Financials** — ~$3.3B ERP revenue (2024); HCM-led, strong in services
  industries. Finance uses accounting center, procure-to-pay, close. API style: SOAP
  (WWS), REST, RaaS report extracts. MCP/agents: Workday Agent System of Record + Agent
  Gateway support MCP and A2A; "Agent-Ready Tools" launched June 2026
  (https://newsroom.workday.com/2026-06-02-...); native public MCP endpoint not yet GA —
  third-party MCP servers (Cequence, Merge, StackOne ~128 actions) fill the gap.
- **Sage Intacct** — Mid-market/nonprofit favorite, multi-entity dimensions. API style:
  legacy XML API + newer REST. MCP: **official** — Sage Intacct AI Gateway includes an MCP
  server built on the REST APIs, governed/auditable
  (https://www.sage.com/en-us/sage-business-cloud/intacct/product-capabilities/platform/ai-gateway/).
  Sage Copilot embedded for AP processing, close tracking, anomaly spotting.
- **QuickBooks Online** — SMB king: >6.5M subscribers (10M+ per some sources), ~62% overall
  accounting-software share, >80% US SMB share. Finance (or the one-person team) does
  everything: invoices, bills, banking feeds, reports. API style: QBO REST API (OAuth2).
  MCP: **official** — intuit/quickbooks-online-mcp-server on GitHub: 144 tools, 29 entity
  types, 11 financial reports, local stdio (https://github.com/intuit/quickbooks-online-mcp-server).
- **Xero** — ~3.9M subscribers (ANZ/UK-heavy). Same SMB surface as QBO. API style: Xero
  Accounting REST API (OAuth2). MCP: **official** — XeroAPI/xero-mcp-server on GitHub,
  read/write (https://github.com/xeroapi/xero-mcp-server).

**Relevance to finance-world:** Our D365 ERP mock is well chosen — Microsoft's official
Dynamics 365 ERP MCP (now "dynamic" preview; the 13-tool static server retires Oct 2026 —
note our 22-tool 1:1 mapping should be re-checked against the current server) is one of
several *official* ERP MCPs (NetSuite, Intacct, QBO, Xero). Chaos patterns: (a) an
"ERP migration" scenario (books split between D365 and a NetSuite-shaped or Rillet-shaped
system mid-cutover); (b) subsidiary-on-QBO already exists — a Xero-shaped second sub is a
cheap variant; (c) SAP-shaped supplier portal for intercompany counterparties.

## 2. AP automation / spend

Market context: BILL + Coupa + Concur + Ramp + Brex ≈ 64% of AP/AR/spend category
(per pulserevops **UNVERIFIED**). AvidXchange taken private by Corpay/TPG ($2.2B, 2025).

- **BILL (Bill.com)** — Dominant SMB/mid-market AP+AR+spend: ~480k customers, ~$1.4B ARR.
  AP specialist does invoice inbox → capture → approval chain → payment run (ACH/check/
  virtual card) → sync to QBO/NetSuite/Intacct. API: v3 REST (v2 LTS), sandbox, developer
  keys (https://developer.bill.com). MCP: community only (caffeinebounce/billcom-mcp-server,
  civicteam/bill-mcp-server).
- **Ramp** — Corporate card + spend + AP + procurement. Finance sets policies; Ramp
  auto-collects receipts, codes transactions, syncs to ERP. API: Ramp Developer API
  (OAuth2, scoped). MCP: **official** — ramp-public/ramp_mcp (ETL into ephemeral SQLite
  for analysis) (https://github.com/ramp-public/ramp_mcp). See §9 for agents.
- **Brex** — Card + spend + reimbursements + travel, startup/enterprise. API: Brex
  developer REST APIs (expenses, transactions, budgets). MCP: community —
  crazyrabbitLTC/mcp-brex-server (read-only-optimized).
- **Tipalti** — Global mass-payables: supplier onboarding, W-9/W-8 tax forms, multi-entity,
  multi-currency payouts in 190+ countries, 32-language invoice OCR. API: REST (plus older
  SOAP payer API — **UNVERIFIED** current split). No official MCP found.
- **Stampli** — AP "collaboration hub"; Billy the Bot AI does invoice capture/coding/
  approval nudges; real-time bidirectional ERP sync. API: not self-serve public
  (**UNVERIFIED**). No MCP found.
- **AvidXchange** — 8,500+ mid-market buyers, 1.35M+ paid suppliers; US-centric invoice +
  payment automation, strong real estate/HOA/construction verticals. API: partner-oriented
  REST (**UNVERIFIED** self-serve). No MCP found.
- **Coupa** — Enterprise Business Spend Management: procure-to-pay, sourcing, invoicing,
  expenses, treasury (acquired Bellin). API: REST (OAuth2 since R35; strict 50-record
  pagination). MCP: community/aggregator only (Composio toolkit, PulseMCP entries).
- **Airbase (Paylocity)** — Mid-market (100–5,000 employees) procure-to-pay + cards +
  reimbursements (46 countries); now "Paylocity for Finance." API: REST (**UNVERIFIED**
  public self-serve). No MCP found.
- **Mercury** — Startup banking (checking/savings/treasury/cards). API: REST — accounts,
  transactions, statements, recipients, ACH/wire, webhooks — plus a terminal-native CLI and
  an **official AI-ready MCP server** advertised on mercury.com/api.

**Relevance to finance-world:** AP automation is the highest-value adjacent mock: a
BILL/Stampli-shaped "AP inbox + approval + payment run" tool would let tasks span ERP ↔ AP
tool sync lag (classic chaos: invoice approved in AP tool, not yet posted in ERP; duplicate
vendor bill in both). A Ramp/Brex-shaped card feed is the natural source for uncoded
transactions and policy-violation chaos. Mercury-shaped bank API pairs with treasury tasks.

## 3. AR / collections / cash application

- **HighRadius** — Enterprise O2C leader (3x Gartner MQ Leader; 1,300+ finance teams;
  claims 90%+ touchless cash application). Credit, collections worklists, deductions,
  cash app, EIPP. Now sells "60+ agentic AI agents" (186 agents claimed in marketing —
  **UNVERIFIED** count) incl. behavior-based collections and payment-intent prediction.
  API: enterprise integration (ERP connectors); no public self-serve API or MCP found.
- **Billtrust** — Invoice-to-cash: invoice delivery, payments network (2,400+ customers),
  cash application. API: REST platform API (arc-aegis.billtrust.com;
  https://api-docs.aws-prod.billtrust.com/). No MCP found.
- **Versapay** — Collaborative AR: shared buyer-seller portal for disputes/short-pays +
  payments + cash app. API: REST with API token/key basic auth, webhook + watermark-polling
  endpoints for customers/invoices/payments/settlements (https://developers.versapay.com/).
- **Tesorio** — Mid-market "agentic financial operations": collections email automation,
  payment-promise extraction, 95%+ auto-match cash app, cash forecasting. API exists
  (apitracker lists it) but docs are thin — **UNVERIFIED** surface. No MCP found.
- **Upflow** — SMB/mid-market AR workflow: aging visualization, automated dunning
  sequences, task assignment. API: REST (developer docs exist — **UNVERIFIED** detail).
- **Invoiced (Flywire)** — SMB AR: invoicing, subscriptions, CashMatch AI auto-application.
  API: clean REST (https://developer.invoiced.com/api).

**Relevance to finance-world:** Our AR/collections analyst persona currently works out of
ERP + mailbox — exactly what these tools replace, so the *absence* is realistic for a
mid-market shop. If we add one, a Versapay/Upflow-shaped "customer portal + dunning
sequencer" is the best fit: chaos patterns include disputed invoices living only in the
portal (not the ERP), short-pay/deduction codes that must be reconciled to ERP receipts,
and promise-to-pay dates contradicting the aging report.

## 4. Close management

Market context: close/reconciliation software ≈ $5.8B, ~12% CAGR.

- **BlackLine** — Enterprise standard: 4,300+ customers. Account reconciliations,
  transaction matching (millions of rows; 43–85% auto-certification), journal entry
  management, intercompany, close task governance. Platform: Studio360 (integrate/
  orchestrate/report, "Verity" AI). API: REST APIs exist (partner/customer-oriented;
  **UNVERIFIED** self-serve). No MCP found.
- **FloQast** — Mid-market: 2,800+ customers. Close checklist, reconciliation tie-outs to
  Excel workbooks (its signature pattern — matches our Excel shadow drive), flux analysis.
  AI: "FloQast Transform" AI-agent builder (natural-language custom agents). API:
  developer.floqast.app public portal.
- **Numeric** — AI-native close for NetSuite/QBO teams: close management, auto-drafted flux
  analysis, reconciliations. MCP: **official** — Numeric MCP server with 20+ tools across
  workspace context, close-task lifecycle (create/assign/comment), and 17 pre-built
  "skills" like auto-draft flux or scan for department miscodes
  (https://www.numeric.io/blog/numeric-mcp-server). Also publishes the best practical
  guides to NetSuite/QBO MCP for controllers.

**Relevance to finance-world:** A FloQast-shaped close checklist tool is the single most
world-coherent addition: it formalizes the controller persona's month-end close and links
directly to the Excel shadow drive (recon workbooks) — chaos = checklist says recon done
but workbook balance ≠ ERP balance; reassigned tasks; auto-certification hiding a broken
rec. Numeric's MCP tool list (close-task CRUD + flux skills) is a ready-made schema to
crib for tool design.

## 5. Treasury / cash

- **Kyriba** — Enterprise TMS leader: 3,400+ clients, 170 countries, 9,900+ bank
  connections, 66k payment formats; 3B transactions / $15T processed in 2024. Treasury does
  cash positioning, forecasting, payments, bank connectivity, risk (FX/debt/investments).
  API: Open API platform pushing "real-time treasury"; agentic "Trusted AI (TAI)"
  portfolio. No public MCP found.
- **Trovata** — Mid-market cash management via open-banking APIs: multi-bank aggregation,
  cash reporting, forecasting. Trovata AI 2.0 is **built on MCP internally** (model ↔
  treasury tools bridge) with scheduled/triggered AI agents for variance explanations and
  anomaly alerts (https://trovata.io/blog/trovata-ai-agents-insights). External MCP
  endpoint for customers: **UNVERIFIED**.
- **Modern Treasury** — Payment-ops infrastructure for product/finance teams: API objects =
  payment_orders, expected_payments, counterparties, internal/external_accounts,
  transactions, ledgers/ledger_transactions, invoices; reconciliation engine links bank
  transactions to expected payments. MCP: **official** — modern-treasury-mcp on NPM (in
  TypeScript SDK) (https://www.moderntreasury.com/journal/introducing-the-modern-treasury-mcp-server).
- **Plaid / bank portals** — Plaid = bank-data aggregation (auth, balances, transactions).
  MCP: **official** Plaid MCP server for account/transaction access. Real treasury teams
  also live in raw bank portals (JPM Access, BofA CashPro — each now shipping their own AI
  assistants; CashPro API exists — **UNVERIFIED** detail), which remain stubbornly manual:
  dual-control wire release, token auth, cutoff times.

**Relevance to finance-world:** Our treasury persona needs a bank surface more than a TMS.
A minimal "bank portal" mock (balances, prior-day BAI2-style statements, wire initiation
with dual approval, cutoff times) unlocks the best chaos in the whole map: payment-run
timing vs cutoffs, unreleased wires, duplicate payment files, bank statement lines that
don't match ERP cash. Modern Treasury's object model is the cleanest schema to copy.

## 6. FP&A

- **Anaplan** — Enterprise planning standard (Hyperion successor cohort; taken private by
  Thoma Bravo). Connected planning models for revenue/workforce/opex. API: Integration API
  v2 (bulk import/export/actions) + Transactional API (cell-level read/write). $500M AI
  roadmap; role-based agents (Forecaster, CoModeler) Dec 2025. MCP: community only
  (larasrinath/anaplan-mcp — 17 API wrappers); NB Anaplan has *restricted* MCP/AI use of
  its published APIs in policy (https://community.anaplan.com — see repo README).
- **Pigment** — Fastest-growing modern challenger; ranked #1 Agentic AI in EPM by Dresner.
  API: GraphQL/REST import-export (**UNVERIFIED** detail). AI agents for planning Q&A and
  scenario work.
- **Mosaic** — Strategic-finance dashboards/planning for SaaS; real-time ERP/CRM/HRIS sync.
  API: limited public surface (**UNVERIFIED**).
- **Cube** — Spreadsheet-native FP&A (Excel + Google Sheets add-ins over a cloud store);
  SMB/mid-market. Users report wanting API/OData access — public API thin (**UNVERIFIED**).
- **Datarails** — Excel-native FP&A for consolidation/variance: bi-directional Excel add-in
  with cell-level lineage. No public API/MCP found.

**Relevance to finance-world:** Strong argument to NOT mock an FP&A platform: mid-market
FP&A *is* Excel, which we already model via the shadow drive — our most realistic choice.
The FP&A persona's chaos should stay Excel-native (broken links, stale actuals vs ERP,
version forks: "Budget_v7_FINAL_v2"). If we ever add one, Cube/Datarails-shaped
(Excel-add-in-over-database) preserves the Excel-centric chaos while adding a sync surface.

## 7. Expense / procurement

- **SAP Concur** — T&E incumbent: ~62% travel-expense-management share, 75% of Fortune
  100/500 (SAP-published — directional). Expense reports, receipt audit, travel booking,
  invoice. API: REST on api.sap.com (OAuth2 via Partner Portal). MCP: community only
  (thisislance98/concur-mcp-server; Cequence gateway).
- **Expensify** — SMB expense reports/receipts. API: old-school "Integration Server"
  template-driven export API (https://integrations.expensify.com/Integration-Server/doc/).
- **Navan** — Travel + expense combined, traveler-UX-led. API: developer.navan.com —
  expense data API + SFTP sync to ERP.
- **Zip** — Procurement intake/orchestration layer in front of ERP/Coupa: $6B+ claimed
  customer savings; 50+ purpose-built agents (June 2025); customers incl. OpenAI,
  Anthropic, Snowflake; 26M approvals, projecting 30% handled autonomously by 2026. API:
  REST + integrations (**UNVERIFIED** public docs).
- **Coupa** — see §2.

**Relevance to finance-world:** Procurement persona currently implied via ERP POs. A
Zip-shaped "intake + approval chain" tool is the best procurement chaos source: purchase
requests approved in the intake tool but no PO in ERP, renewals auto-approved past budget,
vendor onboarding stuck mid-workflow. Concur-shaped expense feeds give the AP/controller
personas receipt-audit and out-of-policy chaos that today's card-feed mocks can't.

## 8. Financial data / research (adjacent to our EDGAR mock)

- **Bloomberg** — ~325–350k Terminal subscribers, $27k+/yr. Desktop API (BLPAPI) for
  reference/historical/streaming data, licensed per-terminal. MCP: community only
  (djsamseng/blpapi-mcp — requires a running Terminal). No official MCP found.
- **FactSet** — ~120k users class of workstation market (**UNVERIFIED** count; ~16%
  mindshare). APIs: formal developer.factset.com catalog. MCP: FactSet has published MCP
  tooling per press mentions — **UNVERIFIED**; treat as "API-first, MCP emerging."
- **S&P Capital IQ** — via **Kensho LLM-ready API**: official hosted remote MCP at
  https://kfinance.kensho.com/integrations/mcp exposing CapIQ financials, market data,
  transcripts, M&A, relationships; official Anthropic partnership (Claude connector). The
  most agent-ready of the big-three research platforms.
- **PitchBook** — PE/VC data. API exists but is a separate "Direct Data" contract; no
  developer portal, docs behind auth. Effectively closed to agents.
- **Koyfin** — Analyst charting/screening; explicitly **no API** (licensing restrictions).
- **FMP / Alpha Vantage / Polygon** — Developer-tier market data. All three have
  **official MCP servers** (Alpha Vantage official listed on mcpservers.org; FMP MCP
  ~250+ tools incl. SEC filing access; Polygon MCP for tick-level US equities).
- **financial-datasets MCP** — Community/official MCP specializing in structured
  fundamentals + SEC filing text (financialdatasets.ai).
- **Daloopa** — AI-extracted fundamentals (6,000+ tickers, source-linked to filings);
  official MCP + OpenAI connector; claims agents hit ~90% accuracy on Daloopa data vs
  ~19-20% on public web. $13M strategic round to be "data infra for AI in finance."
- **SEC EDGAR itself** — many community MCP servers (stefanoamorelli/sec-edgar-mcp,
  cyanheads/secedgar-mcp-server, edgartools-based ones) doing full-text search + XBRL.

**Relevance to finance-world:** Our EDGAR snapshot is the right primitive — it's what all
of these wrap, and community EDGAR MCPs give us tool-shape precedents (full-text search,
filing fetch, XBRL facts, insider transactions). A Kensho/Daloopa-shaped "clean
fundamentals API" mock would only matter if we add an IR/corp-dev persona. Chaos pattern:
credit manager pulls a customer's 10-K from EDGAR vs a stale D&B-style credit report that
disagrees — data-conflict tasks need no new tool.

## 9. AI finance agents shipping today (agent-ready workflow evidence)

- **Microsoft Finance Agent / Copilot for Finance** — Role-based agent across Excel/
  Outlook/Teams; Wave 2 (Nov 2025) shipped production Reconciliation Agent and Variance
  Analysis Agent; 2026 Wave 1 adds custom reconciliation agents built in Copilot Studio
  against Finance Agent (https://learn.microsoft.com/en-us/copilot/release-plan/2026wave1/finance-agents/).
  Workflows: account reconciliation, variance analysis, ERP Q&A.
- **Ramp agents** — Agents for Controllers (Jul 2025): expense review + policy enforcement
  from an uploaded policy PDF → "reasoning graph," >99% claimed accuracy; Agents for AP
  (Oct 2025); early 2026 pivot to one unified agent with thousands of skills. Workflows:
  expense approval, policy enforcement, AP coding.
- **HighRadius agents** — 60+ agentic agents across O2C/treasury/R2R: cash-app matching,
  deduction coding, behavior-based collections, payment-intent prediction.
- **Numeric AI** — Close automation: auto-drafted flux, recon monitoring, plus official
  MCP for close-task orchestration (see §4).
- **Basis** — $100M Series B at $1.15B valuation (Khosla-led — **UNVERIFIED** lead); agents
  for accounting *firms* (CAS/tax/audit) that do end-to-end prep work, humans as reviewers;
  OpenAI flagship case study.
- **Digits** — "Autonomous General Ledger" for SMB; launched Accounting Agents (Jun 2025)
  running whole workflows; claims 2,000+ month-end closes on AGL.
- **Klarity** — Enterprise document AI for revenue accounting: contract review for ASC 606
  rev-rec checklists, order-form/invoice review (~150k contracts reviewed).
- **Rillet** — AI-native GL/ERP for mid-market SaaS ($100M+ raised; Sequoia, a16z, ICONIQ):
  automated journals, bank recs, ASC 606; positions as NetSuite replacement.
- **Concourse** — $12M Series A (Jan 2026, Standard Capital + a16z/CRV/YC): enterprise AI
  agents for FP&A/finance-ops — pulls data, drafts reports, answers ad-hoc analysis.
- **Auditoria** — SmartVendor (AP Helpdesk/Invoices/Accruals) + SmartCustomer (AR
  Helpdesk/collections): agents that live in the shared AP/AR mailbox, tag and answer
  vendor/customer emails, 24/7. Listed on Workday Marketplace.

**Relevance to finance-world:** This list is the ground truth for "which workflows are
agent-ready" — i.e., what our eval tasks should test: (1) reconciliation + variance/flux
(Microsoft, Numeric), (2) expense/policy enforcement (Ramp), (3) AP invoice coding +
3-way match (Oracle, Ramp, Stampli), (4) cash application + collections email (HighRadius,
Auditoria, Tesorio), (5) shared-mailbox triage (Auditoria — validates our mailbox mock as
a first-class agent surface), (6) close-task orchestration (Numeric). Our chaos mechanics
should stress exactly these: they're where vendors claim >90-99% autonomy, so failure
modes there are the interesting eval frontier.

---

## Cross-cutting observations for the tool census

1. **Official MCP servers now exist at every layer of the finance stack**: ERP (D365,
   NetSuite, Intacct, QBO, Xero), spend (Ramp), banking (Mercury, Plaid), payment ops
   (Modern Treasury), close (Numeric), market data (Alpha Vantage, Polygon, FMP, Kensho/
   S&P, Daloopa). Notably *absent*: enterprise AP (BILL official, Tipalti, AvidXchange),
   AR suites (HighRadius, Billtrust), close governance (BlackLine), TMS (Kyriba), FP&A
   (Anaplan restricts it). The MCP-poor categories are exactly where email + Excel remain
   the integration layer — which our world already models.
2. **The realistic mid-market stack around a D365 shop** (our persona set) is: D365 +
   QBO sub + BILL-or-Stampli AP + a card program (Ramp/Brex) + Concur-or-Navan T&E +
   FloQast close + Excel + bank portals. We mock 4 of 8; the highest-value additions in
   order: bank portal, AP tool, close checklist, card feed.
3. **Sync lag between ERP and satellite tools is the canonical chaos primitive** in every
   category (AP approval vs ERP posting, portal dispute vs ERP aging, intake approval vs
   PO, checklist sign-off vs workbook). Real practitioner complaints (e.g., AvidXchange
   batch-export lag) confirm this is realistic, not contrived.

## Sources

- https://www.cargoson.com/en/blog/how-big-is-the-erp-market
- https://erp-software.org/en/top-erp-systems/
- https://erp.today/sap-anthropic-claude-joule-mcp/
- https://www.mindsetconsulting.com/mindset-press-release-mindset-launches-20-sap-joule-agents-at-sapphire-2026/
- https://www.oracle.com/news/announcement/ai-world-oracle-ai-agents-help-finance-leaders-accelerate-business-insights-and-boost-efficiency-2025-10-15/
- https://blogs.oracle.com/fusioninsider/agentic-ai-in-erp-four-agents-you-can-use-today
- https://www.netsuite.com/portal/products/artificial-intelligence-ai/mcp-server.shtml
- https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_4160616848.html
- https://www.netsuite.com/portal/resource/articles/financial-management/netsuite-2026-1-features-new-ai-close-and-cash-management-ai-agents-for-planning-and-reconciliation-and-more.shtml
- https://newsroom.workday.com/2026-06-02-Workday-Launches-New-Tools-for-Developers-to-Build,-Connect,-and-Verify-AI-Agents-For-HR,-Finance,-and-IT
- https://blog.workday.com/en-us/managing-ai-powered-future-of-work.html
- https://www.sage.com/en-us/sage-business-cloud/intacct/product-capabilities/platform/ai-gateway/
- https://github.com/intuit/quickbooks-online-mcp-server
- https://github.com/xeroapi/xero-mcp-server
- https://electroiq.com/stats/quickbooks-statistics/
- https://6sense.com/tech/financial-reporting/xero-market-share
- https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp
- https://www.microsoft.com/en-us/dynamics-365/blog/it-professional/2025/11/11/dynamics-365-erp-model-context-protocol/
- https://developer.bill.com/docs/home
- https://github.com/caffeinebounce/billcom-mcp-server
- https://pulserevops.com/revenue-architecture/ra0170
- https://github.com/ramp-public/ramp_mcp
- https://github.com/crazyrabbitLTC/mcp-brex-server
- https://www.stampli.com/blog/ap-automation/tipalti-vs-avidxchange/
- https://www.sec.gov/Archives/edgar/data/1858257/000119312525113913/d920050dex991.htm (AvidXchange 8-K)
- https://www.airbase.com/
- https://mercury.com/api
- https://docs.mercury.com/docs/welcome
- https://www.highradius.com/product/order-to-cash-automation-software/
- https://www.highradius.com/product/accounts-receivable-software/
- https://api-docs.aws-prod.billtrust.com/
- https://developers.versapay.com/
- https://developer.invoiced.com/api
- https://www.tesorio.com/
- https://www.ledge.co/content/blackline-vs-floqast-what-100-finance-leaders-and-controllers-say
- https://coefficient.io/month-end-close/blackline-vs-floqast
- https://www.blackline.com/
- https://www.floqast.com/press-releases/floqast-unveils-ai-agent-builder-and-expanded-ai-capabilities-to-redefine-the-future-of-accounting
- https://developer.floqast.app/
- https://www.numeric.io/blog/numeric-mcp-server
- https://www.numeric.io/blog/netsuite-mcp
- https://www.kyriba.com/news/premier-liquidity-performance-event-kyribalive-showcases-treasury-leaders/
- https://trovata.io/blog/trovata-ai-agents-insights
- https://www.moderntreasury.com/journal/introducing-the-modern-treasury-mcp-server
- https://docs.moderntreasury.com/platform/changelog
- https://www.openbankingtracker.com/api-aggregators/plaid/mcp
- https://help.anaplan.com/anaplan-api-844c6d40-a21c-423d-8435-ebaaa0372b76
- https://github.com/larasrinath/anaplan-mcp
- https://www.cfoshortlist.com/reports/anaplan-vs-pigment
- https://www.pigment.com/recognition
- https://www.cubesoftware.com/blog/best-fpa-software-tools
- https://www.concur.com/blog/article/sap-retains-1-2023-market-share-in-travel-and-expense-management-software
- https://6sense.com/tech/travel-expense-management/sap-concur-market-share
- https://api.sap.com/package/ConcurExpense
- https://github.com/thisislance98/concur-mcp-server
- https://help.expensify.com/articles/expensify-classic/connections/Expensify-API
- https://integrations.expensify.com/Integration-Server/doc/
- https://developer.navan.com/
- https://www.businesswire.com/news/home/20251202204445/en/Zip-Surpasses-$6-Billion-in-Customer-Savings-as-Agentic-Procurement-Orchestration-Transforms-Enterprise-Purchasing
- https://zip.com/blog/introducing-agentic-procurement-orchestration
- https://github.com/djsamseng/blpapi-mcp
- https://benzinga.com/z/9223479
- https://kensho.com/news/kensho-llm-ready-api-expands-mcp-server-access-dataset-support-integrations
- https://docs.kensho.com/llmreadyapi/overview
- https://www.prnewswire.com/news-releases/sp-global-and-anthropic-announce-integration-of-sp-globals-trusted-financial-data-into-claude-302505482.html
- https://pitchbook.com/products/direct-access-data/api
- https://pipeline.zoominfo.com/sales/pitchbook-api-review
- https://www.koyfin.com/help/faq/can-i-get-the-data-via-api/
- https://mcpservers.org/servers/alphavantage/alpha_vantage_mcp
- https://marketxls.com/blog/best-financial-data-mcp-servers-ai-market-data
- https://daloopa.com/products/mcp
- https://daloopa.com/blog/press-release/mcp-pr
- https://github.com/stefanoamorelli/sec-edgar-mcp
- https://github.com/cyanheads/secedgar-mcp-server
- https://learn.microsoft.com/en-us/copilot/release-plan/2026wave1/finance-agents/
- https://learn.microsoft.com/en-us/copilot/finance/reconcile/custom-reconciliation-agent
- https://www.prnewswire.com/news-releases/ramp-introduces-ai-agents-to-automate-finance-operations-302502154.html
- https://www.zenml.io/llmops-database/building-production-scale-ai-agents-for-financial-automation
- https://openai.com/index/basis/
- https://www.digitalapplied.com/blog/basis-ai-100m-agentic-accounting-tax-audit-guide
- https://www.globenewswire.com/fr/news-release/2025/06/23/3103524/0/en/Digits-Launches-First-AI-Agents-for-Accounting-Workflows-Built-on-Digits-Autonomous-General-Ledger.html
- https://www.klarity.ai/post/how-klarity-works-automate-workflows
- https://www.erpresearch.com/en-us/rillet
- https://www.prnewswire.com/news-releases/concourse-raises-12m-series-a-and-expands-access-to-its-enterprise-grade-ai-agents-for-finance-302670827.html
- https://www.auditoria.ai/pr-auditoria-ai-revolutionizes-response-time-for-accounts-payable-and-receivable-with-ap-and-ar-helpdesk/
- https://info.auditoria.ai/hubfs/FY25_SDN_Partner_Datasheet_Auditoria.AI_Overview.pdf
