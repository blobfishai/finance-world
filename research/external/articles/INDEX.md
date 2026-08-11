# External practitioner articles — index

49 sources fetched and summarized on **2026-08-10** for `finance-world`. One file per source,
named `<topic>--<publisher>.md`, each with title / URL / publisher / retrieval date, a faithful
summary preserving exact thresholds and step names, and an "Eval-relevant hooks" section.

Companion to `research/domain-workflows.md` (roles + chaos map) and
`research/finance-agent-workflows.md` (12 workflows, step-by-step). Those two synthesize; these
49 files are the primary-source layer with the numbers that make tasks gradable.

Rule observed throughout: nothing invented. Where a source publishes no threshold, the file says
so explicitly (notably: **write-off / close materiality thresholds are unpublished in every close
source fetched** — they must be seeded as world policy, not asserted as industry fact).

---

## 1. Month-end close checklist & subledger tie-outs

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `month-end-close--highradius.md` | Month-End Close Process: Steps, Checklist, and Best Practices | HighRadius | https://www.highradius.com/resources/Blog/what-is-month-end-close-process/ | Six named process steps in which **reconciliation precedes adjusting entries**; close duration 5–10 days typical, under 5 days = "fast close" |
| `month-end-close--vena.md` | Month End Close Steps, Process, Checklist and Best Practices | Vena Solutions | https://www.venasolutions.com/blog/month-end-close-process-checklist | 15 named tasks split across **pre-close / close / post-close**, including a mandated mid-close blocker sync; close-duration bands 3–5 aspirational, 5–7 high performer, 8–10 mid-sized |
| `month-end-close--numeric.md` | Account Reconciliation: Process, Examples & Best Practices | Numeric | https://www.numeric.io/blog/a-comprehensive-approach-to-account-reconciliation | Reconciliation **cadence tiers (daily/weekly/monthly/quarterly) assigned per named account type**, plus a three-role preparer/reviewer/approver model with materiality-gated approval authority |

## 2. AR collections & dunning ladders

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `ar-collections-dunning--creditpulse.md` | The Dunning Process: How It Works and When to Escalate | CreditPulse | https://www.creditpulse.com/blog/dunning-process-guide | Complete **7-stage ladder with day thresholds, action and owning role**: 1–3 soft email (analyst) → 7–10 follow-up → 14–17 phone → 21–25 escalation (manager) → **30 credit hold** → **45 demand letter** (director) → **60+ agency/counsel**; automate stages 1–3 only |
| `ar-collections-dunning--abc-amega.md` | Measure and Manage Collection Efficiency Using DSO | ABC-Amega | https://www.abc-amega.com/articles/measure-and-manage-collection-efficiency-using-dso/ | **Six DSO variants with formulas and worked examples** (Standard, Best Possible, ADD/Delinquent, Sales Weighted, Countback, True); all divide by **credit sales**, not total sales; CRF benchmark: DSO acceptable if no more than **10–15 days longer than terms** |
| `ar-collections-dunning--quadient.md` | Collection Effectiveness Index (CEI): What Is It & Why Is It Important? | Quadient | https://www.quadient.com/en-us/blog/what-collection-effectiveness-index | Full **CEI formula with every term named** and a worked example resolving to **57%**; the denominator uses ending **current** AR (the classic silent-error trap); good bar **85%+** |

## 3. Cash application & remittance matching

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `cash-application--zamp.md` | Cash Application Automation: How It Actually Works and Where It Quietly Breaks | Zamp | https://www.zamp.ai/blogs/cash-application-automation-how-it-actually-works-and-where-it-quietly-breaks | **5-rung match-confidence ladder** (exact → customer-level → fuzzy/multi-invoice subset-sum → ML-assisted → human exception) with segment auto-match bands: **85–95%** clean-remittance mid-market B2B vs **60–75%** deduction-heavy CPG/retail; ACH memo truncation at ~80 chars named as a structural root cause |
| `cash-application--highradius.md` | Cash Application Management Platform | HighRadius | https://www.highradius.com/resources/platform/cash-application-management/ | Named remittance/bank formats the matcher must consume — **BAI2, EDI, CSV, MT940, CAMT** — against a **90%+ straight-through** target |
| `cash-application--stuut.md` | Cash Application Exception Handling: Short Pays and Deductions | Stuut | https://www.stuut.ai/blog/cash-application-exception-handling-short-pays-and-deductions | **Seven named deduction reason codes** (damaged goods, short shipment, pricing error, early payment discount, return chargeback, promotional allowance, freight dispute) plus a de-minimis code, and **reason→function routing rules**; exception aging: 2 days healthy, 2 weeks = broken lane, 60+ days urgent |

## 4. Bank reconciliation

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `bank-reconciliation--accountingtools.md` | Bank Reconciliation (procedure and reconciling-item treatment) | AccountingTools | https://www.accountingtools.com/articles/bank-reconciliation | The **sidedness rule**: deposits-in-transit and outstanding checks adjust the **bank** column (no journal entry); fees/NSF/interest adjust the **book** column (journal entry required) — the single cleanest timing-vs-error decision rule found |
| `bank-reconciliation--numeric.md` | Bank Reconciliations: Steps, Examples, Best Practices | Numeric | https://www.numeric.io/blog/bank-reconciliation | Aging + materiality bands for reconciling items: outstanding checks **>90 days**, deposits in transit **>3 business days**, **<$100** investigated only if recurring, **>$10,000** immediate |
| `bank-reconciliation--university-of-houston.md` | Bank Account Reconciliation (MAPP 05.04.06) | University of Houston | https://uh.edu/policies/mapps/05-finance-and-accounting/050406/ | Hard institutional day counts: reconcile within **30 working days of the later of** statement receipt or fiscal-month close; **20 working days** to route discrepancies; **3 business days** for Treasury to forward bank data; reconcilers may not initiate corrections (segregation of duties) |

## 5. AP invoice processing & 3-way match exceptions

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `ap-3way-match--oracle-fusion.md` | Invoice Tolerances (Oracle Fusion Cloud Payables) | Oracle | https://docs.oracle.com/en/cloud/saas/financials/26b/fappp/invoice-tolerances.html | Full named-tolerance list assigned at **supplier site** level, and the trap: a **blank tolerance = infinite variance allowed**, while **0% = no variance allowed** |
| `ap-3way-match--oracle-matching-holds.md` | Matching Hold Detail Report — hold and release name taxonomy | Oracle | https://docs.oracle.com/cd/A60725_05/html/comnls/us/ap/invoic10.htm | The **16-hold exception taxonomy** with exact trigger text and 4 release statuses; naming rule: `Max Qty Ord`/`Max Qty Rec` = amount-expressed, bare `Qty Ord`/`Qty Rec` = percentage; 7 non-tolerance holds that loosening limits can never clear |
| `ap-3way-match--sap-tolerance-keys.md` | MM-IV-LIV: Set Tolerance Limits for Incoming Invoice | teachSAP (reproducing SAP Customizing) | http://teachsap.blogspot.com/2010/02/mm-iv-liv-cre-set-tolerances-for.html | All **14 SAP tolerance keys** (AN, AP, BD, BR, BW, DQ, DW, KW, LA, LD, PP, PS, ST, VP) with behavior; **an unmaintained key = zero tolerance** — the exact inverse of Oracle's blank-is-infinite rule; release via **MRBR** |
| `ap-3way-match--stampli.md` | Price variance vs. quantity variance on an invoice | Stampli | https://www.stampli.com/resources/invoice-match-exceptions-price-quantity/ | Ownership routing: **price variance → procurement, quantity variance → receiving**, and the hard control that **AP must never edit the invoice price to force a match** |

## 6. Payment runs & early-payment discount capture

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `payment-runs-early-pay-discount--tipalti.md` | Complete Guide to 2/10 Net 30 Early Payment Discounts | Tipalti | https://tipalti.com/resources/learn/210-net-30/ | The full **2/10 net 30 → 36.7%** derivation with its exact convention: ($500/$490)−1 = 2.04%, × (**360 ÷ 20 days** = 18) — the divisor is the **20-day** acceleration, not 30 |
| `payment-runs-early-pay-discount--sap-f110.md` | Automatic Payment Program Run F110 | Guru99 | https://www.guru99.com/all-about-automatic-payment-run.html | F110's **proposal-as-approval-gate**: nothing posts until the payment run step, so Edit Proposal is the last no-reversal exit — the canonical "agent assembles, human releases" shape |
| `payment-runs-early-pay-discount--corpay-positive-pay.md` | What Is Positive Pay? | Corpay | https://www.corpay.com/resources/blog/positive-pay | Positive-pay exception **decision cutoffs commonly 11 a.m. or 2 p.m. local**, with bank-specific default-pay vs default-return behavior on no-decision |

## 7. Vendor master data & bank-change / BEC fraud prevention

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `vendor-master-bec-fraud--fbi-ic3.md` | Business Email Compromise: The $55 Billion Scam | FBI IC3 | https://www.ic3.gov/PSA/2024/PSA240911 | The #1 published control: **use secondary channels and two-factor authentication to verify requests for account information changes**; scale = **$55,499,915,582 across 305,033 incidents** (Oct 2013–Dec 2023) |
| `vendor-master-bec-fraud--afp-truist.md` | 2025 AFP Payments Fraud and Control Survey — Key Highlights | AFP (underwritten by Truist) | https://www.truist.com/content/dam/truist-bank/us/en/documents/info/cci/2025-afp-payments-fraud-control-survey-report-key-highlights.pdf | **13-item fraud-origination taxonomy with 2024 percentages** — vendor imposter jumped 34%→**45%**, invoice fraud 14%→**24%**; 79% experienced attempted/actual fraud; only **22% recovered >75%** of losses |
| `vendor-master-bec-fraud--wa-state-auditor.md` | Protect Your Vendor Master File from Fraudsters | WA State Auditor | https://sao.wa.gov/the-audit-connection-blog/protect-your-vendor-master-file-fraudsters | Verify bank-detail changes **by phone using contact information "known, reliable and already on file"** — never the number in the request; AP clerks must not be able to add or change vendor records |
| `vendor-master-bec-fraud--disbursement-controls.md` | Ensuring Vendor Data Accuracy and Completeness | DisbursementControls.com | https://www.disbursementcontrols.com/vendor-data-accuracy/ | **Dormant-vendor deactivation review at 12–24 months with no payment**, reactivation requiring full re-onboarding validation; dedup analysis at least annually; duplicate payments run **0.8%–2% of total payments** |

## 8. Credit management: limits, blocked orders, review cadence

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `credit-management--nacm.md` | Credit Basics: Setting Credit Limits | NACM-National | https://nacm.org/pdfs/articles/CreditBasicsSettingCreditLimits.pdf | **Nine named credit-limit-setting methods**, including the only explicit arithmetic: **Expectation of Use = expected credit sales volume ÷ expected order count** |
| `credit-management--oracle-credit-management.md` | Overview of Oracle Credit Management | Oracle EBS R12.1 | https://docs.oracle.com/cd/E18727_01/doc.121/e13502/T395686T401719.htm | **Periodic Credit Review fires at 6 months elapsed**; five-item recommendation taxonomy distinguishing **account-level hold vs party-level hold** |
| `credit-management--sap-press.md` | Credit Management Operations in SAP SD | SAP PRESS blog | https://blog.sap-press.com/credit-management-operations-in-sap-sd-sap-erp | **Eight named credit checks that can block a sales order** (static limit, dynamic limit, document value, critical fields, next check date, max dunning level, open items, oldest open item) — a block is *not* necessarily a limit breach; exposure = open orders + deliveries + billing + AR; VKM1/FD32/F.31/F.34 |

## 9. 13-week direct cash forecasting

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `cash-forecast-13-week--wall-street-prep.md` | 13-Week Cash Flow Model (TWCF) | Wall Street Prep | https://www.wallstreetprep.com/knowledge/demystifying-the-13-week-cash-flow-model-in-excel/ | The **four required roll-forwards** — AR/DSO, Inventory/COGS-turnover, AP/DPO, Accrued Wages/payroll timing — and reconciliation of weekly cash back to the EBITDA forecast |
| `cash-forecast-13-week--zone-and-co.md` | Mastering 13-Week Cash Flow Forecasting in NetSuite | Zone & Co | https://www.zoneandco.com/articles/13-week-cash-flow-forecasting-netsuite | **Acceptable variance 5–10% weekly for the first four weeks** (wider beyond), an 8-step weekly refresh, and **six named failure modes**; model unreliable after 2 weeks without actuals |
| `cash-forecast-13-week--eightx.md` | How to Build a 13-Week Cash Flow Forecast | Eightx | https://eightx.co/blog/build-13-week-cash-flow-forecast | The **Monday roll-forward ritual** (drop Wk1, shift 2–13, append new Wk13, document variance) and a **minimum-cash trigger at 20–30% of monthly burn**, acting 2–3 weeks before the trough |

## 10. Intercompany reconciliation & elimination

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `intercompany-reconciliation--oracle-epm-matching-reports.md` | Setting Up Intercompany Matching Reports | Oracle EPM (FCC) | https://docs.oracle.com/en/cloud/saas/financial-consolidation-cloud/usfcc/setting_up_intercompany_matching_reports.html | The **fully specified tolerance algorithm**: amount tolerance suppresses when \|variance\| ≤ value; percent tolerance = **min(\|Accounts portion\|, \|Matching Accounts portion\|) × (Tolerance % ÷ 100)**; when both set, the **minimum governs**; default tolerance 0 |
| `intercompany-reconciliation--oracle-epm-eliminations.md` | Intercompany Eliminations | Oracle EPM (FCC) | https://docs.oracle.com/en/cloud/saas/financial-consolidation-cloud/agfcc/intercompany_eliminations.html | Every elimination is **exactly two entries (reversal + plug)** and the eliminated amount is the **lower of entity vs partner cumulative Consolidation %**; 0% on either side → no elimination |
| `intercompany-reconciliation--oracle-fusion-reports.md` | Intercompany Reconciliation Reports | Oracle Fusion Cloud Financials | https://docs.oracle.com/en/cloud/saas/financials/26a/ocuar/intercompany-reconciliation-reports.html | Three-report drill chain (**Period Summary → Summary by Source → Journal Lines**) with paired Provider/Receiver ledger+period parameters, so a cut-off difference is isolated by running the two sides on *different* periods |
| `intercompany-reconciliation--element61.md` | Next-Generation Intercompany Reconciliation within S/4HANA Group Reporting (ICMR) | element61 | https://www.element61.be/en/resource/next-generation-intercompany-reconciliation-within-s4-hana-group-reporting | Published **reason codes for unmatched items** ("open items longer than 30 days", "goods in transit") and the close sequence in which adjustment postings precede currency conversion |

## 11. Audit PBC lists & evidence gathering

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `audit-pbc-evidence--pcaob-as1105.md` | AS 1105: Audit Evidence | PCAOB | https://pcaobus.org/oversight/standards/auditing-standards/details/AS1105 | The **.08 evidence reliability hierarchy** plus the **.10 duty to test accuracy and completeness of client-produced information** — the codified basis for "every schedule must tie to the GL" |
| `audit-pbc-evidence--pcaob-as2315.md` | AS 2315: Audit Sampling | PCAOB | https://pcaobus.org/oversight/standards/auditing-standards/details/AS2315 | The **projection mechanic with the standard's own numbers**: 50 items from 1,000 with $3,000 found → **$60,000 projected**; controls gate at **tolerable rate 5%, 60 items, 0 deviations pass / ≥2 fail**; risk model **TD = AR/(IR × CR × AP)** |
| `audit-pbc-evidence--pcaob-as2310.md` | AS 2310: The Auditor's Use of Confirmation | PCAOB | https://pcaobus.org/oversight/standards/auditing-standards/details/AS2310 | **Cash and trade AR must be confirmed**, and the auditor must select, send and receive — **the client may never touch the confirmation**; an oral-only reply counts as a nonresponse |
| `audit-pbc-evidence--madras-accountancy.md` | Audit-Ready in 30 Days: PBC Request List Template | Madras Accountancy | https://madrasaccountancy.com/blog-posts/audit-ready-in-30-days-pbc-request-list-template-for-first-time-audits | A **day-numbered 30-day readiness calendar** with a five-criterion delivery quality gate and the file-naming convention `PBC_[Number]_[Description]_[Year].xlsx` |

## 12. T&E policy audit / expense compliance testing

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `te-expense-audit--irs.md` | Publication 463 — Travel, Gift, and Car Expenses | IRS | https://www.irs.gov/publications/p463 | The federal substantiation floor: **60/120/30-day safe harbors**, **$0.70/mile**, **$25 gift cap**, **3/4 first-and-last-day** meal allowance, and the **five required record elements** |
| `te-expense-audit--ecfr-accountable-plan.md` | 26 CFR § 1.62-2 — Reimbursements and Other Expense Allowance Arrangements | Cornell LII (regulation text) | https://www.law.cornell.edu/cfr/text/26/1.62-2 | The **periodic-statement alternative** (quarterly statements, **120 days from the statement**) and the consequence rule: excess per diem is **taxed on Form W-2**, not clawed back |
| `te-expense-audit--gsa-mie-breakdown.md` | M&IE Breakdown | GSA | https://www.gsa.gov/travel/plan-book/per-diem-rates/mie-breakdown | The **five-tier M&IE table** ($68/$74/$80/$86/$92) where **incidentals are always $5** and components sum exactly to the total; first/last day at 75% = **$51.00 / $55.50 / $60.00 / $64.50 / $69.00** |
| `te-expense-audit--gsa-perdiem-faq.md` | Frequently Asked Questions, Per Diem | GSA | https://www.gsa.gov/travel/plan-a-trip/per-diem-rates/faqs | Per diem follows the **work location, not the lodging location**, unless lodging is unavailable there; one-day travel qualifies only if **>12 hours**, then at 75%; complimentary hotel/carrier meals do **not** reduce per diem |
| `te-expense-audit--oracle.md` | Audit Rules to Identify Anomalies in the Expense Report | Oracle Fusion Cloud Expenses | https://docs.oracle.com/en/cloud/saas/financials/25d/faiex/audit-rules-to-identify-anomalies-in-the-expense-report.html | **Seven named audit-selection rules**, including the threshold-shaving detector: a **10% band below a USD 500 receipt threshold (USD 450–499) more than 5 times in 6 months**; duplicates matched on **Amount + Date + Currency + Expense Type + Merchant** |

## 13. AI agents in finance: what's actually shipping

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `ai-agents-in-finance--microsoft-dynamics365.md` | Account Reconciliation Agent (production ready preview) | Microsoft Learn (D365 Finance) | https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/acct-rec-agent | The agent recommends actions **only for "Voucher amount mismatch" exceptions**, and the human picks from exactly four actions (**Create journal entry / Reverse / Link transactions / Accept without change**); exception-limit alerts at **50% / 75% / 90%** |
| `ai-agents-in-finance--microsoft-copilot-finance-agent.md` | Create Custom reconciliation agents with Finance Agent (preview) | Microsoft Learn (M365 Copilot Finance) | https://learn.microsoft.com/en-us/copilot/finance/reconcile/custom-reconciliation-agent | Microsoft warns that **auto-detected mapping keys vary run to run**, so a saved **Reconciliation Template ID** is required for deterministic results — and is the only way to set partial matching and amount tolerances |
| `ai-agents-in-finance--ramp.md` | Policy Agent Overview | Ramp | https://support.ramp.com/hc/en-us/articles/44072387128979-Policy-Agent-Overview | Policy Agent starts **review-only, never auto-approves by default**, emits *Approval recommended / Requires review / Rejection recommended*, and **cannot look across multiple transactions** — an explicit published capability boundary |
| `ai-agents-in-finance--highradius.md` | An Introduction to AI Agents for the Order-to-Cash Process | HighRadius | https://www.highradius.com/resources/Blog/an-introduction-to-ai-agents-for-the-order-to-cash-process/ | Per-stage **trigger → automated steps → human-review carve-out** for all five O2C stages (credit, invoicing, cash application, deductions, collections), with **90%+ same-day cash posting** as the published bar |

## 14. Financial ratio analysis for credit evaluation

| File | Title | Publisher | URL | Most useful operational detail |
|---|---|---|---|---|
| `credit-ratio-analysis--wall-street-prep-altman-z-score.md` | Altman Z-Score — Formula + Calculator | Wall Street Prep | https://www.wallstreetprep.com/knowledge/altman-z-score/ | **All three Z variants with coefficients and distinct cutoffs**: Z = 1.2X₁+1.4X₂+3.3X₃+0.6X₄+0.99X₅ (safe >2.99 / grey 1.81–2.99 / distress <1.81); Z′ = .717/.847/3.107/.42/.998; Z″ = 3.25+6.56X₁+3.26X₂+6.72X₃+1.05X₄ (safe >2.60 / grey 1.10–2.60 / distress <1.10) |
| `credit-ratio-analysis--wall-street-prep-credit-analysis.md` | Credit Analysis — Financial Ratios + Lending Process | Wall Street Prep | https://www.wallstreetprep.com/knowledge/credit-risk-analysis/ | Four illustrative **maintenance covenants with correct inequality directions** — total leverage ≤ **6.0x**, senior ≤ **3.0x**, EBITDA coverage ≥ **2.0x**, FCCR ≥ **1.0x** (leverage = ceiling, coverage = floor) |
| `credit-ratio-analysis--corporate-finance-institute.md` | Coverage Ratio — Guide to Understanding All the Coverage Ratios | Corporate Finance Institute | https://corporatefinanceinstitute.com/resources/accounting/coverage-ratio-overview/ | Exact **ICR / DSCR / cash coverage / asset coverage formulas with benchmarks** (ICR minimum acceptable **1.5**, DSCR ideal **≥2**) and worked examples |

---

## Cross-cutting notes

- **Two ERP tolerance conventions are exact inverses** — an unmaintained SAP tolerance key blocks
  everything (zero tolerance); a blank Oracle Fusion tolerance blocks nothing (infinite). Any task
  that asks an agent to reason about "no tolerance configured" must name the dialect.
- **Unpublished-on-purpose values.** Close/write-off materiality (all three close sources), stale-date
  and escheatment dormancy periods (no fetchable source carried day counts), and the CreditPulse sales-hold
  day cap are explicitly absent from the sources. Seed them as world policy documents; do not cite them as
  industry standards.
- **Sources deliberately discarded** (fetch-blocked or no operational specifics) are listed in each
  agent's notes rather than represented here: Alvarez & Marsal 13-week materials (403), NYU Stern Altman
  PDF (500), BlackLine Net & Settle, PwC Viewpoint 4.2, Suralink, AuditDashboard, SAP Help Portal ICMR,
  C2FO dynamic discounting, Auditoria.AI datasheet (binary PDF). **Auditoria and Oracle/SAP AI-agent
  claims are therefore not covered by a primary source** — the existing teardown in
  `research/finance-agent-workflows.md` §13.8 remains the only record.
