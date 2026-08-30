INSERT OR REPLACE INTO erp_vendors
  (account,dataareaid,name,vendor_group,currency,payment_term,cash_disc_code,payment_method,on_hold,city,state,contact_name,contact_email,phone)
VALUES
  ('FA-V701','USMF','Northstar Industrial Controls','CAPEX','USD','Net30',NULL,'ELECTRONIC','Open','Milwaukee','WI','Iris Cole','billing@northstar-controls-sim.example','555-0701');

INSERT OR REPLACE INTO erp_purch_orders
  (po_number,line,dataareaid,vendor,item,description,qty_ordered,unit_price,order_date,status)
VALUES
  ('PO-L7-701',1,'USMF','FA-V701','LINE7-RETROFIT','Line 7 controls retrofit final scope',1,390000.00,'2026-01-19','received');

INSERT OR REPLACE INTO erp_product_receipts
  (receipt_id,po_number,line,receipt_date,qty_received)
VALUES ('PR-L7-701','PO-L7-701',1,'2026-02-24',1);

INSERT OR REPLACE INTO erp_vend_trans
  (id,dataareaid,account,voucher,invoice,txn_type,description,trans_date,due_date,currency,amount,settled,closed,cash_disc_code,po_number)
VALUES
  (90701,'USMF','FA-V701','APV-L7-701','PINV-L7-701','Invoice','Line 7 controls retrofit - final scope rev 2','2026-02-24','2026-03-26','USD',390000.00,0,0,NULL,'PO-L7-701');

INSERT OR REPLACE INTO erp_finance_cases
  (case_id,task_id,workflow,subject,status,decision_code,evidence_refs,rationale,owner,opened_at,decided_at)
VALUES
  ('FA-L7-2026','fixed_assets/line7-capitalization','fixed_asset_capitalization','Line 7 controls retrofit','open',NULL,NULL,NULL,NULL,'2026-02-26T15:10:00Z',NULL);
