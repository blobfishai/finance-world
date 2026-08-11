-- close_mgmt/period-lock-correction — the correction that cannot go where it belongs.
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M1 write-and-approve (this one actually posts,
-- exercising the full propose -> confirm -> post path) · M3 non-collapse (the obvious
-- answer, "book it in January where the error is", is refused by the ERP) · M5 the period
-- calendar diverges from the calendar month, so the destination must be READ, not assumed.
--
-- Closes the tracked coverage gap `erpnext.period_close_lock` (sim/coverage.py): "needs a
-- period-status table so writes into a closed period are refused".
--
-- Core ships 2025-12 closed, 2026-01 closed, 2026-02 on_hold, 2026-03 open. The error is in
-- January (closed); February is mid-close (on_hold, explicitly not a parking space); so the
-- only lawful destination is March. SIMULATION ONLY.

-- The mis-coded January charge: a software subscription booked to travel & entertainment.
INSERT INTO erp_ledger_journals
  (journal_id, dataareaid, voucher, voucher_type, description, user_remark, posting_date,
   period_id, currency, total_debit, total_credit, difference, state, created_by, created_at,
   posted_by, posted_at)
VALUES
 ('GJ-00900','USMF','GJ-00900','Journal Entry',
  'January vendor invoice coding - Northwind analytics subscription','', '2026-01-22',
  '2026-01','USD',8400.00,8400.00,0.0,'posted','accountant','2026-01-22T10:00:00Z',
  'accountant','2026-01-22T10:00:00Z');

INSERT INTO erp_ledger_journal_lines
  (journal_id, line, account_code, description, debit, credit, currency, fx_rate,
   party_type, party, dimension_dept) VALUES
 ('GJ-00900',1,'600300','Analytics subscription (MIS-CODED to T&E)',8400.00,0,'USD',1.0,NULL,NULL,'IT'),
 ('GJ-00900',2,'200100','Accounts payable',0,8400.00,'USD',1.0,'Vendor','PVEN-11',NULL);
