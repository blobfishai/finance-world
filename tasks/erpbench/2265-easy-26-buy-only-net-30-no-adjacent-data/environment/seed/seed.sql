-- agentic-labs/erp-bench scenario 2265: Wall-Mount Acoustic Tile Set
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r07C4A84267_c01','Iron Solutions Group','customer',0,1797.11,NULL,NULL,'orders@ironsolutionsgroup.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r07C4A84267_c02','Gateway Supply Co','customer',0,2095.69,NULL,NULL,'orders@gatewaysupplyco.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r07C4A84267_c03','Alpine Studios East','customer',0,1699.31,NULL,NULL,'orders@alpinestudioseast.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r07C4A84267_c04','Borough Workspaces','customer',0,2778.55,NULL,NULL,'orders@boroughworkspaces.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r07C4A84267_q01','Crestview Distributors','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r07C4A84267_q02','Coral Exporters','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r07C4A84267_q03','Dune Components','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P07C4A84267-SPP-WAT-004','Wall-Mount Acoustic Tile Set','Office Systems','consu',276.45,154.56,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P07C4A84267-SPP-WAT-004','r07C4A84267_q01','Priority Shuttle lane (5d transit, 8-27 units)',5,8.0,27.0,159.41);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P07C4A84267-SPP-WAT-004','r07C4A84267_q02','Express Air lane (4d transit, 3-4 units)',4,3.0,4.0,226.92);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P07C4A84267-SPP-WAT-004','r07C4A84267_q03','Economy Ocean lane (15d transit, 9-21 units)',15,9.0,21.0,141.99);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P07C4A84267-SPP-WAT-004',NULL,24.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r07C4A84267_c01','P07C4A84267-SPP-WAT-004',6,5,1797.11,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r07C4A84267_c02','P07C4A84267-SPP-WAT-004',7,5,2095.69,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r07C4A84267_c03','P07C4A84267-SPP-WAT-004',6,8,1699.31,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r07C4A84267_c04','P07C4A84267-SPP-WAT-004',9,9,2778.55,NULL);
