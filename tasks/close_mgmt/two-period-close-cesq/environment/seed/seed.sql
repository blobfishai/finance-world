INSERT INTO erp_companies VALUES('CESQ','CES Quarterly Services LLC (SIMULATED)');
INSERT INTO erp_vendors VALUES
  ('CESQ-V1','CESQ','Tundra Facilities','30','USD','Net30',NULL,'CHECK','No','Fargo','ND','Wren','wren@tundra-sim.example','701-555-0180');
INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('CESQ','CESQ-V1','QV-01','QINV-001','Invoice','January facilities services','2026-01-10','2026-02-09','USD',12000.00,0,0),
  ('CESQ','CESQ-V1','QV-02','QINV-002','Invoice','January late-posted repair','2026-01-28','2026-02-27','USD',1800.00,0,0),
  ('CESQ','CESQ-V1','QV-03','QINV-003','Invoice','February facilities services','2026-02-25','2026-03-27','USD',3200.00,0,0);
