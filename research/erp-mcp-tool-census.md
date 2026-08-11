# ERP MCP tool census — six real servers in the wild

Research date: 2026-08-11. Purpose: establish what an **agent-facing ERP tool surface actually looks like**
beyond the Microsoft D365 MCP already documented in `research/erp-domain.md` §4.2, so finance-world can
mock shapes it has evidence for and port tasks it can ground.

All claims below cite a path under `research/external/repos/` (paths are written relative to that
directory). Vendor prose that contradicts the shipped code is recorded in §11 with **the code winning**.
Anything not verifiable in the checked-out source is marked **UNVERIFIED**.

> License note: these repos are **fact sources, not code sources**. `erpnext` is GPL-v3
> (`erpnext/license.txt`), `opensuitemcp-netsuite` ships a Sustainable Use License
> (`opensuitemcp-netsuite/LICENSE`), `mcp-erp-multivendor` is Apache-2.0, the other three are MIT.
> finance-world copies *names, shapes and behaviors*, never source.

---

## 0. The six servers at a glance

| # | Server | Path | Lang / version | Tools (in code) | Access pattern | Write surface | Auth |
|---|---|---|---|---|---|---|---|
| 1 | ERPNext MCP (rakeshgangwar) | `erpnext-mcp-server/src/index.ts` | TS, v0.1.0 (`package.json`) | **11** (`src/index.ts:359-585` — the `tools: [` … `]` literal; 11 `name:` keys at `:361,369,383,413,436,463,482,500,524,546,568`, matched by 11 `case` arms at `:604-976`) | generic CRUD over DocTypes + method passthrough | full: create/update/submit/cancel/delete + arbitrary whitelisted method | API key/secret header `token <key>:<secret>` (`src/index.ts:59-60`) |
| 2 | ERPNext MCP Extended (Kai-Oesterling / SVAN) | `erpnext-mcp-server-extended/src/index.ts` | TS, v1.0.0 MIT | **19** (`src/index.ts:438-458`) | same + **schema-mutation** (DocType/field/workflow authoring) | full + creates DocTypes, Custom Fields, Property Setters, Workflows | API key/secret, **or** interactive `authenticate_erpnext` → `/api/method/login` (`src/index.ts:177-188`) |
| 3 | mcp-erp multivendor (zavora-ai) | `mcp-erp-multivendor/src/server.rs` | Rust, v1.0.1 (`mcp-server.toml`), Apache-2.0 | **79** (`src/server.rs`, `#[tool(...)]` count) | curated business verbs over a unified schema, 6 pluggable backends | lifecycle-gated (`draft → submit → post`), risk-classed in a manifest | per backend: OAuth2 token / JSON-RPC session / OAuth1a / Azure AD (`docs/backends.md`) |
| 4 | OpenSuiteMCP (unstackedapps) | `opensuitemcp-netsuite/lib/netsuite/mcp.ts` | TS/Next.js, v3.1.1 | **0 of its own** for ERP — it is a *client* proxying Oracle's hosted MCP (`lib/netsuite/mcp.ts:13`) | discovery-first ladder over Oracle's `ns_*` tools; SuiteQL last resort | inherits NetSuite's `ns_createRecord` / `ns_updateRecord`, gated by prompt policy | OAuth 2.0 + PKCE, Dynamic Client Registration (`lib/netsuite/oauth.ts`, `lib/netsuite/dcr.ts`) |
| 5 | CData SAP ERP MCP | `sap-erp-mcp-cdata/src/main/java/com/cdata/mcp/` | Java/Maven, MIT | **3** (`Program.java:93-97`, the `ITool[]` literal inside `registerTools` at `:92-102`) | pure SQL passthrough over a JDBC driver + metadata discovery | **read-only by convention, not by check** — the tool is named and described as `SELECT`-only (`tools/RunQueryTool.java:42-43`) but `run()` hands the string straight to `Statement.executeQuery(sql)` with no validation (`:71-75`); read-only-ness comes from the description, the README header and the JDBC driver | whatever the JDBC URL carries (`Config.java`, `JdbcUrl` property) |
| 6 | ECOUNT MCP (Gilbreth) | `mcp-server-ecount/src/tools/register.ts` | TS, v0.1.3 MIT | **23** (`register.ts`, `server.tool(` count) | curated business verbs, one per ECOUNT OpenAPI endpoint | create-only writes (no update/delete/cancel tools) | company code + user id + API cert key → Zone lookup (`src/client/session-manager.ts:199-205`) → session id (`:97-151`) |

**Headline**: only one of the six (mcp-erp) is shaped like the "curated finance verbs" server finance-world
already ships. Two are pure generic-CRUD (Frappe style), one is pure SQL, one is a discovery ladder, one is
a per-endpoint bag. The D365 dynamic server's *discovery + query + action* shape (`research/erp-domain.md`
§4.2) is closest to #4 and #5, not to #1/#2.

---

## 1. Access-pattern taxonomy (classification)

| Class | Definition | Servers | Agent cost | What it teaches |
|---|---|---|---|---|
| **A. Generic CRUD over doctypes** | One `get/create/update/delete` pair parameterised by an entity-name string; the model must know the entity vocabulary | 1, 2 | Model must know or discover the DocType vocabulary and every field name; nothing is typed. Lower bound, re-derived: the `erpnext` app alone ships **534** doctype folders (`find erpnext -type d -path '*/doctype/*' -not -path '*/doctype/*/*' \| wc -l`), of which **191** are in `accounts/`. The framework's own DocTypes come from `frappe/frappe`, which is **not checked out** — so the true catalogue size is **UNVERIFIED** and larger than 534 (§14 #1) | Cheap to build, brutal to use. All the semantics live in *data*, not tools |
| **B. Curated business verbs** | One tool per business action (`post_bill`, `record_payment`, `run_payroll`) | 3, 6 | Cheap per-call, but the tool list gets huge (79 tools) and vendor-specific | The "unified schema" fantasy leaks: 45 of mcp-erp's 79 tools only work on one backend (§4) |
| **C. SQL / query passthrough** | `run_query(sql)` over a relational projection | 5 (SQL-92 via JDBC), 4 (SuiteQL) | Model must author correct SQL against a schema it discovers | Real servers *demote* this: NetSuite's ladder puts SuiteQL at PRIORITY 4, "last resort" |
| **D. Discovery-first** | `list_*` metadata → `get_*_metadata` → act; act is forbidden before discovery | 4 (explicit ladder), 5 (`get_tables` → `get_columns` → `run_query`), 2 (`get_doctype_meta`) | Extra round-trips, but the model can't invent identifiers | This is where the industry converged, matching D365's `data_find_entity_type` → `data_get_entity_metadata` → `data_find_entities_sql` |

Note the direction of travel: **every** server built after ~2025 in this set (3, 4, 5) forces a discovery
step; only the two Frappe wrappers (1, 2) let the agent guess an entity name cold.

---

## 2. Server 1 — `erpnext-mcp-server` (rakeshgangwar): generic CRUD over doctypes

Registration: `erpnext-mcp-server/src/index.ts:357-587`. Dispatch: `:592-1002`.

| Tool | Args (JSON Schema) | Underlying call | Returns |
|---|---|---|---|
| `get_doctypes` | `{}` | `GET /api/resource/DocType?fields=["name"]&limit_page_length=500` (`:181-186`) | JSON array of DocType names |
| `get_doctype_fields` | `{doctype*}` | **infers** from one sample doc: `getDocList(doctype, {}, ["*"], 1)` (`:939`) | `[{fieldname, value: typeof, sample: first 50 chars}]` (`:953-957`) |
| `get_documents` | `{doctype*, fields[], filters{}, limit}` | `GET /api/resource/<DocType>?fields=<json>&filters=<json>&limit_page_length=<limit>` (`:82-102`) | raw `response.data.data` array |
| `get_document` | `{doctype*, name*}` | `GET /api/resource/<DocType>/<name>` (`:72-74`) | full doc incl. child tables |
| `create_document` | `{doctype*, data*, verbose}` | `POST /api/resource/<DocType>` body **`{data: doc}`** (`:111-114`) | `{status, doctype, name, docstatus}`; `verbose:true` → whole doc (`:650-662`) |
| `update_document` | `{doctype*, name*, data*, verbose}` | `PUT /api/resource/<DocType>/<name>` body `{data: doc}` (`:124-127`) | same minimal envelope |
| `submit_document` | `{doctype*, name*, verbose}` | **fetch full doc first**, then `POST /api/method/frappe.client.submit` with `{doc: fullDoc}` (`:817-820`) | `{status, doctype, name, docstatus}` — docstatus 1 |
| `cancel_document` | `{doctype*, name*, verbose}` | `POST /api/method/frappe.client.cancel` `{doctype, name}` (`:864`) | docstatus 2 |
| `delete_document` | `{doctype*, name*}` | `DELETE /api/resource/<DocType>/<name>` (`:169-171`) | `{status:"success", action:"deleted", …}` |
| `run_report` | `{report_name*, filters{}}` | `GET /api/method/frappe.desk.query_report.run?report_name=&filters=<json>` (`:137-142`) | `response.data.message` (columns + result rows) |
| `call_method` | `{method*, args{}, http_method: GET\|POST}` | `/api/method/<dotted.path>` (`:150-164`) | `message` payload. Description warns "Can invoke **any** whitelisted method — use with caution" (`:501`) |

Resources (MCP `resources/*`): `erpnext://DocTypes` and template `erpnext://{doctype}/{name}`
(`:263-293`). Note the resource *list* advertises only one URI while a `commonDoctypes` array of 8 is
declared and then never used (`:252-271`) — dead-code drift worth imitating as realism, not as design.

**Friction/behaviors worth reproducing**
- **No pagination at all.** Only `limit` → `limit_page_length`. No `limit_start`/offset, no `order_by`.
  An agent cannot page a large ledger; it must filter (`:82-106`).
- **Silent fabrication on failure.** If both DocType-listing strategies fail, `getAllDocTypes()` returns a
  **hardcoded list of 14 doctypes** — `Customer, Supplier, Item, Sales Order, Purchase Order, Sales Invoice,
  Purchase Invoice, Employee, Lead, Opportunity, Quotation, Payment Entry, Journal Entry, Stock Entry`
  (`:216-220`). The agent gets a plausible answer that is not the account's truth. **Best chaos pattern in
  the whole census.**
- **Schema inference fails on empty tables**: `get_doctype_fields` returns `isError: true` with
  "No documents found for X. Cannot determine fields." (`:941-949`) — a real "you can't learn the schema
  until data exists" trap.
- **Unauthenticated short-circuit**: every tool call returns `isError` text "Not authenticated with ERPNext.
  Please configure API key authentication." before dispatch (`:592-601`).
- **Errors are stringified and lossy**: `Failed to get ${doctype} ${name}: ${error?.message}` (`:77`) —
  axios's message, not ERPNext's. Server 2 exists specifically to fix this (§3).

---

## 3. Server 2 — `erpnext-mcp-server-extended` (SVAN GmbH): CRUD + schema mutation

Registration: `erpnext-mcp-server-extended/src/index.ts:437-459` (19 tools, one per line).

| Group | Tools | Notes / evidence |
|---|---|---|
| Auth | `authenticate_erpnext{username*,password*}` | `POST /api/method/login {usr,pwd}`, success iff `message === 'Logged In'` (`:179-181`) |
| Read | `get_documents{doctype*,fields[],filters{},limit}`, `get_document{doctype*,name*}` | identical REST shape to server 1 (`:199-211`) |
| Write | `create_document{doctype*,data*}`, `update_document{doctype*,name*,data*}`, `delete_document`, `submit_document`, `cancel_document` | **body shape differs**: posts `doc` **un-wrapped** (`:216`) where server 1 posts `{data: doc}` (§11) |
| Metadata | `get_doctypes`, `get_doctype_fields`, `get_doctype_meta` | `get_doctype_fields` queries the real `DocField` table: fields `fieldname,label,fieldtype,options,reqd,default,description,in_list_view,read_only,hidden,idx`, `order_by: 'idx asc'`, `limit_page_length: 0` (`:287-295`). `get_doctype_meta` → `frappe.desk.form.utils.get_meta`, falling back to `GET /api/resource/DocType/<name>` (`:302-313`) |
| Schema authoring | `create_doctype{name*,module*,fields*[],is_submittable,is_child_table,autoname,title_field,permissions[]}`, `add_doctype_field`, `create_custom_field`, `create_property_setter` | Default permission block when none supplied: `[{role:'System Manager', read:1,write:1,create:1,delete:1}]` (`:324`). Custom Field named `${doctype}-${fieldname}` (`:336`); Property Setter named `${doctype}-${fieldname}-${property}` or `${doctype}-main-${property}` (`:353`) |
| Workflow | `get_workflow{doctype*}`, `create_workflow{workflow_name*,document_type*,states*[],transitions*[],is_active}`, `update_workflow{name*,updates*}` | `get_workflow` filters `Workflow` on `{document_type, is_active:1}`, `limit_page_length:1` (`:369`). State shape `{state, doc_status, allow_edit, style}`; transition shape `{state, action, next_state, allowed, condition}` (`:453`) |
| Report | `run_report{report_name*,filters{}}` | same `frappe.desk.query_report.run` (`:265-267`) |

**The error taxonomy is the valuable part** (`:38-116`). `extractERPNextError()` unwinds, in order:
1. `_server_messages` — a JSON-encoded array of JSON-encoded strings; each parsed for `.message`/`.msg`, joined with `; ` (`:43-61`).
2. `data.message` (string) (`:63-65`).
3. `data.exception`, regex-matched against
   `ValidationError|MandatoryError|LinkValidationError|DuplicateEntryError|TimestampMismatchError` (`:69`).
4. `data.exc_type` → `"${exc_type}: ${msg}"` (`:76-79`).
5. `data._error_message` (`:81-83`).
6. HTTP-status fallback map (`:88-98`):
   `400 Bad Request – Invalid data sent to ERPNext`, `401 Unauthorized – Check your API key and secret`,
   **`403 Forbidden – You do not have permission for this operation`**, `404 Not Found`,
   **`409 Conflict – Document may have been modified by another user`**,
   **`417 Expectation Failed – Validation error in ERPNext`**, `500`, `502`, `503`.

Final wire format: `` `${operation} (HTTP ${status}): ${details}` `` (`:112-116`), e.g. the README's own
example: `Failed to create Fiscal Year (HTTP 417): ValidationError: Companies is required for Fiscal Year`
(`erpnext-mcp-server-extended/README.md`). **417 as the validation-error status is a Frappe idiom and is
exactly the kind of detail a mock should copy.**

**Regression vs server 1**: `submitDocument()` posts `{doc: {doctype, name}}` only (`:246`), while server 1
comments that `frappe.client.submit` "constructs the doc from the passed dict rather than loading from DB,
so it needs the full document with all fields" (`erpnext-mcp-server/src/index.ts:817-820`). One of the two
is wrong against a live instance — **UNVERIFIED which**, but the disagreement itself is a shipped fact.

---

## 4. Server 3 — `mcp-erp` multivendor (zavora-ai): curated verbs, lifecycle gates, 6 backends

Tool router: `mcp-erp-multivendor/src/server.rs` (79 `#[tool]` attributes). Unified types + backend trait:
`src/types.rs`. Governance manifest: `mcp-erp-multivendor/mcp-server.toml`.

### 4.1 Tool inventory (79, by group)

| Group | Count | Tools |
|---|---|---|
| Customers | 4 | `list_customers{limit=20}`, `get_customer{id}`, `create_customer{name,email?,phone?}`, `update_customer{id,name?,email?,phone?}` (`server.rs:231-261`) |
| Vendors | 4 | `list_vendors`, `get_vendor`, `create_vendor`, `update_vendor` (`:265-295`) |
| Products | 4 | `list_products`, `get_product`, `create_product{name,sku?,unit_price?}`, `update_product` (`:299-329`) |
| Sales orders | 4 | `list_sales_orders`, `get_sales_order`, `create_sales_order_draft{party_id,line_items[]}`, `submit_sales_order{id}` (`:333-363`) |
| Purchase orders | 4 | `list_purchase_orders`, `get_purchase_order`, `create_purchase_order_draft`, `submit_purchase_order` (`:367-397`) |
| Invoices | 5 | `list_invoices`, `get_invoice`, `create_invoice_draft{customer_id,line_items[]}`, `submit_invoice`, **`post_invoice`** (`:401-439`) |
| Inventory | 3 | `get_stock_levels{product_id?}`, `adjust_stock{product_id,quantity,reason}`, `transfer_stock{product_id,from_warehouse,to_warehouse,quantity}` (`:443-465`) |
| General ledger | 3 | `list_accounts`, `get_journal_entries{from,to}`, `get_trial_balance{as_of}` (`:469-491`) |
| Governance | 3 | `request_erp_approval{entity_type,entity_id,note?}`, `attach_erp_evidence{entity_type,entity_id,description,url?}`, `get_erp_audit_trail{entity_type,entity_id}` (`:495-512`) |
| **Accounting** | 10 | `list_bills{limit,status?}`, `get_bill`, `create_bill_draft`, `post_bill`, `list_payments`, `record_payment`, `run_report{report_type,as_at?,from?,to?}`, `get_dashboard`, `list_bank_accounts`, `post_journal_entry` (`:516-594`) |
| **HR/payroll** | 11 | `list_employees`, `list_fiscal_periods`, `list_departments`, `list_pay_runs`, `get_pay_run`, `run_payroll{period_id,pay_date}`, `add_pay_run_input{run_id,employee_id,kind,name,amount,taxable=true,type_code?}`, `recompute_pay_run`, `approve_pay_run`, `post_pay_run`, `mark_pay_run_paid` (`:598-692`) |
| **Procurement (P2P)** | 14 | `procurement_list_requisitions`, `_create_requisition`, `_approve_requisition`, `_convert_requisition{id,body{target:'tender'\|'purchase_order',…}}`, `_create_purchase_order`, `_send_purchase_order`, `_receive_goods`, **`_three_way_match{id}`**, `_create_debit_note`, `_list_expense_claims`, `_create_expense_claim`, `_approve_expense_claim`, `_analytics`, `_budget_control` (`:696-764`) |
| Tax device (Kenya) | 2 | `etims_status`, `etims_transmit_invoice{id}` (`:766-774`) |
| Bank/period/statutory | 8 | `list_reconciliations`, `compute_reconciliation{body}`, `complete_reconciliation{body}`, `close_period{id}`, `reopen_period{id}`, `list_tax_filings`, `file_tax_return{body}`, `remit_tax_filing{id,body}` (`:778-816`) |

### 4.2 The typed shapes (steal these)

- `LifecycleState` enum, one vocabulary for orders/invoices/POs:
  `draft, pending_approval, approved, released, posted, sent, fulfilled, partially_fulfilled, closed, cancelled, voided` (`types.rs:5-19`).
- `Invoice{id, customer_id?, customer_name?, state, total, balance_due?, currency?, line_items[], due_date?, created_at?, backend}` (`types.rs:114-127`) — note **`balance_due` is the open remainder**, mapped from Odoo's `amount_residual` (`odoo.rs:208`).
- `CreateBillInput{vendor_id, vendor_invoice_number?, issue_date?, due_date?, currency?, fx_rate?, line_items[], notes?}` (`types.rs:334-354`) — `vendor_invoice_number` is explicitly "the supplier's own invoice number (the legal document reference)", i.e. the ERP id ≠ the paper id. Exactly finance-world's `INV-001042` vs `1042` chaos.
- `RecordPaymentInput{payment_type:"customer_payment"|"vendor_payment", party_id, payment_date?, amount, currency?, fx_rate?, method:"bank_transfer"|"mpesa"|"cash"|"cheque", reference?, bank_account_id?, applications[{document_id, amount}], wht_amount?, funding_account?}` (`types.rs:366-394`). **`applications[]` is the settlement model** — a payment applied across N documents, mirroring `CustSettlement`.
- `PostJournalInput{date, reference, description, lines[{account_code, debit?, credit?, currency?, fx_rate?, description?}]}` with the tool description "Debits must equal credits" (`server.rs:588`).
- Report vocabulary as a *string enum in the description* (`server.rs:564`):
  financial — `TrialBalance, BalanceSheet, ProfitAndLoss, CashFlow, ArAgeing, ApAgeing, VatReturn, GlDetail, IncomeByCustomer, ExpenseByVendor, EquityChanges`; payroll — `PayrollRegister, StatutorySchedule, PayeP9, PayeP10, PayrollBankFile, PayrollSummary`.

### 4.3 Governance metadata (the part D365 does with RBAC, this does declaratively)

`mcp-server.toml` header: `risk_level = "high"`, `writes_allowed = "gated"`, `transports = ["stdio"]`,
`governance_gates = ["erp-write-policy", "financial-action-policy"]`, credentials as `vault://…` URIs.
Every declared tool carries `risk_class ∈ {read_only, internal_write, external_write, financial_action}`
and `requires_approval: bool`. Concretely: `create_customer` → `internal_write`/approval **true**;
`create_invoice_draft` → `internal_write`/approval **false**; `submit_invoice` and `post_invoice` →
`financial_action`/approval **true**. Plus a per-tool confirmation convention in prose — "Confirm with the
user first" appears in `approve_pay_run`, `post_pay_run`, `close_period`, `file_tax_return`,
`complete_reconciliation`, `etims_transmit_invoice`, `procurement_approve_*` descriptions (`server.rs`).

### 4.4 Backend fan-out — and where "unified" breaks

| Backend | Protocol | Auth | Entity mapping (from `docs/backends.md`) |
|---|---|---|---|
| Zoho Books | REST `https://www.zohoapis.com/books/v3` | OAuth2 token + `ZOHO_ORG_ID` | customers = `contacts?contact_type=customer`; vendors = same endpoint, `contact_type=vendor`; `salesorders`, `purchaseorders`, `invoices`, `chartofaccounts`, `journals`; paging `per_page={limit}` (`zoho.rs:50,96,266`) |
| Odoo | JSON-RPC `/jsonrpc`, `execute_kw` | `common.authenticate` → uid, then uid+password on every call (`odoo.rs:16-33`) | `res.partner` split by `customer_rank>0` / `supplier_rank>0`; `product.product`; `sale.order`; `purchase.order`; **`account.move` with `move_type='out_invoice'`**; `stock.quant`; `account.account`; `account.move.line`; audit = `mail.message` |
| Business Central | OData v4 `…/api/v2.0/companies({company})` | Azure AD bearer | `customers`, `vendors`, `items`, `salesOrders(+Lines)`, `purchaseOrders`, `salesInvoices(+Lines)`, `accounts`, `generalLedgerEntries`; **ETag optimistic concurrency on PATCH** (`business_central.rs:72,101,130`); `Microsoft.NAV.ship` / `Microsoft.NAV.post` bound actions |
| NetSuite | SuiteTalk REST `/services/rest/record/v1` | OAuth 1.0a TBA | record types `customer, vendor, inventoryItem, salesOrder, purchaseOrder, invoice, account, journalEntry`; sends `Prefer: respond-async` (`netsuite.rs:39`); status letter codes A/B/C/H per record type |
| SAP S/4HANA | OData `/sap/opu/odata/sap/…` | OAuth2 or Basic | `API_BUSINESS_PARTNER/A_BusinessPartner?$filter=BusinessPartnerCategory eq '1'` (customers) / `'2'` (vendors); `API_PRODUCT_SRV/A_Product`; `API_SALES_ORDER_SRV/A_SalesOrder`; `API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder`; `API_BILLING_DOCUMENT_SRV/A_BillingDocument`; `API_MATERIAL_STOCK_SRV/A_MatlStkInAcctMod`; `API_GLACCOUNTINCHARTOFACCOUNTS_SRV/A_GLAccountInChartOfAccounts`; `API_JOURNALENTRYITEMBASIC_SRV/A_JournalEntryItemBasic?$filter=PostingDate ge datetime'…'` (`sap.rs:49-222`) |
| Zavora ERA (vendor's own) | REST `{base}/api/v1` | JWT email/password, 15-min TTL, auto re-login (`CHANGELOG.md`, `zavora.rs:66-90`) | `customers`, `vendors`, `products`, `invoices`, `invoices/{id}/post`, `bills`, `journal-entries?from&to&limit=200`, `audit/{entity_type}/{entity_id}` |

**Backend selection is first-configured-wins by env var**, priority Zavora → Zoho → Odoo → BC → NetSuite →
SAP — read off `init_backend()` in `src/main.rs:57-101` (Zavora `:58-63`, Zoho `:65-70`, Odoo `:72-77`, BC
`:79-84`, NetSuite `:86-91`, SAP `:93-98`, then `anyhow::bail!` at `:100`). **`docs/backends.md` does *not*
corroborate this**: its "Backend Selection Priority" list (`:7-15`) has only five entries and starts at Zoho
— Zavora, the highest-priority backend in code, is absent from the doc entirely (§11, last row). Only
**one** backend is live per process.

**Capability holes are returned as tool errors, not hidden**: every accounting/payroll/procurement method
has a default trait impl returning `"{backend}: vendor bills not supported by this backend"` etc.
(`types.rs:234-331`). Only Zavora implements them. Odoo additionally refuses transfers:
`"Odoo stock transfers require picking workflow — use the Odoo UI"` (`odoo.rs:254`) and fakes the trial
balance by returning the chart of accounts (`odoo.rs:268-271`, documented as a limitation in
`docs/backends.md`). Two `governance` tools are **pure theatre** — `request_erp_approval` and
`attach_erp_evidence` just format a string and never touch a backend (`server.rs:495-504`).

---

## 5. Server 4 — `opensuitemcp-netsuite` (unstackedapps): a client to Oracle's hosted MCP

This repo does **not** implement ERP tools. It speaks JSON-RPC 2.0 to
`https://{NS_ACCOUNT_ID}.suitetalk.api.netsuite.com/services/mcp/v1/all` with a bearer token
(`lib/netsuite/mcp.ts:7-13, 84-120`), calling `tools/list`, `tools/call`, `resources/read`
(`:148-160, 189-215, 228-250`). Timeouts: 30 s for tools, 45 s for resource reads (`:110, 244`).

**Oracle's shipped tool names** (this is the census value — these are the real hosted-server tool names):

| Tool | Role in the ladder | Evidence |
|---|---|---|
| `ns_listAllReports` → `ns_runReport` | PRIORITY 1 | `lib/ai/prompts.ts:88` |
| `ns_listSavedSearches` → `ns_runSavedSearch` | PRIORITY 2 | `:89` |
| `ns_getRecordTypeMetadata` → `ns_getRecord` / `ns_createRecord` / `ns_updateRecord` | PRIORITY 3 | `:90` |
| `ns_getSuiteQLMetadata` → `ns_runCustomSuiteQL` | PRIORITY 4, "last resort" | `:91` |
| `ns_getSubsidiaries` | called "when a report needs a subsidiary filter" | `:101` |
| `ns_prompt_library_app` | MCP **App** (UI-bearing tool, `_meta.ui.resourceUri` = `ui://…`) | `:108`, `lib/netsuite/mcp.ts:68-82`, `components/prompt-library-dialog.tsx:134` |

The v1.0.0 changelog independently lists the first five as the shipped set:
`ns_runReport, ns_listAllReports, ns_listSavedSearches, ns_runSavedSearch, ns_runCustomSuiteQL`
(`opensuitemcp-netsuite/CHANGELOG.md:448-452`).

**The operating policy is the portable artifact** (`lib/ai/prompts.ts:99-108`) — these are house rules a
finance-world grader could enforce:
- "Prefer `ns_runReport`/`ns_runSavedSearch` over SuiteQL … **standard reports apply NetSuite business rules
  that SuiteQL does not.**" (the report-vs-raw-query truth split — finance-world's aging-snapshot-vs-live
  tension, restated)
- "Always discover before assuming"; "Use exact IDs returned by tools. Never invent report IDs, saved-search
  IDs, record IDs, or field joins."
- "Never run SuiteQL without user confirmation."
- SuiteQL must include **`ROWNUM <= 1000`**, explicit columns (no `SELECT *`), `NVL` on nullable amounts,
  and prefer **`posting = 'T'` and `approvalstatus = 2` for GL-accurate approved data** (`:104`).
- "Do not auto-retry a failed `ns_createRecord`; ask the user to verify in NetSuite and use a new unique
  `externalId` if retrying." (`:105`) — idempotency friction, verbatim.
- "For financial multi-subsidiary asks, clarify subsidiary vs consolidated when unspecified." (`:106`)

Ops surface worth noting: NetSuite integration setup requires `Authorization Code Grant` + `Public Client`
+ redirect URI + scope **"NetSuite AI Connector Service"** (`lib/netsuite/integration-checklist.ts:44-68`);
Oracle SuiteCloud **Agent Skills** are synced as `SKILL.md` files from
`github.com/oracle/…/packages/agent-skills` (`lib/ai/skills/sync-oracle.ts:11,63,85`); the app enforces its
own daily message caps (guest 20 / regular 100, `lib/ai/entitlements.ts:22,31`) and Redis-backed rate
limiting (`lib/rate-limit.ts`).

---

## 6. Server 5 — `sap-erp-mcp-cdata` (CData): three tools, SQL only

Registration: `sap-erp-mcp-cdata/src/main/java/com/cdata/mcp/Program.java:92-102` (`registerTools`; the
three-element `ITool[]` literal is `:93-97` — `:88-91` is the tail of `registerResources`). Tool names are
**prefixed from config**: `{Prefix}_get_tables`, `{Prefix}_get_columns`, `{Prefix}_run_query` (e.g.
`saperp_run_query`), where `Prefix` comes from a `.prp` properties file (`Config.java`, README example
`Prefix=saperp`).

| Tool | Args | Behavior | Return |
|---|---|---|---|
| `*_get_tables` | `{catalog?, schema?}` | JDBC `DatabaseMetaData.getTables()` (`GetTablesTool.java:78-90`) | **CSV** with header row: `Catalog?, Schema?, Table, Description`; appends `Default Catalog: …` / `Default Schema: …` text blocks when the driver reports single-catalog/schema (`:57-68`) |
| `*_get_columns` | `{catalog?, schema?, table*}` | `DatabaseMetaData.getColumns()` (`GetColumnsTool.java:69-83`) | CSV: `…, Table, Column, DataType, Remarks` |
| `*_run_query` | `{sql*}` | `Statement.executeQuery(sql)` → CSV (`RunQueryTool.java:71-75`) — **the SQL is passed through unvalidated**; nothing in the tool checks for `SELECT` | CSV, header row first |

The `run_query` **description is the dialect contract — and the only "read-only" enforcement there is**
(`RunQueryTool.java:29-35`, the composed `description` string): "The SELECT statement to execute. … The SQL dialect is
mostly based around SQL-92. Identifiers should be quoted using `<quotes>` characters. Valid clauses: FROM,
INNER JOIN, LEFT JOIN, GROUP BY, ORDER BY, LIMIT/OFFSET." The quote characters are **discovered at startup**
from the driver via `SELECT NAME, VALUE FROM sys_sqlinfo` (`Config.java`, `retrieveSqlInfo`), as are
`SUPPORTS_MULTIPLE_CATALOGS` / `SUPPORTS_MULTIPLE_SCHEMAS`.

Also ships MCP **resources**: one per configured table, URI `{prefix}://{catalog}/{schema}/{table}`,
returning the column list as CSV (`resources/TableMetadataResource.java:28-53`). Resources are registered
only for tables named in the `Tables=` property (`registerResources`, `Program.java:84-91`, iterating
`config.getTables()` — `Config.java:25, 94`) — i.e. **the admin can narrow the agent's visible schema**, a
cheap and realistic permission mechanic.

Errors are thrown as `RuntimeException("ERROR: " + ex.getMessage())` — raw JDBC/driver text reaches the
model (`RunQueryTool.java:67`).

---

## 7. Server 6 — `mcp-server-ecount` (ECOUNT ERP, Korean SMB cloud ERP): 23 verbs with real rate limits

Registration: `mcp-server-ecount/src/tools/register.ts` (23 `server.tool(...)` calls; the file's own log
line says `count: 22` at `:654` — see §11). Tool descriptions are Korean and embed both the rate limit and
the response field dictionary inline — a genuinely good pattern for a mock's tool docs.

| Group | Tool | Args | Rate limit (from description + `client/rate-limiter.ts`) |
|---|---|---|---|
| Connection | `ecount_test_connection` | `{}` | — |
| | `ecount_get_session_info` | `{}` | — |
| | `ecount_server_status` | `{}` | returns `{version, rateLimits, errorCounter, cache}` (`:100-105`) |
| Products | `ecount_get_product` | `{prodCode*}` | **1 s** |
| | `ecount_get_products` | `{prodCodes[]?, prodType?}` | **10 min**, result cached 10 min |
| | `ecount_create_product` | `{products[≤300]*}` | **10 s** |
| Parties | `ecount_create_customer` | `{customers[≤300]*}` | 10 s |
| Inventory | `ecount_get_inventory` | `{baseDate*, prodCode*, whCode?}` | 1 s |
| | `ecount_get_inventory_list` | `{baseDate*, prodCodes[]?, whCode?, includeZeroStock, includeBalanceExcluded, includeDiscontinued}` | 10 min + cache |
| | `ecount_get_inventory_by_warehouse` | `{baseDate*, prodCode*, whCode?}` | 1 s |
| | `ecount_get_inventory_by_warehouse_list` | same as list | 10 min + cache |
| Sales | `ecount_create_quotation` / `_create_sale_order` / `_create_sale` | `{items[]*}` | 10 s each |
| Purchasing | `ecount_get_purchase_orders` | `{baseDateFrom*, baseDateTo*, customerCode?, prodCode?}` — **max 30-day window** (`:419`) | 10 min + cache |
| | `ecount_create_purchase` | `{items[]*}` | 10 s |
| Production | `ecount_create_job_order`, `_create_goods_issued`, `_create_goods_receipt` | `{items[]*}` | 10 s each |
| **Accounting** | `ecount_create_invoice` | `{items[≤300]*}`, each `{TRX_DATE?, TAX_GUBUN*, CUST?, CUST_DES?, CR_CODE?, DR_CODE?, SUPPLY_AMT?, VAT_AMT?, REMARKS?, SITE_CD?, PJT_CD?}` (`tools/schemas.ts:335-366`) | 10 s |
| E-commerce | `ecount_create_openmarket_order` | `{openmarketCode*, orders[]*}` | 10 s |
| HR | `ecount_create_clock_in_out` | `{items[]*}` | 10 s |
| Collab | `ecount_create_board_post` | `{posts[]*}` | 10 s |

**Mechanics worth stealing wholesale**

- **Per-API independent rate limits**, not a global bucket (`src/client/rate-limiter.ts:14-53`): auth/zone
  10 min; each *multi-row query* API 10 min; each *single-row query* API 1 s; each *save* API 10 s. Each
  API type has its own timer, with a **100 ms safety margin** added (`:69`) and file-based state so
  multiple processes share the limiter.
- **Rate-limit error is typed and actionable**: `EcountRateLimitError{retryAfterMs, apiType}` with message
  `Rate Limit 초과 (…). N초 후 재시도 가능.` (`src/utils/errors.ts:84-110`).
- **Three-step auth**: company code → `/OAPI/V2/Zone` (returns a zone letter; the URL is built in
  `fetchZone()` at `src/client/session-manager.ts:199-205` and the call is **`method: 'POST'`**, `:209-210`,
  despite the path reading like a lookup) → base URL becomes `https://oapi{zone}.ecount.com` (prod) or
  `https://sboapi{zone}.ecount.com` (test) (`:142-151`, host constants at `:96-97`) → login → `SESSION_ID`
  carried as a **query parameter** on every call (`src/client/session-manager.ts:97-151`,
  `docs/api-accounting.md`). Session considered valid only until `expiresAt − 5 min` (`:135`).
- **Typed auth failures**: `SESSION_EXPIRED`, `TIMEOUT`, `INVALID_CREDENTIALS`, `ZONE_NOT_FOUND`
  (`src/utils/errors.ts:52-79`).
- **Batch writes return a partial-success envelope**, never a single ok/fail:
  `{SuccessCnt, FailCnt, SlipNos[], ResultDetails[{IsSuccess, TotalError, Errors[]}]}` (`register.ts:176-180`,
  `docs/api-accounting.md`). **Partial batch failure is a first-class outcome.** Voucher numbers come back as
  `YYYYMMDD-N` (`register.ts:344`).
- **Grouping key inside a flat array**: rows sharing `UPLOAD_SER_NO` become one voucher
  (`register.ts:342`, `schemas.ts:76-83`) — i.e. the agent constructs document headers implicitly.
- Domain vocabulary: `TAX_GUBUN` 11 과세매출 / 12 영세매출 / 13 면세매출 / 14 신용카드매출 / 21 과세매입 /
  22 영세매입 / 23 면세매입 / 24 신용카드매입; `CR_CODE` = revenue account (e.g. `4019`), `DR_CODE` =
  purchase account (e.g. `1469`) (`schemas.ts:340-355`, `docs/api-accounting.md`).
- Even the API version's sunset is in the response: `Data.EXPIRE_DATE` = "API 현재버전 서비스 종료일"
  (`docs/api-accounting.md`).

---

## 8. Frappe/ERPNext REST semantics, cross-checked against the ERPNext source

### 8.1 The wire protocol (as exercised by servers 1 and 2)

| Concern | Shape | Evidence |
|---|---|---|
| List | `GET /api/resource/<DocType>` | `erpnext-mcp-server/src/index.ts:98-101` |
| Read one | `GET /api/resource/<DocType>/<name>` | `:72-74` |
| Create | `POST /api/resource/<DocType>` | `:111-114` (body `{data: doc}`) vs `erpnext-mcp-server-extended/src/index.ts:216` (body `doc`) |
| Update | `PUT /api/resource/<DocType>/<name>` | `:124-127` |
| Delete | `DELETE /api/resource/<DocType>/<name>` | `:169-171` |
| RPC | `GET`/`POST /api/method/<dotted.python.path>` | `:150-164` |
| `fields` | JSON-encoded array in the query string: `fields=["name","status"]`; `["*"]` for all | `:86-88`, `:939` |
| `filters` | JSON-encoded object `{field: value}` (the servers only expose the equality form; Frappe's `[[fieldname, op, value]]` list form is **not** exposed by either server) | `:90-92`, tool schema `:399-403` |
| `limit_page_length` | page size; **`0` = unbounded** | `erpnext-mcp-server-extended/src/index.ts:277, 292`; `erpnext/erpnext/accounts/bulk_payment.py:84` uses `limit_page_length=0` for the same "give me everything" intent |
| Default page size | **20** — not set by either MCP server, but ERPNext's own list handlers default to `limit_page_length=20` (`erpnext/erpnext/projects/doctype/project/project.py:488`, `.../timesheet/timesheet.py:538`) | |
| `order_by` | supported by `frappe.client.get_list` (`erpnext-mcp-server-extended/src/index.ts:293`, `order_by:'idx asc'`); **not exposed** by either server's `get_documents` tool | |
| Auth header | `Authorization: token <api_key>:<api_secret>` | `erpnext-mcp-server/src/index.ts:59-60` |
| Session auth | `POST /api/method/login {usr,pwd}` → `message === 'Logged In'` | `erpnext-mcp-server-extended/src/index.ts:179-181` |
| Report runner | `GET /api/method/frappe.desk.query_report.run?report_name=&filters=<json>` → `.message` | `erpnext-mcp-server/src/index.ts:137-142` |
| Submit / cancel | `frappe.client.submit` / `frappe.client.cancel` | `:820, :864` |
| Docstatus | `0` draft → `1` submitted → `2` cancelled; cancelled docs cannot be modified, "use amend workflow to create a corrected copy" | tool descriptions `:525, :547` |
| DocType search fallback | `GET /api/method/frappe.desk.search.search_link?doctype=DocType&txt=&limit=500` | `:199-205` |

**UNVERIFIED (frappe framework not checked out here)**: the exact default of `limit_page_length` on the raw
`/api/resource` endpoint (20 is inferred from ERPNext's own callers), the `[[doctype, field, op, value]]`
filter form, `limit_start` offset paging, and `X-Frappe-*` response headers.

### 8.2 Real accounting DocTypes (from `erpnext/`, version `17.0.0-dev` / `develop_version 17.x.x-develop`, `erpnext/erpnext/__init__.py`)

The accounting module ships **191 doctype folders** (`ls -d erpnext/erpnext/accounts/doctype/*/ | wc -l`;
534 across the whole app — §1). The ones that matter for an AP/AR world:

| DocType | Submittable | Key fields (verified from the `.json`) |
|---|---|---|
| **Sales Invoice** | yes (`autoname: naming_series:`) | `company, posting_date, due_date, currency, conversion_rate, grand_total, paid_amount, outstanding_amount` (currency = `party_account_currency`), `status ∈ {Draft, Return, Credit Note Issued, Submitted, Paid, Partly Paid, Unpaid, Unpaid and Discounted, Partly Paid and Discounted, Overdue…}` |
| **Purchase Invoice** | yes | same core; `status ∈ {Draft, Return, Debit Note Issued, Submitted, Paid, Partly Paid, Unpaid, Overdue, Cancelled, Internal Transfer}`; has an `on_hold` flag (referenced at `accounts/doctype/payment_entry/payment_entry.py:720-724`) |
| **Payment Entry** | yes | `payment_type ∈ {Receive, Pay, Internal Transfer}`, `party_type` (Link→DocType) + `party` (Dynamic Link), `paid_amount`, **`unallocated_amount`**, `posting_date`, `status ∈ {Draft, Submitted, Cancelled}` |
| **Payment Entry Reference** (child) | — | `reference_doctype, reference_name, due_date, total_amount, outstanding_amount, allocated_amount, payment_type` — **this is the settlement line** |
| **Journal Entry** | yes | `voucher_type` — the full 18-value `options` list (`journal_entry.json`, field `voucher_type`): `Journal Entry, Inter Company Journal Entry, Bank Entry, Cash Entry, Credit Card Entry, Debit Note, Credit Note, Contra Entry, Excise Entry, Write Off Entry, Opening Entry, Depreciation Entry, Asset Disposal, Periodic Accounting Entry, Exchange Rate Revaluation, Exchange Gain Or Loss, Deferred Revenue, Deferred Expense`; plus `posting_date, total_amount, due_date` |
| **GL Entry** | yes; `autoname: ACC-GLE-.YYYY.-.#####` | `posting_date, party_type, party, debit, credit, voucher_type, voucher_no, against_voucher_type, against_voucher, due_date, is_cancelled` |
| **Payment Ledger Entry** | yes | `posting_date, party_type, party, voucher_type, voucher_no, against_voucher_type, due_date` — the party-subledger projection (ERPNext's `CustTransOpen` analogue) |
| **Dunning** | yes | `posting_date, grand_total, currency, conversion_rate, status ∈ {Draft, Resolved, Unresolved, Cancelled}` |
| **Dunning Type** | — | `dunning_type, dunning_fee, dunning_letter_text, rate_of_interest, is_default, income_account, cost_center, company` |
| **Overdue Payment** (child of Dunning) | — | `payment_term, description, due_date, mode_of_payment, invoice_portion, payment_amount, outstanding, paid_amount, discounted_amount, sales_invoice, payment_schedule, **overdue_days**, **dunning_level**, interest` |
| **Payment Term** | — | `payment_term_name, invoice_portion, mode_of_payment, due_date_based_on, credit_days, credit_months, description, **discount_type, discount, discount_validity_based_on, discount_validity**` |

Mapping to what finance-world already models (`research/erp-domain.md` §1.1): D365's `CustTrans` →
Sales/Purchase Invoice + GL Entry; `CustTransOpen` → `outstanding_amount` + Payment Ledger Entry;
`CustSettlement` → Payment Entry Reference (`allocated_amount`); collection letters → **Dunning + Dunning
Type + Overdue Payment.dunning_level**; cash-discount codes → Payment Term's
`discount/discount_validity` fields (ERPNext folds discount into the term rather than a separate code
chain). **ERPNext is a structurally equivalent world with different names — porting is a rename, not a
re-model.**

Reports (each is a `run_report` target — `erpnext/erpnext/accounts/report/`): `accounts_receivable`,
`accounts_receivable_summary`, `accounts_payable`, `accounts_payable_summary`, `general_ledger`,
`payment_ledger`, `trial_balance`, `trial_balance_for_party`, `balance_sheet`,
`profit_and_loss_statement`, `cash_flow`, `customer_ledger_summary`, `supplier_ledger_summary`,
`sales_register`, `purchase_register`, `bank_reconciliation_statement`, `bank_clearance_summary`,
`payment_period_based_on_invoice_date`, `financial_ratios`, `voucher_wise_balance`,
`consolidated_financial_statement`, and ~30 more.

**Accounts Receivable report filters** (`erpnext/erpnext/accounts/report/accounts_receivable/accounts_receivable.js`),
i.e. the exact knobs an aging task must pin: `company` (required), `report_date` (default today),
`finance_book`, `cost_center[]`, `project[]`, `party_type`, **`ageing_based_on ∈ {Posting Date, Due Date}`
default `Due Date`**, **`age_as_on ∈ {Report Date, Today}` default `Report Date`**, **`range` default
`"30, 60, 90, 120"`**, `customer_group[]`, `payment_terms_template`, `sales_partner`, `sales_person`,
`territory[]`, `group_by_party`, `based_on_payment_terms`, `show_future_payments`, `show_delivery_notes`,
`show_sales_person`, `show_remarks`. **Two independent "as of" knobs plus a bucket string is a
ready-made ambiguity trap.**

### 8.3 Validation errors worth reproducing verbatim (ERPNext source)

From `erpnext/erpnext/accounts/doctype/payment_entry/payment_entry.py`:
- `"{0} {1} does not exist"` (`:630, :683`)
- `"{0} {1} is not associated with {2} {3}"` (party mismatch between payment and invoice, `:687-691`)
- `"{0} {1} is associated with {2}, but Party Account is {3}"` (`:709-715`)
- `"{0} {1} is on hold"` with title `"Invalid Purchase Invoice"` (`:720-724`)
- `"{0} {1} must be submitted"` (docstatus ≠ 1, `:727-730`)
- `"Reference Doctype must be one of {0}"` — valid sets are party-dependent:
  Customer → `Sales Order, Sales Invoice, Journal Entry, Dunning, Payment Entry`;
  Supplier → `Purchase Order, Purchase Invoice, Journal Entry, Payment Entry`;
  Shareholder/Employee → `Journal Entry` only (`:732-738`)
- `"Difference Amount must be zero"` (`:204`), `"Party Type is mandatory"` (`:537`),
  `"Payment Type must be one of Receive, Pay, or Internal Transfer"` (`:626`)

From `sales_invoice.py`: `"Debit To is required"` with title `"Account Missing"` (`:760`),
`"Sales Order {0} is not submitted"` (`:1022`), `"Warehouse required for stock Item {0}"` (`:902`).

---

## 9. Cross-server capability matrix

Capability classes as requested; ✅ = a named tool exists, ⚠️ = achievable only indirectly (generic CRUD or
SQL), ❌ = absent.

| Capability | 1 ERPNext | 2 ERPNext-Ext | 3 mcp-erp | 4 NetSuite (Oracle tools) | 5 CData SAP | 6 ECOUNT | **finance-world `erp` today** |
|---|---|---|---|---|---|---|---|
| **Query / list** | ✅ `get_documents` (generic) | ✅ | ✅ 12 `list_*` + 8 `get_*` | ✅ `ns_getRecord`, `ns_runCustomSuiteQL` | ✅ `*_run_query` | ✅ 7 read tools | ✅ `data_find_entities_sql` + OData |
| **Discovery / metadata** | ✅ `get_doctypes`, `get_doctype_fields` (inferred!) | ✅ + `get_doctype_meta` | ❌ (fixed tool list is the schema) | ✅ `ns_getRecordTypeMetadata`, `ns_getSuiteQLMetadata`, `ns_listAllReports`, `ns_listSavedSearches` | ✅ `*_get_tables`, `*_get_columns` + resources | ❌ | ✅ `data_find_entity_type`, `data_get_entity_metadata` |
| **Create** | ⚠️ `create_document` (any doctype) | ⚠️ same | ✅ 7 typed creators (`create_bill_draft`, `create_invoice_draft`, …) | ✅ `ns_createRecord` | ❌ | ✅ 12 typed creators | ✅ `data_create_entities` |
| **Update** | ⚠️ `update_document` | ⚠️ same | ✅ `update_customer/vendor/product` | ✅ `ns_updateRecord` | ❌ | ❌ | ✅ `data_update_entities` |
| **Submit / post** | ✅ `submit_document`, `cancel_document` (docstatus 0→1→2) | ✅ same | ✅ `submit_*`, `post_invoice`, `post_bill`, `post_journal_entry`, `post_pay_run` | ⚠️ via record status fields | ❌ | ⚠️ create *is* the post (`ecount_create_invoice` = 자동분개) | ✅ **5** `api_invoke_action` Contoso actions (`mcp/servers/erp_server.py:396-402`: `ContosoCustAgedBalancesLive`, `ContosoCashDiscountForecast`, `ContosoCollectionStatus`, `ContosoIssueCollectionLetter`, `ContosoSetCreditHold` — the last two `requires_role: collections`) |
| **Reconcile** | ⚠️ via `call_method` on Payment Reconciliation | ⚠️ same | ✅ `compute_reconciliation`, `complete_reconciliation`, `list_reconciliations` | ❌ | ❌ | ❌ | ❌ (queued with bank server, `docs/TOOL-CENSUS.md`) |
| **Report** | ✅ `run_report{report_name, filters}` | ✅ same | ✅ `run_report{report_type,…}` (16 named report types) | ✅ `ns_listAllReports`/`ns_runReport`, `ns_runSavedSearch` | ⚠️ author SQL | ❌ (only entity reads) | ⚠️ via SQL |
| **Workflow action** | ⚠️ `call_method` | ✅ `get/create/update_workflow` (**authors** the state machine) | ✅ approval verbs (`approve_pay_run`, `procurement_approve_*`, `request_erp_approval`) | ❌ | ❌ | ❌ | ✅ form tools + actions |
| **Period control** | ⚠️ | ⚠️ | ✅ `close_period`, `reopen_period` | ❌ | ❌ | ❌ | ❌ |
| **Schema mutation** | ❌ | ✅ `create_doctype`, `add_doctype_field`, `create_custom_field`, `create_property_setter` | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Rate limiting** | ❌ | ❌ | ❌ | ⚠️ app-level (`lib/rate-limit.ts`, entitlements) | ❌ | ✅ **per-API, 1 s / 10 s / 10 min** | ❌ |
| **Pagination** | ❌ (limit only) | ❌ | ❌ (`limit`, default 20) | ⚠️ SuiteQL `ROWNUM <= 1000` | ✅ SQL `LIMIT/OFFSET` | ❌ (date windows ≤ 30 days) | ✅ 25-row pages |
| **Approval gating metadata** | ❌ | ❌ | ✅ `risk_class` + `requires_approval` per tool | ⚠️ prompt-policy only | ❌ | ❌ | ⚠️ RBAC denial |

---

## 10. Error & friction catalog (ranked by portability)

| # | Pattern | Source | Why it's worth mocking |
|---|---|---|---|
| 1 | **Fabricated fallback catalog** — metadata call fails, server silently returns a hardcoded 14-item DocType list | `erpnext-mcp-server/src/index.ts:214-221` | The agent gets a confident wrong world model. Perfect "verify your ground truth" task |
| 2 | **HTTP 417 = validation error** (Frappe idiom), 403 = permission, 409 = concurrent modification | `erpnext-mcp-server-extended/src/index.ts:88-98` | Status codes that don't mean what a model assumes |
| 3 | **`_server_messages` double-encoding** — JSON array of JSON strings, each with `.message` | `…-extended/src/index.ts:43-61` | Realistic parse friction; a naive agent reports the raw blob |
| 4 | **Partial batch success** `{SuccessCnt, FailCnt, SlipNos[], ResultDetails[]}` | `mcp-server-ecount/src/tools/register.ts:176-180` | "12 of 15 posted" is the real outcome of bulk ERP writes |
| 5 | **Per-API rate limits with different tiers** (single-read 1 s, bulk-read 10 min, write 10 s) + typed `retryAfterMs` | `mcp-server-ecount/src/client/rate-limiter.ts:14-53`, `src/utils/errors.ts:84-110` | Forces planning: the agent must batch reads or wait 10 minutes |
| 6 | **Capability holes surfaced as errors**: `"{backend}: vendor bills not supported by this backend"` | `mcp-erp-multivendor/src/types.rs:234-331` | A tool exists but is a no-op for this tenant — extremely common and rarely mocked |
| 7 | **"Use the UI"** dead-ends: `"Odoo stock transfers require picking workflow — use the Odoo UI"` | `mcp-erp-multivendor/src/odoo.rs:254` | Legitimate refusal the agent must report, not work around |
| 8 | **Silent substitution**: Odoo `get_trial_balance` returns the chart of accounts | `mcp-erp-multivendor/src/odoo.rs:268-271` + `docs/backends.md` "no native report API" | Right-shaped, wrong-semantics response |
| 9 | **Schema-before-data**: `get_doctype_fields` can't answer for an empty doctype | `erpnext-mcp-server/src/index.ts:941-949` | |
| 10 | **Idempotency trap**: "Do not auto-retry a failed `ns_createRecord`; use a new unique `externalId`" | `opensuitemcp-netsuite/lib/ai/prompts.ts:105` | Double-posting an invoice is the classic ERP agent failure |
| 11 | **Report ≠ query**: "standard reports apply NetSuite business rules that SuiteQL does not" | `…/lib/ai/prompts.ts:100` | Two defensible numbers; the grader picks the report |
| 12 | **Approval theatre**: `request_erp_approval` returns a formatted string and touches nothing | `mcp-erp-multivendor/src/server.rs:495-504` | An agent that "got approval" got nothing |
| 13 | **Reference-doctype whitelist by party type** (Customer may settle against Dunning; Supplier may not) | `erpnext/…/payment_entry.py:732-738` | Asymmetric rule the model cannot guess |
| 14 | **Session/zone indirection**: company code → zone letter → per-zone host → session id in the query string, valid until `expiresAt − 5 min` | `mcp-server-ecount/src/client/session-manager.ts:199-205` (the `/OAPI/V2/Zone` hop) + `:97-151` (per-zone host construction, `:135` expiry margin) | Multi-hop auth realism at low cost |
| 15 | **Prefixed tool names from config** (`saperp_run_query`) — the tool name isn't stable across deployments | `sap-erp-mcp-cdata/src/main/java/com/cdata/mcp/tools/RunQueryTool.java:42` (`prefix + "_run_query"`) | |

---

## 11. Doc-vs-code drift ledger (shipped code wins)

| Server | Doc claims | Code shows | Verdict |
|---|---|---|---|
| mcp-erp | "**44 tools** across 6 backends" (`README.md:8`); `CHANGELOG.md` 1.1.0 "44 tools total" | **79** `#[tool]` registrations (`src/server.rs`) | Code wins: 79. README documents only groups 1-10; payroll (11), procurement (14), eTIMS (2), banking/period/tax (8) are undocumented |
| mcp-erp | governance manifest declares **34** tools (`mcp-server.toml`, `[[tools]]` count) | 79 in code | 45 tools ship with **no** declared `risk_class` / `requires_approval` despite `writes_allowed = "gated"` and startup manifest validation (`src/main.rs:40-45`) |
| ECOUNT | README "**22 Tools**"; `register.ts:654` logs `count: 22` | **23** `server.tool(` calls | Code wins: 23 |
| CData SAP | README `:110`: "the AI client will be able to use the built-in tools to **read, write, update, and delete** the underlying data" | 3 tools, none of which is a writer; `run_query` is *described* as `SELECT`-only (`RunQueryTool.java:42-43`) but **enforces nothing** — `executeQuery(sql)` takes the string as given (`:71-75`). README `:4` and `:6` both say "**read-only MCP server**" | Read-only wins as *intent* — README `:110` is boilerplate from CData's generic template. But the guarantee is the driver's and the description's, **not the server's**; a write statement reaching `executeQuery` is refused (if at all) downstream of this repo |
| ERPNext base vs extended | both target `POST /api/resource/<DocType>` | base sends `{data: doc}` (`index.ts:113`), extended sends `doc` (`index.ts:216`) | Unresolved — **UNVERIFIED** which Frappe accepts; the divergence is itself the finding |
| ERPNext base vs extended | both implement `submit_document` | base loads the full doc first and explains why (`index.ts:817-820`); extended posts `{doc:{doctype,name}}` (`index.ts:246`) | Base's comment implies extended's form fails; **UNVERIFIED** |
| mcp-erp | README backend table lists **5** backends; prose says **6** | 6 modules incl. `zavora` (`src/main.rs:5-16`) | 6; `docs/backends.md` documents only 5 (Zavora missing) |

---

## 12. Portable task candidates (with the ground-truth mechanism)

| Task | What it tests | Ground truth from |
|---|---|---|
| **Aging-knob disambiguation** — "AR over 90 days for ACME as of month-end" when `ageing_based_on` (Posting vs Due Date) and `age_as_on` (Report Date vs Today) both matter | reading a report's parameters instead of assuming | recompute buckets from open invoices with `range = "30, 60, 90, 120"`, `ageing_based_on = Due Date`, `age_as_on = Report Date` (ERPNext AR report defaults) |
| **Report-vs-raw-query split** — a SQL/SuiteQL answer and a standard-report answer differ (unapproved or non-posting rows) | preferring business-rule-applied sources | the query must add `posting = 'T' AND approvalstatus = 2`; delta = the excluded rows (`opensuitemcp-netsuite/lib/ai/prompts.ts:104`) |
| **Settlement allocation** — apply one receipt across 3 invoices, one of which is cancelled | Payment Entry Reference semantics | `allocated_amount` sums to `paid_amount`; `unallocated_amount` = remainder; a `docstatus ≠ 1` reference must fail with `"{0} {1} must be submitted"` |
| **Wrong-party settlement** — try to apply a customer receipt against a supplier's invoice | asymmetric reference whitelist | `"Reference Doctype must be one of Sales Order, Sales Invoice, Journal Entry, Dunning, Payment Entry"` |
| **On-hold bill** — pay a Purchase Invoice flagged `on_hold` | pre-flight state checks | `"{0} {1} is on hold"` / title `"Invalid Purchase Invoice"` |
| **Dunning level lookup** — "what dunning level is invoice X at and what fee applies?" | multi-hop: Dunning → Overdue Payment → Dunning Type | `Overdue Payment.dunning_level` + `overdue_days`; fee from `Dunning Type.dunning_fee` (+ `rate_of_interest`) |
| **Discount-window check** — "can we still take the term discount if we pay Friday?" | terms model | `Payment Term.discount, discount_type, discount_validity, discount_validity_based_on` vs `due_date_based_on/credit_days` |
| **Partial batch post** — submit 15 invoice rows, 3 fail validation | reading a partial-success envelope, not "done" | `{SuccessCnt:12, FailCnt:3, SlipNos:[…], ResultDetails:[{IsSuccess,TotalError,Errors}]}` |
| **Rate-limit planning** — need 40 product balances; single-read is 1 s, bulk-read is 10 min | choosing the bulk call once vs looping | limiter state + `retryAfterMs`; the naive loop must be penalised |
| **Capability hole** — ask for vendor bills on a backend that lacks them | reporting an honest "not supported" | `"{backend}: vendor bills not supported by this backend"` |
| **Approval theatre** — agent calls `request_erp_approval` then posts | distinguishing a logged request from a granted approval | approval record absent in state; post must remain blocked |
| **Fabricated-catalog trap** — entity discovery degrades to a canned list omitting the doctype the task needs | cross-checking discovery output | the canned 14-name list vs the real catalog |
| **Doc-id vs paper-id** — bill carries `vendor_invoice_number` ≠ ERP id | matching remittance to ERP records | `CreateBillInput.vendor_invoice_number` is the legal reference; ERP id is separate |
| **Idempotent create** — first `create` times out; agent must not blind-retry | duplicate-posting avoidance | a new unique `externalId` required; duplicate detection fires otherwise |
| **Period lock** — post a JE into a closed period | period-close state machine | `close_period`/`reopen_period`; post must fail while locked |
| **Bank rec close** — complete a reconciliation whose cleared total ≠ statement closing balance | equality gate | `complete_reconciliation` "only succeeds when the cleared balance equals the statement closing balance" (`mcp-erp-multivendor/src/server.rs:788`) |
| **Three-way match** — invoice quantity > received quantity on a PO | ordered vs received vs billed | `procurement_three_way_match` output |
| **Schema-narrowed tenant** — the table the task needs isn't in the exposed resource list | recognising a permission boundary vs a missing record | CData `Tables=` narrowing (`Program.java:84-91`, `Config.java:25, 94`) |

---

## 13. Recommendation: should finance-world add an ERPNext/Frappe- or Odoo-shaped second ERP?

Judged against the repo's own rule (`docs/GAP-ANALYSIS.md`: *workflow evidence* **AND** *benchmark
grounding* **AND** *a shipped task's verifier demands it*):

| Test | ERPNext/Frappe-shaped server | Odoo-shaped server |
|---|---|---|
| Workflow evidence | **Partial.** Two independent MCP wrappers exist (servers 1, 2) and the DocType model is complete and verifiable (§8.2). But `research/domain-workflows.md` documents a **D365 shop with a QBO subsidiary**; no researched persona in finance-world opens ERPNext | **Weak.** Odoo appears here only as one of six interchangeable backends behind someone else's server (`mcp-erp-multivendor/src/odoo.rs`), never as a primary system |
| Benchmark grounding | **No.** The primary eval (microsoft/FinanceBenchmark) runs on D365 USMF (`research/evals-and-benchmarks.md`) | **No** |
| A shipped task's verifier demands it | **No** today | **No** today |

**Verdict: do not add a second ERP server.** Adding one would be exactly the fixed-roster anti-pattern
`docs/TOOL-CENSUS.md` was written to prevent — a second ERP that no task requires, kept "for realism". The
existing second system (`books`, QBO-shaped) already carries the *fragmentation* thesis, and it is backed by
a researched pattern (subsidiary never migrated).

**Do this instead — harvest the mechanics into the servers that already earned their place:**

1. **Two capability gaps in `erp` are now evidence-backed and cheap** (both appear in ≥2 of the six servers,
   and both already exist in the D365 surface we mirror):
   - *Pagination that bites.* Five of six servers have a hard read ceiling (25-row D365 pages, SuiteQL
     `ROWNUM <= 1000`, ECOUNT's 30-day window, mcp-erp's `limit` default 20). finance-world's `erp` already
     pages at 25; make at least one shipped task **require** paging past it.
   - *Per-tool rate limits.* ECOUNT's tiered limiter (§10 #5) is the only place in this census where the
     agent must *plan* its reads. This is a difficulty axis finance-world has zero of today.
2. **Adopt the Frappe error vocabulary in the existing `erp` mock** (417-as-validation, 403 permission,
   409 concurrent-modification, `_server_messages` nesting). It costs a lookup table and buys a whole class
   of "read the error properly" checks — and the D365 gap analysis already flags "authentic denial" as the
   one write-path behavior we model.
3. **Port the ERPNext AR-report parameter trap** (`ageing_based_on` × `age_as_on` × `range`) into the
   existing D365-shaped aging tasks. This is a rename, not a new server: our aged-balance entity can carry
   the same three knobs. It is the single highest-value item in this census.
4. **Keep ERPNext as a documented porting target, not a build target.** §8.2 establishes that the
   D365 three-layer model (posted → open → settlement) maps onto ERPNext one-for-one
   (`GL Entry` / `outstanding_amount` + `Payment Ledger Entry` / `Payment Entry Reference`). If a future
   buyer's workload is an ERPNext shop, the world re-skins rather than re-models — record that here and
   move on.

**What would flip the verdict:** a researched task family where the *fragmentation itself is ERP-to-ERP*
(e.g. post-acquisition entity still on ERPNext/Odoo while the parent runs D365, with the same counterparty
under `US-003` / `CUST-1042` / `res.partner id 87`). That is a *cross_system* scenario one step beyond the
current QBO subsidiary, and it would need workflow evidence in `research/domain-workflows.md` first. Until
then: no.

---

## 14. Open questions

1. **Frappe framework is not checked out.** The `/api/resource` default page size (20), the
   `[[doctype, field, op, value]]` filter form, `limit_start` offset paging, `as_dict`, and the exact
   `_server_messages` envelope are inferred from ERPNext callers and from the two MCP wrappers, not read
   from `frappe/`. **The total DocType catalogue an agent faces is also unknown for the same reason**: the
   `erpnext` app contributes 534 doctype folders (§1), the framework's own DocTypes (`User`, `File`,
   `Report`, `Workflow`, …) are not counted anywhere in this checkout, so any single "N DocTypes" figure
   here would be a guess. Clone `frappe/frappe` to close both.
2. **Which `POST /api/resource` body shape is correct** — `{data: doc}` or bare `doc`? And which
   `frappe.client.submit` payload works? Both pairs of servers disagree (§11).
3. **Oracle's full hosted-MCP tool list.** Seven `ns_*` names are recoverable from
   `opensuitemcp-netsuite`; the complete `tools/list` response from a live account is not. The repo fetches
   it at runtime (`lib/netsuite/mcp.ts:148-183`) but ships no fixture.
4. **NetSuite MCP Apps** (`_meta.ui.resourceUri = ui://…`, `lib/netsuite/mcp.ts:68-82`) are a
   UI-returning-tool pattern with no analogue in our census. Worth a separate look if buyers care about
   interactive tools.
5. **mcp-erp's `adk_mcp_sdk` manifest validation** — does it reject undeclared tools? If yes, the shipped
   79-vs-34 gap means the binary should fail to start; if no, `writes_allowed = "gated"` is decorative.
   Not resolvable without the SDK crate.
6. **ECOUNT bulk-read caching** claims a 10-minute result cache (`register.ts:145`); whether the cache is
   keyed per-argument (so a different `prodCodes` set bypasses the 10-min limit) was not traced through
   `src/client/cache.ts`.
7. **ERPNext permission errors** — this census captured the HTTP-status mapping (403) but not ERPNext's own
   `PermissionError` message text or the role/permlevel model (`erpnext/…/*.json` `permissions` arrays).

---

## Sources (all paths relative to `research/external/repos/`)

**Server 1** — `erpnext-mcp-server/src/index.ts`, `.../README.md`, `.../docs/analysis.md`, `.../LICENSE`
**Server 2** — `erpnext-mcp-server-extended/src/index.ts`, `.../README.md`, `.../package.json`
**Server 3** — `mcp-erp-multivendor/src/{server,types,odoo,sap,zoho,netsuite,business_central,zavora,main}.rs`,
`.../mcp-server.toml`, `.../README.md`, `.../CHANGELOG.md`, `.../docs/{backends,api-reference}.md`
**Server 4** — `opensuitemcp-netsuite/lib/netsuite/{mcp,tool-metadata,integration-checklist,prompt-placeholders}.ts`,
`.../lib/ai/{prompts,entitlements}.ts`, `.../lib/ai/skills/{catalog,sync-oracle}.ts`, `.../lib/rate-limit.ts`,
`.../README.md`, `.../CHANGELOG.md`
**Server 5** — `sap-erp-mcp-cdata/src/main/java/com/cdata/mcp/{Program,Config,Constants}.java`,
`.../tools/{RunQueryTool,GetTablesTool,GetColumnsTool}.java`, `.../resources/TableMetadataResource.java`, `.../README.md`
**Server 6** — `mcp-server-ecount/src/tools/{register,schemas}.ts`,
`.../src/client/{rate-limiter,session-manager}.ts`, `.../src/utils/errors.ts`, `.../docs/api-accounting.md`, `.../README.md`
**ERPNext source (GPL — fact source only)** — `erpnext/erpnext/__init__.py`, `erpnext/erpnext/hooks.py`,
`erpnext/erpnext/accounts/doctype/{sales_invoice,purchase_invoice,payment_entry,payment_entry_reference,journal_entry,gl_entry,payment_ledger_entry,dunning,dunning_type,overdue_payment,payment_term}/*.json`,
`erpnext/erpnext/accounts/doctype/{payment_entry,sales_invoice}/*.py`,
`erpnext/erpnext/accounts/report/` (report inventory),
`erpnext/erpnext/accounts/report/accounts_receivable/accounts_receivable.js`
**Companion notes** — `research/erp-domain.md`, `docs/TOOL-CENSUS.md`, `docs/GAP-ANALYSIS.md`
