INSERT OR REPLACE INTO erp_customers
  (account,dataareaid,name,customer_group,currency,payment_term,cash_disc_code,credit_max,credit_rating,on_hold,city,state,contact_name,contact_email,phone)
VALUES
  ('NW-HS-480','USMF','Northwind Health Systems','ENTERPRISE','USD','Net30',NULL,750000.00,'A','Open','Minneapolis','MN','Talia Brooks','ap@northwind-health-sim.example','555-0480');

INSERT OR REPLACE INTO erp_sales_orders
  (sales_id,dataareaid,account,customer_name,order_date,status,hold_code,responsible,amount)
VALUES
  ('SO-NW-480','USMF','NW-HS-480','Northwind Health Systems','2026-02-03','Delivered',NULL,'Riley Stone',480000.00);

INSERT OR REPLACE INTO erp_cust_trans
  (id,dataareaid,account,voucher,invoice,txn_type,description,trans_date,due_date,currency,amount,settled,closed,cash_disc_code,disputed,deduction,payment_method)
VALUES
  (90480,'USMF','NW-HS-480','ARV-NW-480','INV-NW-480','Invoice','Edge appliance and twelve-month managed support bundle','2026-02-28','2026-03-30','USD',480000.00,0,0,NULL,0,0,'WIRE');

INSERT OR REPLACE INTO erp_finance_cases
  (case_id,task_id,workflow,subject,status,decision_code,evidence_refs,rationale,owner,opened_at,decided_at)
VALUES
  ('REV-NW-2026','revenue_accounting/northwind-contract-allocation','revenue_allocation','Northwind bundled appliance and support','open',NULL,NULL,NULL,NULL,'2026-02-28T17:15:00Z',NULL);
