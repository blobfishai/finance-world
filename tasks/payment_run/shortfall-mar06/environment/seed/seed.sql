-- payment_run/shortfall-mar06 — the Friday run that cannot be fully funded.
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M1 write-and-approve · M2 unsatisfiable demand
-- (77/300 ERP-Bench tasks are unsat_demand; the correct plan necessarily rejects) ·
-- M3 objective non-collapse (the naive earliest-due-first answer differs from the graded
-- one) · M4 money re-derivation (discounts are recomputed, never read back) ·
-- M5 a hard constraint that exists only in an unstructured document (the dispute is in
-- email; nothing in the ERP marks PINV-104).
--
-- Sourced: SAP F110 payment proposals + Corpay positive-pay (research/external/articles/
-- payment-runs-early-pay-discount--*), and the discount-capture policy in
-- research/domain-workflows.md §2. SIMULATION ONLY.

-- Cash is the binding constraint. Eligible net is 307,800.00 against 190,000.00 available.
UPDATE erp_bank_accounts SET available_balance = 190000.00, as_of = '2026-03-06T08:00:00Z'
 WHERE bank_account = 'USMF-OPER';

INSERT OR REPLACE INTO erp_vendors
  (account, dataareaid, name, vendor_group, currency, payment_term, cash_disc_code,
   payment_method, on_hold, city, state, contact_name, contact_email, phone) VALUES
 ('PVEN-01','USMF','Northwind Paper Supply','PAYRUN','USD','Net30','2%10N30','ELECTRONIC','Open','Reno','NV','Dale Ortiz','ap@northwind-sim.example','555-0111'),
 ('PVEN-02','USMF','Contoso Freight Lines','PAYRUN','USD','Net30',NULL,'ELECTRONIC','Open','Fresno','CA','Mei Lin','ap@cfl-sim.example','555-0112'),
 ('PVEN-03','USMF','Litware Facility Services','PAYRUN','USD','Net30',NULL,'ELECTRONIC','Yes','Tucson','AZ','Sam Boyd','ar@litware-sim.example','555-0113'),
 ('PVEN-04','USMF','Fabrikam Print & Signage','PAYRUN','USD','Net30',NULL,'ELECTRONIC','Open','Boise','ID','Ana Reyes','billing@fabrikam-sim.example','555-0114'),
 ('PVEN-05','USMF','Tailspin Security Systems','PAYRUN','USD','Net30',NULL,'ELECTRONIC','Open','Denver','CO','Lee Park','ar@tailspin-sim.example','555-0115'),
 ('PVEN-06','USMF','Adatum Catering Co','PAYRUN','USD','Net30','2%10N30','ELECTRONIC','Open','Austin','TX','Ruth Vance','ap@adatum-sim.example','555-0116');

-- Seven open obligations, all due on or before the 2026-03-06 pay date.
-- Discount windows are trans_date + 10 days (code 2%10N30): PINV-101 -> 2026-03-10,
-- PINV-106 -> 2026-03-11. Both close before the NEXT run (2026-03-13), which is what the
-- SOP's first priority turns on.
INSERT INTO erp_vend_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed, cash_disc_code, po_number) VALUES
 ('USMF','PVEN-01','PVENV-9101','PINV-101','Invoice','Paper & janitorial supplies Feb','2026-02-28','2026-03-04','USD',60000.00,0,0,'2%10N30',NULL),
 ('USMF','PVEN-02','PVENV-9102','PINV-102','Invoice','Inbound freight Feb','2026-02-01','2026-03-02','USD',45000.00,0,0,NULL,NULL),
 ('USMF','PVEN-03','PVENV-9103','PINV-103','Invoice','Facility cleaning Feb','2026-02-03','2026-03-05','USD',30000.00,0,0,NULL,NULL),
 ('USMF','PVEN-04','PVENV-9104','PINV-104','Invoice','Trade show signage','2026-02-04','2026-03-06','USD',25000.00,0,0,NULL,NULL),
 ('USMF','PVEN-05','PVENV-9105','PINV-105','Invoice','Badge readers + monitoring Q1','2026-01-30','2026-03-01','USD',80000.00,0,0,NULL,NULL),
 ('USMF','PVEN-06','PVENV-9106','PINV-106','Invoice','Onsite catering Feb','2026-03-01','2026-03-06','USD',50000.00,0,0,'2%10N30',NULL),
 ('USMF','PVEN-01','PVENV-9107','PINV-107','Invoice','Toner & print consumables','2026-02-05','2026-03-06','USD',20000.00,0,0,NULL,NULL);
