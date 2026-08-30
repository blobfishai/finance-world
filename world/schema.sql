-- finance-world state schema. One SQLite file per task run; every MCP server sees only its namespace.
-- Epoch/world clock lives in meta (WORLD_NOW). SIMULATION ONLY.

CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);

-- ============ ERP (Dynamics-365-Finance-shaped, legal entity USMF) ============
CREATE TABLE erp_companies(dataareaid TEXT PRIMARY KEY, name TEXT);
CREATE TABLE erp_payment_terms(code TEXT PRIMARY KEY, days INTEGER, description TEXT);
CREATE TABLE erp_cash_disc(code TEXT PRIMARY KEY, percent REAL, days INTEGER, next_code TEXT, description TEXT);
CREATE TABLE erp_customers(
  account TEXT PRIMARY KEY, dataareaid TEXT, name TEXT, customer_group TEXT,
  currency TEXT, payment_term TEXT, cash_disc_code TEXT, credit_max REAL,
  credit_rating TEXT, on_hold TEXT, city TEXT, state TEXT,
  contact_name TEXT, contact_email TEXT, phone TEXT);
CREATE TABLE erp_vendors(
  account TEXT PRIMARY KEY, dataareaid TEXT, name TEXT, vendor_group TEXT,
  currency TEXT, payment_term TEXT, cash_disc_code TEXT, payment_method TEXT,
  on_hold TEXT, city TEXT, state TEXT, contact_name TEXT, contact_email TEXT, phone TEXT);
-- Posted subledger. Open remainder = amount - settled where closed=0 (three-layer model).
CREATE TABLE erp_cust_trans(
  id INTEGER PRIMARY KEY, dataareaid TEXT, account TEXT, voucher TEXT, invoice TEXT,
  txn_type TEXT, description TEXT, trans_date TEXT, due_date TEXT, currency TEXT,
  amount REAL, settled REAL DEFAULT 0, closed INTEGER DEFAULT 0, cash_disc_code TEXT,
  disputed INTEGER DEFAULT 0, deduction INTEGER DEFAULT 0, payment_method TEXT);
CREATE TABLE erp_vend_trans(
  id INTEGER PRIMARY KEY, dataareaid TEXT, account TEXT, voucher TEXT, invoice TEXT,
  txn_type TEXT, description TEXT, trans_date TEXT, due_date TEXT, currency TEXT,
  amount REAL, settled REAL DEFAULT 0, closed INTEGER DEFAULT 0, cash_disc_code TEXT,
  po_number TEXT);
-- Procurement (3-way match surface: PO -> product receipt -> vendor invoice).
CREATE TABLE erp_purch_orders(
  po_number TEXT, line INTEGER, dataareaid TEXT, vendor TEXT, item TEXT, description TEXT,
  qty_ordered REAL, unit_price REAL, order_date TEXT, status TEXT,
  PRIMARY KEY(po_number, line));
CREATE TABLE erp_product_receipts(
  receipt_id TEXT, po_number TEXT, line INTEGER, receipt_date TEXT, qty_received REAL,
  PRIMARY KEY(receipt_id, po_number, line));
CREATE TABLE erp_settlements(
  id INTEGER PRIMARY KEY, side TEXT, dataareaid TEXT, account TEXT,
  payment_id INTEGER, invoice_id INTEGER, amount REAL, cash_disc_taken REAL DEFAULT 0,
  settle_date TEXT);
CREATE TABLE erp_collection_letters(
  id INTEGER PRIMARY KEY, dataareaid TEXT, account TEXT, letter_code TEXT,
  letter_date TEXT, status TEXT, fee REAL, note TEXT);
-- Sales orders (SalesTable): status, hold codes, responsible worker.
CREATE TABLE erp_sales_orders(
  sales_id TEXT PRIMARY KEY, dataareaid TEXT, account TEXT, customer_name TEXT,
  order_date TEXT, status TEXT, hold_code TEXT, responsible TEXT, amount REAL);
-- Collections activities/tasks (SmmActivities) and collections pools (CustPool).
CREATE TABLE erp_activities(
  activity_id TEXT PRIMARY KEY, dataareaid TEXT, account TEXT, activity_type TEXT,
  purpose TEXT, start_date TEXT, end_date TEXT, closed INTEGER DEFAULT 0, responsible TEXT);
CREATE TABLE erp_collection_pools(pool_id TEXT PRIMARY KEY, name TEXT, criteria TEXT);
CREATE TABLE erp_customer_pool(account TEXT PRIMARY KEY, pool_id TEXT);
-- Methods of payment (CustPaymModeTable/VendPaymModeTable) and their payment accounts.
CREATE TABLE erp_methods_of_payment(
  method TEXT, side TEXT, dataareaid TEXT, description TEXT, payment_account TEXT,
  PRIMARY KEY(method, side));
-- Form-tool runtime state (mirrors the real server's per-session view models; SQL-backed).
CREATE TABLE erp_form_sessions(form_id TEXT PRIMARY KEY, form TEXT, state TEXT);
-- Batch aging snapshot (the "second truth"; may lawfully diverge from live bucketing).
CREATE TABLE erp_aging_snapshot(
  run_id TEXT, as_of TEXT, dataareaid TEXT, account TEXT, name TEXT,
  not_due REAL, b1_30 REAL, b31_60 REAL, b61_90 REAL, b90_plus REAL, total_due REAL,
  PRIMARY KEY(run_id, account));

-- ============ Subsidiary books: CES Direct LLC (QuickBooks-Online-shaped) ============
CREATE TABLE books_customers(id TEXT PRIMARY KEY, display_name TEXT, erp_ref TEXT, email TEXT);
CREATE TABLE books_invoices(
  id TEXT PRIMARY KEY, customer_id TEXT, doc_number TEXT, txn_date TEXT, due_date TEXT,
  amount REAL, balance REAL, status TEXT, memo TEXT);
CREATE TABLE books_credit_memos(
  id TEXT PRIMARY KEY, customer_id TEXT, doc_number TEXT, txn_date TEXT,
  amount REAL, remaining REAL, memo TEXT);
CREATE TABLE books_payments(
  id TEXT PRIMARY KEY, customer_id TEXT, txn_date TEXT, amount REAL,
  applied_to_invoice TEXT, method TEXT, memo TEXT);

-- ============ Shadow spreadsheets ============
CREATE TABLE sheet_files(name TEXT PRIMARY KEY, owner TEXT, modified_at TEXT, description TEXT);
CREATE TABLE sheet_rows(file TEXT, row_no INTEGER, cells TEXT, PRIMARY KEY(file, row_no));

-- ============ Email (read-only inbox) ============
CREATE TABLE email_messages(
  id TEXT PRIMARY KEY, folder TEXT, from_addr TEXT, to_addr TEXT, subject TEXT,
  sent_at TEXT, body TEXT, attachment_name TEXT, attachment_text TEXT);

-- Scripted counterparties: deterministic replies when the agent sends mail.
CREATE TABLE email_npc_scripts(
  id TEXT PRIMARY KEY, match_to TEXT, match_keywords TEXT, reply_from TEXT,
  reply_subject TEXT, reply_body TEXT, attachment_name TEXT, attachment_text TEXT);

-- ============ Filings (SEC-EDGAR-shaped frozen snapshots) ============
CREATE TABLE filings_companies(cik TEXT PRIMARY KEY, ticker TEXT, name TEXT);
CREATE TABLE filings_facts(
  cik TEXT, concept TEXT, unit TEXT, fy TEXT, fp TEXT, period_end TEXT,
  value REAL, form TEXT, filed TEXT, accession TEXT);
CREATE TABLE filings_documents(cik TEXT, form TEXT, filed TEXT, accession TEXT, title TEXT, excerpt TEXT);

-- ============ Document store (policies/SOPs; every body starts "> SIMULATION ONLY") ============
CREATE TABLE docs_documents(
  doc_id TEXT PRIMARY KEY, title TEXT, doc_type TEXT, version TEXT,
  effective_date TEXT, body TEXT);

-- ============ Harness (answers are state; verified deterministically) ============
CREATE TABLE answers(field TEXT PRIMARY KEY, value TEXT, submitted_at TEXT);

-- The reporting contract: what this task requires filed, and in what shape.
--
-- This used to be stapled onto the end of the human's message ("Reply with `submit_answer`:
-- - `dormant_count` (number) ..."), which no colleague would ever type and which handed the
-- model the decomposition for free — being told to report `overpayment_usd` AND
-- `underpayment_usd` separately reveals there are two directions of error before you look.
--
-- It belongs where it belongs in a real deployment: on the reporting tool. The harness server
-- exposes it through `reporting_fields`, so the agent discovers the contract by inspecting the
-- system, exactly as it would any other API, and the prompt is free to be a message.
CREATE TABLE answer_schema(
  ordinal INTEGER, field TEXT PRIMARY KEY, type TEXT, description TEXT);

-- ============ Write-and-approve surface (hard layer M1/M2/M7) ============
-- Chart of accounts (Odoo account.account / ERPNext Account). account_type vocabulary is
-- Odoo's, truncated: asset_receivable, asset_cash, asset_current, liability_payable,
-- liability_current, equity, income, expense, off_balance.
CREATE TABLE erp_main_accounts(
  account_code TEXT PRIMARY KEY, dataareaid TEXT, name TEXT, account_type TEXT,
  currency TEXT, blocked INTEGER DEFAULT 0, reconcilable INTEGER DEFAULT 0,
  requires_dimension TEXT);

-- Fiscal periods / period lock (Odoo company lock dates; mcp-erp close_period/reopen_period).
CREATE TABLE erp_fiscal_periods(
  period_id TEXT PRIMARY KEY, dataareaid TEXT, period_start TEXT, period_end TEXT,
  status TEXT DEFAULT 'open');            -- open | on_hold | closed

-- GL journal header. state: Odoo account.move.state (draft/posted/cancel), one-way draft->posted.
-- voucher_type: ERPNext Journal Entry.voucher_type subset. reversed_entry_id: Odoo
-- account.move.reversed_entry_id / ERPNext Journal Entry.reversal_of.
CREATE TABLE erp_ledger_journals(
  journal_id TEXT PRIMARY KEY, dataareaid TEXT, voucher TEXT, voucher_type TEXT,
  description TEXT, user_remark TEXT, posting_date TEXT, period_id TEXT, currency TEXT,
  total_debit REAL DEFAULT 0, total_credit REAL DEFAULT 0, difference REAL DEFAULT 0,
  state TEXT DEFAULT 'draft',
  reversed_entry_id TEXT, reversal_reason TEXT,
  created_by TEXT, created_at TEXT, posted_by TEXT, posted_at TEXT,
  source_doc_id TEXT);                    -- the docs_documents row the amounts derive from (M4)

-- GL journal lines (Odoo account.move.line debit/credit/balance; mcp-erp PostJournalInput.lines).
CREATE TABLE erp_ledger_journal_lines(
  journal_id TEXT, line INTEGER, account_code TEXT, description TEXT,
  debit REAL DEFAULT 0, credit REAL DEFAULT 0, currency TEXT, fx_rate REAL DEFAULT 1,
  party_type TEXT, party TEXT, dimension_dept TEXT,
  PRIMARY KEY(journal_id, line));

-- Delegation of authority (ERPNext Authorization Rule: transaction/based_on/value/
-- system_role/approving_role/company). company-scoped rules SHADOW global rules.
CREATE TABLE erp_approval_policies(
  policy_id TEXT PRIMARY KEY, dataareaid TEXT, doc_type TEXT,
  based_on TEXT DEFAULT 'Grand Total', threshold_amount REAL, currency TEXT,
  applies_to_role TEXT, approving_role TEXT, approving_user TEXT,
  escalation_policy_id TEXT, active INTEGER DEFAULT 1);

-- Approval inbox (ERPNext AuthorizationControl outcome, materialised as a queue).
CREATE TABLE erp_approval_requests(
  request_id TEXT PRIMARY KEY, dataareaid TEXT, doc_type TEXT, doc_id TEXT,
  amount REAL, currency TEXT, submitted_by TEXT, submitted_at TEXT, note TEXT,
  policy_id TEXT, required_role TEXT,
  status TEXT DEFAULT 'pending',          -- pending | approved | rejected | withdrawn
  decided_by TEXT, decided_at TEXT, decision_reason TEXT);

-- Bank cash position: the constraint that makes M2 bite.
CREATE TABLE erp_bank_accounts(
  bank_account TEXT PRIMARY KEY, dataareaid TEXT, name TEXT, currency TEXT,
  available_balance REAL, as_of TEXT, overdraft_limit REAL DEFAULT 0);

-- Payment run header (ERPNext Payment Order; D365 payment proposal).
-- period_option: D365 method-of-payment Period (Invoice | Date | Total).
CREATE TABLE erp_payment_runs(
  run_id TEXT PRIMARY KEY, dataareaid TEXT, pay_date TEXT, bank_account TEXT, currency TEXT,
  period_option TEXT DEFAULT 'Invoice',
  cash_available REAL, eligible_net REAL, total_paid REAL, total_rejected REAL,
  state TEXT DEFAULT 'proposed',          -- proposed | committed | cancelled
  created_by TEXT, created_at TEXT, approved_by TEXT, committed_at TEXT);

-- Payment run lines: BOTH halves of the partition, one row each.
-- reason_code enum from erpnext/accounts/bulk_payment.py::_partition_payable_invoices
-- plus Vendor On Hold / Discount Window Expired / Awaiting Approval / Insufficient Cash.
CREATE TABLE erp_payment_run_lines(
  run_id TEXT, line INTEGER, invoice TEXT, vendor TEXT, due_date TEXT,
  gross_amount REAL, discount_taken REAL DEFAULT 0, withholding REAL DEFAULT 0,
  net_amount REAL, disposition TEXT, reason_code TEXT, reason TEXT, priority_rank INTEGER,
  PRIMARY KEY(run_id, line));

-- FX rates: without these, M4 cannot re-derive any cross-currency amount
-- (odoo-domain.md §8 gap #15 — we have a currency column and no rate table).
CREATE TABLE erp_fx_rates(
  from_ccy TEXT, to_ccy TEXT, rate_date TEXT, rate REAL,
  PRIMARY KEY(from_ccy, to_ccy, rate_date));

-- Two-phase confirm-gate token store. RUNTIME state: never graded, never readable as an entity.
CREATE TABLE erp_confirm_tokens(
  token TEXT PRIMARY KEY, seq INTEGER, action TEXT, actor TEXT, role TEXT,
  target_id TEXT, args_hash TEXT, effect_preview TEXT, minted_at TEXT,
  consumed_at TEXT, superseded_by TEXT);

-- Audit trail (mcp-erp get_erp_audit_trail; odoo-ai-agent GET /chat/{id}/audit).
-- Derived from the graded writes; excluded from the state veto, assertable by row_count.
CREATE TABLE erp_audit_trail(
  audit_id INTEGER PRIMARY KEY, entity_type TEXT, entity_id TEXT, action TEXT,
  actor TEXT, role TEXT, at TEXT, before_json TEXT, after_json TEXT);

-- Task-scoped finance work items.  This is exposed through the ordinary D365
-- FinanceCases data entity for reads and a governed ICustomAPI action for the
-- decision transition.  It is deliberately not a benchmark-only convenience
-- tool: agents discover and call it through the same generic Dynamics MCP
-- surfaces as any other customer extension.
CREATE TABLE erp_finance_cases(
  case_id TEXT PRIMARY KEY, task_id TEXT UNIQUE, workflow TEXT, subject TEXT,
  status TEXT, decision_code TEXT, evidence_refs TEXT, rationale TEXT,
  owner TEXT, opened_at TEXT, decided_at TEXT);

-- Documents in scope for a finance case (the FinanceCaseLines data entity): the
-- control requirement is derived by summing these amounts, never read off a header.
-- Seeded per case by the release builder, which also creates the table on demand so
-- a core world built before this revision still serves it.
CREATE TABLE erp_finance_case_lines(
  case_id TEXT, line INTEGER, document_ref TEXT, description TEXT, amount REAL,
  currency TEXT, control_basis TEXT, PRIMARY KEY(case_id, line));

-- Deduction / short-pay reason codes (art.deduction_coding). Vocabulary follows AR
-- cash-application practice: research/external/articles/cash-application--{highradius,stuut,
-- zamp}.md — a deduction is coded, routed to an owner, and either conceded or charged back.
CREATE TABLE erp_deduction_reasons(
  reason_code TEXT PRIMARY KEY, description TEXT, valid_claim INTEGER,
  owner TEXT, disposition TEXT);

-- Withholding tax (erpnext.withholding_tax). ERPNext models this as Tax Withholding
-- Category + rates with a cumulative threshold; the vendor-side profile carries the
-- exemption certificate and its expiry, which is what actually decides whether we withhold.
CREATE TABLE erp_withholding_tax(
  tax_category TEXT PRIMARY KEY, description TEXT, rate_pct REAL,
  threshold_amount REAL DEFAULT 0, statutory_ref TEXT);

CREATE TABLE erp_vendor_tax_profile(
  account TEXT PRIMARY KEY, tax_category TEXT, certificate_type TEXT,
  certificate_on_file INTEGER DEFAULT 0, certificate_expiry TEXT, notes TEXT);

-- ═══ Procure-to-pay / make-or-buy surface (agentic-labs/erp-bench, 300 tasks) ═══
--
-- ERP-Bench ships each task as a Harbor dir that boots a real Odoo 19 in Docker and grades it
-- with odoolib queries against the live server. The plumbing does not port; the JUDGEMENT does,
-- because `environment/scenario_data.json` is a fully DECLARATIVE world spec — partners with
-- budgets, products with per-vendor min/max/price offers, BOMs, workcenters, stock and existing
-- orders. So the scenario seeds our world and the grading becomes deterministic state diffs
-- (docs/PARITY.md, docs/INGESTION.md `needs_surface` -> built).
--
-- These tables are EMPTY in core by design. Each ERP-Bench scenario is its own small world, so
-- it arrives through the per-task seed layer rather than the shared ledger — the same mechanic
-- that already carries every other task's chaos.

CREATE TABLE erpb_partners(
  ref TEXT PRIMARY KEY, name TEXT, kind TEXT,              -- kind: customer | vendor
  supplier_rank INTEGER DEFAULT 0, budget_dollars REAL, credit_limit REAL,
  payment_term TEXT, email TEXT,
  comment TEXT);          -- Odoo "Internal Notes": several tasks hide the binding
                          -- max-order-quantity rule here and nowhere else

CREATE TABLE erpb_products(
  code TEXT PRIMARY KEY, name TEXT, category TEXT, type TEXT,
  list_price REAL, standard_price REAL,
  routes TEXT,            -- csv of {buy, manufacture}: whether make-or-buy is even a choice
  comment TEXT);

CREATE TABLE erpb_vendor_offers(
  id INTEGER PRIMARY KEY, product_code TEXT, partner_ref TEXT, name TEXT,
  delay INTEGER,          -- lead time in days, against the order's due date
  min_qty REAL, max_qty REAL,   -- horizon-wide totals, NOT per-line minimums
  price REAL);

CREATE TABLE erpb_boms(
  id INTEGER PRIMARY KEY, product_code TEXT, type TEXT, quantity REAL, warehouse_code TEXT);
CREATE TABLE erpb_bom_components(
  bom_id INTEGER, component_code TEXT, quantity REAL);

CREATE TABLE erpb_workcenters(
  code TEXT PRIMARY KEY, name TEXT, capacity_per_day REAL, cost_per_hour REAL,
  warehouse_code TEXT, comment TEXT);

CREATE TABLE erpb_stock(
  product_code TEXT, warehouse_code TEXT, quantity REAL, location_type TEXT);

-- The demand named in the instruction: who wants how many, by when, under what budget cap.
CREATE TABLE erpb_demand(
  id INTEGER PRIMARY KEY, partner_ref TEXT, product_code TEXT, units REAL,
  due_days INTEGER, budget_cap REAL, seeded_order_state TEXT);

-- ── agent-written state: what the verifier grades ──
CREATE TABLE erpb_sale_orders(
  name TEXT PRIMARY KEY, partner_ref TEXT, state TEXT,
  commitment_date TEXT, origin TEXT);
CREATE TABLE erpb_sale_order_lines(
  id INTEGER PRIMARY KEY, order_name TEXT, product_code TEXT, qty REAL, price_unit REAL);

CREATE TABLE erpb_purchase_orders(
  name TEXT PRIMARY KEY, partner_ref TEXT, state TEXT,
  date_planned TEXT,
  origin TEXT);           -- the SO reference(s): the SO->PO lineage the tasks require
CREATE TABLE erpb_purchase_order_lines(
  id INTEGER PRIMARY KEY, order_name TEXT, product_code TEXT, qty REAL, price_unit REAL);

CREATE TABLE erpb_manufacturing_orders(
  name TEXT PRIMARY KEY, product_code TEXT, qty REAL, state TEXT,
  workcenter_code TEXT, date_planned TEXT, origin TEXT);
