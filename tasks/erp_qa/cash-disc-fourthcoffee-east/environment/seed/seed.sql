-- Special core data for this task: assign a cash-discount code to vendor Fourth Coffee East
-- and post two fresh invoices whose 10-day discount windows are still open on 2026-03-02.
UPDATE erp_vendors SET cash_disc_code = '2%10N30' WHERE account = 'SYNVEN-0069';

INSERT INTO erp_vend_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, cash_disc_code)
VALUES
  ('USMF', 'SYNVEN-0069', 'VINVV-900001', 'VINV-900001', 'Invoice',
   'Espresso equipment order - negotiated 2/10 net 30', '2026-02-25', '2026-03-27', 'USD', 12480.00, 0, 0, '2%10N30'),
  ('USMF', 'SYNVEN-0069', 'VINVV-900002', 'VINV-900002', 'Invoice',
   'February beans supply - negotiated 2/10 net 30', '2026-02-28', '2026-03-30', 'USD', 9375.50, 0, 0, '2%10N30');
