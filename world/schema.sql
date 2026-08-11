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
