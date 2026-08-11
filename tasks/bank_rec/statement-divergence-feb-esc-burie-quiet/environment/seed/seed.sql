-- Posted customer payments (book side of the reconciliation window).
INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('USMF','SYNCUS-0003','PMTV-2101','PMT-2101','Payment','Wire - Alpine Ski House','2026-02-24','2026-02-24','USD',-12400.00,-12400.00,1),
  ('USMF','SYNCUS-0005','PMTV-2102','PMT-2102','Payment','ACH - City Power & Light','2026-02-25','2026-02-25','USD',-8150.75,-8150.75,1),
  ('USMF','SYNCUS-0007','PMTV-2103','PMT-2103','Payment','Wire - Coho Winery','2026-02-26','2026-02-26','USD',-22000.00,-22000.00,1),
  ('USMF','SYNCUS-0011','PMTV-2104','PMT-2104','Payment','Check 8841 - Consolidated Messenger','2026-02-27','2026-02-27','USD',-5325.50,-5325.50,1);
