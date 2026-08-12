-- agentic-labs/erp-bench scenario 2264: Door Seal Acoustic Kit
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r143D3DE0A2_c01','Mosaic Advisory','customer',0,192.39,NULL,NULL,'orders@mosaicadvisory.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r143D3DE0A2_c02','Alloy Agency','customer',0,1399.7,NULL,NULL,'orders@alloyagency.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r143D3DE0A2_c03','Oxide Innovations','customer',0,2278.95,NULL,NULL,'orders@oxideinnovations.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r143D3DE0A2_c04','Cobalt Academy','customer',0,2322.34,NULL,NULL,'orders@cobaltacademy.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r143D3DE0A2_q01','Millbrook Fulfillment','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r143D3DE0A2_q02','Lance Exporters','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r143D3DE0A2_q03','Steel Partners','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r143D3DE0A2_q04','Arbor Resources','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P143D3DE0A2-SPP-DSK-007','Door Seal Acoustic Kit','Office Systems','consu',185.43,112.45,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P143D3DE0A2-SPP-DSK-007','r143D3DE0A2_q01','Priority Shuttle lane (6d transit, 13-13 units)',6,13.0,13.0,97.75);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P143D3DE0A2-SPP-DSK-007','r143D3DE0A2_q02','Express Air lane (3d transit, 5-5 units)',3,5.0,5.0,147.02);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P143D3DE0A2-SPP-DSK-007','r143D3DE0A2_q03','Bulk Container lane (20d transit, 26-26 units)',20,26.0,26.0,68.92);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'P143D3DE0A2-SPP-DSK-007','r143D3DE0A2_q04','Bulk Container lane (21d transit, 19-19 units)',21,19.0,19.0,56.44);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P143D3DE0A2-SPP-DSK-007',NULL,27.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r143D3DE0A2_c01','P143D3DE0A2-SPP-DSK-007',1,6,192.39,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r143D3DE0A2_c02','P143D3DE0A2-SPP-DSK-007',7,7,1399.7,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r143D3DE0A2_c03','P143D3DE0A2-SPP-DSK-007',12,7,2278.95,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r143D3DE0A2_c04','P143D3DE0A2-SPP-DSK-007',12,9,2322.34,NULL);
