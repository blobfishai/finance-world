-- Wingtip Toys (SYNVEN-0027) already exists in the master; give it the AP contact used
-- for correspondence, the unreferenced invoice, and the PO the vendor will cite.
UPDATE erp_vendors SET contact_email='ap@wingtip-sim.example', contact_name='Lee'
 WHERE account='SYNVEN-0027';
INSERT OR REPLACE INTO erp_purch_orders VALUES
  ('PO-7003',1,'USMF','SYNVEN-0027','PKG-LABEL-ROLL','Packaging label rolls',200,18.50,'2026-02-01','Open');
INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, po_number)
VALUES ('USMF','SYNVEN-0027','TWV-303','TWINV-303','Invoice','Packaging supplies - no PO reference on document','2026-02-20','2026-03-22','USD',3700.00,0,0,NULL);
