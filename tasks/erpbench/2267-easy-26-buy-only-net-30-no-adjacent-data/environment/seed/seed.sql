-- agentic-labs/erp-bench scenario 2267: Freestanding Sound Divider
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r34F91039C2_c01','Catalyst Works','customer',0,1969.19,NULL,NULL,'orders@catalystworks.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r34F91039C2_c02','Vantage Alliance','customer',0,7489.8,NULL,NULL,'orders@vantagealliance.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r34F91039C2_c03','Gateway Studios','customer',0,1902.09,NULL,NULL,'orders@gatewaystudios.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r34F91039C2_c04','Brookfield Forum','customer',0,3657.78,NULL,NULL,'orders@brookfieldforum.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r34F91039C2_q01','Nimbus Partners','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r34F91039C2_q02','Solace Manufacturing','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r34F91039C2_q03','Silverline Wholesalers','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P34F91039C2-SPP-FSD-003','Freestanding Sound Divider','Office Systems','consu',593.23,315.2,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P34F91039C2-SPP-FSD-003','r34F91039C2_q01','Priority Shuttle lane (6d transit, 7-20 units)',6,7.0,20.0,327.22);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P34F91039C2-SPP-FSD-003','r34F91039C2_q02','Express Air lane (3d transit, 3-13 units)',3,3.0,13.0,485.97);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P34F91039C2-SPP-FSD-003','r34F91039C2_q03','Economy Ocean lane (17d transit, 8-23 units)',17,8.0,23.0,312.33);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P34F91039C2-SPP-FSD-003',NULL,20.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r34F91039C2_c01','P34F91039C2-SPP-FSD-003',3,6,1969.19,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r34F91039C2_c02','P34F91039C2-SPP-FSD-003',12,7,7489.8,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r34F91039C2_c03','P34F91039C2-SPP-FSD-003',3,7,1902.09,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r34F91039C2_c04','P34F91039C2-SPP-FSD-003',6,8,3657.78,NULL);
