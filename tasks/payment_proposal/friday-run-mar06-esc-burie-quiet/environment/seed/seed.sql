-- The PPINV batch. SYNVEN-0069 carries 2/10 net 30 terms; SYNVEN-0044 goes on payment hold.
UPDATE erp_vendors SET cash_disc_code = '2%10N30' WHERE account = 'SYNVEN-0069';
UPDATE erp_vendors SET on_hold = 'Yes' WHERE account = 'SYNVEN-0044';

INSERT INTO erp_vend_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed, cash_disc_code)
VALUES
  ('USMF','SYNVEN-0069','PPV-101','PPINV-101','Invoice','Espresso equipment order - 2/10 net 30','2026-02-25','2026-03-27','USD',12480.00,0,0,'2%10N30'),
  ('USMF','SYNVEN-0069','PPV-102','PPINV-102','Invoice','February beans supply - 2/10 net 30','2026-02-28','2026-03-30','USD',9375.50,0,0,'2%10N30'),
  ('USMF','SYNVEN-0011','PPV-103','PPINV-103','Invoice','Courier services February','2026-02-02','2026-03-04','USD',15000.00,0,0,NULL),
  ('USMF','SYNVEN-0044','PPV-104','PPINV-104','Invoice','Facilities maintenance February','2026-02-01','2026-03-03','USD',7700.00,0,0,NULL);
