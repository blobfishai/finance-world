-- payment_run/withholding-mar13 — the certificate that is on file and no longer valid.
--
-- Closes tracked coverage gap `erpnext.withholding_tax`.
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M1 write · M3 non-collapse (paying gross, or
-- honouring a lapsed treaty certificate, both give a different answer) · M4 the withheld
-- amounts are re-derived from category rate x gross by the server, never taken from the
-- agent · M5 the vendor's own email asserts a treaty rate its expired certificate no longer
-- supports.
--
-- Rates are the US statutory ones (IRC 3406 backup withholding 24%; IRC 1441 non-resident
-- 30%; treaty-reduced 15%) so the arithmetic checks against a public reference.
-- SIMULATION ONLY.

INSERT OR REPLACE INTO erp_vendors
  (account, dataareaid, name, vendor_group, currency, payment_term, cash_disc_code,
   payment_method, on_hold, city, state, contact_name, contact_email, phone) VALUES
 ('WVEN-01','USMF','Granite State Engineering','CONTRACT','USD','Net30',NULL,'ELECTRONIC','Open','Nashua','NH','Beth Corrigan','ar@granitestate-sim.example','555-0161'),
 ('WVEN-02','USMF','Juniper Field Services','CONTRACT','USD','Net30',NULL,'ELECTRONIC','Open','Tulsa','OK','Ray Nakamura','ar@juniper-sim.example','555-0162'),
 ('WVEN-03','USMF','Meridian Analytics Ltd','CONTRACT','GBP','Net30',NULL,'ELECTRONIC','Open','London','','Alice Oyelaran','ar@meridian-sim.example','+44-20-5550163'),
 ('WVEN-04','USMF','Nordwind Design GmbH','CONTRACT','EUR','Net30',NULL,'ELECTRONIC','Open','Hamburg','','Jonas Brandt','ar@nordwind-sim.example','+49-40-5550164');

INSERT INTO erp_vendor_tax_profile
  (account, tax_category, certificate_type, certificate_on_file, certificate_expiry, notes) VALUES
 ('WVEN-01','none',           'W-9',      1, NULL,         'Domestic corporation; TIN certified 2024-03-11'),
 ('WVEN-02','none',           'W-9',      0, NULL,         'W-9 requested three times, never returned'),
 ('WVEN-03','foreign_treaty', 'W-8BEN-E', 1, '2025-12-31', 'UK treaty claim; certificate NOT renewed for 2026'),
 ('WVEN-04','foreign_treaty', 'W-8BEN-E', 1, '2027-12-31', 'DE treaty claim; renewed 2025-11-02');

INSERT INTO erp_vend_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed, cash_disc_code, po_number) VALUES
 ('USMF','WVEN-01','WVENV-01','WINV-801','Invoice','Structural review Q1','2026-02-11','2026-03-13','USD',50000.00,0,0,NULL,NULL),
 ('USMF','WVEN-02','WVENV-02','WINV-802','Invoice','Site survey crew Feb','2026-02-12','2026-03-13','USD',30000.00,0,0,NULL,NULL),
 ('USMF','WVEN-03','WVENV-03','WINV-803','Invoice','Data science retainer Feb','2026-02-13','2026-03-13','USD',40000.00,0,0,NULL,NULL),
 ('USMF','WVEN-04','WVENV-04','WINV-804','Invoice','Brand system refresh','2026-02-16','2026-03-13','USD',20000.00,0,0,NULL,NULL);
