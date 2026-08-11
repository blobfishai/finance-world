-- 3-way match fixtures. TWINV-301 clean; TWINV-302 price variance (+$6/unit x 50 = $300);
-- TWINV-303 quantity variance (billed 200, received 160 -> 40 units over-billed).
INSERT INTO erp_purch_orders VALUES
  ('PO-7001', 1, 'USMF', 'SYNVEN-0003', 'SKI-RACK-STD', 'Standard ski racks', 100, 45.00, '2026-01-20', 'Received'),
  ('PO-7002', 1, 'USMF', 'SYNVEN-0007', 'WINE-CRATE-OAK', 'Oak wine crates', 50, 120.00, '2026-01-25', 'Received'),
  ('PO-7003', 1, 'USMF', 'SYNVEN-0011', 'PKG-LABEL-ROLL', 'Packaging label rolls', 200, 18.50, '2026-02-01', 'Partially received');

INSERT INTO erp_product_receipts VALUES
  ('PR-8101', 'PO-7001', 1, '2026-02-05', 100),
  ('PR-8102', 'PO-7002', 1, '2026-02-08', 50),
  ('PR-8103', 'PO-7003', 1, '2026-02-12', 120),
  ('PR-8104', 'PO-7003', 1, '2026-02-19', 40);

INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, po_number)
VALUES
  ('USMF','SYNVEN-0003','TWV-301','TWINV-301','Invoice','Standard ski racks per PO-7001','2026-02-10','2026-03-12','USD',4500.00,0,0,'PO-7001'),
  ('USMF','SYNVEN-0007','TWV-302','TWINV-302','Invoice','Oak wine crates per PO-7002','2026-02-12','2026-03-14','USD',6300.00,0,0,'PO-7002'),
  ('USMF','SYNVEN-0011','TWV-303','TWINV-303','Invoice','Packaging label rolls per PO-7003','2026-02-20','2026-03-22','USD',3700.00,0,0,'PO-7003');
