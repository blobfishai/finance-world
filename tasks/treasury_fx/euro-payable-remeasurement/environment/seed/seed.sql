INSERT OR REPLACE INTO erp_vendors
  (account,dataareaid,name,vendor_group,currency,payment_term,cash_disc_code,payment_method,on_hold,city,state,contact_name,contact_email,phone)
VALUES
  ('EUR-V250','USMF','Lumina Robotics GmbH','EQUIPMENT','EUR','Net30',NULL,'WIRE','Open','Munich',NULL,'Anja Weiss','ar@lumina-robotics-sim.example','+49-89-555-0250');

INSERT OR REPLACE INTO erp_vend_trans
  (id,dataareaid,account,voucher,invoice,txn_type,description,trans_date,due_date,currency,amount,settled,closed,cash_disc_code,po_number)
VALUES
  (90250,'USMF','EUR-V250','APV-EUR-250','PINV-EUR-250','Invoice','Robotics cell; EUR 250000 initially recorded at 1.08 USD/EUR (USD 270000)','2026-02-10','2026-03-10','EUR',250000.00,0,0,NULL,'PO-EUR-250');

INSERT OR REPLACE INTO erp_fx_rates(from_ccy,to_ccy,rate_date,rate) VALUES
  ('EUR','USD','2026-02-10',1.08),
  ('EUR','USD','2026-02-27',1.10),
  ('EUR','USD','2026-02-28',1.12),
  ('EUR','USD','2026-03-02',1.11);

INSERT OR REPLACE INTO erp_finance_cases
  (case_id,task_id,workflow,subject,status,decision_code,evidence_refs,rationale,owner,opened_at,decided_at)
VALUES
  ('FX-EUR-2026','treasury_fx/euro-payable-remeasurement','fx_remeasurement','Lumina Robotics EUR payable','open',NULL,NULL,NULL,NULL,'2026-02-28T18:05:00Z',NULL);
