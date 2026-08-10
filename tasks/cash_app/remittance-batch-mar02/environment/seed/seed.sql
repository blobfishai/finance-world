INSERT INTO erp_customers VALUES
  ('US-021','USMF','Lamna Healthcare Company','20','USD','Net30',NULL,150000,'Good','Open',
   'Austin','TX','Devi','devi@lamna-sim.example','512-555-0177');

INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('USMF','US-021','LHV-001','LHINV-001','Invoice','January platform fees','2026-01-15','2026-02-14','USD',18000.00,0,0),
  ('USMF','US-021','LHV-002','LHINV-002','Invoice','January usage overage','2026-01-20','2026-02-19','USD',9500.00,0,0),
  ('USMF','US-021','LHV-003','LHINV-003','Invoice','February platform fees','2026-02-15','2026-03-17','USD',6200.00,0,0),
  ('USMF','US-021','LHV-004','LHINV-004','Invoice','February usage overage','2026-02-20','2026-03-22','USD',11000.00,0,0);
