-- agentic-labs/erp-bench scenario 2269: Wall-Mount Acoustic Tile Set
-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.

INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r6B4376EEC5_c01','Element Brands','customer',0,864.88,NULL,NULL,'orders@elementbrands.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r6B4376EEC5_c02','Steel Foundry','customer',0,3620.07,NULL,NULL,'orders@steelfoundry.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r6B4376EEC5_c03','Comet Bazaar','customer',0,1500.53,NULL,NULL,'orders@cometbazaar.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,budget_dollars,credit_limit,payment_term,email,comment) VALUES('r6B4376EEC5_c04','Redstone Atelier','customer',0,3628.73,NULL,NULL,'orders@redstoneatelier.io',NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r6B4376EEC5_q01','Alpine Freight','vendor',1,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r6B4376EEC5_q02','Crestview Carriers','vendor',2,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r6B4376EEC5_q03','Lumen Warehousing','vendor',3,NULL);
INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) VALUES('r6B4376EEC5_q04','Summit Haulage','vendor',4,NULL);
INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,standard_price,routes,comment) VALUES('P6B4376EEC5-SPP-WAT-004','Wall-Mount Acoustic Tile Set','Office Systems','consu',280.96,170.04,'buy',NULL);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(1,'P6B4376EEC5-SPP-WAT-004','r6B4376EEC5_q01','Priority Shuttle lane (5d transit, 11-31 units)',5,11.0,31.0,175.37);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(2,'P6B4376EEC5-SPP-WAT-004','r6B4376EEC5_q02','Express Air lane (3d transit, 4-25 units)',3,4.0,25.0,244.56);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(3,'P6B4376EEC5-SPP-WAT-004','r6B4376EEC5_q03','Bulk Container lane (18d transit, 24-31 units)',18,24.0,31.0,94.62);
INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,min_qty,max_qty,price) VALUES(4,'P6B4376EEC5-SPP-WAT-004','r6B4376EEC5_q04','Economy Ocean lane (20d transit, 12-12 units)',20,12.0,12.0,134.07);
INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) VALUES('P6B4376EEC5-SPP-WAT-004',NULL,27.0,'stock');

INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(1,'r6B4376EEC5_c01','P6B4376EEC5-SPP-WAT-004',3,5,864.88,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(2,'r6B4376EEC5_c02','P6B4376EEC5-SPP-WAT-004',12,6,3620.07,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(3,'r6B4376EEC5_c03','P6B4376EEC5-SPP-WAT-004',5,9,1500.53,NULL);
INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,seeded_order_state) VALUES(4,'r6B4376EEC5_c04','P6B4376EEC5-SPP-WAT-004',12,9,3628.73,NULL);
