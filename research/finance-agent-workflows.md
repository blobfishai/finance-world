# Finance-World Research II: Agent-Relevant Finance Workflows, Step-by-Step

Research date: 2026-08-10. Companion to `domain-workflows.md` (roles, chaos map, EDGAR stack). This file goes deeper and wider: 12 workflows an AI agent would actually be asked to run, each documented step-by-step with the tool touched per step, plus teardowns of shipping finance agents as proof of agent-relevance.

**Mock-server key** (which of OUR servers carries each step):
- `erp` — D365-shaped ERP (data/form/action MCP tools): GL, AP/AR subledgers, bank transactions, vendor/customer master, POs, credit management, payment journals
- `books` — QBO-style subsidiary books
- `sheets` — Excel shadow drive (close checklist, recon workpapers, trackers, bank-statement exports)
- `email` — shared mailbox (remittances, approvals, vendor requests, auditor requests)
- `filings` — EDGAR-style public filings
- `docs` — policy documents (AP policy, credit policy, T&E policy, close calendar policy)

Anything not tied to a fetched source is marked **UNVERIFIED**. Full Sources list at end.

---

## 1. Bank Reconciliation

**Trigger**: Bank statement arrives (monthly cutoff, or daily for high-volume accounts); close checklist task "reconcile bank accounts."

**Steps (D365 "advanced bank reconciliation" is the canonical ERP dialect — Microsoft Learn):**

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Export/receive bank statement (BAI2, ISO 20022 camt.053, MT940, or CSV from bank portal) | Bank portal / SFTP / SharePoint auto-import into D365 | `sheets` (statement export file) or `email` (bank sends PDF/CSV) |
| 2 | Import statement into ERP; bank account identified via routing/SWIFT/IBAN; duplicate check on AccountNo+StatementID+FromDate+ToDate | D365 Bank statements page → Import statement | `erp` (action tool) |
| 3 | Validate statement: currency matches account; opening balance = prior statement's closing; no date overlap; line dates within header dates; opening + line sum = ending | D365 Validate action | `erp` |
| 4 | Create reconciliation + worksheet (one open recon per account; cut-off date bounds included transactions) | D365 Bank reconciliation page | `erp` |
| 5 | Run matching rules (rule = filter criteria [amount, date tolerance, reference, transaction code, doc type] + action [match, generate voucher, generate customer/vendor payment journal, clear reversal]) | D365 Run matching rules | `erp` |
| 6 | Manually match residual lines: 1:1, many:1, many:many; penny differences within tolerance post as Correction amount | D365 worksheet (4 grids: unmatched bank/ERP on top, matched below) | `erp` |
| 7 | Handle bank-initiated items not in ERP (fees, interest, charges): Mark as New → post to GL from Bank statement page | D365 Mark as new + Post | `erp` |
| 8 | Handle ERP items not on statement = timing items (outstanding checks, deposits in transit) — leave unmatched; they roll forward to next worksheet | D365 | `erp` |
| 9 | Mark reconciled (irreversible; unmatched statement lines carry to next recon); document in workpaper | D365 + Excel recon workpaper | `erp` + `sheets` |

- Modern bank reconciliation adds: posting customer/vendor payment journals directly from statement lines (cash application from the bank rec — settles open invoices), and generating GL vouchers from the worksheet (Microsoft Learn).
- **QBO dialect** (for `books` subsidiary): match/categorize all bank-feed transactions first; Settings → Reconcile; verify beginning balance matches statement; enter ending balance + date; work every rec to a $0.00 difference — forced adjustment entries hide errors (Intuit help; ezqgroup; bankreconciler.app).

**Definition of done**: statement fully matched or every residual explained as timing/new item; ending book balance + outstanding items = bank ending balance; fees/interest posted; recon marked reconciled and workpaper saved.

**Failure modes / exceptions (eval gold)**:
- Opening balance mismatch (prior statement skipped or edited after reconciling) — validation fails.
- Duplicate statement import attempt.
- Payment cleared at bank, never posted in ERP (or vice versa) — the classic timing vs missing-entry judgment call.
- Penny/FX differences vs true errors; bank fee vs unrecorded transaction.
- Statement for the wrong account/entity in a multi-entity zip.

**Candidate tasks**:
1. *Month-end bank rec*: bank CSV on `sheets` vs ERP bank transactions; agent must classify every unmatched item (timing / bank fee to post / missing ERP entry / error), post the fee voucher, and report the reconciled balance. Ground truth: seeded decomposition — exact item list and adjusted balance are checkable.
2. *Broken opening balance* (QBO sub): beginning balance ≠ statement because a previously-reconciled transaction was deleted/edited; agent must find the changed transaction. Ground truth: the specific transaction ID.

---

## 2. Month-End Close Checklist (end-to-end)

**Trigger**: Calendar (business day 1 of new month); controller owns the close calendar.

**Steps** (Trullion, Dokka, CheckFlow, Finlens close checklists; flux: Ramp, NetSuite, Double, Numeric):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Pre-close prep: confirm cutoff, chase un-entered invoices/expenses | ERP + email chasing | `erp` + `email` |
| 2 | Open the close checklist; check task status/owners/due dates/dependencies | Excel checklist (57% of teams keep the close calendar in spreadsheets — prior research) or FloQast/Numeric | `sheets` |
| 3 | Record all transactions: post pending journals, accruals, prepaid amortization | ERP GL | `erp` |
| 4 | Reconcile bank + credit card accounts (see §1) | ERP + bank statements | `erp` + `sheets` |
| 5 | Subledger tie-outs: AP aging → AP subledger → GL control account; AR likewise; payroll liabilities; clear suspense/clearing accounts | ERP reports + Excel tie-out workpaper | `erp` + `sheets` |
| 6 | Intercompany reconciliation + eliminations (see §7) | ERP + subsidiary books | `erp` + `books` |
| 7 | Flux analysis: compare every material account to prior period and budget; explain variances above threshold (e.g., 10% AND $5K; mid-market commonly 5–10% + $25–50K minimums) | Excel / close tool | `sheets` + `erp` |
| 8 | Produce statements; controller/CFO review + sign-off; lock the period | ERP + review meeting | `erp` |
| 9 | Retrospective: log what slowed the close | Checklist notes | `sheets` |

**Definition of done**: every checklist task signed off with evidence; all subledgers tie to GL; all flux items above threshold have commentary covering what changed, why, dollar quantification, and "a narrative any auditor can follow without a follow-up call" (Double/Ramp); period locked.

**Failure modes**: task marked done in tracker but recon shows unexplained difference; direct-to-GL journal breaks subledger tie; two versions of the checklist on the drive disagree (prior research chaos pattern #10); flux commentary that restates the number without a driver.

**Candidate tasks**:
1. *Close status + tie-out*: seeded checklist on `sheets` with some tasks done/undone; agent performs the AP tie-out, finds the $X difference caused by a seeded manual JE to the control account, and updates the tracker. Ground truth: the JE and amount.
2. *Flux commentary*: agent computes MoM flux from the ERP TB, identifies the accounts breaching the policy threshold (threshold lives in `docs`), and writes driver commentary recoverable from seeded transactions (e.g., a one-time vendor credit). Ground truth: correct account list + drivers; grade commentary with rubric.

---

## 3. Payment Run / Payment Proposal

**Trigger**: Recurring schedule (e.g., weekly check run Monday, ACH Wednesday); or ad-hoc urgent payment.

**Steps** (D365: Microsoft Learn vendor payment overview + automate-vendor-payment-proposal; SAP F110 in prior research):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Create/select vendor payment journal | D365 AP > Payment journal | `erp` |
| 2 | Run payment proposal — selection criteria: **Due date**, **Cash discount**, or **Due date and cash discount** (picks invoices whose discount date falls in window so the discount is kept); from/to dates, minimum payment date, amount limit, method of payment filters | D365 Payment proposal | `erp` |
| 3 | Review proposal: edit/remove lines, check blocked vendors/invoices, verify no invoice with pending bank-detail change (fraud control, §5) | D365 journal lines + AP clerk judgment | `erp` (+ `email` for pending-change context) |
| 4 | Approval per authorization matrix (often via workflow or email outside the system of record) | ERP workflow / email thread | `erp` or `email` |
| 5 | Create payments → Generate payments: print checks or generate electronic payment file (ISO 20022 pain.001 credit transfer via Electronic reporting) | D365 Generate payments | `erp` |
| 6 | Generate positive-pay file (electronic list of issued checks; bank compares presented checks against it, holds non-matching for review) | D365 positive pay via Electronic reporting | `erp` |
| 7 | Transmit file to bank; confirm acceptance | Bank portal / SFTP | `email` or `sheets` (simulated bank ack) |
| 8 | Post the payment journal; send vendor remittance advice | D365 Post + email | `erp` + `email` |

- **Automation dialect**: D365 "vendor payment proposal automation" schedules proposals via the Process automation framework using *relative* dates ("Number of days adjustment for To date": run Wednesday with +2 → selects invoices due/discount-dated through Friday; "minimum payment date" −2 → earliest pay date Monday). Crucially, "payment proposal automations don't automatically post the payments" — human review/workflow is retained. Statuses: Scheduled / Error / Completed; deleting the created journal reopens invoices (Microsoft Learn).

**Definition of done**: all invoices due in window paid or consciously excluded with reason; all capturable discounts captured; file transmitted and acknowledged; journal posted; remittances sent.

**Failure modes**: discount window missed by scheduling (proposal run after discount date); invoice on hold included; a vendor with a just-changed bank account paid without callback verification; duplicate payment of an invoice already paid manually; run exceeds available cash (link to §8).

**Candidate tasks**:
1. *Build Friday's run*: policy in `docs` (pay due-through-Wednesday + all discounts capturable; exclude vendors with unverified bank changes flagged in `email`); agent selects the invoice set, computes total and discount taken. Ground truth: exact invoice set, payment total, discount dollars (2/10 net 30 math is objectively gradable).
2. *Proposal review*: seeded proposal contains one duplicate, one on-hold invoice, one fraud-flagged vendor; agent must remove exactly those three and post. Ground truth: final journal contents.

---

## 4. Cash Application

**Trigger**: Daily bank receipts (ACH/wire/lockbox); remittance emails in shared mailbox.

**Steps** (J.P. Morgan 7-step guide; HighRadius/Emagia; D365 settle transactions):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Collect payments: checks/lockbox, ACH, wires, cards | Bank / lockbox provider | `sheets` (bank export) |
| 2 | Batch by method/date | AR team convention | `sheets` |
| 3 | Capture remittance detail: attached to ACH addenda, EDI 820, emails to shared AR inbox, customer portals | Email/EDI/portal | `email` |
| 4 | Match payment → customer → open invoices (invoice number, amount, PO ref); one payment may cover many invoices or match none exactly | ERP + remittance | `erp` + `email` |
| 5 | Exceptions: short pays coded as deduction/dispute with owner; missing remittance → unapplied/on-account cash; contact customer | ERP + email outreach | `erp` + `email` |
| 6 | Post + settle: customer payment journal, mark invoices, enter partial amounts where needed | D365 Enter customer payments / Settle transactions | `erp` |
| 7 | Reconcile applied cash to bank records | ERP vs bank statement | `erp` + `sheets` |

- D365 Modern bank reconciliation can generate + settle customer payment journals directly from bank statement lines (Microsoft Learn) — cash application and bank rec converge.
- Unapplied-cash causes: missing remittance, short payments, deductions, wrong invoice references, disputes, bank-vs-ERP timing, bulk payments (Emagia; prior research: 46% of teams cite unapplied cash as top challenge).

**Definition of done**: every receipt applied to specific invoices same/next day; residual unapplied cash has an owner and an outreach in flight; short pays coded; AR subledger reflects reality.

**Failure modes (eval gold)**: one wire pays 5 invoices, remittance in a separate email; short-pay with no explanation (dispute? deduction? early-pay discount taken late?); payment to the wrong entity (parent bank account for a `books`-subsidiary invoice); remittance references a credit memo the ERP lacks.

**Candidate tasks**:
1. *Apply the day's cash*: bank export (`sheets`) + remittance emails (`email`) → agent produces payment-to-invoice settlement mapping and posts it. Ground truth: exact mapping incl. one unapplied residual and one short-pay coded to dispute.
2. *Unapplied-cash aging cleanup*: $40k of seeded on-account cash; agent traces each item to its cause and drafts customer emails. Ground truth: cause per item; email drafts graded by rubric.

---

## 5. Vendor Onboarding + Master Data

**Trigger**: New-vendor request from a requester/procurement; or vendor emails a bank-detail change.

**Steps** (Ramp 5-phase model with day-counts; Stampli; ProcureDesk; MonitorPay):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Pre-onboarding (1–3d): intake request form, validate business need, assign owner | Intake form / email | `email` |
| 2 | Due diligence (3–7d): risk assessment, sanctions/OFAC screening, compliance verification | Screening services | `docs` policy + **UNVERIFIED** mock screening step |
| 3 | Data collection (2–5d): W-9/W-8, banking details, legal entity docs, insurance certs; TIN check + duplicate-vendor check | Vendor portal or email attachments | `email` |
| 4 | Bank verification: verify bank details via controlled channel — vendor portal or **callback to an independently-sourced phone number; never accept bank details or changes by email alone** (MonitorPay; Stampli callback protocol) | Phone callback, documented | `email` (callback log) **UNVERIFIED** how to mock voice step — log artifact instead |
| 5 | Approval: an approver who isn't the requester or validator activates the vendor (segregation of duties) | Workflow | `erp` or `email` |
| 6 | System setup (1–3d): create vendor master record, payment terms, method of payment; record syncs to ERP | D365 vendor master | `erp` |
| 7 | Bank-detail *changes* post-onboarding: same callback + dual approval before any payment uses the new account; for vendors above a payment threshold, re-verify account ownership before each cycle | AP control | `erp` + `email` + `docs` |

**Definition of done**: vendor active in ERP with verified tax + bank data, non-duplicate, approvals documented; first invoice can post and pay without exception.

**Failure modes (eval gold)**:
- **Entity-setup lag**: invoice arrives before vendor exists in ERP → invoice can't post; liability invisible (chaos pattern #2 in prior research). **UNVERIFIED** as a named pattern but directly implied by onboarding lead times (7–18 days across Ramp's phases).
- BEC/vendor-impersonation: "new banking details on a known invoice is the most common loss trigger"; verify via number on file, never the one in the request (Stampli; Corpay; Adaptive Security).
- Duplicate vendor records (same vendor keyed twice → duplicate-payment vector, prior research §2.5).
- W-9 legal name ≠ vendor form name; TIN mismatch.

**Candidate tasks**:
1. *Onboarding queue triage*: shared mailbox holds 6 vendor requests: one complete, one missing W-9, one with TIN/name mismatch, one duplicate of an existing vendor, one bank-change email that fails the callback policy (reply-to domain differs). Agent disposition per policy in `docs`; creates only the valid vendor in `erp`. Ground truth: disposition per request.
2. *Bank-change audit*: given vendor master change log (`erp`) + mailbox, find the change that lacked callback documentation before a payment ran. Ground truth: the specific vendor/payment.

---

## 6. Three-Way Match Exception Handling

**Trigger**: Invoice fails PO/receipt/invoice match and lands in the exception queue.

**Steps** (Klippa; Nexus; engini.ai SAP AI-worker teardown; Tier2):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Pull exception queue: each blocked invoice with discrepancy, related PO + receipt data | ERP match workbench | `erp` |
| 2 | Classify root cause: price variance / quantity variance (invoiced > received) / missing goods receipt / partial delivery / item mismatch / missing PO / duplicate invoice | ERP data comparison | `erp` |
| 3 | Check tolerance: variances within configured threshold (commonly 2–5% price tolerance) auto-approve | ERP tolerance config; policy | `erp` + `docs` |
| 4 | Route by cause: price → procurement; quantity/receipt → receiving/warehouse; variance approval → budget owner | Workflow/email with full context | `email` |
| 5 | Resolve: accept variance, request vendor credit note, obtain corrected goods receipt, or reject invoice | ERP + vendor email | `erp` + `email` |
| 6 | Release invoice for payment; document resolution | ERP | `erp` |

**Definition of done**: exception classified, routed, resolved with documented reason; invoice paid or rejected; GR/IR aged items don't accumulate (90-day/1-year action thresholds, prior research §2.1).

**Failure modes**: receiving never posted the GR (goods physically arrived); vendor invoiced at old price after a price change; partial shipment fully invoiced; the "exception" is actually a duplicate of a paid invoice; tolerance abuse (repeated just-under-threshold overbilling — **UNVERIFIED**, standard audit heuristic).

**Candidate tasks**:
1. *Work the queue*: 8 seeded exceptions covering all root causes; agent classifies each and dispositions per the tolerance table in `docs`, drafting the vendor credit-note request for the price variance. Ground truth: classification + disposition matrix.
2. *GR/IR aging*: find the 8-month-old received-not-invoiced PO line and determine (from vendor emails) whether it's an accrual, vendor error, or duplicate under another PO. Ground truth: seeded answer.

---

## 7. Intercompany Reconciliation

**Trigger**: Close checklist task; consolidation cannot proceed until IC balances agree.

**Steps** (Numeric 6-step framework; Solvexia; AccountsIQ; coefficient.io):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Identify IC transactions: scan GLs/subledgers for intercompany-flagged accounts (service charges, product transfers, loans, royalties, management fees) | Both entities' ledgers | `erp` (parent) + `books` (sub) |
| 2 | Collect + standardize: uniform formats, consistent policies, standardized FX conversion at predetermined rates | Export to workpaper | `sheets` |
| 3 | Match: parent AR vs subsidiary AP must offset exactly; apply materiality thresholds | Matching in workpaper/close tool | `sheets` |
| 4 | Investigate mismatches: timing (wire sent the 30th, recorded by counterparty the 1st–2nd), FX differences, missing entries, incorrect bookings | Both systems + inter-team email | `erp` + `books` + `email` |
| 5 | Book adjustments with documented rationale on the side that's wrong | JE in the deficient system | `erp` or `books` |
| 6 | Eliminate: elimination entries so consolidated statements don't overstate revenue/expenses/assets; eliminate unrealized profit on unsold inventory | Consolidation layer / workpaper | `sheets` (+ `erp`) |
| 7 | Document workpaper + archive evidence for audit | Workpaper | `sheets` |

**Definition of done**: parent-side and sub-side balances equal (or difference fully explained as documented timing), eliminations booked, workpaper archived.

**Failure modes**: management-fee invoice booked by parent, never entered by sub; wire in transit at cutoff; the two systems age/timestamp differently; sub records at different FX rate (**UNVERIFIED** for our USD-only world — likely out of scope); markup on IC inventory not eliminated.

**Candidate tasks**:
1. *IC tie-out (flagship — exercises `erp`+`books` jointly)*: parent IC-receivable $412,300 vs sub IC-payable $371,050; agent decomposes the $41,250 difference (seeded: one in-transit wire + one unbooked management-fee invoice) and drafts the sub-side JE. Ground truth: exact decomposition.
2. *Elimination check*: given both trial balances, compute the elimination entries needed for consolidation. Ground truth: entry list.

---

## 8. Cash Forecasting (13-Week)

**Trigger**: Weekly treasury cadence; or an event (big payment run, covenant test, cash crunch).

**Steps** (Centime; Abacum; Coefficient; Dwight Funding; HighRadius):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Start from opening cash: current bank balances by account/entity | Bank portals / ERP cash position | `erp` + `books` (+ `sheets` bank export) |
| 2 | Build weekly columns ×13; rows grouped by inflow/outflow category; direct method (actual receipts/disbursements at the dates they hit the account) | Excel model | `sheets` |
| 3 | Schedule AR inflows: from AR aging + customer terms/DSO history (who actually pays when, not when due) | ERP AR aging → model | `erp` → `sheets` |
| 4 | Schedule payroll FIRST — largest, most time-sensitive outflow, incl. taxes + benefits | Payroll calendar | `sheets` or `docs` |
| 5 | Schedule AP outflows: AP aging + supplier terms + planned payment runs (§3) | ERP AP aging → model | `erp` → `sheets` |
| 6 | Add rent, debt service, taxes, insurance, capex, subscriptions | Contracts/schedules | `sheets` |
| 7 | Compute: net weekly flow; ending balance = beginning + net; ending feeds next week's beginning | Excel | `sheets` |
| 8 | Compare to minimum-cash threshold; if a week breaches, plan levers: accelerate collections, defer payments, draw financing | Policy + judgment | `docs` + `sheets` |
| 9 | Weekly: compare actual vs forecast, analyze variances, re-forecast ("a living document"); owner: controller/treasury analyst | Excel + bank actuals | `sheets` |

**Definition of done**: 13 weeks of ending balances computed; breach weeks identified with mitigation; weekly variance reviewed and model refreshed.

**Failure modes**: AR scheduled at due date instead of behavioral pay date; payroll week missed (biweekly vs monthly grid mismatch); double-counting a payment run already in AP; stale opening balance (bank vs ERP timing).

**Candidate tasks**:
1. *Build the forecast*: AR aging + AP aging from `erp`/`books` + payroll calendar in `sheets`; agent produces the 13-week grid and identifies the week ending balance dips below the $ minimum in `docs`. Ground truth: arithmetic is fully checkable; breach week is seeded.
2. *Explain the miss*: last week's forecast vs bank actuals differ by $X; agent attributes the variance (a customer paid early, a payment run slipped). Ground truth: seeded attribution.

---

## 9. Audit Support / PBC Lists

**Trigger**: Auditor issues the PBC ("Prepared By Client") list ~30–60 days before fieldwork (Accounting Insights); follow-up sample requests arrive during fieldwork.

**Steps** (Accounting Insights; DataSnipper; Glasscubes; Suralink tick-and-tie):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Receive PBC list (drafted by audit senior/manager from templates + prior year) | Email or audit portal (Suralink/DataSnipper-style) | `email` |
| 2 | Parse requests; typical items: trial balance, GL (current + prior year), bank statements, outstanding-check listings, **AR and AP aging reports reconciled to GL**, customer/vendor listings, major contracts, payroll summaries, board minutes, tax filings | — | — |
| 3 | Pull each artifact from its system of record | ERP reports, bank files, contract drive | `erp`, `books`, `sheets` |
| 4 | For sample selections: provide invoice copies + approval evidence + payment support per sampled transaction | ERP docs + approval email threads | `erp` + `email` |
| 5 | Upload with an index; track submitted/missing/pending status; respond to follow-ups | Portal/status tracker | `email` + `sheets` (request tracker) |
| 6 | Tie-out support: every schedule provided must agree to the GL ("agree totals; if they don't, a reconciliation is performed") | Excel tie-outs | `sheets` |

**Definition of done**: every request fulfilled or status-tracked with owner/date; every schedule ties to GL; follow-ups answered; no "scattered email, misplaced attachments, missed deadlines" (Glasscubes pain-point list).

**Failure modes (eval gold)**: aging report as-of the wrong date; approval evidence exists only in an email thread, not the ERP (chaos pattern #4); the sampled invoice is one of the seeded exceptions (duplicate/unapproved) — the "right" answer is to disclose, not paper over; version drift between the schedule provided and the GL.

**Candidate tasks**:
1. *Fulfill a PBC sublist*: 5 requests (AP aging as of 6/30 tying to GL, bank statement + rec, 3 sampled invoices with approval evidence); agent assembles the package + index. Ground truth: correct artifacts are seeded and enumerable; the tie-out difference (if seeded) must be flagged.
2. *Sample-support hunt*: one sampled invoice's approval lives only in an email thread; agent must find and cite it. Ground truth: the thread.

---

## 10. Credit Review Cadence + Blocked-Order Release

**Trigger**: Order lands on the credit hold list (rule-triggered); or scheduled periodic review comes due; or a trigger event (bounced payment, rating downgrade, bankruptcy news).

**D365 credit-hold machinery** (Microsoft Learn cm-sales-order-credit-holds — richest documented dialect):
- **Blocking rules** respond to: days overdue, account status, terms of payment, credit limit expired, overdue amount (+ credit-limit threshold %), sales order amount, portion of credit limit used; plus riskier payment-term or settlement-discount changes (ranked terms trigger review).
- **Exclusion rules** override blocking rules; processed Table → Group → All; "Release sales order" checkbox releases regardless of other rules.
- Held orders from **all legal entities** flow to one centralized **credit management hold list**; blocking reason(s) displayed ("Multiple" if several).

**Steps (release workflow)**:

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Open hold list; read blocking reason(s) per order | D365 All credit holds | `erp` |
| 2 | Investigate: customer balance, aging, payment history, credit limit utilization; recent payments that may have cleared the reason | D365 customer/collections pages | `erp` |
| 3 | For public customers: refresh financial view (10-K/10-Q ratios per credit policy — prior research §2.4) | EDGAR/bureau data | `filings` |
| 4 | Decide per policy: release (select **Release reason** + **Review date**; release *with posting* re-runs the blocked document posting, or *without posting*), reject, or keep on hold | D365 Release/Reject menus; credit policy thresholds | `erp` + `docs` |
| 5 | Or run **Evaluate for release**: re-runs blocking rules; orders whose reasons cleared become "Ready to release" (auto-release with/without posting per parameter). Forced holds can never auto-release | D365 Evaluate for release | `erp` |
| 6 | Optional approval workflow: release/reject goes through credit management workflow before taking effect | D365 credit management workflows | `erp` |

**Periodic review cadence** (CreditPulse; ClearReceivables; rationalgo): high-exposure accounts (top ~20% of AR) quarterly; standard accounts annually; plus event-triggered reviews (bounced payment, DSO drift, rating downgrade, disputes aging, order-volume spikes, ownership change). Review updates limit, terms, risk rating, next review date (Oracle, prior research).

**Definition of done**: every held order dispositioned with reason code + review date; releases within the deciding role's authority (credit manager vs director per policy); periodic reviews completed on schedule.

**Failure modes**: order blocked for "Multiple" reasons where only one cleared; released order re-blocks at the next checkpoint (confirmation vs packing slip vs invoice); forced hold mistakenly expected to auto-release; sales pressure to release against policy (good judgment test); stale credit limit vs newly-filed deteriorating financials.

**Candidate tasks**:
1. *Work the hold list*: 6 held orders with different blocking reasons; policy in `docs` (e.g., release if overdue cleared or <$1k residual; reject if >90dpd + limit exceeded); one requires pulling the customer's latest 10-Q from `filings` to confirm deterioration. Ground truth: disposition per order + reason codes.
2. *Review-cadence sweep*: from customer master review dates, find accounts overdue for review; run one full review (aging + payment history + filings ratios) and set a new limit per the policy formula. Ground truth: overdue list; limit formula output.

---

## 11. Expense / T&E Audit

**Trigger**: Monthly audit cycle on submitted expense reports; or a fraud tip/anomaly alert.

**Steps** (Emburse expense-audit guide; Oversight; NetSuite):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Choose sample: baseline is review-everything if automated; manual programs sample 20–30% monthly (Oversight); risk-based selection prioritizes cash purchases, frequent travelers, new employees, historically noncompliant departments | Expense system (Concur/Emburse/Ramp) | `sheets` (expense export) + `docs` (policy) |
| 2 | Verify receipts: receipt matches reported amount; documentation present above receipt threshold | OCR/expense tool; manual review | `sheets` (+ `email` receipts) |
| 3 | Policy compliance: approved categories, spending limits, approved vendors, correct authorization level, submission timeliness | Policy engine / checklist | `docs` + `sheets` |
| 4 | Fraud screens: duplicate submissions (same amount/date/merchant, possibly across two reports or card + cash), inflated vs market rates, tampered documents, personal purchases as business | Pattern analysis | `sheets` |
| 5 | Handle findings: communicate first (misunderstanding, data error, missing doc); suspected fraud → dedicated investigation | Email to employee/manager | `email` |
| 6 | Track metrics: exception rate, rejection %, cycle times, violation categories | Dashboard/tracker | `sheets` |

**Definition of done**: sample audited; every violation documented with rule citation; employee communications sent; metrics updated.

**Failure modes (eval gold)**: duplicate claimed on card AND cash; amounts kept just under the receipt-required threshold across many reports (per-report review misses it — Oversight); mileage padding visible only across time; alcohol/personal in a bundled hotel folio (**UNVERIFIED** — common practitioner example); approver = submitter.

**Candidate tasks**:
1. *Audit the batch*: 40 expense lines on `sheets`, policy in `docs`; seeded violations: 1 duplicate pair, 2 over-limit, 1 missing receipt, 1 unapproved category, 1 split-to-avoid-threshold pattern. Ground truth: exact violation list with rule citations.
2. *Cross-report pattern*: violations detectable only by aggregating one employee across 3 months. Ground truth: the employee + pattern.

---

## 12. Quarter-End External Reporting Support

**Trigger**: Quarter close complete; draft 10-Q/press release circulating for tie-out before filing.

**Steps** (DFIN tie-out binders; Universal CPA; Suralink tick-and-tie; Workiva community):

| # | Step | Real tool | Our server |
|---|---|---|---|
| 1 | Finalize quarter close: JEs, reconciliations, accruals, consolidation (§2, §7) | ERP | `erp` + `books` |
| 2 | Build support schedules / lead schedules for every filed number | Excel workpapers | `sheets` |
| 3 | **Tie-out**: agree *every single number* in the draft filing back to workpapers/GL — trace, tick-mark, agree totals; "if they don't agree, a reconciliation is performed to find and fix the difference" | Tie-out binder (paper or DFIN/Workiva) | `sheets` + `erp` + draft in `docs` |
| 4 | XBRL tagging of statements + notes; roll forward tags 10-Q→10-K via linked spreadsheets | Workiva-type tool | `filings` (as the published artifact) |
| 5 | File; the filed 10-Q becomes public | EDGAR | `filings` |
| 6 | Post-filing uses: our finance team ties *counterparties'* filed numbers into credit reviews and briefs (§10; prior research §2.4/§2.6) | EDGAR APIs | `filings` |

**Definition of done**: zero untied numbers in the filing; tie-out binder complete with support for each figure; XBRL consistent with the HTML statements.

**Failure modes**: draft revised after tie-out (version drift); rounding/presentation differences (thousands vs millions) mistaken for errors; a note figure sourced from an offline spreadsheet nobody reconciled; prior-period comparative doesn't match what was actually filed last quarter.

**Candidate tasks**:
1. *Tie-out check*: draft earnings-release excerpt in `docs` vs trial balance in `erp` + last quarter's filed 10-Q in `filings`; agent finds the 2 seeded numbers that don't tie (one transposition, one stale prior-period comparative). Ground truth: the discrepancies.
2. *Counterparty cross-check*: verify claims in an internal credit memo against the customer's actual filed 10-Q figures in `filings`; flag the wrong ratio. Ground truth: seeded error.

---

## 13. Teardowns: What Shipping Finance Agents Actually Do

Proof of which workflows are agent-relevant *today*, and design patterns worth copying.

### 13.1 Microsoft FinanceBenchmark (the buyer's own eval)
GitHub `microsoft/FinanceBenchmark` + Microsoft 365 Copilot blog. Three task categories (~300 questions):
1. **Financial Obligation queries (ERP QA)** — internal AP/AR questions answered by querying a live **MCP server connected to Dynamics 365 Finance** with **synthetic AP/AR data** ("What is the outstanding receivables balance for Birch Company as of March 2, 2026?"; sample ERP queries include vendor payment terms, outstanding balances, **collection letter levels**).
2. **Financial entity performance research** — public figures (earnings, ratios, cash flows, ESG) from live internet sources incl. SEC filings and MSN Money ("What was Tesla's GAAP operating margin for the September 2025 quarter?").
3. **Business briefs** — "structured company profile synthesising public financial data, business context, and — where available — internal ERP data" ("Business Brief report of Apple Inc.").
Scoring: LLM judge (GPT 5.2) grounded in per-metric rubric assertions; results (May 8, 2026) compare Finance Agent vs OpenAI Responses API vs **Claude Code CLI**. **Implication**: finance-world's ERP-QA + research + brief triad matches the buyer's eval exactly; "collection letter level" should be a queryable field in our ERP mock.

### 13.2 Finance Agent in Microsoft 365 Copilot (GA Oct 20, 2025; Home/Chat preview 2026)
Capabilities (MS blog/search summaries; Nexairi): **Financial Reconciliation** (below), **Variance analysis** — pivot-table + time-series analysis where the user states criteria in natural language and the agent "identifies key drivers and produces structured summaries," and **Financial data preparation** — cleanse/standardize/enrich inconsistent datasets. Separate license on top of Copilot. **UNVERIFIED** details beyond marketing summaries (blog body not fetchable).

### 13.3 Copilot Financial Reconciliation agent in Excel (Microsoft Learn — full mechanics)
Assistive *or* autonomous (autonomous requires a saved template). Flow: select two Excel tables → agent AI-suggests **mapping keys + monetary keys** (user can Keep/Regenerate/Remove; modifiers for partial matching, amount tolerances, no-monetary-key matching) → reconcile → report classifies every transaction: **Matched**, **Potentially matched** (keys+amounts match but 1:N/N:1/N:N combinations), **Unmatched: "Discrepancy Unmatched"** (keys match, amounts differ) vs **"Exclusively Unmatched"** (no counterpart) → aggregation IDs + reconciliation IDs for traceability, "_reconciled" copies of source sheets → generative summary + **Troubleshoot transactions** (per-row explanation + next steps). **Implication**: this taxonomy (matched / potential / discrepancy / exclusive) is a ready-made grading schema for any reconciliation task in our world.

### 13.4 D365 Account Reconciliation Agent (production-ready preview, 10.0.44+)
Continuous subledger→GL reconciliation across **AP, AR, bank, and tax**; raises exceptions in the Account reconciliation workspace; agent evaluates and recommends per exception — for **Voucher amount mismatch**: "Create journal entry," alternatives Reverse / Link transactions / Accept without change; second exception type "Pending accounting transferred to general ledger"; every action logged with undo. **Implication**: exception-plus-recommended-action is the task shape ("here are the exceptions; disposition each").

### 13.5 D365 vendor payment proposal automation
Scheduled proposals via Process automation with relative-date criteria; creates but never posts the journal — human validation/workflow retained (§3). **Implication**: agent builds the run, human releases; our tasks should grade the *proposal*, and can make posting a separate approval step.

### 13.6 Ramp Agents for AP (launched Oct 7, 2025)
Three agents inside Bill Pay: **invoice coding** ("85% of accounting fields right the first time," learning per cycle), **approval** (recommendation + summary of "vendor history, contracts, prior bills, and coding consistency" so approvers don't search), **payment processing** (finds card-payment opportunities "directly in the vendor's payment portal"). CTO claims near-100% automation on some workflows. **Implication**: coding + approval-context-assembly + portal actions are proven agent surfaces.

### 13.7 HighRadius O2C agent roster
Named agents: **Cash application** ("captures remittances from emails and portals, matches them to payments, and posts to ERP," 90%+ automation; agentic version "log[s] into portals, read[s] emails, and reason[s] through complex remittances"); **Collections** (analyzes payment behavior/aging/risk → prioritized call list; drafts follow-up emails; updates notes); **Credit** (fetches financial docs, calculates ratios, verifies references, flags inconsistencies); **Deductions** (reviews reason codes, checks backup like contracts/notes, validates or escalates); **EIPP** (invoice delivery/payment tracking). **Implication**: cash app + collections + credit are the most agent-mature AR workflows.

### 13.8 Auditoria.AI SmartBots
**AP Helpdesk**: continuously monitors the **shared AP email inbox** and "respond[s] conversationally to inquiries on approval status, invoice payments, short pay issues, and missed invoices." **SmartCustomer**: prioritizes receivables, executes collections outreach, matches remittances, applies cash. Also automates vendor onboarding, accruals, audit readiness. **Implication**: strongest external validation for our shared-mailbox server as a first-class agent surface — inbox-driven Q&A ("has invoice X been approved?") is a shipping product category.

### 13.9 Agent-relevance ranking (synthesis — **UNVERIFIED** as ranking, grounded in the teardowns above)
Tier 1 (multiple shipping products): reconciliation (bank + subledger + generic two-dataset), cash application, collections, AP invoice coding/approval/exceptions, inbox Q&A on AP/AR status.
Tier 2 (shipping but thinner): credit evaluation/blocked orders, vendor onboarding, variance/flux analysis, T&E audit (Oversight/AppZen category), payment-run assembly.
Tier 3 (agent-assisted, human-led): 13-week forecast, intercompany, PBC/audit support, external-reporting tie-out — high eval value precisely because they're multi-system judgment work with objective arithmetic ground truth.

---

## Sources

### Bank reconciliation
- https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/reconcile-bank-statements-advanced-bank-reconciliation
- https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/advanced-bank-reconciliation-overview
- https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/configure-advanced-bank-reconciliation
- https://www.forvismazars.us/forsights/2025/06/advanced-bank-reconciliation-in-dynamics-365-finance
- https://stoneridgesoftware.com/advanced-bank-reconciliation-configuration-guide-for-dynamics-365-finance/
- https://quickbooks.intuit.com/learn-support/en-ca/help-article/reconciliation-reports/reconcile-account-quickbooks-online/L96JWj4je_CA_en_CA
- https://ezqgroup.com/blog/how-to-reconcile-in-quickbooks-online-step-by-step/
- https://bankreconciler.app/blogQuickBooksReconciliation

### Month-end close & flux
- https://trullion.com/blog/month-end-close-checklist/
- https://dokka.com/month-end-close-checklist/
- https://checkflow.io/blog/month-end-close-checklist
- https://www.finlens.app/tools/month-end-close-checklist
- https://ramp.com/blog/flux-analysis
- https://www.netsuite.com/portal/resource/articles/accounting/flux-variance-analysis.shtml
- https://doublehq.com/blog/what-is-flux-analysis-accounting/
- https://www.runfutureproof.com/articles/month-end-close

### Payment run
- https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/tasks/vendor-payment-overview
- https://learn.microsoft.com/en-us/dynamics365/finance/accounts-payable/automate-vendor-payment-proposal
- https://dynamicscommunities.com/ug/creating-a-payment-proposal-in-dynamics-365-finance-operations/
- https://www.d365training.com/post/payment-proposals-in-d365-finance-setup-and-controls
- https://learn.microsoft.com/en-us/dynamics365/finance/accounts-payable/positive-pay-overview
- https://learn.microsoft.com/en-us/dynamics365/finance/accounts-payable/set-up-positive-pay-er
- https://dynatechconsultancy.com/blog/generating-sepa-iso-20022-credit-transfer-payment-file

### Cash application
- https://www.jpmorgan.com/insights/treasury/receivables/the-cash-application-process-a-how-to-guide
- https://www.highradius.com/resources/Blog/cash-application/
- https://www.emagia.com/blog/what-is-cash-application/
- https://monk.com/blog/what-is-remittance-matching
- https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/apply-cash-adv-bank-rec
- https://learn.microsoft.com/en-us/dynamics365/finance/cash-bank-management/tasks/customer-payment-overview
- https://www.loganconsulting.com/blog/a-comprehensive-overview-of-the-financial-transaction-settlement-process-in-microsoft-dynamics-365-finance/

### Vendor onboarding & fraud controls
- https://ramp.com/blog/vendor-onboarding
- https://www.stampli.com/resources/vendor-onboarding-accounts-payable/
- https://www.procuredesk.com/vendor-onboarding-process/
- https://monitorpay.ai/vendor-onboarding-checklist-how-to-verify-every-new-supplier-before-the-first-payment/
- https://www.stampli.com/resources/vendor-bank-change-callback-protocol/
- https://www.corpay.com/resources/blog/business-email-compromise-ap
- https://www.adaptivesecurity.com/blog/prevent-business-email-compromise
- https://www.financialprofessionals.org/training-resources/resources/articles/Details/managing-vendors-to-prevent-fraud

### 3-way match exceptions
- https://www.klippa.com/en/blog/information/three-way-matching/
- https://www.nexusap.com/blog/three-way-matching-accounts-payable
- https://engini.ai/blog/ap-3-way-match-sap-automation-ai-workers
- https://tier2systems.com/en/blog/three-way-match-ap-guide/
- https://www.zoneandco.com/glossary/3-way-match

### Intercompany
- https://www.numeric.io/blog/intercompany-reconciliation
- https://www.solvexia.com/blog/intercompany-reconciliation
- https://www.accountsiq.com/blog/intercompany-eliminations-explained
- https://coefficient.io/cfo-resources/intercompany-reconciliation
- https://www.glencoyne.com/guides/intercompany-elimination-errors-fixes

### 13-week cash forecast
- https://www.centime.com/posts/13-week-cash-flow-forecast
- https://www.abacum.ai/blog/13-week-cash-flow
- https://coefficient.io/cfo-resources/build-cashflow-forecasting-in-excel
- https://dwightfunding.com/the-practical-guide-to-establishing-a-13-week-cash-flow-model/
- https://www.highradius.com/resources/Blog/build-13-week-cash-flow-forecast/

### Audit support / PBC & tie-out
- https://accountinginsights.org/what-is-a-pbc-list-in-an-audit-and-what-is-included/
- https://www.datasnipper.com/resources/what-is-a-pbc-list
- https://www.glasscubes.com/what-is-pbc-list-in-audit-a-comprehensive-overview/
- https://www.dfinsolutions.com/knowledge-hub/thought-leadership/knowledge-resources/financial-statement-tie-out
- https://www.universalcpareview.com/ask-joey/what-is-the-financial-statement-tie-out/
- https://www.suralink.com/blog/tick-and-tie
- https://support.workiva.com/hc/en-us/community/posts/360062563052-XBRL-rollforward-10-Q-to-10-K

### Credit management & blocked orders
- https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/cm-sales-order-credit-holds
- https://dynamics-tips.com/credit-management-blocking-rules/
- https://www.creditpulse.com/blog/credit-limit-management-b2b-guide
- https://clearreceivables.com/blog/credit-management-best-practices
- https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/collections-credit-accounts-receivable
- https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/tasks/process-collection-letters

### T&E audit
- https://www.emburse.com/resources/expense-report-audit-guide-for-finance-teams
- https://www.oversight.com/blog/9-questions-to-evaluate-your-te-expense-risk
- https://www.netsuite.com/portal/resource/articles/financial-management/t-e-report-managements.shtml
- https://safebooks.ai/resources/financial-audit/preparing-for-an-expense-audit-checklist-best-practices-2025/

### Agent teardowns
- https://github.com/microsoft/FinanceBenchmark
- https://techcommunity.microsoft.com/blog/microsoft365copilotblog/finance-agent-benchmark-evaluating-and-improving-ai-for-finance/4522978
- https://techcommunity.microsoft.com/blog/microsoft365copilotblog/scaling-the-reach-of-finance-what%E2%80%99s-next-with-finance-agent-in-microsoft-365-cop/4522976
- https://www.microsoft.com/en-us/dynamics-365/blog/it-professional/2025/10/20/empowering-finance-with-an-ai-assistant-in-microsoft-365-copilot/
- https://learn.microsoft.com/en-us/copilot/finance/reconcile/reconcile-data
- https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/acct-rec-agent
- https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/configure-acct-recon-agent
- https://www.cpapracticeadvisor.com/2025/10/07/ramp-launches-accounts-payable-agents/170422/
- https://www.prnewswire.com/news-releases/ramp-launches-agents-for-ap-to-automate-accounts-payable-302576975.html
- https://www.pymnts.com/news/artificial-intelligence/2025/ramp-adds-ai-agents-invoice-coding-approval-payment-processing/
- https://www.highradius.com/resources/Blog/an-introduction-to-ai-agents-for-the-order-to-cash-process/
- https://www.highradius.com/product/order-to-cash-automation-software/
- https://www.auditoria.ai/
- https://marketplace.intacct.com/MPListing?lid=a2D0H00000gluj4UAA
- https://info.auditoria.ai/hubfs/FY25_SDN_Partner_Datasheet_Auditoria.AI_Overview.pdf
