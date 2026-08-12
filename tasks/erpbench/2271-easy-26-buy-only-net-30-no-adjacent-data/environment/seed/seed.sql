-- agentic-labs/erp-bench scenario 2271: Under-Desk Sound Shield
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rFF7D4DAF03_c01','Oxide Office','customer',0,1507.15,NULL,NULL,'orders@oxideoffice.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rFF7D4DAF03_c02','Grove Research','customer',0,2957.88,NULL,NULL,'orders@groveresearch.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rFF7D4DAF03_c03','Nexus Observatory','customer',0,484.03,NULL,NULL,'orders@nexusobservatory.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('rFF7D4DAF03_c04','Peak Bazaar','customer',0,2911.65,NULL,NULL,'orders@peakbazaar.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rFF7D4DAF03_q01','Aegis Shipping','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rFF7D4DAF03_q02','Quartz Operations','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rFF7D4DAF03_q03','Millbrook Networks','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('rFF7D4DAF03_q04','Stonewall Logistics','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('PFF7D4DAF03-SPP-USS-009','Under-Desk Sound Shield','Office Systems','consu',233.21,144.87,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'PFF7D4DAF03-SPP-USS-009','rFF7D4DAF03_q01','Priority Shuttle lane (6d transit, 5-31 units)',6,5.0,31.0,121.59);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'PFF7D4DAF03-SPP-USS-009','rFF7D4DAF03_q02','Express Air lane (3d transit, 5-17 units)',3,5.0,17.0,172.64);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'PFF7D4DAF03-SPP-USS-009','rFF7D4DAF03_q03','Bulk Container lane (16d transit, 21-22 units)',16,21.0,22.0,78.06);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'PFF7D4DAF03-SPP-USS-009','rFF7D4DAF03_q04','Microfactory Build-to-Order lane (4d transit, 6-31 units)',4,6.0,31.0,152.39);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('PFF7D4DAF03-SPP-USS-009',NULL,26.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'rFF7D4DAF03_c01','PFF7D4DAF03-SPP-USS-009',6,5,1507.15,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'rFF7D4DAF03_c02','PFF7D4DAF03-SPP-USS-009',12,7,2957.88,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'rFF7D4DAF03_c03','PFF7D4DAF03-SPP-USS-009',2,9,484.03,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'rFF7D4DAF03_c04','PFF7D4DAF03-SPP-USS-009',12,9,2911.65,NULL);
