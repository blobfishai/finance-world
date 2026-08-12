-- business_brief_fb: American Airlines Group is also a customer of USMF.
-- Half the brief subjects carry real internal exposure and half carry none, so the
-- "do we already trade with them?" field cannot be answered without querying the ERP
-- (docs/AUDIT.md A11). Account id uses the reserved BRF- prefix so generated world
-- data can never squat on it (A14). SIMULATION ONLY.
INSERT OR REPLACE INTO erp_customers
  (account, dataareaid, name, customer_group, currency, payment_term, cash_disc_code,
   credit_max, credit_rating, on_hold, city, state, contact_name, contact_email, phone) VALUES
  ('BRF-20','USMF','American Airlines Group','30','USD','Net30',NULL,500000,'Good','Open',
   'Redmond','WA','A. Reyes','ar@brf-sim.example','555-0120');

INSERT INTO erp_cust_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed) VALUES
  ('USMF','BRF-20','BRFV-201','BRFINV-201','Invoice','Managed services 1','2026-01-11','2026-02-11','USD',12844,0,0),
  ('USMF','BRF-20','BRFV-202','BRFINV-202','Invoice','Managed services 1','2026-01-12','2026-02-12','USD',11236,0,0),
  ('USMF','BRF-20','BRFV-203','BRFINV-203','Invoice','Managed services 2','2026-02-13','2026-03-13','USD',18052,0,0);
