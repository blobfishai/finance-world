-- Watchlist customers with controlled live ERP balances:
-- Northwind Field Services 52,300 (tracker fresh) · Tailwind Bikes 41,650 (tracker shows 38,100)
-- · Ostara Labs 33,500 (tracker shows 31,500). ERP live total 127,450.
INSERT INTO erp_customers VALUES
  ('US-031','USMF','Northwind Field Services','30','USD','Net30',NULL,80000,'Fair','Open','Tacoma','WA','Mel','mel@northwindfs-sim.example','253-555-0101'),
  ('US-032','USMF','Tailwind Bikes','30','USD','Net30',NULL,60000,'Fair','Open','Boulder','CO','Jo','jo@tailwindbikes-sim.example','303-555-0177'),
  ('US-033','USMF','Ostara Labs','30','USD','Net30',NULL,50000,'Poor','Open','Madison','WI','Ren','ren@ostaralabs-sim.example','608-555-0155');

INSERT INTO erp_cust_trans (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date, currency, amount, settled, closed)
VALUES
  ('USMF','US-031','WLV-01','WLINV-101','Invoice','Field services retainer','2026-01-05','2026-02-04','USD',30000.00,0,0),
  ('USMF','US-031','WLV-02','WLINV-102','Invoice','January overage','2026-01-25','2026-02-24','USD',22300.00,0,0),
  ('USMF','US-032','WLV-03','WLINV-103','Invoice','Fleet order','2026-01-10','2026-02-09','USD',38100.00,0,0),
  ('USMF','US-032','WLV-04','WLINV-104','Invoice','February add-on order','2026-02-21','2026-03-23','USD',3550.00,0,0),
  ('USMF','US-033','WLV-05','WLINV-105','Invoice','Lab equipment lease Q1','2026-01-08','2026-02-07','USD',31500.00,0,0),
  ('USMF','US-033','WLV-06','WLINV-106','Invoice','Calibration services Feb','2026-02-24','2026-03-26','USD',2000.00,0,0);
