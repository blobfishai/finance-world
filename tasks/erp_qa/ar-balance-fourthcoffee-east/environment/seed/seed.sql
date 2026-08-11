-- Fourth Coffee East's current open items (task-owned, so the balance survives any
-- regeneration of the shared ledger). Seven other 'Fourth Coffee *' accounts exist.
INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('USMF','SYNCUS-0069','FCEV-01','FCE-2201','Invoice','Q1 wholesale beans order','2025-11-03','2025-12-03','USD',36319.23,0,0),
  ('USMF','SYNCUS-0069','FCEV-02','FCE-2202','Invoice','Store fit-out supplies','2026-01-14','2026-02-13','USD',48255.68,0,0),
  ('USMF','SYNCUS-0069','FCEV-03','FCE-2203','Invoice','February roast delivery','2026-02-05','2026-03-07','USD',23841.80,0,0),
  ('USMF','SYNCUS-0069','FCEV-04','FCE-2204','Invoice','Equipment servicing','2026-02-18','2026-03-20','USD',12904.55,0,0);
