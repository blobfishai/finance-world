-- Wingtip Logistics as a USMF vendor with the unreferenced invoice, and PO-7003 on file.
INSERT OR REPLACE INTO erp_vendors VALUES
  ('SYNVEN-0011','USMF','Wingtip Logistics','20','USD','Net30',NULL,'ELECTRONIC','No',
   'Boise','ID','Lee','ap@wingtip-sim.example','208-555-0144');
INSERT OR REPLACE INTO erp_purch_orders VALUES
  ('PO-7003',1,'USMF','SYNVEN-0011','PKG-LABEL-ROLL','Packaging label rolls',200,18.50,'2026-02-01','Open');
INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, po_number)
VALUES ('USMF','SYNVEN-0011','TWV-303','TWINV-303','Invoice','Packaging supplies - no PO reference on document','2026-02-20','2026-03-22','USD',3700.00,0,0,NULL);
