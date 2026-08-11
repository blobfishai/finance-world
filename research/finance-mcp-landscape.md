# Finance MCP landscape — the master tool inventory

Research date: 2026-08-11. Source of record: the BlockRunAI curated list checked out at
`research/external/repos/awesome-finance-mcp/` (README 231 lines, CC0 at `README.md:227-231`;
**no upstream commit pin** — the directory ships no `.git`, so `git` there resolves to
finance-world's own repo and any HEAD hash read from it describes this repo, not the list),
cross-referenced against the eight finance MCP repos already cloned under
`research/external/repos/` and against `research/finance-tool-landscape.md` (the vendor/
market survey) and `docs/TOOL-CENSUS.md` (our selection rule).

Purpose: answer *"what is the FULL universe of tools a finance agent could be expected to
call?"* across ERP · CRM · spreadsheets · accounting · payments · data providers — and say
which of those finance-world already mocks, which it deliberately doesn't, and which (if
any) earn a new server.

Every claim below cites a repo-relative path under `research/external/repos/` or a URL that
was actually fetched on 2026-08-11. Unverifiable items say **UNVERIFIED** and carry the URL
to fetch later. When a vendor README and the shipped code disagree, the shipped code wins
(both recorded).

**Two evidence tiers, kept separate.** *Tier 1 — repo-verified*: re-derivable today from a
tree under `research/external/repos/` (Ramp, QBO, Xero, EDGAR, Financial Datasets, Modern
Treasury, the curated list itself, and — partially — Stripe). *Tier 2 — URL-attested, no
local artifact*: fetched on 2026-08-11 but never captured to disk, so nothing under
`research/external/` (which holds only `repos/`, `articles/`, `financebenchmark-extracts/`)
can reproduce it. Tier 2 covers **FRED, FMP, Alpha Vantage, Monarch**, and the *hosted*
Stripe surface (`mcp.stripe.com`). Tier-2 rows are marked `(tier 2)` at their first
appearance and must not be treated as repo evidence. Open question §9.8 tracks capturing them.

---

## 0. Headline

**The curated list is a trading/crypto list wearing a finance label. It is not a corporate
back-office inventory, and it cannot be used as one.** Of 49 unique MCP servers:

| Requested bucket | Servers in the curated list | Share |
|---|---|---|
| Market + filings data | 17 | 35% |
| Other (crypto/DeFi/web3/trading execution) | 21 | 43% |
| Banking / treasury / payments | 7 (only **2** corporate fiat: Stripe, Qonto) | 14% |
| Personal finance | 2 | 4% |
| ERP / accounting | **1** (Norman Finance) | 2% |
| Expense / cards | **1** (Ramp) | 2% |
| Spreadsheets / docs | **0** | 0% |
| CRM / billing | **0** | 0% |
| Analytics / BI | **0** | 0% |

Grep proof of absence (`awesome-finance-mcp/README.md`, case-insensitive, 0 hits each):
QuickBooks · Xero · NetSuite · Dynamics · SAP · Sage · BILL · Brex · Concur · Coupa · Plaid ·
Modern Treasury · Mercury · EDGAR · Excel · Salesforce · HubSpot · Anaplan · BlackLine ·
FloQast · Numeric · Kyriba · Gusto · ADP · Avalara · Zip · Tipalti · Workday · Oracle.
(The only "Sheets" hits are inside the phrase "balance sheets".)

Consequences for finance-world:

1. **Our 7-server roster is not under-built relative to this list** — it is *orthogonal*
   to it. Five of our seven mocks (`erp`, `books`, `sheets`, `email`, `docs`) have zero
   counterpart in the curated list; only `filings` (market/filings data) overlaps its
   dominant category, and the list doesn't even contain an EDGAR server.
2. **The list's real value is tool-surface archetypes, not vendor coverage.** Four distinct
   surface designs recur (§4) and all four are already reflected — or should be — in our
   mock design.
3. **The master inventory has to be a fusion**: curated list (§2) + the cloned real MCP
   servers (§3) + `research/finance-tool-landscape.md` §§1–9 (the vendors that matter but
   have no entry here). §6 is that fused inventory.

---

## 1. What the list is, mechanically

- Format is fixed by `awesome-finance-mcp/AGENTS.md:26-45`: one markdown table row per
  entry, `| [Name](url) | description <60 chars | Pricing | stars-badge |` (`AGENTS.md:28`),
  with a closed pricing vocabulary of **8** values (`AGENTS.md:34-41`, "Use one of these
  exact values") — `Free`, `Freemium`, `Requires API key`, `Paid API key`,
  `Requires credentials`, `Requires wallet`, `Free (x402)`, `Free (self-hosted)`.
- `AGENTS.md:9` states it is "a documentation-only repository"; there is no machine-readable
  index — the README table *is* the data structure. No tool counts, no schemas, no
  verification that entries still exist.
- Contribution bar (`awesome-finance-mcp/CONTRIBUTING.md`, quick checklist at
  `README.md:207-211`): finance-related, working GitHub link, accurate description +
  pricing, "test that it actually works". No requirement to publish tool names.
- Sponsor/maintainer BlockRun sells agent-wallet infrastructure (`README.md:215-223`), which
  explains the x402/crypto-payments tilt.
- Totals: 59 table rows = 1 featured meta-list + **51 MCP server rows** + **7 skill rows**.
  51 rows → **49 unique servers** (Alpaca listed twice, `README.md:51` and `:67`; OpenBB
  twice, `:148` and `:174`).

---

## 2. Complete parse — every entry (no truncation)

Bucket codes: **ERP** ERP/accounting · **BNK** banking/treasury/payments · **SHT**
spreadsheets/docs · **MKT** market+filings data · **EXP** expense/cards · **CRM** CRM/billing ·
**BI** analytics/BI · **OTH** other (crypto/DeFi/web3/trading execution) · **PF** personal
finance.

### 2.1 MCP servers (51 rows / 49 unique)

| # | Name | Vendor/system | List section | Bucket | Pricing (as listed) | URL |
|---|---|---|---|---|---|---|
| 1 | Maverick MCP | wshobson (community) | Stock → Data Providers | MKT | Free | github.com/wshobson/maverick-mcp |
| 2 | MCP Trader | wshobson (community) | Stock → Data Providers | MKT | Free | github.com/wshobson/mcp-trader |
| 3 | Alpaca MCP | Alpaca (vendor) | Stock → Data Providers | MKT | Free (commission-free) | github.com/alpacahq/alpaca-mcp-server |
| 4 | Financial Datasets MCP | financialdatasets.ai (vendor) | Stock → Data Providers | MKT | Freemium | github.com/financial-datasets/mcp-server |
| 5 | Alpha Vantage MCP | Alpha Vantage (vendor) | Stock → Data Providers | MKT | Freemium | github.com/alphavantage/alpha_vantage_mcp |
| 6 | Financial Modeling Prep MCP | FMP (community wrapper) | Stock → Data Providers | MKT | Freemium | github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server |
| 7 | Finnhub MCP | Finnhub (community) | Stock → Data Providers | MKT | Freemium | github.com/sverze/stock-market-mcp-server |
| 8 | Massive MCP | Massive (vendor) | Stock → Data Providers | MKT | Freemium | github.com/massive-com/mcp_massive |
| 9 | QuantConnect MCP | QuantConnect (vendor) | Stock → Data Providers | MKT/OTH | Freemium | github.com/QuantConnect/mcp-server |
| 10 | FRED MCP | St. Louis Fed / FRED (community) | Stock → Data Providers | MKT | Free | github.com/stefanoamorelli/fred-mcp-server |
| 11 | KOSPI/KOSDAQ MCP | Korean exchanges (community) | Stock → Data Providers | MKT | Free | github.com/dragon1086/kospi-kosdaq-stock-server |
| 12 | Yahoo Finance MCP | Yahoo (community) | Stock → Data Providers | MKT | Free | github.com/maxscheijen/mcp-yahoo-finance |
| 13 | HK Finance MCP | HK OpenAI (community) | Stock → Data Providers | MKT | Free | github.com/hkopenai/hk-finance-mcp-server |
| 14 | Alpaca MCP *(dup of #3)* | Alpaca | Stock → Trading Execution | OTH | Free | same as #3 |
| 15 | MetaTrader 5 MCP | MetaQuotes MT5 (community) | Stock → Trading Execution | OTH | Free (requires MT5) | github.com/ariadng/metatrader-mcp-server |
| 16 | Paper MCP | paperinvest (vendor) | Stock → Trading Execution | OTH | Free | github.com/paperinvest/mcp-server |
| 17 | DexPaprika MCP | Coinpaprika (vendor) | Crypto → Data | OTH | Free | github.com/coinpaprika/dexpaprika-mcp |
| 18 | CCXT MCP | CCXT lib (community) | Crypto → Data | OTH | Free | github.com/Nayshins/mcp-server-ccxt |
| 19 | Crypto Indicators MCP | kukapay (community) | Crypto → Data | OTH | Free | github.com/kukapay/crypto-indicators-mcp |
| 20 | TradingView MCP | TradingView (community) | Crypto → Data | OTH | Freemium | github.com/atilaahmettaner/tradingview-mcp |
| 21 | Binance MCP | Binance (community) | Crypto → Trading | OTH | Requires API key | github.com/TermiX-official/binance-mcp |
| 22 | Coinbase MCP (AgentKit) | Coinbase (vendor) | Crypto → Trading | OTH | Requires credentials | github.com/coinbase/agentkit |
| 23 | DeFi Trading MCP | edkdev (community) | Crypto → Trading | OTH | Requires wallet | github.com/edkdev/defi-trading-mcp |
| 24 | Armor Crypto MCP | Armor Wallet (vendor) | Crypto → Trading | OTH | Requires wallet | github.com/armorwallet/armor-crypto-mcp |
| 25 | Bankless Onchain MCP | Bankless (vendor) | Crypto → On-Chain | OTH | Free | github.com/bankless/onchain-mcp |
| 26 | Hive Crypto MCP | Hive Intelligence (vendor) | Crypto → On-Chain | OTH | Freemium | github.com/hive-intel/hive-crypto-mcp |
| 27 | Crypto Liquidations MCP | kukapay (community) | Crypto → On-Chain | OTH | Requires API key | github.com/kukapay/crypto-liquidations-mcp |
| 28 | PancakeSwap PoolSpy MCP | kukapay (community) | DeFi & Swaps | OTH | Free | github.com/kukapay/pancakeswap-poolspy-mcp |
| 29 | Free USDC Transfer MCP | MagnetAI (community) | DeFi & Swaps | BNK | Free (x402) | github.com/magnetai/mcp-free-usdc-transfer |
| 30 | LunchMoney MCP | Lunch Money (community) | Personal Finance | PF | Requires account | github.com/akutishevsky/lunchmoney-mcp |
| 31 | Monarch Money MCP | Monarch (community) | Personal Finance | PF | Requires account | github.com/carsol/monarch-mcp-server |
| 32 | Stripe MCP | Stripe (vendor, official) | Payments & Banking | BNK/CRM | Requires API key | github.com/stripe/ai → mcp.stripe.com |
| 33 | Qonto MCP | Qonto (vendor, official) | Payments & Banking | BNK | Requires API key | github.com/qonto/qonto-mcp-server → mcp.qonto.com |
| 34 | Ramp MCP | Ramp (vendor, official) | Payments & Banking | EXP | Requires credentials | github.com/ramp-public/ramp_mcp |
| 35 | Fewsats MCP | Fewsats (vendor) | Payments & Banking | BNK | Freemium | github.com/Fewsats/fewsats-mcp |
| 36 | x402 Payment MCP | Coinbase (vendor) | Payments & Banking | BNK | Free (x402) | github.com/coinbase/x402 |
| 37 | Thirdweb MCP | thirdweb (vendor) | Blockchain & Web3 | OTH | Freemium | github.com/thirdweb-dev/ai |
| 38 | Base MCP | Base/Coinbase (vendor) | Blockchain & Web3 | OTH | Requires credentials | github.com/base/base-mcp |
| 39 | Solana MCP (Agent Kit) | SendAI (community) | Blockchain & Web3 | OTH | Free | github.com/sendaifun/solana-agent-kit |
| 40 | Bitcoin Lightning MCP | AbdelStark (community) | Blockchain & Web3 | OTH | Free | github.com/AbdelStark/bitcoin-mcp |
| 41 | OpenBB Platform | OpenBB (vendor) | Financial Intelligence | MKT | Free + Paid | github.com/OpenBB-finance/OpenBB |
| 42 | TrendRadar | sansan0 (community) | Financial Intelligence | MKT | Free | github.com/sansan0/TrendRadar |
| 43 | Finbrain MCP | Finbrain (vendor) | Financial Intelligence | MKT | Requires API key | github.com/ahmetsbilgin/finbrain-mcp |
| 44 | **Norman Finance MCP** | Norman Finance (vendor) | Financial Intelligence | **ERP** | Requires credentials | github.com/norman-finance/norman-mcp-server |
| 45 | Lightning Faucet | community | Community → Crypto | BNK/OTH | Free | github.com/lightningfaucet/mcp-server |
| 46 | LNbits MCP | LNbits (community) | Community → Crypto | BNK/OTH | Free | github.com/lnbits/LNbits-MCP-Server |
| 47 | Hashnet MCP | Hashgraph Online (community) | Community → Crypto | OTH | Free | github.com/hashgraph-online/hashnet-mcp-js |
| 48 | dexscreener-trending-mcp | kukapay (community) | Community → Crypto | OTH | Free | github.com/kukapay/dexscreener-trending-mcp |
| 49 | investor-agent | ferdousbhai (community) | Community → Crypto | MKT | Free | github.com/ferdousbhai/investor-agent |
| 50 | coincap-mcp | CoinCap (community) | Community → Crypto | OTH | Free | github.com/QuantGeekDev/coincap-mcp |
| 51 | OpenBB MCP *(dup of #41)* | OpenBB | Community → Fin. Intelligence | MKT | Free | same as #41 |

Row-level provenance: `awesome-finance-mcp/README.md:49-61` (stock data), `:67-69`
(trading execution), `:79-82` (crypto data), `:88-91` (crypto trading), `:97-99` (on-chain),
`:107-108` (DeFi), `:116-117` (personal finance), `:125-129` (payments & banking),
`:137-140` (blockchain), `:148-151` (financial intelligence), `:163-168` + `:174`
(community).

### 2.2 Skills / workflows (7 rows, `README.md:183-190`)

| Name | What it does | Built on | Bucket | URL |
|---|---|---|---|---|
| Equity Research | Institutional equity research: buy/sell recs, fundamentals, technicals | Claude Code Plugin | MKT | github.com/quant-sentiment-ai/claude-equity-research |
| FinLab AI | Mass-produce quant strategies; Taiwan market | FinLab + Claude | OTH | github.com/koreal6803/finlab-ai |
| Trading Terminal | Sub-agents for trades/positions/risk | Claude Code + Jupiter | OTH | github.com/degentic-tools/claude-code-trading-terminal |
| Claude Investor | Price data, balance sheets, sentiment, analyst ratings | Claude 3 | MKT | github.com/martinxu9/claude-investor |
| Trading Skills | IBD-style RS Rating momentum screen | Claude Code Skill | OTH | github.com/tradermonty/claude-trading-skills |
| **Invoice Organizer** | Extract/rename/sort invoices + receipts for tax prep | Claude Code Skill | **ERP** | github.com/ComposioHQ/awesome-claude-skills/tree/main/invoice-organizer |
| Twitter Intel | X/Twitter intel for finance; monitor/summarize/alert | Grok + BlockRun (~$0.25-0.50/query) | MKT | github.com/BlockRunAI/blockrun-agent-wallet/tree/main/skills/twitter-intel |

The skill-entry bar (`README.md:194-199`) is the interesting artifact: stable link, explicit
inputs/outputs, **which MCP servers/APIs it uses**, pricing, and a runnable example prompt —
i.e. a skill is defined as *task-level workflow over a tool set*. That is exactly the
task-shape our ladder produces, and it's the one place the list is more rigorous than its
server tables.

---

## 3. Verified tool surfaces — the back-office-relevant subset

Ranked by relevance to a **corporate finance back-office** persona (controller / AP / AR /
treasury / FP&A), not trading. Rows 1–12 are the top-12 ask; rows 13–16 are the
already-cloned cross-references that the curated list omits entirely but that matter far
more to our world.

| # | Server | Tool count | Surface shape (verified) | Evidence |
|---|---|---|---|---|
| 1 | **Ramp** (cards/spend) | **19** = 3 db + 2 fetch + **14 load** | Load-then-SQL ETL into an ephemeral in-memory SQLite | `ramp_mcp/src/ramp_mcp/tools.py:66-406`, `ramp_mcp/src/ramp_mcp/memory_db.py:9-22` |
| 2 | **Stripe** (payments/billing) | *hosted* **11 named** + ~100 whitelisted REST methods **(tier 2)**; *local* `@stripe/mcp` ships a flat **23**-tool roster | Two different surfaces from one vendor: hosted = meta-API (search → details → generic read/write); local = named per-resource tools | hosted: fetched https://docs.stripe.com/mcp. Local, repo-verified: `stripe-agent-toolkit/tools/modelcontextprotocol/manifest.json:32-55` |
| 3 | Norman Finance (SMB accounting/tax) | 11 published *skills*; tool names **UNVERIFIED** | OAuth 2.1 remote at `https://mcp.norman.finance/mcp` | fetched https://github.com/norman-finance/norman-mcp-server |
| 4 | Qonto (business banking) | **UNVERIFIED** (4 categories only) | Remote at `mcp.qonto.com`; env `QONTO_API_KEY` + `QONTO_ORGANIZATION_ID` | fetched https://github.com/qonto/qonto-mcp-server |
| 5 | Financial Datasets (fundamentals) | **11** | Flat typed getters | `financial-datasets-mcp-server/server.py:43-338` |
| 6 | FMP (fundamentals + filings) | **250+ in 24 categories** **(tier 2)** | Three modes; **dynamic mode = 5 meta-tools** that load toolsets at runtime | fetched https://github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server |
| 7 | Alpha Vantage (market + fundamentals) | 9 fundamentals + 4 FX + **54 technical indicators** + more **(tier 2)** | One tool per API function, named like the REST params | fetched https://github.com/alphavantage/alpha_vantage_mcp |
| 8 | FRED (macro) | **3** **(tier 2)** | Catalog-navigation: browse → search → get_series | fetched https://github.com/stefanoamorelli/fred-mcp-server |
| 9 | Monarch Money (PF, read model) | 6 tools + 4 MCP **resources** **(tier 2)** | Tools for queries, resources for standing views | fetched https://github.com/carsol/monarch-mcp-server |
| 10 | LunchMoney | **UNVERIFIED** | — | fetch later: https://github.com/akutishevsky/lunchmoney-mcp |
| 11 | OpenBB | **UNVERIFIED** (platform, not a single server) | — | fetch later: https://github.com/OpenBB-finance/OpenBB |
| 12 | Invoice Organizer (skill) | n/a (skill) | Document extract → rename → sort for tax prep | fetch later: github.com/ComposioHQ/awesome-claude-skills |
| 13 | **QuickBooks Online** *(not in list)* | **142 tool files** shipped; README badge claims **145** across 29 entities + 11 reports | Many small typed tools: create/get/update/delete/search per entity | `quickbooks-online-mcp-server/src/tools/` (142 `*.tool.ts`), `quickbooks-online-mcp-server/README.md:8,26` |
| 14 | **Xero** *(not in list)* | **51** = 25 list + 11 create + **13** update + 1 get + 1 delete | Verb-partitioned tools; OAuth scope tiers V1/V2 | Registered exports, not a file glob: `xero-mcp-server/src/tools/update/index.ts:16-30` (13 `UpdateTools`) + the five `index.ts` arrays wired at `src/tools/tool-factory.ts:3-7,11-23`; corroborated by `xero-mcp-server/README.md:140-190` (51 documented commands) |
| 15 | **SEC EDGAR** *(not in list)* | **21** | Discovery + retrieval + analysis, incl. self-describing `get_recommended_tools(form_type)` | `sec-edgar-mcp/sec_edgar_mcp/server.py:41-463` |
| 16 | **Modern Treasury** *(not in list)* | **65** MCP tools over **104** API paths | Resource×verb grid over a payment-ops object model | `modern-treasury-mcp-http/src/tools.ts`, `modern-treasury-openapi/openapi/mt_openapi_spec_v1.yaml` |

### 3.1 Exact tool names (the ones a mock would copy)

**Ramp** (`ramp_mcp/src/ramp_mcp/tools.py`, line numbers in parens):
`clear_table`(66) · `process_data`(75) · `execute_query`(88) · `get_ramp_categories`(103) ·
`get_currencies`(111) · `load_transactions`(125) · `load_spend_export`(158) ·
`load_receipts`(182) · `load_reimbursements`(212) · `load_bills`(241) · `load_locations`(270) ·
`load_departments`(287) · `load_bank_accounts`(298) · `load_vendors`(315) ·
`load_vendor_bank_accounts`(346) · `load_entities`(361) · `load_spend_limits`(378) ·
`load_spend_programs`(395) · `load_users`(406).

> **Docs-vs-shipped conflict (shipped wins):** `ramp_mcp/README.md:29-42` (header at :29,
> 12 data rows at :31-42) documents **12** load tools against **11 unique scopes**
> (`vendors:read` covers both `load_vendors` and `load_vendor_bank_accounts`); the code ships
> **14** — `load_spend_export` and `load_receipts` are undocumented.
> The README documents the OAuth scope required per tool (`transactions:read`,
> `reimbursements:read`, `bills:read`, `locations:read`, `departments:read`,
> `bank_accounts:read`, `vendors:read`, `entities:read`, `limits:read`,
> `spend_programs:read`, `users:read`) and the server refuses tools whose scope wasn't passed
> at launch (`-s <COMMA-SEPARATED-SCOPES>`, `README.md:64`).
>
> The **shipped mechanism is strictly better evidence** and lives at
> `ramp_mcp/src/ramp_mcp/__init__.py:40-54`: `scope_to_tools_mapping` is **12 scopes over 13
> load tools** (`"vendors:read": [load_vendors, load_vendor_bank_accounts]` at :49, and
> `receipts:read` at :43 which the README table omits). Two further primitives the docs
> version hides: an **unrecognized scope is silently skipped** (`if scope not in
> scope_to_tools_mapping: continue`, `:72-73` — no error, the tool just never appears), and
> the 14th load tool `load_spend_export` is **composite-gated behind holding all three** of
> `transactions:read`/`reimbursements:read`/`bills:read` simultaneously (`:77-82`). The five
> non-load tools are registered unconditionally (`:84-89`). **This is the cleanest real
> example of scope-gated tool availability we have** — a ready-made difficulty axis.

Ramp friction constants worth copying verbatim: `CLIENT_MAX_PAGES = 100`
(`ramp_mcp/src/ramp_mcp/constants.py:1`) — and the constant's **only** use site is
`ramp_mcp/src/ramp_mcp/client.py:81-82`, inside `while _url is not None:`:
`if i > CLIENT_MAX_PAGES: raise Exception("Too many pages, try to filter more results out.")`.
So this is a **loud hard failure carrying its own remediation hint**, not silent truncation:
the agent gets no partial result at all past page 100, and is told to filter. (Earlier drafts
of this note read the constant without opening the call site and described it as a silent
cap — corrected here under our own shipped-code-wins rule.) Amounts
are **integers in the smallest denomination** ("1000 refers to 1000 cents or $10.00",
`constants.py:2-5`); a fixed 43-entry category taxonomy `SK_CATEGORIES` (`constants.py:6-50`
— the file is 50 lines and the dict's closing brace is the last one; ids 1–44 with **22
absent** — a real gap in a real enum). The README also warns "Large
datasets may not be processable due to API and/or your MCP client limitations"
(`ramp_mcp/README.md:5`) — vendor-admitted truncation.

**Stripe hosted MCP** (**tier 2** — fetched https://docs.stripe.com/mcp; the 11-name roster
and the ~100-method whitelist below are not re-derivable from any local tree). *Partial
tier-1 corroboration exists* in the cloned `stripe-agent-toolkit/`: the meta-API triple
`stripe_api_search` / `stripe_api_details` / `stripe_api_read` appears as expected
`tools_triggered` in `providers/codex/plugin/test-cases.json:15,21,33`;
`get_stripe_account_info` at `:27`; `search_stripe_documentation` at `benchmarks/README.md:24`
("the sole resource available beyond the starting state of each eval") and `skills/README.md:8`;
`create_refund` at `tools/modelcontextprotocol/manifest.json:47`. The other five names
(`stripe_api_write`, `get_balance_summary`, `stripe_implementation_planner`,
`send_stripe_mcp_feedback`, `stripe_report`) appear nowhere on disk and remain tier 2.
Full hosted roster: `stripe_api_search` ·
`stripe_api_details` · `stripe_api_read` · `stripe_api_write` · `get_stripe_account_info` ·
`create_refund` · `get_balance_summary` (Treasury, public preview) ·
`search_stripe_documentation` · `stripe_implementation_planner` · `send_stripe_mcp_feedback` ·
`stripe_report`. The doc states the point of the design outright: the read/write pair "makes
much of the API available through MCP without increasing the context window unnecessarily",
over a published whitelist of ~100 methods (customers, charges, refunds, payment_intents,
checkout sessions, invoices incl. finalize, invoiceitems, subscriptions, coupons, promotion
codes, products, prices, payment links, disputes, webhook endpoints, balance,
balance_transactions, payouts, tax settings/codes/registrations, Issuing
authorizations/cardholders/cards/disputes/transactions, and v2 money-management
financial_accounts / inbound & outbound transfers / received credits & debits / transaction
entries). Auth: OAuth preferred; restricted API key as `Authorization: Bearer` fallback;
`Stripe-Account` header for connected-account calls; admins can revoke OAuth sessions and
gate MCP access per environment (sandbox vs live).

**Stripe *local* MCP — `@stripe/mcp` (tier 1, repo-verified)**, a genuinely different surface
from the same vendor. `stripe-agent-toolkit/tools/modelcontextprotocol/manifest.json:32-55`
declares **23 flat named tools**: `search_documentation` · `get_stripe_account_in` *(sic —
truncated in the manifest)* · `create_customer` · `list_customers` · `create_product` ·
`list_products` · `create_price` · `list_prices` · `create_payment_link` · `create_invoice` ·
`list_invoices` · `create_invoice_item` · `finalize_invoice` · `retrieve_balance` ·
`create_refund` · `list_payment_intents` · `list_subscriptions` · `cancel_subscription` ·
`update_subscription` · `list_coupons` · `create_coupon` · `update_dispute` · `list_disputes`.
That is **archetype B, not A** — so Stripe ships *both* archetypes depending on deployment,
which is a sharper finding than "Stripe is the meta-API vendor". Two more shipped primitives:
the `--tools` selection flag **was removed**, and tool availability is now decided entirely by
the Restricted API Key's permissions (`tools/modelcontextprotocol/src/cli.ts:17-24` warns
"The --tools flag has been removed. Tool permissions are now controlled by your Restricted API
Key (RAK)."; same rule at `tools/modelcontextprotocol/README.md:23`) — i.e. **a second,
independent instance of scope-gated tool availability**, keyed on credential rather than CLI
argument. And `tools/modelcontextprotocol/README.md:60-62` points at the hosted docs instead
of listing tools, so the local repo cannot self-describe its own roster.

**FRED** (**tier 2**, fetched — `fred_browse` appears nowhere on disk except in this note):
`fred_browse(browse_type, category_id, release_id, limit, offset,
order_by, sort_order)` · `fred_search(search_text, search_type, tag_names, exclude_tag_names,
limit, offset, order_by, sort_order, filter_variable, filter_value)` ·
`fred_get_series(series_id, observation_start, observation_end, limit, offset, sort_order,
units, frequency, aggregation_method)`. Three tools for an entire national statistics
catalog — the extreme end of the discovery-first spectrum.

**Financial Datasets** (`financial-datasets-mcp-server/server.py`): `get_income_statements`(44) ·
`get_balance_sheets`(76) · `get_cash_flow_statements`(108) · `get_current_stock_price`(140) ·
`get_historical_stock_prices`(166) · `get_company_news`(202) · `get_available_crypto_tickers`(226) ·
`get_crypto_prices`(246) · `get_historical_crypto_prices`(276) · `get_current_crypto_price`(312) ·
`get_sec_filings`(338).

**SEC EDGAR** (`sec-edgar-mcp/sec_edgar_mcp/server.py`): `get_cik_by_ticker` ·
`get_company_info` · `search_companies` · `get_company_facts` · `get_recent_filings` ·
`get_filing_content(offset, max_chars=50000)` · `analyze_8k` · `get_filing_sections` ·
`get_financials` · `get_segment_data` · `get_key_metrics` · `compare_periods` ·
`discover_company_metrics` · `get_xbrl_concepts` · `discover_xbrl_concepts` ·
`get_insider_transactions` · `get_insider_summary` · `get_form4_details` ·
`analyze_form4_transactions` · `analyze_insider_sentiment` · `get_recommended_tools`.
Note the `offset`/`max_chars` pair on `get_filing_content` (:116) — real, shipped
document-chunking friction, and `get_recommended_tools(form_type)` (:463), a
self-documentation tool that tells the agent which tools suit a given filing type.

**Modern Treasury** (`modern-treasury-mcp-http/src/tools.ts`, 65 tools, verbatim): `ping` ·
`payment_order_create` · `payment_orders_list` · `payment_order_get` · `payment_order_update` ·
`return_create` · `returns_list` · `return_get` · `incoming_payments_list` ·
`incoming_payment_get` · `incoming_payment_update` · `counterparty_create` ·
`counterparties_list` · `counterparty_get` · `counterparty_update` · `counterparty_delete` ·
`internal_accounts_list` · `internal_account_get` · `external_account_create` ·
`external_accounts_list` · `external_account_get` · `external_account_update` ·
`external_account_delete` · `virtual_account_create` · `virtual_accounts_list` ·
`virtual_account_get` · `transactions_list` · `transaction_get` · `transaction_update` ·
`expected_payment_create` · `expected_payments_list` · `expected_payment_get` ·
`expected_payment_update` · `ledger_create` · `ledgers_list` · `ledger_get` · `ledger_update` ·
`ledger_account_create` · `ledger_accounts_list` · `ledger_account_get` ·
`ledger_account_update` · `ledger_tx_create` · `ledger_txs_list` · `ledger_tx_get` ·
`ledger_tx_update` · `ledger_tx_reverse` · `ledger_entries_list` · `ledger_entry_get` ·
`invoice_create` · `invoices_list` · `invoice_get` · `invoice_update` · `fx_quote_create` ·
`fx_quotes_list` · `fx_quote_get` · `balance_reports_list` · `balance_report_get` ·
`connections_list` · `events_list` · `event_get` · `line_items_list` · `line_item_get` ·
`payment_references_list` · `payment_reference_get` · `routing_number_validate`.

**Xero** — **51** verb-partitioned tools under `xero-mcp-server/src/tools/`, counted from the
per-directory `index.ts` export arrays (which `src/tools/tool-factory.ts:11-23` registers),
**not** from a `*.tool.ts` file glob: 25 `list-*` (incl. `list-aged-receivables-by-contact`,
`list-aged-payables-by-contact`, `list-trial-balance`, `list-profit-and-loss`,
`list-report-balance-sheet`, plus **7** payroll ones — `list-payroll-employees`,
`list-payroll-employee-leave`, `-leave-balances`, `-leave-types`, `list-payroll-leave-periods`,
`list-payroll-leave-types`, `list-payroll-timesheets`), 11 `create-*`,
**13** `update-*` (`src/tools/update/index.ts:16-30`; incl. `approve-payroll-timesheet`,
`revert-payroll-timesheet`, and `UpdateManualJournalTool`), 1 `get-*`,
1 `delete-*`. Tool ids are kebab-case (`"list-invoices"`,
`xero-mcp-server/src/tools/list/list-invoices.tool.ts:6`).

> **Count-the-registration, not the file.** A `*.tool.ts` glob yields 50 because
> `src/tools/update/update-manual-journal-tool.ts` uses a **hyphen instead of a dot** before
> `tool.ts` while still being imported and exported (`update/index.ts:11,20`). The repo's own
> README documents **51** commands (`xero-mcp-server/README.md:140-190`). This is the exact
> file-vs-registered-id error §9.6 warns about for QBO — recorded here because this note
> previously committed it.

**QuickBooks Online** — 142 shipped `*.tool.ts` files: 25 `create-*`, 20 `delete-*`,
40 `get-*` (incl. the 11 report tools `get-aged-payables`, `get-aged-receivables`,
`get-balance-sheet`, `get-cash-flow`, `get-customer-balance`, `get-customer-sales`,
`get-general-ledger`, `get-profit-and-loss`, `get-trial-balance`, `get-vendor-balance`,
`get-vendor-expenses`), 2 `read-*`, 29 `search-*`, 26 `update-*`. Tool ids are snake_case
(`const toolName = "search_invoices"`,
`quickbooks-online-mcp-server/src/tools/search-invoices.tool.ts:5`).

### 3.2 Friction / limits / error behavior worth stealing (tier 1 unless marked **tier 2**)

| Mechanism | Real instance | Evidence |
|---|---|---|
| **Scope-gated tool availability** — a tool exists only if its OAuth scope was granted at launch | Ramp: README table = 12 load tools over **11 unique** scopes; shipped map = **12 scopes over 13** load tools + a 14th (`load_spend_export`) gated on **all three** of transactions/reimbursements/bills. Unrecognized scopes are silently `continue`d, so a typo'd scope removes tools with no error. Second instance: Stripe local MCP gates the roster on the Restricted API Key, having **removed** its `--tools` flag | `ramp_mcp/README.md:29-42,64` (docs) + `ramp_mcp/src/ramp_mcp/__init__.py:40-54,72-73,77-82` (shipped); `stripe-agent-toolkit/tools/modelcontextprotocol/src/cli.ts:17-24` |
| **Hard page cap that aborts the whole call** — not silent truncation: past 100 pages the agent gets an exception and *zero* rows, plus a remediation hint telling it to filter | Ramp: `if i > CLIENT_MAX_PAGES: raise Exception("Too many pages, try to filter more results out.")` | `ramp_mcp/src/ramp_mcp/client.py:81-82` (behavior); `constants.py:1` (the 100) |
| **Integer minor units** — precision trap | "1000 refers to 1000 cents or $10.00" | `ramp_mcp/src/ramp_mcp/constants.py:2-5` |
| **Gapped enum** — ids 1–44 with 22 missing | Ramp `SK_CATEGORIES` | `ramp_mcp/src/ramp_mcp/constants.py:6-50` |
| **Ephemeral analysis DB** — data must be loaded, then processed, before it's queryable; unprocessed tables error | Ramp `store_data` → `data_is_processed` → `execute_query` | `ramp_mcp/src/ramp_mcp/memory_db.py:25-45` |
| **Cursor pagination with response headers** | Modern Treasury `after_cursor` / `per_page` in, `X-After-Cursor` / `X-Per-Page` out | `modern-treasury-openapi/openapi/mt_openapi_spec_v1.yaml:22-57` |
| **Payment state machine (13 states)** | MT `GET /api/payment_orders?status=` enum: `approved, cancelled, completed, denied, failed, held, needs_approval, pending, processing, returned, reversed, sent, stopped` | `mt_openapi_spec_v1.yaml:6920-6938` |
| **Whitelisted-verb meta-API** — an operation exists only if it's on the published method list | Stripe `stripe_api_read` / `stripe_api_write` | **tier 2** — fetched docs.stripe.com/mcp (only `stripe_api_read`/`_search`/`_details` have local corroboration, at `stripe-agent-toolkit/providers/codex/plugin/test-cases.json:15,21,33`; `stripe_api_write` is on disk nowhere) |
| **Write-class kill switches** | QBO `QUICKBOOKS_DISABLE_WRITE` / `_UPDATE` / `_DELETE`; "Read tools (`get_*`, `search_*`) are always available" | `quickbooks-online-mcp-server/README.md:71-73,105` |
| **Allowed-field whitelists per entity** (query rejects anything else) | QBO invoice filter fields `Id, MetaData.CreateTime, MetaData.LastUpdatedTime, DocNumber, TxnDate, DueDate, CustomerRef, ClassRef, DepartmentRef, Balance, TotalAmt` | `quickbooks-online-mcp-server/src/tools/search-invoices.tool.ts:8-22` |
| **Fixed small page + "ask for the next page"** in the tool description itself | Xero list-invoices: "Ask the user if they want the next page … if 10 invoices are returned" | `xero-mcp-server/src/tools/list/list-invoices.tool.ts:6-16` |
| **Scope-version drift** — the same server needs different scopes depending on when the connection was created, with automatic V1→V2 fallback | Xero SCOPES_V1 (before 2026-04-29) vs SCOPES_V2 | `xero-mcp-server/README.md:54-59` |
| **Document chunking** on filing text | EDGAR `get_filing_content(offset=0, max_chars=50000)` | `sec-edgar-mcp/sec_edgar_mcp/server.py:116` |
| **Runtime toolset loading** — start with meta-tools, load categories on demand | FMP dynamic mode: "Starts with 5 meta-tools; load toolsets at runtime" | **tier 2** — fetched github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server |
| **Demo-vs-prod environment flag** defaulting to demo | Ramp `RAMP_ENV=demo` default | `ramp_mcp/README.md:5` |

---

## 4. The four tool-surface archetypes (the list's real deliverable)

| Archetype | Definition | Real instances | Where finance-world already uses it |
|---|---|---|---|
| **A. Discovery-first / meta-API** | 3–7 tools that find, describe, then read/write anything | Stripe *hosted* (4 meta-tools, **tier 2**) · D365 dynamic ERP MCP (`data_find_entity_type` → `data_get_entity_metadata` → `data_find_entities_sql`) · FRED (3, **tier 2**) · FMP dynamic mode (5, **tier 2**) | `erp` — 1:1 with D365's 22 tools (`docs/GAP-ANALYSIS.md:22-37`) |
| **B. Many small typed tools** | One tool per entity × verb | QBO (142) · Xero (**51**) · Modern Treasury (65) · Stripe *local* `@stripe/mcp` (23, `stripe-agent-toolkit/tools/modelcontextprotocol/manifest.json:32-55`) · Alpha Vantage (67+, **tier 2**) | `books` (14, a QBO slice), `filings` (7) |
| **C. Load-then-SQL ETL** | `load_*` pulls API pages into an ephemeral SQLite, then the agent writes SQL | Ramp (19) | not used — the closest is `erp.data_find_entities_sql` |
| **D. Domain navigation / progressive disclosure** | Navigate into a domain, then that domain's tools appear | **No repo-verified instance.** FMP toolsets (**tier 2**). ~~Xero `xero_navigate`~~ — **retracted**: a recursive grep for `xero_navigate` (and for the bare word `navigate`) across `xero-mcp-server/src/` and its `README.md` returns **zero** hits; the cloned official server is 51 flat verb-partitioned tools (archetype B). The claim came from `research/erp-domain.md:166`, which is itself uncited; shipped code wins | not used |

Two observations that matter for the world:

- **A and C are converging.** Microsoft replaced its OData find with
  `data_find_entities_sql` in 10.0.48 (`research/erp-domain.md` §4.2); Ramp's whole product
  is "get it into SQLite, then query"; Stripe's read/write pair exists to keep the context
  window small. Agent-facing finance tools are trending toward *few tools + a query
  language*, which is exactly what our `erp` mock is shaped like.
- **Every archetype has a distinct failure mode**, which is the difficulty axis: A fails on
  *discovery* (the agent never finds the entity); B fails on *selection* (142 tools, picks
  the wrong one); C fails on *sequencing* (queries before processing, or forgets to load);
  D fails on *navigation* (never enters the domain holding the answer). A task ladder can be
  organized along exactly these four — with the caveat that **D is now the weakest-evidenced
  archetype**: after the `xero_navigate` retraction its only instance is tier-2 FMP, so a
  D-shaped task would be designed from an unverified pattern. A/B/C each have multiple
  repo-verified instances.
- **The archetype is a deployment choice, not a vendor property.** Stripe ships archetype A
  hosted and archetype B locally (23 named tools, `manifest.json:32-55`) from the same
  product. Any claim of the form "vendor X uses surface shape Y" has to name *which* server.

---

## 5. Cross-reference: what each finance-world server stands for

Roster from `mcp/mcp-servers.json`; counts from `docs/TOOLS.md`.

| Our server | Tools | `shaped_after` | Real products it stands for | In the curated list? | Nearest verified analog + evidence |
|---|---|---|---|---|---|
| `erp` | 23 | Microsoft D365 ERP MCP (discovery-first) | D365 F&O, SAP S/4HANA, Oracle Fusion, NetSuite, Sage Intacct, Workday Financials | **No** — zero ERP vendors listed | D365 dynamic MCP 22 tools (`research/erp-domain.md` §4.2); archetype A ≡ Stripe's *hosted* meta-API (**tier 2**, fetched docs.stripe.com/mcp) |
| `books` | 14 | QuickBooks Online (subsidiary CES Direct LLC) | QBO, Xero, Sage Intacct, FreshBooks, Norman Finance | **Partly** — only Norman Finance (#44) | QBO 142 shipped tools (`quickbooks-online-mcp-server/src/tools/`); Xero **51** registered (`xero-mcp-server/src/tools/*/index.ts` via `tool-factory.ts:11-23`) |
| `sheets` | 5 | Excel shadow trackers on the shared drive | Microsoft Graph workbook API, Google Sheets v4, Cube/Datarails-style Excel-native FP&A | **No** — zero spreadsheet servers | none in the list; Graph surface in `docs/GAP-ANALYSIS.md:39-58` |
| `email` | 5 | Shared AP/AR mailbox | Gmail/Graph mail; Auditoria-style mailbox agents | **No** | none |
| `filings` | 7 | SEC EDGAR companyconcept/submissions | EDGAR, FMP, Financial Datasets, Alpha Vantage, OpenBB, Kensho/CapIQ, Daloopa | **Yes — the list's dominant category (17 servers)**, though EDGAR itself is absent | `sec-edgar-mcp` 21 tools; `financial-datasets-mcp-server` 11 tools; FMP 250+ |
| `docs` | 5 | Internal policy/SOP document store | SharePoint/Confluence/Drive policy libraries | **No** | none (the Invoice Organizer *skill* is the only document-handling entry) |
| `harness` | 2 | Answer submission (graded state) | n/a — eval-only, off the business surface | n/a | `docs/TOOL-CENSUS.md:18` |

### 5.1 Major tool classes with **no mock at all**

| Class | Real products | Curated-list coverage | Evidence a finance agent needs it | Verdict |
|---|---|---|---|---|
| **Bank portal / treasury** | JPM Access, BofA CashPro, Mercury, Modern Treasury, Kyriba, Trovata, Plaid | Qonto (#33) only; MT/Mercury/Plaid absent | Already flagged in `docs/TOOL-CENSUS.md:26-27` ("in the research … but not yet required by a shipped task"); we ship a `bank_rec` task today that *simulates* the statement inside the world rather than behind a bank tool (`PLAN.md:82-84`) | **Strongest candidate** — see §7 |
| **AP automation / vendor bills** | BILL, Tipalti, Stampli, AvidXchange, Coupa | none | `research/finance-tool-landscape.md` §2: BILL ~480k customers; sync lag is "the canonical chaos primitive" | Candidate, blocked on task evidence |
| **Expense / corporate cards** | Ramp, Brex, Concur, Navan, Expensify | Ramp (#34) only | Ramp MCP is cloned and fully readable; but no shipped task needs card spend | Not yet — no task |
| **Procurement / intake** | Zip, Coupa, Ariba | none | `research/finance-tool-landscape.md` §7 | No — needs PO/receipt tables first (3-way match is already parked, `PLAN.md:89`) |
| **Payroll** | ADP, Gusto, Paylocity, Workday | none | no finance-world workflow touches it | No |
| **Tax** | Avalara, Vertex, Norman (SMB) | Norman (#44) partial | no shipped task | No |
| **BI / analytics** | Power BI, Grafana, D365 ERP Analytics MCP (`get-bpa-dataset-schema`, `execute-dax-query`) | none | `research/erp-domain.md` §4.2 | No — our `erp` SQL tool already covers the "query the warehouse" motion |
| **CRM** | Salesforce, HubSpot | none | explicitly excluded (`docs/TOOL-CENSUS.md:28`, `docs/GAP-ANALYSIS.md:60-74`) | **No — and the curated list corroborates**: a finance-tool list built by an independent party contains zero CRM servers |
| **Close management** | BlackLine, FloQast, Numeric | none | `research/finance-tool-landscape.md` §4 | Not yet — no close task ships |

The CRM row is the most useful negative result in this document: our exclusion of Salesforce
was argued from workflow evidence; an independently curated finance-MCP list containing 49
servers and **zero** CRM entries is external corroboration.

---

## 6. The fused master inventory

The universe a corporate finance agent could be asked to call, by class, with the
best-verified MCP surface per class. "Source" = curated list (§2 row #), cloned repo, or
`research/finance-tool-landscape.md` (FTL) §.

| Class | Systems | Best-documented MCP surface | Source |
|---|---|---|---|
| ERP (enterprise) | D365 F&O, SAP S/4HANA, Oracle Fusion, NetSuite, Workday | D365 dynamic MCP: 7 data + 13 form + 2 action tools | `research/erp-domain.md` §4.2; FTL §1 |
| ERP/accounting (SMB–mid) | QBO, Xero, Sage Intacct, Norman, Rillet, Digits | QBO 142 shipped tools / 29 entities / 11 reports; Xero **51** | `quickbooks-online-mcp-server/`, `xero-mcp-server/src/tools/*/index.ts`, list #44 |
| AP automation | BILL, Tipalti, Stampli, AvidXchange, Coupa, Airbase | community only | FTL §2 |
| Expense / cards | Ramp, Brex, Concur, Navan, Expensify | **Ramp 19 tools (official, cloned)** | `ramp_mcp/`, list #34 |
| AR / collections | HighRadius, Billtrust, Versapay, Tesorio, Upflow, Invoiced | none official | FTL §3 |
| Close management | BlackLine, FloQast, Numeric | Numeric MCP 20+ tools + 17 skills | FTL §4 |
| Treasury / payment ops | Kyriba, Trovata, Modern Treasury, Mercury, Plaid | **MT 65 tools / 104 paths (cloned)** | `modern-treasury-*`, FTL §5 |
| Business banking | Qonto, Mercury, bank portals (JPM/BofA) | Qonto (categories only, **UNVERIFIED** tools) | list #33, FTL §5 |
| Payments / billing | Stripe, PayPal, Adyen | Stripe *hosted* 11 tools + ~100 whitelisted methods (**tier 2**); Stripe *local* `@stripe/mcp` **23 named tools (repo-verified)** | list #32, fetched docs.stripe.com/mcp; `stripe-agent-toolkit/tools/modelcontextprotocol/manifest.json:32-55` |
| FP&A | Anaplan, Pigment, Mosaic, Cube, Datarails, **Excel** | Anaplan community only (vendor restricts MCP use) | FTL §6 |
| Spreadsheets | Graph Excel, Google Sheets | Graph workbook API (not MCP) | `docs/GAP-ANALYSIS.md:39-58` |
| Procurement | Zip, Coupa, Ariba | none | FTL §7 |
| Payroll / HRIS | ADP, Gusto, Paylocity, Workday | none in scope | — |
| Tax | Avalara, Vertex, Norman | Norman (11 skills, tools **UNVERIFIED**) | list #44 |
| Filings / fundamentals | SEC EDGAR, FMP, Financial Datasets, Alpha Vantage, OpenBB, Kensho, Daloopa | **EDGAR 21 (cloned)**, FinDatasets 11 (cloned), FMP 250+ (**tier 2**), AV 67+ (**tier 2**) | `sec-edgar-mcp/`, `financial-datasets-mcp-server/`, list #4-#7 |
| Macro data | FRED, BLS, Census | FRED 3 tools (**tier 2**) | list #10, fetched |
| Market/trading | Alpaca, IBKR, MT5, QuantConnect, CCXT, exchanges | 21 servers | list #1-#28 |
| Comms | Gmail/Graph mail, Teams/Slack | n/a | `docs/TOOL-CENSUS.md:15` |
| Docs | SharePoint, Confluence, Drive | n/a | `docs/TOOL-CENSUS.md:17` |
| CRM | Salesforce, HubSpot | Salesforce hosted MCP (SObject All / Headless 360) | `docs/GAP-ANALYSIS.md:60-74`; **absent from list** |
| BI | Power BI, Grafana, D365 ERP Analytics | ERP Analytics MCP: 2 tools | `research/erp-domain.md` §4.2 |
| Agent payments (novel) | x402, Fewsats, BlockRun | 3 servers | list #35, #36, #29 |

---

## 7. Recommendation — new servers to mock

Census rule. The **three-part** formulation — (1) workflow evidence, (2) benchmark grounding,
**and** (3) a shipped task's verifier requires it (`required_servers`) — is stated only at
`docs/GAP-ANALYSIS.md:6-14`. `docs/TOOL-CENSUS.md:6-8` states a **two-part** rule ("a server
exists here iff (a) research evidence says this team uses that system class, and (b) at least
one shipped task requires it") — it has no separate benchmark clause. The stricter
GAP-ANALYSIS version is what this section applies. Tested honestly, **this research justifies
at most one new server, and even that one is gated on authoring its task first.**

| Rank | Candidate | (1) Workflow evidence | (2) Benchmark grounding | (3) Shipped task needs it | Verdict |
|---|---|---|---|---|---|
| 1 | **`bank` — bank portal / payment ops** (Modern Treasury object model, bank-portal UX) | ✅ FTL §5; `docs/TOOL-CENSUS.md:26` already names the timing-gap chaos | 🟡 no FinanceBenchmark item; our own `bank_rec` + `cash_app` + `payment_proposal` tasks are researched-scenario-grounded (`PLAN.md:82-88`) | ❌ **not yet** — `bank_rec` ships today with the statement seeded in-world | **Build only with a new task that requires it** (e.g. an unreleased-wire / cutoff-time task). Otherwise it is realism for its own sake. |
| 2 | AP automation (`bill`) | ✅ FTL §2 (BILL ~480k customers; sync lag) | ❌ | ❌ | **No** |
| 3 | Expense/cards (`cards`, Ramp-shaped) | ✅ FTL §2/§9; list #34; **surface fully verified and cloned** | ❌ | ❌ | **No** — cheapest to build, but nothing needs it |
| 4 | Close checklist (`close`, FloQast/Numeric-shaped) | ✅ FTL §4 | ❌ | ❌ | **No** |
| 5 | Anything CRM / payroll / tax / BI / procurement | ❌ | ❌ | ❌ | **No** — and the curated list's zero CRM entries corroborate |

**Recommendation: ship zero new servers on the strength of this research alone.** The
correct next move is not a server but three cheap, zero-new-server upgrades that this
research *does* justify:

1. **Densify `sheets`** — already named as the biggest honesty gap (`docs/GAP-ANALYSIS.md:39-58`)
   and the curated list confirms there is no spreadsheet MCP anywhere in the ecosystem to
   copy, which makes our Graph-shaped mock the differentiator rather than a liability.
2. **Import the verified friction mechanics from §3.2 into existing servers** — scope-gated
   tool availability (Ramp `__init__.py:40-54,72-73,77-82`, incl. the silently-skipped
   unrecognized scope and the composite three-scope gate), **hard page caps that abort the
   call and return nothing** (Ramp `client.py:81-82` — note this is a *loud* failure with a
   remediation hint, so the difficulty is recovery-and-refilter, not undetected truncation),
   allowed-field whitelists that reject a plausible filter (QBO), 10-row pages that require an
   explicit next-page call (Xero), `offset`/`max_chars` document chunking (EDGAR),
   minor-unit integer amounts (Ramp). Each is a real, cited behavior and a difficulty lever
   that costs no new server. **A *silent*-truncation primitive is not available for import
   from this cluster** — nothing here does it; if we want one it must be sourced elsewhere or
   built as an acknowledged invention rather than described as copied from Ramp.
   The `ap-overdue` pagination-truncation failure already observed in the flake scan
   (`PLAN.md:112-114`) is exactly this class of difficulty, and it's currently under-exploited.
3. **Add a `data_load_*` → `execute_query` (archetype C) motion** to `erp` or a small
   analysis surface, because it's the one archetype the world doesn't exercise, it's the
   *official Ramp design*, and it produces a distinct failure mode (sequencing) the ladder
   can't currently test.

If a bank/treasury server is later authorized, the schema is already fully specified by the
cloned artifacts: 13-state payment order machine (`mt_openapi_spec_v1.yaml:6920-6938`),
cursor pagination with `X-After-Cursor`/`X-Per-Page` (`:22-57`), and the object set
`internal_accounts` / `external_accounts` / `virtual_accounts` / `transactions` /
`expected_payments` / `payment_orders` / `returns` / `balance_reports` / `ledgers` /
`ledger_transactions` / `ledger_entries` (104 paths in the same file).

---

## 8. Chaos patterns extractable from this cluster

| Pattern | Real instance | Evidence |
|---|---|---|
| **Docs lie about the tool roster** — README documents 12 load tools, code ships 14 | Ramp | `ramp_mcp/README.md:29-42` vs `ramp_mcp/src/ramp_mcp/tools.py:158,182` |
| **Docs lie about the tool count** — badge says 145, repo ships 142 tool files (and our own `docs/GAP-ANALYSIS.md:97` records 144 from a third reading) | QBO | `quickbooks-online-mcp-server/README.md:8` vs `src/tools/` |
| **Docs lie about the tool count (again)** — file header says 55, the array holds 65 | Modern Treasury | `modern-treasury-mcp-http/src/tools.ts:7` ("55 tools covering: Payments, Counterparties, Accounts, / Transactions, Reconciliation, Ledgers, Invoices, FX") vs 65 `name:` entries at `:27-778` |
| **Tool exists but is invisible without the right scope**, and a *misspelled* scope removes it with no error at all | Ramp scope gating | `ramp_mcp/src/ramp_mcp/__init__.py:72-73` (silent `continue`), `:77-82` (composite gate); docs at `README.md:29-42,64` |
| **The same vendor ships two different tool surfaces** — an agent tuned to one is lost on the other | Stripe: hosted = 4 meta-tools; local `@stripe/mcp` = 23 named tools | `stripe-agent-toolkit/tools/modelcontextprotocol/manifest.json:32-55` vs docs.stripe.com/mcp (**tier 2**) |
| **Tool roster keyed to credential permissions, not configuration** — the `--tools` flag was removed; what you can call depends on the Restricted API Key | Stripe local MCP | `stripe-agent-toolkit/tools/modelcontextprotocol/src/cli.ts:17-24`, `README.md:23` |
| **Same server, different scope requirements by connection vintage**, with silent fallback | Xero SCOPES_V1 vs V2 (cutover 2026-04-29) | `xero-mcp-server/README.md:54-59` |
| **All-or-nothing page cap** — at page 101 the call throws and returns *zero* rows rather than a partial set; the agent must narrow its filter and start over. (Not silent truncation — this note previously mis-described it as such; no silent-truncation instance exists anywhere in this cluster) | Ramp `CLIENT_MAX_PAGES=100` | `ramp_mcp/src/ramp_mcp/client.py:81-82`; constant at `constants.py:1` |
| **Minor-unit amounts** — off-by-100 answers that look plausible | Ramp | `ramp_mcp/src/ramp_mcp/constants.py:2-5` |
| **Enum with holes** — id 22 doesn't exist; category lookups fail on a "valid-looking" id | Ramp `SK_CATEGORIES` | `ramp_mcp/src/ramp_mcp/constants.py:6-50` |
| **Load-before-query sequencing trap** — querying an unprocessed table errors | Ramp memory DB | `ramp_mcp/src/ramp_mcp/memory_db.py:25-45` |
| **Whitelisted filter fields** — a natural filter (`Balance` ok, `PrivateNote` not) is rejected | QBO invoice search | `quickbooks-online-mcp-server/src/tools/search-invoices.tool.ts:8-22` |
| **Write kill switches** — the same server presents different rosters per deployment | QBO `DISABLE_WRITE/UPDATE/DELETE` | `quickbooks-online-mcp-server/README.md:71-73,105` |
| **Environment defaults to demo** — the agent reads sandbox data believing it's production | Ramp `RAMP_ENV=demo` | `ramp_mcp/README.md:5` |
| **Whitelisted-verb meta-API** — the operation the agent wants isn't on the published list, though the API "supports" it | Stripe `stripe_api_write` | **tier 2** — fetched docs.stripe.com/mcp; `stripe_api_write` has no local attestation |
| **Payment stuck mid-state** — `needs_approval` / `held` / `stopped` payments that neither cleared nor failed | Modern Treasury payment_order status | `mt_openapi_spec_v1.yaml:6920-6938` |
| **Document chunking** — the answer sits past `max_chars` and the agent never pages | EDGAR `get_filing_content` | `sec-edgar-mcp/sec_edgar_mcp/server.py:116` |
| **Curated-index rot** — an "awesome" list with no verification: 2 duplicate rows, no tool counts, no last-checked dates; an agent that trusts it about tool availability is wrong | awesome-finance-mcp | `README.md:51` vs `:67`; `:148` vs `:174`; `AGENTS.md:9` |

---

## 9. Open questions

1. Exact tool names/args for **Qonto** and **Norman Finance** — both are remote-hosted
   (`mcp.qonto.com`, `mcp.norman.finance/mcp`) and publish only categories/skills. Would
   need a live connection or a client that dumps `tools/list`.
   (https://github.com/qonto/qonto-mcp-server · https://github.com/norman-finance/norman-mcp-server)
2. **LunchMoney** and **OpenBB** MCP tool surfaces — not fetched this pass
   (https://github.com/akutishevsky/lunchmoney-mcp · https://github.com/OpenBB-finance/OpenBB).
3. **FMP's 5 dynamic meta-tools** — names not in the README; they're in the repo's
   `API_REFERENCE.md`. Worth fetching: it's the cleanest published archetype-D/A hybrid.
4. **Alpha Vantage rate limits** — the MCP README doesn't state them; the free tier's
   documented API limits (5 req/min class) would be a great friction template if confirmed.
5. Whether the **Invoice Organizer** skill's extract→rename→sort pipeline maps onto a
   `docs` + `email` task (invoice-from-attachment) without a new server — likely yes, and it
   would be the only back-office-relevant *workflow* the curated list contributes.
6. QBO shipped tool count: 142 files vs 145 badge vs 144 in our own gap analysis — resolve
   by counting registered tool ids at runtime, not files, before we cite a number again.
   **This warning was earned the hard way**: the same file-glob error produced "Xero 50" in
   an earlier draft of this note (real answer 51 — see §3.1). Whatever resolves QBO should be
   applied to every count in §3 that came from a glob rather than an export array.
7. Whether a `bank` server should mirror **Modern Treasury's object model** (verified, clean,
   payment-ops native) or a **bank-portal UX** (dual-control release, cutoff times, BAI2
   statements) — the chaos value is in the portal, the schema value is in MT.
8. **Capture the tier-2 URLs to disk.** `research/external/` has no page-capture directory
   (only `repos/`, `articles/`, `financebenchmark-extracts/`), so FRED, FMP, Alpha Vantage,
   Monarch and the *hosted* Stripe surface cannot be re-derived by anyone reading this note.
   Stripe is the urgent one: it is archetype A's headline instance, a §3.2 friction row and a
   §8 chaos pattern, and only 6 of its 11 tool names have any local attestation
   (`stripe-agent-toolkit/`). Until captured, no tier-2 figure should be used as the sole
   support for a task design.
9. **Archetype D has no repo-verified instance** after the `xero_navigate` retraction (§4).
   Either find a real progressive-disclosure MCP server to clone, or drop D from the
   four-archetype ladder and admit the taxonomy is A/B/C plus a hypothesis. Related:
   `research/erp-domain.md:166` still asserts the `xero_navigate` / `xero_contacts_list`
   pattern and should be corrected there too, since it is the upstream source of the error.
10. **Does `research/external/repos/openbb/` answer §9.2?** OpenBB is checked out but was
    treated as UNVERIFIED in this pass; its tool surface was never read off the tree.

---

## Sources

**Cloned repos (paths relative to `research/external/repos/`)**
- `awesome-finance-mcp/README.md` (**231** lines, CC0), `AGENTS.md`, `CONTRIBUTING.md` —
  **no commit pin available**: the directory has no `.git`, so it carries no HEAD of its own
  (a hash read there is finance-world's). Provenance is fetch-date 2026-08-11 only.
- `ramp_mcp/` — `README.md`, `src/ramp_mcp/__init__.py` (scope→tool map), `tools.py`,
  `constants.py`, `memory_db.py`, `client.py` (the page-cap raise)
- `stripe-agent-toolkit/` — `tools/modelcontextprotocol/manifest.json` (23-tool local roster),
  `src/cli.ts` (RAK-gated tools), `README.md`; `providers/codex/plugin/test-cases.json`,
  `benchmarks/README.md`, `skills/README.md` (meta-API tool-name attestations)
- `quickbooks-online-mcp-server/` — `README.md`, `src/tools/` (142 `*.tool.ts`)
- `xero-mcp-server/` — `README.md`, `src/tools/tool-factory.ts`, `src/tools/{list,create,get,update,delete}/index.ts` (51 registered)
- `sec-edgar-mcp/` — `sec_edgar_mcp/server.py`, `sec_edgar_mcp/tools/`
- `financial-datasets-mcp-server/server.py`
- `modern-treasury-mcp-http/src/tools.ts`; `modern-treasury-openapi/openapi/mt_openapi_spec_v1.yaml`
- `mcp-grafana/` — density benchmark referenced by `docs/TOOLS.md`

**URLs fetched 2026-08-11 — tier 2, no local capture, not re-derivable (see §9.8)**
- https://docs.stripe.com/mcp (tool table, auth, whitelisted API methods, Treasury preview)
- https://github.com/stefanoamorelli/fred-mcp-server (3 tools + args)
- https://github.com/imbenrabi/Financial-Modeling-Prep-MCP-Server (250+ tools, 24 categories, 3 modes)
- https://github.com/alphavantage/alpha_vantage_mcp (fundamentals/forex/54 indicators)
- https://github.com/qonto/qonto-mcp-server (categories only; env vars)
- https://github.com/norman-finance/norman-mcp-server (11 skills; OAuth 2.1; hosted endpoint)
- https://github.com/carsol/monarch-mcp-server (6 tools + 4 resources)

**Prior finance-world research**
- `research/finance-tool-landscape.md` (vendor/market survey; the non-MCP half of the universe)
- `research/erp-domain.md` §4 (D365 MCP surfaces), §5 (adjacent systems)
- `research/domain-workflows.md` (personas, chaos patterns)
- `docs/TOOL-CENSUS.md` (the three-part rule + exclusion list), `docs/GAP-ANALYSIS.md`,
  `docs/TOOLS.md`, `mcp/mcp-servers.json`, `PLAN.md`
