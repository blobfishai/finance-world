-- agentic-labs/erp-bench scenario 2262: Open-Plan Noise Barrier Wall
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rF3119DF4C3_c01','Nimbus Bureau','customer',0,5926.83,NULL,NULL,'orders@nimbusbureau.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rF3119DF4C3_c02','Clearwater Collective','customer',0,3060.14,NULL,NULL,'orders@clearwatercollective.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rF3119DF4C3_c03','Flint Analytics','customer',0,8637.73,NULL,NULL,'orders@flintanalytics.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rF3119DF4C3_c04','Spark Archive','customer',0,9245.16,NULL,NULL,'orders@sparkarchive.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rF3119DF4C3_q01','Marble Movers','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rF3119DF4C3_q02','Alpine Assemblies','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rF3119DF4C3_q03','Monarch Commodities','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rF3119DF4C3_q04','Chrome Provisions','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('PF3119DF4C3-SPP-NBW-010','Open-Plan Noise Barrier Wall','Office Systems','consu',695.22,403.03,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'PF3119DF4C3-SPP-NBW-010','rF3119DF4C3_q01','Priority Shuttle lane (7d transit, 10-14 units)',7,10.0,14.0,400.18);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'PF3119DF4C3-SPP-NBW-010','rF3119DF4C3_q02','Express Air lane (3d transit, 1-35 units)',3,1.0,35.0,504.73);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'PF3119DF4C3-SPP-NBW-010','rF3119DF4C3_q03','Bulk Container lane (17d transit, 25-35 units)',17,25.0,35.0,268.47);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'PF3119DF4C3-SPP-NBW-010','rF3119DF4C3_q04','Air Charter lane (3d transit, 1-35 units)',3,1.0,35.0,557.08);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('PF3119DF4C3-SPP-NBW-010',NULL,29.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'rF3119DF4C3_c01','PF3119DF4C3-SPP-NBW-010',8,6,5926.83,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'rF3119DF4C3_c02','PF3119DF4C3-SPP-NBW-010',4,6,3060.14,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'rF3119DF4C3_c03','PF3119DF4C3-SPP-NBW-010',12,6,8637.73,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'rF3119DF4C3_c04','PF3119DF4C3-SPP-NBW-010',12,9,9245.16,NULL);
