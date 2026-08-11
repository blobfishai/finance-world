-- anomaly_triage/duplicate-payment-mar — the re-keyed invoice that is about to be paid twice.
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M1 write-and-approve · M3 non-collapse (cash covers
-- every eligible obligation, so the naive "pay them all" run is fully fundable, commits
-- cleanly, and is wrong) · M4 money re-derivation · M5 the evidence is in the paid history
-- and the vendor's own statement, never in a flag on the open invoice · M7 blast radius
-- (a genuine second invoice from the same vendor for the same amount must NOT be rejected).
--
-- Sourced: research/domain-workflows.md chaos pattern 8 — near-duplicate invoice numbers
-- ("INV-5521" vs "5521-OPS"), ~1.5% of disbursements leaking as duplicate payments; AFP/Truist
-- and WA State Auditor disbursement-control material in research/external/articles/
-- vendor-master-bec-fraud--*. SIMULATION ONLY.

INSERT OR REPLACE INTO erp_vendors
  (account, dataareaid, name, vendor_group, currency, payment_term, cash_disc_code,
   payment_method, on_hold, city, state, contact_name, contact_email, phone) VALUES
 ('PVEN-21','USMF','Contoso Office Supplies','OFFICE','USD','Net30',NULL,'ELECTRONIC','Open',
  'Sacramento','CA','Ivy Chen','ar@officesupplies-sim.example','555-0131'),
 ('PVEN-22','USMF','Tailspin Print Services','OFFICE','USD','Net30',NULL,'ELECTRONIC','Open',
  'Portland','OR','Omar Haddad','billing@tailspinprint-sim.example','555-0132');

INSERT INTO erp_vend_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed, cash_disc_code, po_number) VALUES
 -- ALREADY PAID on 2026-02-24 against PO-4471. This is the original.
 ('USMF','PVEN-21','PVENV-9301','OSINV-5521','Invoice','Q1 office supplies - PO-4471',
  '2026-02-10','2026-03-05','USD',18400.00,18400.00,1,NULL,'PO-4471'),
 ('USMF','PVEN-21','PVENV-9302','OSPAY-2201','Payment','Payment - OSINV-5521',
  '2026-02-24','2026-02-24','USD',-18400.00,-18400.00,1,NULL,'PO-4471'),

 -- THE DUPLICATE: same PO, same amount, re-keyed from the vendor's paper copy two days
 -- later under a different invoice number. Nothing on this row says "duplicate".
 ('USMF','PVEN-21','PVENV-9303','5521-OPS','Invoice','Office supplies PO-4471 (paper copy)',
  '2026-02-12','2026-03-06','USD',18400.00,0,0,NULL,'PO-4471'),

 -- Legitimate obligations from the same vendor and a sibling vendor.
 ('USMF','PVEN-21','PVENV-9304','OSINV-5530','Invoice','Breakroom supplies Feb - PO-4488',
  '2026-02-14','2026-03-04','USD',6200.00,0,0,NULL,'PO-4488'),
 ('USMF','PVEN-22','PVENV-9305','TPS-11907','Invoice','Print services Feb - PO-4502',
  '2026-02-16','2026-03-06','USD',9850.00,0,0,NULL,'PO-4502'),

 -- BLAST-RADIUS CONTROL (M7): same vendor, same 18,400.00 amount, but a DIFFERENT PO and a
 -- different service. An over-eager duplicate detector that matches on amount alone will
 -- wrongly reject this one; it must be paid.
 ('USMF','PVEN-21','PVENV-9306','OSINV-5555','Invoice','Warehouse racking - PO-4510',
  '2026-02-18','2026-03-06','USD',18400.00,0,0,NULL,'PO-4510');
