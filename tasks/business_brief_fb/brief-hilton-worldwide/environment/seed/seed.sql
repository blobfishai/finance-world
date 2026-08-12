-- business_brief_fb: Hilton Worldwide is also a customer of USMF.
-- Half the brief subjects carry real internal exposure and half carry none, so the
-- "do we already trade with them?" field cannot be answered without querying the ERP
-- (docs/AUDIT.md A11). Account id uses the reserved BRF- prefix so generated world
-- data can never squat on it (A14). SIMULATION ONLY.
INSERT OR REPLACE INTO erp_customers
  (account, dataareaid, name, customer_group, currency, payment_term, cash_disc_code,
   credit_max, credit_rating, on_hold, city, state, contact_name, contact_email, phone) VALUES
  ('BRF-16','USMF','Hilton Worldwide','30','USD','Net30',NULL,500000,'Good','Open',
   'Redmond','WA','A. Reyes','ar@brf-sim.example','555-0116');

INSERT INTO erp_cust_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed) VALUES
  ('USMF','BRF-16','BRFV-161','BRFINV-161','Invoice','Managed services 1','2026-01-11','2026-02-11','USD',17163,0,0),
  ('USMF','BRF-16','BRFV-162','BRFINV-162','Invoice','Managed services 1','2026-01-12','2026-02-12','USD',8747,0,0),
  ('USMF','BRF-16','BRFV-163','BRFINV-163','Invoice','Managed services 2','2026-02-13','2026-03-13','USD',18529,0,0);
