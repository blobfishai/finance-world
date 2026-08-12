-- agentic-labs/erp-bench scenario 2270: Freestanding Sound Divider
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r3E1953B69E_c01','Jade Collective East','customer',0,4240.55,NULL,NULL,'orders@jadecollectiveeast.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r3E1953B69E_c02','Trident Workshop','customer',0,7216.16,NULL,NULL,'orders@tridentworkshop.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r3E1953B69E_c03','Lakewood Manufactory','customer',0,612.98,NULL,NULL,'orders@lakewoodmanufactory.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r3E1953B69E_c04','Garnet Media','customer',0,7688.89,NULL,NULL,'orders@garnetmedia.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r3E1953B69E_q01','Riverdale Packagers','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r3E1953B69E_q02','Thornton Holdings','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r3E1953B69E_q03','Ember Microfactory','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r3E1953B69E_q04','Horizon Haulage','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P3E1953B69E-SPP-FSD-003','Freestanding Sound Divider','Office Systems','consu',583.05,368.31,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P3E1953B69E-SPP-FSD-003','r3E1953B69E_q01','Priority Shuttle lane (7d transit, 5-29 units)',7,5.0,29.0,327.54);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P3E1953B69E-SPP-FSD-003','r3E1953B69E_q02','Express Air lane (5d transit, 3-31 units)',5,3.0,31.0,489.29);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P3E1953B69E-SPP-FSD-003','r3E1953B69E_q03','Bulk Container lane (19d transit, 19-23 units)',19,19.0,23.0,221.89);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'P3E1953B69E-SPP-FSD-003','r3E1953B69E_q04','Regional Cross-Dock lane (10d transit, 5-6 units)',10,5.0,6.0,288.19);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P3E1953B69E-SPP-FSD-003',NULL,27.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r3E1953B69E_c01','P3E1953B69E-SPP-FSD-003',7,7,4240.55,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r3E1953B69E_c02','P3E1953B69E-SPP-FSD-003',12,7,7216.16,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r3E1953B69E_c03','P3E1953B69E-SPP-FSD-003',1,7,612.98,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r3E1953B69E_c04','P3E1953B69E-SPP-FSD-003',12,8,7688.89,NULL);
