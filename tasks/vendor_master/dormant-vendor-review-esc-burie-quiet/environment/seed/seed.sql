-- vendor_master/dormant-vendor-review — dormant is not the same as unused.
--
-- Closes tracked coverage gap `art.vendor_dormancy` (sim/coverage.py): "vendor master +
-- transaction history support it; needs a task and a hygiene policy doc".
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M3 non-collapse — the naive filter "no activity in
-- 12 months" sweeps in a never-used vendor and one already on hold, and SOP-AP-11 excludes
-- both · M5 the distinction lives only in the policy document, not in any ERP field.
--
-- Sourced: BEC/dormant-account exposure in research/external/articles/
-- vendor-master-bec-fraud--{afp-truist,fbi-ic3,wa-state-auditor}.md. Review date is the
-- world epoch 2026-03-02, so the 12-month cutoff is 2025-03-02. SIMULATION ONLY.

INSERT OR REPLACE INTO erp_vendors
  (account, dataareaid, name, vendor_group, currency, payment_term, cash_disc_code,
   payment_method, on_hold, city, state, contact_name, contact_email, phone) VALUES
 ('DVEN-01','USMF','Cascade Industrial Supply','REVIEW','USD','Net30',NULL,'ELECTRONIC','Open','Tacoma','WA','Rae Molina','ar@cascade-sim.example','555-0141'),
 ('DVEN-02','USMF','Harbor Point Logistics','REVIEW','USD','Net30',NULL,'ELECTRONIC','Open','Mobile','AL','Sana Iqbal','ar@harborpoint-sim.example','555-0142'),
 ('DVEN-03','USMF','Redstone Calibration Labs','REVIEW','USD','Net30',NULL,'ELECTRONIC','Open','Huntsville','AL','Tom Vega','ar@redstone-sim.example','555-0143'),
 ('DVEN-04','USMF','Vermillion Safety Consultants','REVIEW','USD','Net30',NULL,'ELECTRONIC','Open','Fargo','ND','Ingrid Sol','ar@vermillion-sim.example','555-0144'),
 ('DVEN-05','USMF','Beacon Uniform Services','REVIEW','USD','Net30',NULL,'ELECTRONIC','Open','Akron','OH','Paul Ng','ar@beacon-sim.example','555-0145'),
 ('DVEN-06','USMF','Kestrel Metal Finishing','REVIEW','USD','Net30',NULL,'ELECTRONIC','Yes','Erie','PA','Dot Ames','ar@kestrel-sim.example','555-0146');

INSERT INTO erp_vend_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed, cash_disc_code, po_number) VALUES
 -- DVEN-01: current. Not dormant.
 ('USMF','DVEN-01','DVENV-01','DINV-101','Invoice','Shop consumables Feb','2026-02-10','2026-03-12','USD',4200.00,0,0,NULL,NULL),
 ('USMF','DVEN-01','DVENV-02','DINV-100','Invoice','Shop consumables Jan','2026-01-08','2026-02-07','USD',3900.00,3900.00,1,NULL,NULL),
 -- DVEN-02: last activity 2024-11-15. DORMANT.
 ('USMF','DVEN-02','DVENV-03','DINV-201','Invoice','Drayage - Gulf lane','2024-11-15','2024-12-15','USD',15600.00,15600.00,1,NULL,NULL),
 -- DVEN-03: last INVOICE 2024-12-02, but a credit note in 2025-01-20 is still contact.
 -- Both precede the 2025-03-02 cutoff, so it is DORMANT either way - and an agent that
 -- measures from invoices only still gets this one right, which is deliberate: the
 -- measure-from-any-transaction rule is tested by DVEN-05, not here.
 ('USMF','DVEN-03','DVENV-04','DINV-301','Invoice','Annual gauge calibration','2024-12-02','2025-01-01','USD',8800.00,8800.00,1,NULL,NULL),
 ('USMF','DVEN-03','DVENV-05','DCN-301','CreditNote','Calibration rework credit','2025-01-20','2025-01-20','USD',-1200.00,-1200.00,1,NULL,NULL),
 -- DVEN-05: last INVOICE 2024-10-04 (before the cutoff) but a PAYMENT on 2025-09-30 is
 -- contact with the counterparty and falls AFTER it. Not dormant - unless you measure
 -- from invoices only, which the policy forbids.
 ('USMF','DVEN-05','DVENV-06','DINV-501','Invoice','Uniform rental FY25','2024-10-04','2024-11-03','USD',6100.00,6100.00,1,NULL,NULL),
 ('USMF','DVEN-05','DVENV-07','DPAY-501','Payment','Payment - DINV-501','2025-09-30','2025-09-30','USD',-6100.00,-6100.00,1,NULL,NULL),
 -- DVEN-06: last activity 2024-08-01 and already on hold. Actioned, out of scope.
 ('USMF','DVEN-06','DVENV-08','DINV-601','Invoice','Anodising batch','2024-08-01','2024-08-31','USD',9450.00,9450.00,1,NULL,NULL);
 -- DVEN-04 deliberately has NO transactions: unused, not dormant.
