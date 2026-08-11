-- Lamna Healthcare: LHINV-001 (18,000) settled by LHPAY-77 on 2026-02-24; LHINV-002 (9,500)
-- and LHINV-003 (7,700) remain open. The 2026-03-01 bank file returns LHPAY-77, so
-- LHINV-001 reopens: true open = 9,500 + 7,700 + 18,000 = 35,200.
INSERT INTO erp_customers VALUES
  ('US-021','USMF','Lamna Healthcare Company','20','USD','Net30',NULL,150000,'Good','Open',
   'Austin','TX','Devi','devi@lamna-sim.example','512-555-0177');
INSERT INTO erp_cust_trans (id, dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  (930001,'USMF','US-021','LHV-001','LHINV-001','Invoice','January platform fees','2026-01-15','2026-02-14','USD',18000.00,18000.00,1),
  (930002,'USMF','US-021','LHV-002','LHINV-002','Invoice','January usage overage','2026-01-20','2026-02-19','USD',9500.00,0,0),
  (930003,'USMF','US-021','LHV-003','LHINV-003','Invoice','February platform fees','2026-02-15','2026-03-17','USD',7700.00,0,0),
  (930004,'USMF','US-021','LHV-077','LHPAY-77','Payment','ACH receipt - applied to LHINV-001','2026-02-24','2026-02-24','USD',-18000.00,-18000.00,1);
INSERT INTO erp_settlements (side, dataareaid, account, payment_id, invoice_id, amount, cash_disc_taken, settle_date)
VALUES ('AR','USMF','US-021',930004,930001,18000.00,0,'2026-02-24');
