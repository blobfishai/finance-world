-- agentic-labs/erp-bench scenario 2268: Desktop Privacy Screen
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r1EB04CD113_c01','Clearwater Designs','customer',0,2733.17,NULL,NULL,'orders@clearwaterdesigns.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r1EB04CD113_c02','Opal Advisory','customer',0,1099.25,NULL,NULL,'orders@opaladvisory.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r1EB04CD113_c03','Velocity Trust','customer',0,2727.43,NULL,NULL,'orders@velocitytrust.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r1EB04CD113_c04','Monarch Cooperative','customer',0,2427.4,NULL,NULL,'orders@monarchcooperative.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r1EB04CD113_q01','Cobalt Partners','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r1EB04CD113_q02','Zenith Solutions','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r1EB04CD113_q03','Baltic Resources','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r1EB04CD113_q04','Coral Transport','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P1EB04CD113-SPP-DPS-005','Desktop Privacy Screen','Office Systems','consu',206.64,138.13,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P1EB04CD113-SPP-DPS-005','r1EB04CD113_q01','Priority Shuttle lane (6d transit, 7-39 units)',6,7.0,39.0,120.07);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P1EB04CD113-SPP-DPS-005','r1EB04CD113_q02','Express Air lane (3d transit, 5-39 units)',3,5.0,39.0,162.7);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P1EB04CD113-SPP-DPS-005','r1EB04CD113_q03','Bulk Container lane (20d transit, 22-39 units)',20,22.0,39.0,82.9);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'P1EB04CD113-SPP-DPS-005','r1EB04CD113_q04','Scheduled Freight lane (14d transit, 10-13 units)',14,10.0,13.0,104.36);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P1EB04CD113-SPP-DPS-005',NULL,36.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r1EB04CD113_c01','P1EB04CD113-SPP-DPS-005',12,5,2733.17,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r1EB04CD113_c02','P1EB04CD113-SPP-DPS-005',5,7,1099.25,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r1EB04CD113_c03','P1EB04CD113-SPP-DPS-005',12,8,2727.43,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r1EB04CD113_c04','P1EB04CD113-SPP-DPS-005',11,9,2427.4,NULL);
