-- PO-8101 legacy ledger: 100 x 32.00 = 3,200.00; invoiced 3,240.00 -> variance 40.00 (BLOCKS: unmaintained key = zero tolerance)
-- PO-8102 new ledger:    150 x 21.00 = 3,150.00; invoiced 3,465.00 -> variance 315.00 (PASSES: blank limit = unlimited)
INSERT OR REPLACE INTO erp_purch_orders VALUES
  ('PO-8101',1,'USMF','SYNVEN-0003','BRACKET-STD','Standard brackets (legacy ledger)',100,32.00,'2026-01-15','Received'),
  ('PO-8102',1,'USMF','SYNVEN-0007','CRATE-LT','Light crates (new ledger)',150,21.00,'2026-01-20','Received');
INSERT INTO erp_product_receipts VALUES
  ('PR-9101','PO-8101',1,'2026-02-02',100),
  ('PR-9102','PO-8102',1,'2026-02-04',150);
INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, po_number)
VALUES
  ('USMF','SYNVEN-0003','TDV-401','TDINV-401','Invoice','Brackets per PO-8101 (legacy ledger)','2026-02-10','2026-03-12','USD',3240.00,0,0,'PO-8101'),
  ('USMF','SYNVEN-0007','TDV-402','TDINV-402','Invoice','Crates per PO-8102 (new ledger)','2026-02-12','2026-03-14','USD',3465.00,0,0,'PO-8102');
