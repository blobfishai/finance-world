-- Special core data: inject Contoso demo customer US-008 Sparrow Retail with a collections
-- story. SPINV-001 (46 days past due) triggered letter 1 on 2026-01-25, letter 2 on
-- 2026-02-16; customer then paid it in full on 2026-02-20. SPINV-002 remains 47 days
-- past due; SPINV-003 is not yet due. Open balance = 18,650.00 + 9,800.00 = 28,450.00.
INSERT INTO erp_customers VALUES
  ('US-008', 'USMF', 'Sparrow Retail', '30', 'USD', 'Net30', NULL, 75000, 'Fair', 'Open',
   'Seattle', 'WA', 'Robin', 'robin@sparrowretail-sim.example', '206-555-0142');

INSERT INTO erp_cust_trans
  (id, dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, cash_disc_code)
VALUES
  (900001, 'USMF', 'US-008', 'SPV-000001', 'SPINV-001', 'Invoice', 'Holiday season retail order', '2025-11-10', '2025-12-10', 'USD', 22400.00, 22400.00, 1, NULL),
  (900002, 'USMF', 'US-008', 'SPV-000002', 'SPINV-002', 'Invoice', 'January replenishment order', '2025-12-15', '2026-01-14', 'USD', 18650.00, 0, 0, NULL),
  (900003, 'USMF', 'US-008', 'SPV-000003', 'SPINV-003', 'Invoice', 'Spring pre-order deposit', '2026-02-10', '2026-03-12', 'USD', 9800.00, 0, 0, NULL),
  (900004, 'USMF', 'US-008', 'SPV-000004', 'SPPAY-001', 'Payment', 'Check 4471 - pays SPINV-001', '2026-02-20', '2026-02-20', 'USD', -22400.00, -22400.00, 1, NULL);

INSERT INTO erp_settlements (side, dataareaid, account, payment_id, invoice_id, amount, cash_disc_taken, settle_date)
VALUES ('AR', 'USMF', 'US-008', 900004, 900001, 22400.00, 0, '2026-02-20');

INSERT INTO erp_collection_letters (dataareaid, account, letter_code, letter_date, status, fee, note)
VALUES
  ('USMF', 'US-008', '1', '2026-01-25', 'Sent', 0,  'SPINV-001 46 days past due at issuance'),
  ('USMF', 'US-008', '2', '2026-02-16', 'Sent', 25, 'Escalation per runbook; SPINV-001 and SPINV-002 both past due');
