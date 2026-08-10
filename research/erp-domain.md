# ERP Domain Research for finance-world

Research date: 2026-08-10. Target: mock a corporate-finance AP/AR environment modeled on **Microsoft Dynamics 365 Finance** (F&O apps, demo company **USMF**), exposed to an agent via MCP tools, with realistic "data chaos" from adjacent systems.

Items marked **UNVERIFIED** could not be confirmed against a primary source during this research pass. Everything else traces to a URL in [Sources](#sources).

---

## 1. Dynamics 365 Finance AP/AR domain model

### 1.1 Core concepts

D365 Finance (lineage: Dynamics AX) keeps master data, open-transaction ledgers, and settlement as separate layers. The pattern is symmetric for AR (Cust\*) and AP (Vend\*):

| Concept | AR artifact | AP artifact | Notes |
|---|---|---|---|
| Master record | `CustTable` | `VendTable` | Keyed by `AccountNum` per company (`dataAreaId`); name lives in the Global Address Book (`DirPartyTable`, party number ≠ account number) |
| Posted subledger transactions | `CustTrans` | `VendTrans` | One row per invoice, payment, credit note, fee, etc. (`TransType`) |
| Open (unsettled) remainder | `CustTransOpen` | `VendTransOpen` | Row exists only while (part of) a transaction is unsettled; carries the **DueDate** used for aging. Verified: CustTrans = posted transactions, CustTransOpen = unsettled state; `VendTransOpen` confirmed in Microsoft FastTrack SQL assets |
| Settlement history | `CustSettlement` | `VendSettlement` | Links invoice↔payment pairs with settled amount + cash discount taken; created by `CustTrans::settleTransaction` / settlement service (X++ `settleTransact` API documented by Microsoft) |
| Invoice journal (posted invoice headers) | `CustInvoiceJour` (+ `CustInvoiceTrans` lines); free text invoices post here too | `VendInvoiceJour` (+ `VendInvoiceTrans`) | **UNVERIFIED at field level** (well-known AX/D365 names; not re-verified against a primary table reference this pass) |
| Payment/GL journals | `LedgerJournalTable` + `LedgerJournalTrans` | same | Customer/vendor payment journals are ledger journals with account type Customer/Vendor |
| Terms of payment | `PaymTerm` (shared) | shared | Confirmed present in Microsoft docs; drives **due date** calculation (e.g., Net + N days) |
| Cash discount codes | `CashDisc` (shared; form name `CashDisc` confirmed in docs metadata) | shared | Drives **cash discount date**; independent of terms of payment |
| Collection letters | `CustCollectionLetterJour` (+ lines/notes; form `CustCollectionLetterNote`) | n/a | Confirmed referenced in Microsoft docs |
| Aging | Aging period definitions + customer **aging snapshot** (header + detail per period) | AP aging report exists but collections tooling is AR-side | |
| Credit | Credit limit + credit hold/blocking rules on customer; credit management module | AP side: vendor holds | |
| Method of payment | Customer/vendor methods of payment (`CustPaymModeTable` / `VendPaymModeTable` — **UNVERIFIED table names**, feature verified) | | Period options confirmed: Invoice / Date / Total (one payment per invoice, per due date, or one total) |

### 1.2 Fields that matter for balances, aging, due dates

Verified semantics (Microsoft Learn + Microsoft settlement docs + community X++ settlement posts):

- **`CustTrans`/`VendTrans`** (posted): `AccountNum`, `TransDate`, `Invoice` (invoice number), `Voucher`, `TransType` (invoice/payment/credit note/fee/interest), `CurrencyCode`, `AmountCur` (transaction currency), `AmountMST` (accounting currency), `SettleAmountCur` (cumulative settled), `Closed` (date fully settled), `CashDiscCode`, `DueDate`, `LastSettleVoucher`/`LastSettleDate` (**field list is representative; exact casing from AX lineage — UNVERIFIED at reference level**).
- **`CustTransOpen`/`VendTransOpen`** (open remainder): `RefRecId` → CustTrans, `AccountNum`, `TransDate`, **`DueDate`** (aging + collection letters key off this; a Dynamics User Group thread confirms `DueDate` lives here for open transactions), `AmountCur` (remaining open amount).
- **Balance** = Σ open `AmountCur` per account; **aged balance** = the same bucketed by `DueDate` (or `TransDate`, configurable "aged by" in aging setup).
- **`CustSettlement`**: links `TransRecId` (invoice) and `OffsetRecId` (payment), settled amount, cash-discount amount taken, settlement date. Partial settlements leave a reduced `CustTransOpen` row.
- **Due date** comes from Terms of payment (`PaymTermId` on customer/vendor, overridable per invoice). **Cash discount date** comes from the cash discount code (`Days` field added to invoice date when "Net" option selected).
- **Cash discount setup** (verified, docs page `cash-discounts`): code id, `Days`, `Discount %`, **`Next discount code`** (chains a series, e.g. docs example codes **`5D10%` → `10D5%` → `14D2%`**), main account for customer discounts / vendor discounts. Terms of payment define the due date only, *not* the discount date. Classic US "2%/10 Net 30" is modeled as payment term Net30 + cash discount code with Days=10, 2%.
- **Credit** (verified): customer-level **Credit limit** plus **`Mandatory credit limit`** toggle; credit-limit check types **None / Balance / Balance + packing slip or product receipt / Balance + All**; customer credit groups with group limits; blocking rules can put orders on credit hold. (`CreditMax` field name confirmed present in Microsoft FastTrack SQL assets.)
- **Collection letters** (verified, docs example): sequence of up to 5 codes — demo sequence **"Collection letter 1" → "Collection letter 2" → "Collection"** — each with `Description`, `Fee in currency`, `Minimum over`, `Days` (grace), `Main account` for the fee; tracked per transaction but processed per customer (AR parameter "Create collection letter per: Customer"); flow = Create collection letters → Review and process → Post. Collection letter code advances per transaction; header vs line codes can diverge ("Ignore payments and credit memos when calculating collection letter code").
- **Aging** (verified): **Aging period definitions** define the bucket columns on Aged balances / Collections pages (per-period unit: Day/Week/Month/Quarter/Year/Unlimited). The **customer aging snapshot** = calculated aged balances at a point in time (snapshot header + one detail row per aging period), refreshed by a batch process; definition resolved via customer pool → AR-parameters default → first definition.
- **Method of payment** (verified): per-customer/vendor code; `Period` = Invoice / Date / Total (how payment proposals group invoices); required `Payment status` before posting; check vs electronic with file formats.

### 1.3 Transaction lifecycle (what the mock must reproduce)

1. Invoice posted → `CustInvoiceJour` header + `CustTrans` (type Invoice) + `CustTransOpen` (full amount, DueDate = invoice date + terms).
2. Payment journal posted → `CustTrans` (type Payment, negative) + its own `CustTransOpen`.
3. Settlement (auto or via "Settle open transactions") → `CustSettlement` row(s); open rows reduced/deleted; fully settled transactions get `Closed` date; cash discount posted if paid within discount date.
4. Aging snapshot batch buckets remaining `CustTransOpen` by DueDate.
5. Overdue transactions accumulate collection-letter codes level by level (fees post as new transactions).

---

## 2. Proposed minimal-but-realistic mock schema for finance-world

Our design, shaped to mirror the real tables above (SQLite/Postgres-friendly names; keep D365-ish PascalCase in the MCP layer if we want verisimilitude):

**Company / reference**
- `legal_entities` (data_area_id PK e.g. 'USMF', name e.g. 'Contoso Entertainment System USA', currency)
- `payment_terms` (paym_term_id PK e.g. 'Net30', description, method 'Net'|'COD'|'CurrentMonth', num_days)
- `cash_discounts` (cash_disc_code PK e.g. '2%10NET30' or D365-style '10D2%', days, percent, next_discount_code FK nullable, customer_discount_account, vendor_discount_account)
- `methods_of_payment` (paym_mode PK e.g. 'CHECK','EFT', description, period 'Invoice'|'Date'|'Total', payment_type)
- `aging_period_definitions` (id, name) + `aging_periods` (definition_id, seq, description e.g. '31-60', unit, length) — default buckets: Current, 1–30, 31–60, 61–90, 90+
- `customer_groups` / `vendor_groups` (group_id, description, default paym_term_id)

**Masters**
- `customers` (account_num PK per data_area_id, party_id, name, customer_group, currency, paym_term_id, cash_disc_code, paym_mode, credit_limit, mandatory_credit_limit bool, credit_hold bool, collection_contact, primary_contact_email, address fields)
- `vendors` (account_num, party_id, name, vendor_group, currency, paym_term_id, cash_disc_code, paym_mode, on_hold bool, tax_1099 bool, remit_to fields)
- Optional `parties` (party_id, name) to reproduce the party-number-vs-account-number trap (same party can be customer US-003 and vendor US-103).

**Subledger (the heart of the eval)**
- `cust_trans` (rec_id PK, data_area_id, account_num FK, trans_type 'Invoice'|'Payment'|'CreditNote'|'Fee'|'Interest', trans_date, due_date, invoice_id, voucher, currency, amount_cur signed, amount_mst, settled_cur, closed_date nullable, cash_disc_code, cash_disc_date, last_settle_date)
- `cust_trans_open` (rec_id, ref_rec_id FK→cust_trans, due_date, amount_cur_open) — *derivable, but keeping it as a table reproduces the real system's shape and lets tasks probe the difference between posted and open*
- `cust_settlement` (id, trans_rec_id FK invoice, offset_rec_id FK payment, settle_date, settled_amount, cash_disc_taken)
- `vend_trans`, `vend_trans_open`, `vend_settlement` — mirror images
- `cust_invoice_jour` (invoice_id, account_num, invoice_date, due_date, invoice_amount, currency, sales_id nullable, source 'FTI'|'SO') and `vend_invoice_jour` (invoice_id/internal voucher, vendor account, invoice_date, due_date, amount, purch_id, approval_status)

**Collections / credit**
- `collection_letters` (letter_id, account_num, letter_code 'Collection letter 1'|'Collection letter 2'|'Collection letter 3'|'Collection letter 4'|'Collection', letter_date, fee_amount, status 'Created'|'Posted', printed bool)
- `aging_snapshots` (snapshot_id, as_of_date, account_num, balance) + `aging_snapshot_details` (snapshot_id, period_seq, amount) — snapshot can be deliberately **stale** vs live open-trans data (real systems do this: snapshot is batch-refreshed)
- `collections_cases` / `activities` (optional stretch)

**Relationships:** customers 1—N cust_trans 1—0..1 cust_trans_open; cust_trans 1—N cust_settlement (as invoice or as payment); customers N—1 payment_terms/cash_discounts/methods_of_payment/customer_groups; everything scoped by data_area_id (USMF + at least one sibling like USRT/DEMF to enable cross-company traps).

**Design notes**
- Signed amounts: invoices positive, payments/credit notes negative (matches CustTrans convention).
- Keep `settled_cur` + `closed_date` consistent with settlement rows — good hidden-consistency check for graders.
- Aged-balance answers must derive from open rows by due_date; keeping a slightly stale snapshot table creates the classic "which number is right?" task.

---

## 3. Official demo data (verified)

**USMF exists**: the F&O demo data set's legal-entity table (Microsoft Learn "Demo data overview") includes **USMF = Contoso Entertainment System USA**, plus DEMF (Germany), USRT (Contoso Retail USA), USSI (Contoso Consulting USA), USP2 (Contoso Orange Juice), GLCO Contoso Group, etc. Demo data spans 16 countries / 40 languages. The demo-data doc also confirms demo users (ErinH, INGA, JulieT-style personas) and collections analytics (`CustCollectionsBIMeasurements` aggregate measure).

### Demo customers (USMF unless noted)

| Account | Name | Source |
|---|---|---|
| US-001 | Contoso Retail San Diego | write-off task guide ("select US-001 (Contoso Retail San Diego)") |
| US-003 | Forest Wholesales | lookups doc ('"Forest Wholesales" instead of "US-003"') |
| US-004 | Cave Wholesales | write-off task guide + revenue recognition doc |
| US-007 | Desert Wholesales | MicrosoftLearning MB-330 lab (sales order for Desert Wholesales, account US-007) |
| US-008 | Sparrow Retail | configure-email doc + Office integration tutorial |
| (number **UNVERIFIED**) | Birch Company | write-off task guide (row on Aged balances) — real demo customer, account number not shown in docs |
| US-002, US-005, US-006, US-009, US-010 | names **UNVERIFIED** | accounts appear in Microsoft docs (billing schedules US-001/US-002; credit-hold example releases US-009 by overdue amount; rebate example US-009) |
| US-045 | (created during tutorial) | collection-letters example creates this customer — good precedent for "new customer" tasks |
| 4000 | Northwind Traders | centralized-payments example (legal entities Fabrikam / Fabrikam East / Fabrikam West) — docs example data, not USMF |
| 3004 / "100" | **Fourth Coffee** | centralized-payments **Accounts payable** example: Fourth Coffee is the **vendor** (account 3004 in Fabrikam, 100 in Fabrikam East). Not confirmed as a USMF customer. |

### Demo vendors

| Account | Name | Source |
|---|---|---|
| 1001 | Acme Office Supplies | Copilot application-context doc (PartyNumber 1001, Name "Acme Office Supplies") |
| US-101 | Fabrikam Electronics | MicrosoftLearning MB-330 lab ("US-101 (Fabrikam Electronics)"); also appears across purchasing/forecast/ER docs |
| US-102 | name **UNVERIFIED** | appears in master-planning docs (planned POs, site 1 / warehouse 11) |
| US-104 | name **UNVERIFIED** | demo-data doc: vendor-collaboration vendor, contact user ErinH; PO/RFQ docs |
| 3004 | Fourth Coffee | centralized-payments AP example (Fabrikam companies) |
| US-103 | no hits in docs repo | — |

Naming texture worth imitating: "Contoso Retail <City>" chains, nature-themed wholesalers (Forest/Cave/Desert/Sparrow/Birch), classic Microsoft fictional brands (Fabrikam, Northwind Traders, Fourth Coffee, Adventure Works, Alpine Ski House) as counterparties, `US-0xx` customers / `US-1xx` vendors / legacy 4-digit accounts (1001, 3004, 4000) mixed together — that mix itself is realistic chaos.

---

## 4. API surface & MCP inventory

### 4.1 OData data entities (the REST API)

- Endpoint: `https://<environment>.operations.dynamics.com/data/<EntityCollection>`; `$metadata` lists ~2,000+ entities (>1,500 public). Auth = **Microsoft Entra ID (Azure AD) OAuth 2.0** — authorization-code or client-credentials (secret/cert); token audience = environment URL.
- Entities are company-scoped: filter `?$filter=dataAreaId eq 'usmf'` and use `?cross-company=true` to query across companies (default returns only the user's default company).
- Verified entity collection names (used in Microsoft's own docs/sample code and community code): **`CustomersV3`**, **`VendorsV2`**, **`PaymentTerms`** (52 public-code usages of `/data/PaymentTerms`). Example from Microsoft OData docs: `GET /data/CustomersV3?$filter=PersonGender eq Microsoft.Dynamics.DataEntities.Gender'Unknown'`.
- Entity labels confirmed via community-maintained full entity list (dynamics-tips.com): Customers/V2/V3, Vendors/V2, "Terms of payment", "Cash discount" (collection name **UNVERIFIED**; `/data/CashDiscounts` had zero code hits), "Customer payment method"/"Vendor payment method", "Customer free text invoice", "Vendor invoice header/line", "Customer payment journal header/line", "Vendor payment journal …", "Collection letter setup", **"Customer aged balances"**, "Customer collections history".
- Standard patterns: `$select/$filter/$top/$expand`, JSON batch, and the Data Management Framework (DMF) for bulk import/export packages.

### 4.2 Official Microsoft MCP servers (all announced 2025)

1. **Dynamics 365 ERP MCP server (dynamic)** — the flagship (public preview from ~Nov 2025; docs updated Jul 2026). Requires F&O ≥ 10.0.47 (or PQU-patched 10.0.45/46); enabled by default via Feature Management; Tier-2+/UDE environments only; client platforms must be registered on an **Allowed MCP clients** page (defaults include Microsoft Copilot Studio, VS Code, Microsoft Cowork, **Finance Agent**). Billing: 0.1 Copilot credits per tool call outside Copilot Studio. Tools (exact names):
   - Data tools: `data_find_entity_type`, `data_get_entity_metadata`, `data_create_entities`, `data_update_entities`, `data_delete_entities`, `data_find_entities` (OData), `data_find_entities_sql` (replaces the OData find in 10.0.48 — **SQL over entities**!)
   - Form tools (server-side "form as API", not screen scraping): `form_open_menu_item`, `form_find_menu_item`, `form_find_controls`, `form_click_control`, `form_set_control_values`, `form_open_lookup`, `form_filter_form`, `form_filter_grid`, `form_select_grid_row`, `form_sort_grid_column`, `form_open_or_close_tab`, `form_save_form`, `form_close_form`
   - Action tools: `api_find_actions`, `api_invoke_action` (X++ classes implementing `ICustomAPI`)
   - Context is security-trimmed per role; responses return the application view model. Limitations: en-US metadata, ISO dates, "matches"-only grid filters, no attachment controls, admin forms excluded.
2. **Static Dynamics 365 ERP MCP server** — Build 2025 original; 13 fixed tools on the Dataverse connector framework (examples seen in the wild: `findapprovedvendors`; others cover on-hand inventory, requisition→PO conversion, vendor-invoice matching; full 13-name list **UNVERIFIED** — not published in any page found). **Retires Oct 1, 2026.**
3. **Dynamics 365 ERP Analytics MCP server (preview, Dec 2025)** — natural language over Business Performance Analytics star schemas (Record-to-Report, Procure-to-Pay, Order-to-Cash; transforms run twice daily). Exactly two tools: `get-bpa-dataset-schema`, `execute-dax-query` (row-level security enforced). Example prompts in docs: "Calculate average days sales outstanding", "top 10 customers by revenue".
4. Related: **Dataverse MCP server** (Ignite 2025 advances), Dynamics 365 Sales MCP, Business Central MCP (separate product line).

### 4.3 Community MCP servers / clients for D365 F&O

- **mafzaal/d365fo-client** — Python client library **and MCP server** for D365 F&O: OData CRUD, metadata operations, label lookup (closest open-source analog to what finance-world will mock).
- d365devgit/d365fo-mcp-server-v1 (fork/variant of the above); leon4s4-dynamics-mcp (LobeHub listing).

### 4.4 Design takeaway for our mock MCP

The real 2026-era surface is **metadata-discovery + query** (find entity → get schema → query via OData or SQL → act via forms/actions), not a bag of bespoke `get_invoice` endpoints. A faithful mock offers: `find_entity`, `get_entity_schema`, `query` (SQL or OData-ish), plus a few "action" tools (settle transaction, post collection letters, release credit hold) — and can also ship a "static" flavor for easier tasks.

---

## 5. Competitor / adjacent systems (for data-chaos realism)

| System | API style | Key AP/AR objects | MCP status |
|---|---|---|---|
| **SAP S/4HANA** | OData V2/V4 APIs cataloged on **SAP Business Accelerator Hub** (api.sap.com); SOAP for some postings; classic tables behind CDS views (universal journal ACDOCA — **UNVERIFIED here**, widely documented) | `API_BUSINESS_PARTNER` (customers+suppliers as business partners), `API_SUPPLIERINVOICE_PROCESS_SRV/A_SupplierInvoice`, Journal Entry Post/Reverse (SOAP + OData collection per SAP "APIs for Journal Entries" blog), GL/AR/AP open-item reads | No single official ERP MCP; SAP publishes official **developer** MCP servers/AI skills (CAP MCP etc., community-tracked lists); rich community ABAP ADT MCP servers (abap-ai/mcp SDK, mario-andreschak/mcp-abap-adt) |
| **NetSuite** | SuiteTalk REST + **SuiteQL**: `POST /services/rest/query/v1/suiteql` with `{"q": "SELECT id, tranid, trandate, status FROM transaction WHERE recordtype='salesorder' ..."}`; single `transaction` table + `transactionLine`, `entity`-joined; OAuth 2.0 / TBA | customer, vendor, invoice, vendorbill, customerpayment, vendorpayment — all rows in `transaction` discriminated by `recordtype` (a great chaos pattern: one polymorphic table) | **Official Oracle NetSuite MCP** (2025): "MCP Standard Tools" SuiteApp — records, saved searches, reports, SuiteQL tools; integrated with NetSuite security |
| **QuickBooks Online** | REST + SQL-ish query endpoint (`SELECT * FROM Invoice WHERE ...` via `/query`), `minorversion` pinning, OAuth 2.0 (Intuit platform) | Customer, Vendor, Invoice, Bill, Payment, BillPayment, CreditMemo, Account (~30 entities) | **Official intuit/quickbooks-online-mcp-server** (Oct 2025, Apache-2.0, local): 144 tools over 29 entity types + 11 financial reports |
| **Xero** | Accounting API (REST, JSON), OAuth 2.0 + `xero-tenant-id` header per organisation | Contacts (customer & supplier in one object), Invoices with `Type` **ACCREC** (AR) / **ACCPAY** (AP bills), Payments, CreditNotes, Accounts, Reports (Aged Receivables/Payables) | **Official XeroAPI/xero-mcp-server**: domain-navigation pattern (`xero_navigate` into contacts/invoices/payments/accounts/reports domains, then domain tools like `xero_contacts_list`) |
| **Sage Intacct** | Legacy XML gateway (`readByQuery`, functions per object) + **REST API GA 2025 R1** (developer.sage.com; REST↔XML object mapping table published; webhooks + bulk GA in 2025) | AP: `apbill`; AR: `arinvoice`; vendors, customers; dimensions (department/location) pervasive | No official MCP found (**UNVERIFIED**/absent) |
| **Bill.com** | REST v3 (`developer.bill.com`), auth = `POST /v3/login` → `sessionId` + `devKey` headers; payments need MFA-trusted session; sandbox available | vendors, bills, payments (auto-creates bill if paying without one), invoices (AR side), BILL Network vendor connections | No official MCP found (**UNVERIFIED**) |
| **Ramp** | REST Developer API, OAuth 2.0 client-credentials with scopes | transactions (card), bills, reimbursements, vendors, statements, accounting integrations | **Official** hosted MCP `mcp.ramp.com/mcp` + open-source `ramp-public/ramp_mcp`: ETL pattern — `load_transactions`/`load_bills`/... into in-memory SQLite, then agent runs SQL |
| **HighRadius** | No public general-purpose dev API; integrates to 50+ ERPs (incl. D365 — AppSource connector) via prebuilt connectors, real-time APIs, and **file formats BAI2 / EDI820 / EDI823 / CSV / JSON** | Autonomous Receivables suite: collections worklists, cash application (payment↔invoice matching), credit risk, deductions | None found |
| **Excel / Google Sheets** (the shadow system) | Microsoft Graph workbook API / Google Sheets API v4 (`spreadsheets.values.get`) — or, realistically, a file share | "AR Aging FINAL v3 (2).xlsx": manually keyed aged balances, notes columns, stale as-of dates, one-off credit memos not in ERP | n/a — but this is the highest-realism chaos source: numbers that *almost* match the ERP |

**Chaos patterns to steal:** same counterparty under different IDs per system (D365 `US-003` = QBO `Customer 87` = Netsuite `entity 123`); Xero merging customers+suppliers into Contacts while D365 splits them; NetSuite's polymorphic `transaction` table vs D365's Cust/Vend split; Bill.com auto-generating bills on payment; snapshot/batch staleness (D365 aging snapshot, BPA 12-hour transforms, HighRadius file drops); spreadsheet totals that disagree by one credit memo.

---

## 6. GitHub examples of real API/tool-call sequences worth imitating

- **microsoft/Dynamics-AX-Integration** — canonical OData samples (`ServiceSamples/ODataConsoleApplication`): AAD auth → generate typed proxy from `$metadata` → query/CRUD → JSON batch with changesets (DeepWiki walkthrough of the repo documents the batch semantics). Sequence to imitate: *authenticate → read metadata → filtered entity query → batched writes*.
- **mafzaal/d365fo-client** — Python: OData CRUD + metadata + label APIs + MCP server wrapping them; closest architectural template for finance-world's mock server.
- **d365fo.tools** (community PowerShell, in awesome-msdyn365fo list) — ops-side automation patterns.
- **microsoft/Dynamics-365-FastTrack-Implementation-Assets** — Microsoft-authored SQL over exported F&O tables (where we confirmed `VendTransOpen`, `CreditMax`) — good reference for realistic column names in analytics SQL.
- **ramp-public/ramp_mcp** — the *load-then-SQL* agent pattern: `load_*` tools ETL API pages into ephemeral SQLite; agent then answers with SQL. Strong candidate pattern for finance-world tasks that need aggregation.
- **intuit/quickbooks-online-mcp-server** — per-entity CRUD/search tool generation at scale (144 tools / 29 entities / 11 reports) — the "many small typed tools" end of the design spectrum.
- **XeroAPI/xero-mcp-server** — domain-navigation tool design (navigate → domain toolset) — the "progressive disclosure" end of the spectrum.
- **osodevops/quickbooks-cli** — OAuth2 PKCE + 36 entities + SQLite caching CLI; realistic scripted call sequences.
- NetSuite SuiteQL request/response examples: Tim Dietrich's "Querying Transactions With SuiteQL" and Oracle's SuiteQL-through-REST docs give copy-pasteable POST bodies.

---

## 7. Implications for the finance-world mock design

1. **Model USMF faithfully but small.** One `data_area_id='USMF'` (Contoso Entertainment System USA) plus a sibling (USRT or DEMF) for cross-company traps. Use verified demo names (US-001 Contoso Retail San Diego, US-003 Forest Wholesales, US-004 Cave Wholesales, US-007 Desert Wholesales, US-008 Sparrow Retail, Birch Company; vendors 1001 Acme Office Supplies, US-101 Fabrikam Electronics) and invent the rest in the same style (US-0xx customers, US-1xx vendors, Fabrikam/Northwind/Fourth Coffee counterparties).
2. **The posted-vs-open split is the domain's soul.** Implement `cust_trans` + `cust_trans_open` + `cust_settlement` (and Vend mirrors). Most interesting AP/AR questions — balance, aging, "which invoices does this payment cover", "why is the invoice still showing open" — live in that triangle. Partial settlements are mandatory content.
3. **Due date ≠ discount date.** Payment terms drive due date; cash discount codes (with `Next discount code` chains like 5D10%→10D5%→14D2%) drive discount capture. Tasks: "can we still take the discount if we pay Friday?"
4. **Collections is a state machine.** Collection letter codes (Collection letter 1..4, Collection) with grace days, fees, minimums; per-customer processing; posting fees creates new transactions. Credit: credit_limit + mandatory flag + Balance/Balance+All check types + credit hold.
5. **Aging has two truths**: live computation over open transactions vs a batch **snapshot** (bucketed per aging period definition). Ship both, slightly divergent, to reward agents that check freshness.
6. **MCP tool surface — mirror the real 2026 shape**: discovery-first (`find_entity`, `get_entity_metadata`, `query_entities` with OData-ish filters and/or SQL — note Microsoft itself moved to `data_find_entities_sql`) plus a handful of action tools (`settle_transactions`, `create_collection_letters`, `post_collection_letters`, `release_credit_hold`). Entity names should echo real ones: `CustomersV3`, `VendorsV2`, `PaymentTerms`, `CustomerAgedBalances`.
7. **Chaos layer**: (a) a QBO-or-Xero-shaped second system holding a subset of the same counterparties under different IDs (Xero-style unified Contacts is maximal confusion); (b) a Bill.com/Ramp-shaped AP feed with bills the ERP hasn't ingested; (c) the shadow spreadsheet with a stale, hand-edited aging that disagrees by a known delta; (d) a HighRadius-style collections export (CSV/EDI820-ish) referencing ERP invoice numbers with formatting drift (INV-001042 vs 1042).
8. **Auth realism (cheap)**: require a bearer-ish token or company context header; scope tool results by role the way the real MCP security-trims (a "collections agent" role that can't see vendor data makes good negative tests).
9. **Grading hooks**: keep internal invariants (open = posted − settled; snapshot = f(open, as_of)) so task answers are derivable and checkable.

### Open questions

- Exact names for US-002/005/006/009/010 customers and US-102/US-104 vendors (would need a live demo environment or the demo-data packages from LCS/`generate-demo-data-packages`).
- Birch Company's account number; whether Fourth Coffee also exists inside USMF proper (it's confirmed only in the Fabrikam centralized-payments doc examples).
- The full 13-tool list of the static ERP MCP server (retiring Oct 2026) was never published verbatim in accessible docs.
- Public collection names for a few entities ("Cash discount", "Customer aged balances") — verify against a live `$metadata` when we stand one up, or accept our mock's names as canonical.
- Whether to expose a form-tools tier (probably out of scope for v1; data + action tools cover AP/AR Q&A).

---

## Sources

**Microsoft Learn — D365 Finance domain**
- Demo data overview (legal entities incl. USMF): https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/get-started/demo-data
- Settle transactions by using CustTrans settleTransaction: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/financial/settletransact-obsolete
- Cash discounts (5D10%/10D5%/14D2% example, account defaulting): https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/cash-discounts
- Process collection letters example (codes, fees, USMF/US-045): https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/process-collection-letters-example
- Create a collection letter sequence: https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/tasks/create-collection-letter-sequence
- Set up collections / aging snapshot / aging period definitions: https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/set-up-collections ; https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/tasks/set-up-accounts-receivable-aging-information ; https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/collections-credit-accounts-receivable
- Credit limits: https://learn.microsoft.com/en-us/dynamics365/supply-chain/sales-marketing/credit-limits-customers ; https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/credit-hold-faq
- Write-off task guide (US-001 Contoso Retail San Diego, Cave Wholesales US-004, Birch Company): https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/tasks/create-write-off-journal-customer
- Lookups doc (US-003 Forest Wholesales): https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/fin-ops/get-started/use-lookups-to-find-information
- Configure email / Office integration tutorial (US-008 Sparrow Retail): https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/organization-administration/configure-email ; https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/office-integration/office-integration-tutorial
- Centralized payments AR/AP (Northwind Traders 4000; Fourth Coffee 3004; Fabrikam entities): https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/centralized-payments-accounts-receivable ; https://learn.microsoft.com/en-us/dynamics365/finance/accounts-payable/centralized-payments-accounts-payable
- Copilot application context (vendor 1001 Acme Office Supplies): https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-application-context
- OData: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata ; Data entities overview: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities ; Demo data packages: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/generate-demo-data-packages
- CustTransOpen DueDate discussion: https://www.dynamicsuser.net/t/relation-between-dudate-of-custtransopen-table-and-documentdate-of-custtrans-table/62412 ; X++ settlement walkthrough: https://axvigneshvaran.wordpress.com/2022/12/11/settlement-and-undo-settlement-of-customer-transactions-using-x-in-dynamics-365-for-finance-and-operations/
- Methods of payment: https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/tasks/establish-customer-method-payment ; https://learn.microsoft.com/en-us/dynamicsax-2012/appuser-itpro/set-up-a-method-of-payment-for-checks

**MCP (Microsoft)**
- Use MCP for finance and operations apps (dynamic ERP MCP; full tool tables; allowed clients; licensing; static-server retirement): https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp
- ERP Analytics MCP overview (get-bpa-dataset-schema, execute-dax-query): https://learn.microsoft.com/en-us/dynamics365/finance/business-performance-analytics/erp-analytics-mcp-overview
- Dynamics 365 blog (Nov 11, 2025) MCP evolution: https://www.microsoft.com/en-us/dynamics-365/blog/it-professional/2025/11/11/dynamics-365-erp-model-context-protocol/
- Release plan (expanded MCP): https://learn.microsoft.com/en-us/dynamics365/release-plan/2025wave2/enterprise-resource-planning/finance-operations-crossapp-capabilities/connect-ai-agents-finance-operations-data-business-logic-expanded-model-context-protocol-server
- Ignite 2025 coverage: https://msdynamicsworld.com/story/ignite-2025-microsoft-advances-mcp-servers-dataverse-dynamics-365-fo ; setup walkthroughs: https://dynamicspedia.com/2025/11/how-to-set-up-the-new-dynamics-365-erp-mcp-server/ ; https://elearnd365.com/2025/08/22/understanding-mcp-server-and-using-mcp-server-with-dynamics-365-for-finance-and-operations/

**Demo-name verification (GitHub)**
- MicrosoftDocs/Dynamics-365-Unified-Operations-Public (code-search hits cited above): https://github.com/MicrosoftDocs/Dynamics-365-Unified-Operations-Public
- MicrosoftLearning MB-330 labs (US-007 Desert Wholesales; US-101 Fabrikam Electronics): https://github.com/MicrosoftLearning/MB-330-Microsoft-Dynamics-365-Supply-Chain-Management
- microsoft/Dynamics-365-FastTrack-Implementation-Assets (VendTransOpen, CreditMax in SQL): https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets

**Competitors / adjacent**
- SAP: https://community.sap.com/t5/technology-blog-posts-by-sap/apis-for-journal-entries-the-collection-updated-july-2025/ba-p/13565258 ; https://community.sap.com/t5/enterprise-resource-planning-q-a/s-4hana-on-premise-accounting-document-post-api/qaq-p/12431275 ; https://help.sap.com/docs/SAP_S4HANA_CLOUD/0f69f8fb28ac4bf48d2b57b9637e81fa/1e60f14bdc224c2c975c8fa8bcfd7f3f.html ; SAP MCP lists: https://github.com/marianfoo/sap-ai-mcp-servers ; https://likweitan.github.io/sap-mcp-servers-official/ ; https://github.com/abap-ai/mcp
- NetSuite SuiteQL: https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157909186990.html ; https://timdietrich.me/blog/netsuite-suiteql-querying-transactions/ ; MCP comparisons: https://www.houseblend.io/articles/netsuite-mcp-server-comparison ; https://plative.com/netsuite-ai-mcp-setup-and-troubleshooting-guide/
- QuickBooks Online: https://satvasolutions.com/blog/quickbooks-online-api-guide ; https://www.getknit.dev/blog/quickbooks-online-api-integration-guide-in-depth ; official MCP: https://github.com/intuit/quickbooks-online-mcp-server ; CLI: https://github.com/osodevops/quickbooks-cli
- Xero official MCP: https://github.com/XeroAPI/xero-mcp-server
- Sage Intacct REST GA: https://www.intacct.com/ia/docs/en_GB/releasenotes/2025/2025_Release_1/Platform_Services/2025-R1-platform-restapi-ga.htm ; https://developer.sage.com/intacct/docs/developer-portal/release-notes/2025-r2/ ; XML API: https://developer.intacct.com/api/
- Bill.com v3: https://developer.bill.com/reference/api-reference-overview ; https://developer.bill.com/docs/bill-v3-api-get-started ; https://developer.bill.com/docs/ap-vendors ; https://developer.bill.com/docs/ap-payments
- Ramp: https://github.com/ramp-public/ramp_mcp ; https://mcpservers.org/servers/ramp-public/ramp-mcp ; https://ramp.com/developer-tools
- HighRadius: https://www.highradius.com/product/cash-application-automation/ ; D365 connector: https://marketplace.microsoft.com/en-us/product/dynamics-365-for-operations/highradiuscorporation1667813573717.hrc-ar_automation_suite

**D365 integration code examples**
- https://github.com/microsoft/Dynamics-AX-Integration (ODataConsoleApplication) ; DeepWiki: https://deepwiki.com/microsoft/Dynamics-AX-Integration/2.2-odata-integration
- https://github.com/mafzaal/d365fo-client (Python client + MCP server)
- Entity list (community): https://dynamics-tips.com/dynamics-365-finance-and-operations-data-entity-list/
