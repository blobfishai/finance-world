-- cash_app/deduction-coding-mar — code the short-pay from the evidence, not the narrative.
--
-- Closes tracked coverage gaps `art.deduction_coding` and `fb.erp.deductions`.
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M3 non-collapse (coding by the customer's stated
-- reason gets two of four wrong) · M4 the amounts are re-derived from the order and the
-- contract, never read off the remittance · M5 the governing evidence sits in documents and
-- email while the ERP holds only the number.
--
-- Sourced: research/external/articles/cash-application--{highradius,stuut,zamp}.md — a
-- deduction is coded, routed to an owner, and either conceded or charged back; 46% of teams
-- cite unapplied/uncoded cash as their top AR problem (research/domain-workflows.md).
-- SIMULATION ONLY.

INSERT OR REPLACE INTO erp_customers
  (account, dataareaid, name, customer_group, currency, payment_term, cash_disc_code,
   credit_max, credit_rating, on_hold, city, state, contact_name, contact_email, phone)
SELECT 'CDED-01','USMF','Copper Ridge Retail','30','USD','Net30',NULL,250000,'A','Open','Boise','ID','Nils Andersen','ap@copperridge-sim.example','555-0151'
UNION ALL SELECT 'CDED-02','USMF','Sable & Finch Markets','30','USD','Net30',NULL,150000,'A','Open','Madison','WI','Perla Ruiz','ap@sablefinch-sim.example','555-0152'
UNION ALL SELECT 'CDED-03','USMF','Marlow Grocers','30','USD','Net30',NULL,120000,'B','Open','Dover','DE','Kwame Osei','ap@marlow-sim.example','555-0153'
UNION ALL SELECT 'CDED-04','USMF','Ninebark Supply Co','30','USD','Net30',NULL,90000,'C','Open','Bend','OR','Tessa Groot','ap@ninebark-sim.example','555-0154';

-- Four invoices, each short-paid. `settled` carries what the customer actually paid; the
-- open remainder IS the deduction.
INSERT INTO erp_cust_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed, cash_disc_code, disputed, deduction, payment_method) VALUES
 ('USMF','CDED-01','CDEDV-01','CINV-701','Invoice','Audio panels + freight - PO CR-PO-8841','2026-02-02','2026-03-04','USD',40000.00,37600.00,0,NULL,0,1,'ELECTRONIC'),
 ('USMF','CDED-02','CDEDV-02','CINV-702','Invoice','Q1 promotional shipment','2026-02-05','2026-03-07','USD',18000.00,16200.00,0,NULL,0,1,'ELECTRONIC'),
 ('USMF','CDED-03','CDEDV-03','CINV-703','Invoice','Weekly replenishment wk06','2026-02-06','2026-03-08','USD',25000.00,24850.00,0,NULL,0,1,'ELECTRONIC'),
 ('USMF','CDED-04','CDEDV-04','CINV-704','Invoice','Fixtures order','2026-02-09','2026-03-11','USD',12000.00,9000.00,0,NULL,0,1,'ELECTRONIC');
