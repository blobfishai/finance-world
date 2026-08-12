-- agentic-labs/erp-bench scenario 2266: Ceiling Acoustic Baffle
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r09DC3E1EE3_c01','Baseline Chambers','customer',0,1351.79,NULL,NULL,'orders@baselinechambers.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r09DC3E1EE3_c02','Chrome Boutique','customer',0,3870.93,NULL,NULL,'orders@chromeboutique.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r09DC3E1EE3_c03','Granite Institute','customer',0,3068.93,NULL,NULL,'orders@graniteinstitute.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r09DC3E1EE3_c04','Spectra Lyceum','customer',0,4201.74,NULL,NULL,'orders@spectralyceum.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r09DC3E1EE3_q01','Riverdale Warehouse','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r09DC3E1EE3_q02','Arc Wholesalers','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r09DC3E1EE3_q03','Polar Carriers','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r09DC3E1EE3_q04','Anvil Operations','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P09DC3E1EE3-SPP-CAB-002','Ceiling Acoustic Baffle','Office Systems','consu',316.44,182.45,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P09DC3E1EE3-SPP-CAB-002','r09DC3E1EE3_q01','Priority Shuttle lane (7d transit, 5-8 units)',7,5.0,8.0,230.99);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P09DC3E1EE3-SPP-CAB-002','r09DC3E1EE3_q02','Express Air lane (3d transit, 4-17 units)',3,4.0,17.0,316.88);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P09DC3E1EE3-SPP-CAB-002','r09DC3E1EE3_q03','Bulk Container lane (19d transit, 25-26 units)',19,25.0,26.0,120.9);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'P09DC3E1EE3-SPP-CAB-002','r09DC3E1EE3_q04','Bulk Container lane (20d transit, 23-30 units)',20,23.0,30.0,125.6);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P09DC3E1EE3-SPP-CAB-002',NULL,29.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r09DC3E1EE3_c01','P09DC3E1EE3-SPP-CAB-002',4,6,1351.79,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r09DC3E1EE3_c02','P09DC3E1EE3-SPP-CAB-002',11,7,3870.93,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r09DC3E1EE3_c03','P09DC3E1EE3-SPP-CAB-002',9,7,3068.93,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r09DC3E1EE3_c04','P09DC3E1EE3-SPP-CAB-002',12,8,4201.74,NULL);
