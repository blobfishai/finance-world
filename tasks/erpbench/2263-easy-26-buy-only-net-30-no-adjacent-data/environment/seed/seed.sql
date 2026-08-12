-- agentic-labs/erp-bench scenario 2263: Desktop Privacy Screen
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r97D7104FD3_c01','Brookfield Research','customer',0,228.14,NULL,NULL,'orders@brookfieldresearch.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r97D7104FD3_c02','Westfield Media','customer',0,705.02,NULL,NULL,'orders@westfieldmedia.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r97D7104FD3_c03','Horizon Supply Co','customer',0,2804.76,NULL,NULL,'orders@horizonsupplyco.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r97D7104FD3_c04','Orbital Enterprises','customer',0,890.36,NULL,NULL,'orders@orbitalenterprises.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r97D7104FD3_q01','Riverdale Materials','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r97D7104FD3_q02','Grove Transit','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r97D7104FD3_q03','Sierra Warehousing','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P97D7104FD3-SPP-DPS-005','Desktop Privacy Screen','Office Systems','consu',209.99,121.26,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P97D7104FD3-SPP-DPS-005','r97D7104FD3_q01','Priority Shuttle lane (6d transit, 5-11 units)',6,5.0,11.0,114.56);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P97D7104FD3-SPP-DPS-005','r97D7104FD3_q02','Express Air lane (5d transit, 2-18 units)',5,2.0,18.0,148.97);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P97D7104FD3-SPP-DPS-005','r97D7104FD3_q03','Regional Cross-Dock lane (8d transit, 5-19 units)',8,5.0,19.0,104.51);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P97D7104FD3-SPP-DPS-005',NULL,17.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r97D7104FD3_c01','P97D7104FD3-SPP-DPS-005',1,6,228.14,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r97D7104FD3_c02','P97D7104FD3-SPP-DPS-005',3,6,705.02,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r97D7104FD3_c03','P97D7104FD3-SPP-DPS-005',12,8,2804.76,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r97D7104FD3_c04','P97D7104FD3-SPP-DPS-005',4,9,890.36,NULL);
