-- Legal entity CESP (CES Programs LLC) with a small, fully-controlled AR/AP book.
INSERT INTO erp_companies VALUES('CESP','CES Programs LLC (SIMULATED)');

INSERT INTO erp_customers VALUES
  ('CESP-C1','CESP','Woodgrove Studios','10','USD','Net30',NULL,100000,'Good','Open',
   'Portland','OR','Ari','ari@woodgrove-sim.example','503-555-0111'),
  ('CESP-C2','CESP','Relecloud Events','10','USD','Net30',NULL,100000,'Good','Open',
   'Denver','CO','Sky','sky@relecloud-sim.example','303-555-0122');
INSERT INTO erp_vendors VALUES
  ('CESP-V1','CESP','Proseware Staging','30','USD','Net30',NULL,'ELECTRONIC','No',
   'Reno','NV','Kai','kai@proseware-sim.example','775-555-0133'),
  ('CESP-V2','CESP','Wingtip Logistics','30','USD','Net30',NULL,'CHECK','No',
   'Boise','ID','Lee','lee@wingtip-sim.example','208-555-0144');

INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('CESP','CESP-C1','CFV-A1','CFAR-01','Invoice','Program fees March','2026-02-03','2026-03-05','USD',42000.00,0,0),
  ('CESP','CESP-C2','CFV-A2','CFAR-02','Invoice','Event services','2026-02-10','2026-03-12','USD',35500.00,0,0),
  ('CESP','CESP-C1','CFV-A3','CFAR-03','Invoice','Program fees April prepay','2026-02-16','2026-03-18','USD',51000.00,0,0);

INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('CESP','CESP-V1','CFV-P1','CFAP-01','Invoice','Stage buildout','2026-02-02','2026-03-04','USD',28000.00,0,0),
  ('CESP','CESP-V2','CFV-P2','CFAP-02','Invoice','Freight February','2026-02-09','2026-03-11','USD',19500.00,0,0),
  ('CESP','CESP-V1','CFV-P3','CFAP-03','Invoice','AV equipment rental','2026-02-23','2026-03-25','USD',33000.00,0,0);
