# Workflow → mock mapping — how real finance workflows land on our servers

> Synthesis of `finance-agent-workflows.md` (12 workflows, step-level tool mapping) and
> `finance-tool-landscape.md` (9 categories, ~55 products, MCP inventory). 2026-08-10.

## Coverage verdict per workflow

| # | Workflow | Steps land on (our servers) | Verdict | Task family implied |
|---|---|---|---|---|
| 1 | Bank reconciliation | sheets (bank CSV export) + erp (transactions) | **Coverable now** via a seeded bank-export file; classify timing vs error (Microsoft's recon-agent taxonomy: Matched / Potentially matched 1:N / Discrepancy / Exclusively unmatched = our grading schema) | `bank_rec` (new) |
| 2 | Month-end close checklist | docs (checklist) + erp + books + sheets | Coverable; the three-way divergence (sign-off vs workbook vs ERP) is the chaos | `close_support` (later) |
| 3 | Payment run / proposal | erp (due dates, cash-disc, holds) + docs (policy) | Coverable read-only now (assemble the proposal, human posts — D365's own pattern); posting needs wave-2 write role | `payment_proposal` (new) |
| 4 | Cash application | email (remittance) + sheets (bank export) + erp (open invoices) | **Coverable now** — remittance-in-mailbox is already seeded style; matching is exact-verifiable | `cash_app` (new) |
| 5 | Vendor onboarding / master data | email (W-9, bank change) + erp (vendor master) | Partial — entity-setup lag already our meadow mechanic; fraud-check variant = bank-detail-change email (verify against master) | `vendor_master` (later) |
| 6 | 3-way match exceptions | erp (PO/receipt/invoice) | **Gap**: no PO/receipt tables yet — schema addition required first | parked |
| 7 | Intercompany reconciliation | erp (parent AR) + books (subsidiary AP view) | **Coverable now** — decompose parent-vs-subsidiary difference into named items; exact GT | `intercompany` (new) |
| 8 | 13-week cash forecast | erp (AR/AP agings) + sheets (payroll calendar) | Coverable; fully arithmetic-checkable | `cash_forecast` (new) |
| 9 | Audit support / PBC | email (approvals live only here) + erp + sheets | **Coverable now** — evidence-gathering where the approval exists only in a thread | `pbc` (new) |
| 10 | Credit review / blocked-order release | erp (hold list, limits) + filings (deterioration) + docs (policy) | Coverable; D365 blocking-rule/release-reason machinery is documented — add hold-release as wave-2 write | `credit_ops` |
| 11 | T&E audit | docs (policy) + sheets (expense export) | Coverable via seeded export; violation list = exact GT | `expense_audit` (later) |
| 12 | External reporting tie-out | filings + erp | **Coverable now** — draft number vs erp/filings sources | folds into `business_brief` |

Bottom line: **7 of 12 workflows are coverable with zero new servers** — only new task-level
seeds (bank-export sheet, remittance emails, payroll-calendar sheet, PBC threads). One
workflow (3-way match) is blocked on schema (PO/receipt tables). None require a tool
outside the census.

## Landscape verdicts (from `finance-tool-landscape.md`)

- **Validated**: our email + sheets glue is exactly where the MCP-poor categories
  (enterprise AP, AR suites, BlackLine/Kyriba, FP&A) still run — Auditoria's
  mailbox-triage agents and the 94%-Excel close stats are direct evidence.
- **Watch item**: Microsoft is replacing the D365 MCP lineup again (static retires
  2026-10-01; dynamic server itself evolving) — re-verify our 22-tool parity quarterly.
- **Future mocks, strictly in this order and only when a task needs them** (census rule):
  1. `bank` — portal/statement surface; **Modern Treasury's MCP object model
     (payment_orders, expected_payments, counterparties, ledgers) is the schema to crib**;
     serves workflows 1/4/8 more realistically than sheets-CSV.
  2. `ap` — BILL/Stampli-shaped approval + bill objects; serves 3-way match + sync-lag
     chaos (approval state ≠ ERP posting state).
  3. `close` — Numeric's MCP (close-task CRUD + flux/recon skills) as template.
  4. Card feed (Ramp-shaped) for T&E.
- **Canonical chaos primitive across every category: ERP↔satellite sync lag.** Every
  future seeded inconsistency should be expressible as "system A learned the truth before
  system B."

## Priority queue for wave 1.5 tasks (all zero-new-server)

1. `bank_rec/first-divergence` — bank CSV (sheets) vs erp cash: classify each unmatched
   line timing-vs-error using the 4-bucket taxonomy. Exact GT.
2. `cash_app/remittance-batch` — 3 remittance emails + bank export → apply to open
   invoices; one payment has no remittance (unapplied). Exact GT.
3. `intercompany/parent-sub-tieout` — USMF AR vs CES books: decompose the delta (the
   side-log invoice + credit memo + timing item). Exact GT.
4. `payment_proposal/discount-window` — assemble Friday's payment run per policy: due
   items + discount-qualifying items, excluding one on-hold vendor. Exact GT set.
5. `pbc/approval-evidence` — auditor asks for approval evidence on 2 invoices; one
   approval exists only in an email thread. Exact GT.
6. `cash_forecast/13-week` — AR aging inflow curve + AP due-date outflows + payroll
   calendar sheet. Arithmetic GT.
