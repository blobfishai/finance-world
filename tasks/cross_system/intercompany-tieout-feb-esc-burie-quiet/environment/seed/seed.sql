INSERT INTO erp_customers VALUES
  ('IC-001','USMF','CES Direct LLC (intercompany)','95','USD','Net30',NULL,0,'Good','Open',
   'Seattle','WA','Dana','dana.kim@contoso-sim.example','206-555-0133');

INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('USMF','IC-001','ICV-01','ICINV-01','Invoice','Shared services allocation Q4','2026-01-10','2026-02-09','USD',30000.00,0,0),
  ('USMF','IC-001','ICV-02','ICINV-02','Invoice','Inventory transfer January','2026-02-05','2026-03-07','USD',24000.00,0,0),
  ('USMF','IC-001','ICV-03','ICINV-03','Invoice','February management fee','2026-02-27','2026-03-29','USD',22500.00,0,0);
