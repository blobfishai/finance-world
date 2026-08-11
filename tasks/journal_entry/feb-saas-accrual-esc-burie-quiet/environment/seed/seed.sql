-- journal_entry/feb-saas-accrual — accrue a mid-month SaaS commencement, then hit the
-- delegation-of-authority wall.
--
-- Mechanics (docs/HARD-LAYER-DESIGN.md): M1 write-and-approve (the journal is staged, and
-- the DoA threshold means it must NOT end up posted) · M4 money re-derivation (the accrual
-- appears nowhere; it is computed from contract value, commencement date and the SOP's
-- 365-day basis) · M5 hidden/conflicting constraint (the governing contract is v2.0; v1.0
-- is superseded but still in the document store, and Feb is on_hold so the posting period
-- is not the obvious one).
--
-- Sourced: month-end close accrual practice (research/external/articles/month-end-close--*),
-- ERPNext Authorization Rule DoA shape (research/erp-mcp-tool-census.md), Odoo period lock
-- (research/odoo-domain.md). SIMULATION ONLY.

-- The vendor exists and has NO posted invoice for the service — which is what makes an
-- accrual correct rather than a duplicate (SOP-GL-02 s1).
INSERT OR REPLACE INTO erp_vendors
  (account, dataareaid, name, vendor_group, currency, payment_term, cash_disc_code,
   payment_method, on_hold, city, state, contact_name, contact_email, phone) VALUES
 ('PVEN-11','USMF','CloudScale Analytics Inc','SERVICES','USD','Net30',NULL,'ELECTRONIC','Open',
  'Seattle','WA','Jordan Álvarez','billing@cloudscale-sim.example','555-0121');

-- February is the service period and it is still open for accrual postings at this point in
-- the close. (The core build leaves 2026-02 on_hold; the close calendar reopens it for the
-- accrual window, which is why the agent must check FiscalPeriods rather than assume.)
UPDATE erp_fiscal_periods SET status = 'open' WHERE period_id = '2026-02';

-- A distractor: a DIFFERENT CloudScale charge already posted in February — a one-off
-- implementation fee, not the subscription. Accruing it again would double-count, and its
-- amount (37,500.00) is a plausible wrong answer for an agent that reaches for a number
-- already in the ledger instead of computing one.
INSERT INTO erp_vend_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed, cash_disc_code, po_number) VALUES
 ('USMF','PVEN-11','PVENV-9201','PINV-201','Invoice','CloudScale one-off implementation fee',
  '2026-02-09','2026-03-11','USD',37500.00,0,0,NULL,NULL);
