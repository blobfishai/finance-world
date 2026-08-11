-- clear the shared ledger's rows for this counterparty so the task owns its truth
DELETE FROM erp_cust_trans WHERE account='SYNCUS-0002';
-- Adventure Works Cycles' current USMF open items (task-owned so the answer survives
-- any regeneration of the shared ledger).
INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('USMF','SYNCUS-0002','AWCV-01','AWC-3301','Invoice','Fleet order Q4','2025-12-02','2026-01-01','USD',52400.00,0,0),
  ('USMF','SYNCUS-0002','AWCV-02','AWC-3302','Invoice','Accessories restock','2026-01-19','2026-02-18','USD',28349.19,0,0),
  ('USMF','SYNCUS-0002','AWCV-03','AWC-3303','Invoice','February parts order','2026-02-11','2026-03-13','USD',14000.00,0,0);
