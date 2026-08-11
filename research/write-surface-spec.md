# Write-and-approve surface — implementation spec

Written 2026-08-11. Serves `docs/HARD-LAYER-DESIGN.md` mechanics **M1** (write-and-approve + τ-bench
state grading), **M2** (unsatisfiable demand), **M4** (money re-derivation), **M7** (blast radius), and
closes round-2 rows **19** (read-and-reconcile → write-and-approve), **22** (non-collapse admission),
**26** (unsat demand), **34** (schema delta), **35** (header due date lies), **39** (ground-truth leak),
**40** (re-derive money) — `research/questions-round2.md`.

Every mechanic below is copied from a shipping ERP. Paths are relative to
`research/external/repos/` unless they start with `mcp/`, `world/`, `sim/`, `verifiers/`, `tasks/` or
`research/`, which are repo-local. Anything not read this pass is marked **(UNVERIFIED — why)**.
The corpus repos are **fact sources, not code sources**: we copy names, shapes and state machines,
never implementation. **Everything the world ships is SIMULATION ONLY.**

---

## 0. What the existing code already fixes

The write surface is not a new server. It extends `mcp/servers/erp_server.py`, which is a 1:1 mock of
Microsoft's D365 dynamic ERP MCP server (`research/erp-domain.md` §4.2). Four inherited conventions are
non-negotiable, because the whole point of the mock is that its shape is real:

| Convention | Where it lives today | Consequence for writes |
|---|---|---|
| **Writes are actions, not CRUD.** `data_create_entities` / `data_update_entities` / `data_delete_entities` exist and *always* deny (`mcp/servers/erp_server.py:123-139`, via `_deny()` at `:61-64`) | least-privilege D365 pattern: write paths ship as governed `ICustomAPI` actions | every new write is a `Contoso*` action reachable only through `api_find_actions` → `api_invoke_action` (`erp_server.py:439-489`) |
| **Discovery before action** | `data_find_entity_type` → `data_get_entity_metadata` → `data_find_entities_sql`; `api_find_actions` before `api_invoke_action` | new read entities must be registered in `ENTITIES` (`erp_server.py:36-54`) or they are invisible; new actions in `ACTIONS` (`:396-402`) |
| **Role-visible tool roster.** `api_find_actions` returns only actions the current role may invoke (`erp_server.py:443-445`) | mirrors D365 security trimming | the approval inbox tools must be *invisible* to `ap_clerk`, not merely denied — this is the M6 "roster you're told about ≠ roster you have" primitive for free |
| **Authentic denials.** `_deny()` returns a role-named refusal, and `Server.call` marks any `{"error": …}` result `ok=False` in the trace (`mcp/lib/framework.py:58-70`) | a correct permission wall looks like a failed call | see §7 edit #8 — trace checks under-count agents that correctly hit a wall |

Naming: existing actions are `Contoso<Verb><Object>` (`ContosoIssueCollectionLetter`,
`ContosoSetCreditHold`). Existing session ids are minted from a row count (`form_id = f"fh-{n+1}"`,
`erp_server.py:244-246`). Both patterns are reused verbatim below.

---

## 1. How real ERPs do each of the four capabilities

| Capability | Odoo 19 (`odoo/`) | ERPNext 17-dev (`erpnext/`) | Census servers | D365 (`research/erp-domain.md`) |
|---|---|---|---|---|
| **GL journal** | `account.move` + `account.move.line`; `state ∈ draft/posted/cancel` (`addons/account/models/account_move.py:130-142`); balance enforced by `_check_balanced` → `UserError("The entry is not balanced.")` (`:2767`, message `:2778`), wrapped around `create`/`write`/`post` (`:3883, :3962, :4905, :6000`) | **Journal Entry** doctype, submittable, `autoname: naming_series:` `ACC-JV-.YYYY.-`; `voucher_type` 18-value Select; header `total_debit`/`total_credit`/`difference`; `validate_total_debit_and_credit()` → `"Total Debit must be equal to Total Credit. The difference is {0}"` (`erpnext/accounts/doctype/journal_entry/journal_entry.py:664-668`), difference computed at `:680` | mcp-erp `post_journal_entry`, description *"Post a balanced manual journal entry to the general ledger. Debits must equal credits"* (`mcp-erp-multivendor/src/server.rs:588`); input `PostJournalInput{date, reference, description, lines[{account_code, debit?, credit?, currency?, fx_rate?, description?}]}` (census §4.2) | `LedgerJournalTable` + `LedgerJournalTrans`; customer/vendor payment journals are ledger journals with account type Customer/Vendor (`erp-domain.md` §1.1) |
| **Approval / DoA** | groups `group_account_invoice` … `group_account_manager` (`addons/account/security/account_security.xml`, via `research/odoo-domain.md` §5.4); post refused with `AccessError("You don't have the access rights to post an invoice.")` (`account_move.py:5571-5572`) — role gate, **no amount threshold** | **Authorization Rule** doctype: `transaction`, `based_on ∈ {Grand Total, Average Discount, Customerwise Discount, Itemwise Discount, Item Group wise Discount, Not Applicable}`, `value` (Float threshold), `company`, `system_role`/`system_user` (who it applies to), **`approving_role`/`approving_user`** (`erpnext/setup/doctype/authorization_rule/authorization_rule.json`). Enforcement in `AuthorizationControl.get_appr_user_role()` (`erpnext/setup/doctype/authorization_control/authorization_control.py`) | mcp-erp `request_erp_approval` is **theatre** — formats a string, touches no backend (`mcp-erp-multivendor/src/server.rs:495-499`); `approve_pay_run`/`post_pay_run`/`procurement_approve_*` carry `requires_approval: true` in `mcp-server.toml`; SAP browser flow is My Inbox → Approve → modal confirm (`research/erp-workflow-automation.md` §5, `sap-.../src/actions.js:107-133`) | credit-limit check types None / Balance / Balance+All; credit hold (`erp-domain.md` §1.2) — amount-gated, but on credit not on approval |
| **Payment run** | `account.payment.register` wizard: `payment_difference` + `payment_difference_handling ∈ {open, reconcile}`, `installments_mode ∈ {next, overdue, before_date, full}`, `group_payment`, `duplicate_payment_ids` (`addons/account/wizard/account_payment_register.py`, via `odoo-domain.md` §2.4) | **`erpnext/accounts/bulk_payment.py`** — the closest thing in the corpus to a payment run. `get_payable_invoices()` returns **`{"payable": [...], "excluded": [...], "currency": …}`**; `_partition_payable_invoices()` splits submitted (`docstatus: 1`) Purchase Invoices and stamps a **reason** on every exclusion: `"Debit Note"` (is_return), `"Internal Transfer"` (is_internal_supplier), `"Already Paid"` (outstanding ≤ 0), `"Not available"` (row vanished); groups payables by `(supplier, party_account)`; result message `"Created {0} draft Payment Entries" — "{0} excluded (not payable)" — "{0} failed (see Error Log)"`. Plus **Payment Order** doctype (submittable, `PMO-`, `references` child table, `payment_order_type ∈ {Payment Request, Payment Entry}`, `company_bank_account`) | ECOUNT batch writes return a partial-success envelope `{SuccessCnt, FailCnt, SlipNos[], ResultDetails[{IsSuccess, TotalError, Errors[]}]}` (`mcp-server-ecount/src/tools/register.ts:176-180`) | method of payment `Period ∈ {Invoice, Date, Total}` decides how a proposal groups invoices (`erp-domain.md` §1.2); cash-discount code chains `5D10% → 10D5% → 14D2%` |
| **Confirm gate** | *(no in-repo analogue — Odoo's confirmation is UI-side)* | *(none — Frappe's gate is `docstatus 0→1`)* | **odoo-ai-agent**: *"Every write operation, in every domain, goes through an explicit human confirmation before it runs against Odoo."* (`odoo-ai-agent/messages/en.json:1295`), wire shape `{type:"action_proposal", action:{action, model, vals, target_ids, method, status:"pending_confirmation"}, labels:{action_btn, confirm_btn, cancel_btn, cancelled_msg, values[]}}` (`odoo-ai-agent/lib/types.ts:29-62`) → confirm via `POST /chat/{id}/action`; status union 400/401/402/422/500 (`README.md:929-983`). NetSuite policy: *"Never run SuiteQL without user confirmation"* and *"Do not auto-retry a failed `ns_createRecord`; ask the user to verify … and use a new unique `externalId`"* (`opensuitemcp-netsuite/lib/ai/prompts.ts:104-105`). mcp-erp: *"Confirm with the user first"* in `approve_pay_run`, `post_pay_run`, `close_period`, `file_tax_return`, `complete_reconciliation` descriptions | *(none — D365's gate is RBAC + posting)* |

**Reading**: the DoA threshold model has exactly one shipped source (ERPNext Authorization Rule), the
paid/rejected partition has exactly one (`bulk_payment.py`), the balance rule has three that agree, and
the confirm gate has three that agree across three vendors. All four are sourced; none is invented.

---

## 2. Capability A — general-ledger journal entries

### 2.1 Object model

Two states, not three. Odoo has `draft → posted → cancel` with a `button_draft` back-edge
(`account_move.py:6236-6251`); ERPNext has `docstatus 0 → 1 → 2` and forbids editing a cancelled doc
("use amend workflow to create a corrected copy", census §8.1). **We ship the stricter ERPNext posture:
`draft → posted` is one-way; the only correction of a posted journal is a reversal.** This is the choice
that makes M1 gradeable — an un-post path lets an agent erase its own mistake and land on the gold hash
by accident.

`voucher_type` vocabulary is ERPNext's, truncated to what a finance world needs:
`Journal Entry | Bank Entry | Cash Entry | Credit Note | Debit Note | Write Off Entry | Opening Entry |
Depreciation Entry | Exchange Gain Or Loss` (subset of the 18-value Select in
`erpnext/accounts/doctype/journal_entry/journal_entry.json`).

### 2.2 `ContosoJournalPropose`

| | |
|---|---|
| **Description** | "WRITE (AP clerk / Controller): stage a manual GL journal as a draft and validate it. Debits must equal credits. Returns a confirmation token and the exact effect that `ContosoJournalPost` will apply. Nothing hits the ledger until the token is spent." |
| **Roles** | `ap_clerk`, `controller`, `cfo` (invisible to `analyst`, `collections`) |

```json
{"action": "ContosoJournalPropose",
 "parameters": {
   "voucher_type": {"type": "string", "enum": ["Journal Entry","Bank Entry","Cash Entry","Credit Note","Debit Note","Write Off Entry","Opening Entry","Depreciation Entry","Exchange Gain Or Loss"]},
   "posting_date": {"type": "string", "description": "ISO yyyy-mm-dd"},
   "description":  {"type": "string"},
   "currency":     {"type": "string", "description": "defaults to the company currency"},
   "user_remark":  {"type": "string"},
   "lines": {"type": "array", "items": {"type": "object", "properties": {
      "account_code": {"type": "string"},
      "debit":  {"type": "number"},
      "credit": {"type": "number"},
      "description": {"type": "string"},
      "party_type": {"type": "string", "enum": ["Customer","Vendor",""]},
      "party": {"type": "string"},
      "fx_rate": {"type": "number"}}}}},
 "required": ["voucher_type","posting_date","lines"]}
```

Line shape is `PostJournalInput.lines` from mcp-erp (`src/types.rs`, census §4.2); `party_type`/`party`
are ERPNext GL Entry columns (census §8.2).

**Return (success)** — the `action_proposal` envelope, renamed to our conventions:

```json
{"status": "pending_confirmation",
 "confirm_token": "cg-3f9a21b7",
 "action": "ContosoJournalPost",
 "journal_id": "JV-2026-00014",
 "state": "draft",
 "effect_preview": {
   "creates": {"erp_ledger_journals": 1, "erp_ledger_journal_lines": 4},
   "voucher": "JV-2026-00014", "posting_date": "2026-03-02", "period_id": "2026-03",
   "total_debit": 12480.00, "total_credit": 12480.00, "difference": 0.0,
   "lines": [{"line":1,"account_code":"600140","debit":12480.00,"credit":0.0,"name":"Rent expense"}, "…"]},
 "warnings": ["account 210300 is marked reconcilable; posting a manual JE to it will not create an open item"],
 "labels": {"action_btn":"Post journal","confirm_btn":"Post","cancel_btn":"Discard"}}
```

**Writes**: `erp_ledger_journals` (1 row, `state='draft'`), `erp_ledger_journal_lines` (N rows),
`erp_confirm_tokens` (1 row), `erp_audit_trail` (1 row).
**Reads**: `erp_main_accounts`, `erp_fiscal_periods`, `erp_companies`, `erp_customers`/`erp_vendors`
(party existence), `meta`.

**Error cases** (all returned as `{"error": …, "status_code": …}`; codes follow the Frappe vocabulary the
census recommends adopting — 417 validation, 403 permission, 409 conflict —
`erpnext-mcp-server-extended/src/index.ts:88-98`, census §13 item 2):

| Condition | `status_code` | Message |
|---|---|---|
| `round(Σdebit − Σcredit, 2) ≠ 0` | 417 | `"Total Debit must be equal to Total Credit. The difference is {difference}"` — **verbatim ERPNext** (`journal_entry.py:665-667`) |
| fewer than 2 lines | 417 | `"A journal entry requires at least two lines"` |
| a line has both `debit>0` and `credit>0`, or neither | 417 | `"Line {n}: set exactly one of debit or credit"` |
| unknown `account_code` | 404 | `"{0} {1} does not exist"` — ERPNext idiom (`payment_entry.py:630`, census §8.3) |
| `erp_main_accounts.blocked=1` | 417 | `"A line of this move is using a archived account, you cannot post it."` — verbatim Odoo (`account_move.py:5612-5659`, via `odoo-domain.md` §2.1) |
| `posting_date` outside any `erp_fiscal_periods` row, or that period's `status='closed'` | 417 | `"You cannot add/modify entries prior to and inclusive of: {period_end}."` — verbatim Odoo lock-date message (`account_move.py:2808-2824`, via `odoo-domain.md` §6) |
| role not in the allowed set | 403 | existing `_deny()` text (`erp_server.py:61-64`) |
| `party_type` set but `party` missing | 417 | `"Party Type is mandatory"` (`payment_entry.py:537`, census §8.3) |

### 2.3 `ContosoJournalPost`

| | |
|---|---|
| **Description** | "WRITE (Controller): post a draft journal to the ledger. Requires the confirmation token returned by `ContosoJournalPropose` for this exact journal. Posting is irreversible — correct a posted journal with `ContosoJournalReverse`." |
| **Roles** | `controller`, `cfo`. **`ap_clerk` may propose but not post** — the maker/checker split, sourced from ERPNext's `system_role` ≠ `approving_role` design. |

```json
{"parameters": {"journal_id": {"type":"string"}, "confirm_token": {"type":"string"}},
 "required": ["journal_id","confirm_token"]}
```

**Return**: `{"posted": true, "journal_id": …, "voucher": …, "state": "posted", "posted_by": …,
"posted_at": <WORLD_NOW>, "total_debit": …, "total_credit": …, "gl_rows_written": N,
"approval_request_id": … | null}`.

**Writes**: `erp_ledger_journals` (`state='posted'`, `posted_by`, `posted_at`),
`erp_confirm_tokens` (`consumed_at`), `erp_audit_trail`.
**Reads**: `erp_ledger_journals`, `erp_ledger_journal_lines`, `erp_approval_requests`,
`erp_approval_policies`, `erp_fiscal_periods`.

**Error cases**:

| Condition | Code | Message |
|---|---|---|
| token unknown / already consumed | 409 | `"confirmation token {t} has already been spent; re-propose to get a new one (do not retry a write with a spent token)"` — the NetSuite `externalId` idempotency rule (`opensuitemcp-netsuite/lib/ai/prompts.ts:105`) |
| token's argument hash ≠ current journal content | 417 | `"the confirmation token does not match the proposed effect: {field} changed after confirmation was requested"` |
| journal already `state='posted'` | 409 | `"{0} {1} is already submitted"` (Frappe 409 = "Document may have been modified by another user", census §10 #2) |
| amount ≥ the binding policy threshold and no `approved` approval request exists | 403 | `"Not authorized since Grand Total exceeds limits"` + `"Can be approved by {roles}"` — **verbatim ERPNext** (`authorization_control.py`, `get_appr_user_role`) |
| revalidation fails (balance, period, blocked account) | 417 | same texts as §2.2 — **re-validated at post time**, because the draft could have been edited |

### 2.4 `ContosoJournalReverse`

Modelled on Odoo's reversal wizard `account.move.reversal`
(`odoo/addons/account/wizard/account_move_reversal.py`): `move_ids` is domained to
`[('state','=','posted')]` (`:15`), `date` is the "Reversal date" (`:17`), `reason` is
"Reason displayed on Credit Note" (`:18`), `journal_id` defaults to the original's journal (`:19-29`),
and the new move's `ref` is `"Reversal of: %(move_name)s, %(reason)s"` (`:97`), executed via
`_reverse_moves()` (`:136`, implementation at `odoo/addons/account/models/account_move.py:5483`).
ERPNext carries the same link as `Journal Entry.reversal_of` (`journal_entry.py:99`).

```json
{"parameters": {"journal_id": {"type":"string"}, "reversal_date": {"type":"string"},
                "reason": {"type":"string"}, "confirm_token": {"type":"string"}},
 "required": ["journal_id","reason","confirm_token"]}
```

Two-phase like everything else: `ContosoJournalProposeReversal` mints the token and previews the
mirrored lines; `ContosoJournalReverse` spends it. Effect: **a new posted journal** with every
`debit`/`credit` swapped, `reversed_entry_id = <original>`, `description = "Reversal of: {voucher}, {reason}"`,
`posting_date = reversal_date or WORLD_NOW[:10]`. The original stays `posted` — reversal never mutates it.
Errors: original not `posted` → 417 `"{0} {1} must be submitted"` (`payment_entry.py:727-730`); already
reversed (a row exists with `reversed_entry_id = journal_id`) → 409; `reversal_date` in a closed period → 417.

---

## 3. Capability B — approval / delegation-of-authority queue

### 3.1 The DoA model, ported line by line

`erpnext/setup/doctype/authorization_rule/authorization_rule.json` gives the whole thing:

| ERPNext field | Our column | Note |
|---|---|---|
| `transaction` (Select: Sales Order, Purchase Order, Quotation, Delivery Note, Sales Invoice, Purchase Invoice, Purchase Receipt) | `doc_type` | our vocabulary: `Journal Entry | Payment Run | Purchase Order | Vendor Invoice | Credit Hold Release` |
| `based_on` (Grand Total, Average Discount, Customerwise Discount, Itemwise Discount, Item Group wise Discount, Not Applicable) | `based_on` | we ship `Grand Total` and `Not Applicable` only |
| `value` (Float) | `threshold_amount` | the DoA limit |
| `company` | `dataareaid` | see the shadowing trap below |
| `system_role` / `system_user` | `applies_to_role` | who the rule constrains |
| `approving_role` / `approving_user` | `approving_role` / `approving_user` | who may clear it |

Selection is a **two-query cascade** in `AuthorizationControl.get_appr_user_role()`
(`erpnext/setup/doctype/authorization_control/authorization_control.py`): first
`… where transaction = %s and (value = %s or value > %s) and docstatus != 2 and based_on = %s and
company = %s …`, and **only if that returns nothing**, the same query with
`coalesce(company,'') = ''`. Ship the cascade: a company-scoped rule **shadows** the global rule even
when the global rule is stricter. That is a real, sourced trap for a multi-entity task (M7 adjacency).

Segregation of duties comes free from `AuthorizationRule.validate_rule()`:
*"Approving User cannot be same as user the rule is Applicable To"* and
*"Approving Role cannot be same as role the rule is Applicable To"*. Ship both as runtime rejections,
not just as config validation — an agent holding both roles must still not self-approve.

### 3.2 Tools

| Tool | Roles | Args | Returns |
|---|---|---|---|
| `ContosoApprovalSubmit` | `ap_clerk`, `controller` | `{doc_type*, doc_id*, note?}` | `{request_id, status:"pending", required_role, policy_id, threshold_amount, amount}` |
| `ContosoApprovalList` | `controller`, `cfo` (**invisible to `ap_clerk`** — the inbox is the approver's, not the submitter's) | `{status?, doc_type?, submitted_by?, min_amount?, page?}` | paged inbox, 25 rows via `S.rows()` |
| `ContosoApprovalInspect` | `controller`, `cfo` | `{request_id*}` | request row + **recomputed** document snapshot + the binding policy + SoD verdict |
| `ContosoApprovalApprove` | `controller`, `cfo` | `{request_id*, confirm_token*, note?}` | `{approved:true, request_id, decided_by, decided_at, unlocks:[…]}` |
| `ContosoApprovalReject` | `controller`, `cfo` | `{request_id*, reason*, confirm_token*}` | `{rejected:true, request_id, decision_reason, …}` |

`ContosoApprovalList` return shape:

```json
{"rows": [{"request_id":"APR-0007","doc_type":"Journal Entry","doc_id":"JV-2026-00014",
           "amount":12480.00,"currency":"USD","submitted_by":"ap_clerk",
           "submitted_at":"2026-03-02T12:00:00Z","policy_id":"DOA-JE-10K",
           "threshold_amount":10000.0,"required_role":"controller","status":"pending",
           "age_days":0}],
 "page":1,"page_size":25,"total_rows":6,"has_more":false,
 "note":"amounts shown are the stored request amounts; ContosoApprovalInspect recomputes from the document"}
```

That last `note` is deliberate: the *stored* `amount` may disagree with the document's re-derived total
(M4). `ContosoApprovalInspect` returns both and flags the delta — the ERP-Bench "never trust the number
the agent typed" posture (`erp-bench-deep-dive.md` §1, round-2 Q40).

**Errors**

| Condition | Code | Message |
|---|---|---|
| approver's role ∉ policy `approving_role`, or amount above the approver's own ceiling | 403 | `"Not authorized since Grand Total exceeds limits"` / `"Can be approved by {comma_or(roles)}"` (verbatim) |
| approver == submitter | 403 | `"Approving User cannot be same as user the rule is Applicable To"` (verbatim) |
| request already `approved`/`rejected` | 409 | `"request {id} is already {status} (decided by {who} on {when})"` |
| reject without `reason` | 417 | `"A rejection requires a reason"` |
| no policy matches the doc_type/amount | — | `{"approval_required": false, "reason": "no authorization rule binds Journal Entry at 4,200.00 USD"}` — **not an error**; the honest "you didn't need approval" answer, which is a valid graded outcome |

**Tables**: reads `erp_approval_policies`, `erp_approval_requests`, and the target document's tables;
writes `erp_approval_requests`, `erp_audit_trail`, `erp_confirm_tokens`.

**The approval-theatre trap** (census §10 #12, `mcp-erp-multivendor/src/server.rs:495-499`): our
`ContosoApprovalSubmit` writes a real `pending` row, but an agent that submits and immediately calls
`ContosoJournalPost` must still be refused — `pending ≠ approved`. Grade the rejection.

---

## 4. Capability C — payment run with a shortfall (M2)

### 4.1 Shape

Two phases, matching ERPNext's own two entry points: `get_payable_invoices()` (read-only preview,
returns `{"payable", "excluded", "currency"}`) then `create_payment_entries()` (writes)
— `erpnext/accounts/bulk_payment.py`.

**`ContosoPaymentRunPropose`** — roles `ap_clerk`, `controller`.

```json
{"parameters": {
  "pay_date": {"type":"string"}, "bank_account": {"type":"string"},
  "period_option": {"type":"string","enum":["Invoice","Date","Total"],
                    "description":"D365 method-of-payment Period: one payment per invoice, per due date, or one total"},
  "vendor_filter": {"type":"string"}, "invoice_prefix": {"type":"string"},
  "due_through": {"type":"string","description":"include invoices due on or before this date"}},
 "required": ["pay_date","bank_account"]}
```

Return — the paid/rejected partition is **always** returned, even when cash is sufficient:

```json
{"status":"pending_confirmation","confirm_token":"cg-8c14ee02","run_id":"PMR-0003",
 "pay_date":"2026-03-06","bank_account":"BANK-OPS-USD","currency":"USD",
 "cash_available":42000.00,
 "candidates":[{"invoice":"PPINV-101","vendor":"US-101","due_date":"2026-03-05",
                "gross_amount":18200.00,"cash_disc_code":"10D2%","discount_taken":364.00,
                "net_amount":17836.00,"eligible":true}],
 "ineligible":[{"invoice":"PPINV-104","reason_code":"Vendor On Hold","reason":"vendor SYNVEN-0044 is on payment hold"}],
 "totals":{"eligible_net":58420.00,"cash_available":42000.00,"shortfall":16420.00},
 "note":"eligible_net exceeds cash_available; ContosoPaymentRunCommit requires an explicit rejection set covering the difference"}
```

**`ContosoPaymentRunCommit`** — roles `controller`, `cfo`.

```json
{"parameters": {
  "run_id": {"type":"string"}, "confirm_token": {"type":"string"},
  "paid":     {"type":"array","items":{"type":"object","properties":{
                 "invoice":{"type":"string"},"net_amount":{"type":"number"}}}},
  "rejected": {"type":"array","items":{"type":"object","properties":{
                 "invoice":{"type":"string"},
                 "reason_code":{"type":"string","enum":["Insufficient Cash","Vendor On Hold","Already Paid",
                    "Debit Note","Internal Transfer","Not available","Discount Window Expired","Awaiting Approval"]},
                 "reason":{"type":"string"}}}}},
 "required": ["run_id","confirm_token","paid","rejected"]}
```

**`rejected` is a required argument.** That single schema decision is the whole of M2: an agent cannot
submit a payment run without naming what goes unpaid and why. It is not our invention — ERPNext's own
API returns both halves (`get_payable_invoices` → `{"payable", "excluded"}`) and stamps a reason on
every exclusion. The `reason_code` enum is ERPNext's four (`"Debit Note"`, `"Internal Transfer"`,
`"Already Paid"`, `"Not available"` — `_partition_payable_invoices`) plus four finance-world codes whose
sources are already shipped: `Vendor On Hold` (`erp_vendors.on_hold`, used by
`tasks/payment_proposal/friday-run-mar06`), `Discount Window Expired` (`erp_cash_disc`),
`Awaiting Approval` (§3), and `Insufficient Cash` (the M2 code).

**Server-side validation of the commit** (each failure is a graded refusal, not a silent fix):

| Rule | Code | Message |
|---|---|---|
| `set(paid) ∪ set(rejected)` ≠ the run's candidate set | 417 | `"payment run {id}: {n} candidate invoice(s) are in neither the paid nor the rejected set: {list}"` |
| the two sets intersect | 417 | `"invoice {x} appears in both paid and rejected"` |
| `Σ net(paid) > cash_available + overdraft_limit` | 417 | `"paid total {t} exceeds available cash {c} on {bank_account} as of {as_of}"` |
| any `rejected` row lacks `reason` | 417 | `"rejection of {invoice} requires a reason"` |
| a `paid` row's `net_amount` ≠ the re-derived amount (§8) | 417 | `"invoice {x}: net {given} does not reconcile; expected {derived} (gross {g} − discount {d})"` |
| an ineligible invoice appears in `paid` | 417 | ERPNext-style reason echoed: `"{invoice} is not payable: {reason_code}"` |

**Writes**: `erp_payment_runs` (state `proposed` → `committed`), `erp_payment_run_lines` (one row per
candidate, `disposition ∈ {paid, rejected}`), `erp_settlements` (one per paid invoice),
`erp_vend_trans` (`settled`, `closed`), `erp_bank_accounts` (`available_balance`),
`erp_confirm_tokens`, `erp_audit_trail`.
**Reads**: `erp_vend_trans`, `erp_vendors`, `erp_cash_disc`, `erp_payment_terms`,
`erp_bank_accounts`, `erp_approval_requests`, `docs_documents` (the run SOP).

**Partial-success envelope**: when some settlements fail (e.g. a race with an approval rejection), return
ECOUNT's shape rather than a single ok/fail —
`{"SuccessCnt": 7, "FailCnt": 2, "SlipNos": [...], "ResultDetails": [{"IsSuccess": false, "TotalError": 1,
"Errors": ["…"]}]}` (`mcp-server-ecount/src/tools/register.ts:176-180`). "12 of 15 posted" is the real
outcome of a bulk ERP write (census §10 #4).

### 4.2 The unsat-demand admission gate (generator-side, ported from ERP-Bench)

ERP-Bench refuses to emit a scenario tagged `unsat_demand` unless the certified optimal plan contains
both kept and cancelled orders — four hard `RuntimeError`s in
`erp-bench/erp_bench/procurement/sampler.py:2864-2880`:

```
"Unsat demand produced no kept orders"
"Unsat demand produced no cancelled orders"
"Unsat demand produced no seeded order cancellations"
"Unsat partial-seed scenario produced no prompt-only kept orders"
```

The tag is stamped at `erp_bench/procurement/category.py:110-112`; 77 of 300 shipped tasks carry it
(`research/erp-bench-deep-dive.md` §2). Our port, enforced in the seed generator **before** the task
directory is written:

1. `∃` at least one gold line with `disposition='paid'` — else `"Unsat cash produced no paid invoices"`.
2. `∃` at least one gold line with `disposition='rejected'` **and `reason_code='Insufficient Cash'`** — else
   `"Unsat cash produced no cash-forced rejections"`. A run whose only rejections are eligibility
   rejections (hold, debit note) is *not* an M2 scenario; it is the existing `payment_proposal` family.
3. `Σ net(all eligible) > cash_available + overdraft_limit` — the shortfall is arithmetic, not editorial.
4. **Non-collapse (M3)**: the gold paid set must differ from *both* naive sets — greedy-by-largest-net and
   greedy-by-earliest-due — else `"Naive selection equals the graded selection"`. This is the direct port
   of `_objective_family_certified` (`sampler.py:2769-2801`), which re-solves for the naive objective and
   rejects unless the real objective improves.
5. The discriminating rule must be *sourced and reachable*: the SOP in `docs_documents` names the
   tie-break (e.g. "capture discounts first, then oldest past-due, then never break a payment plan"), so
   the correct set is derivable from the world and not guessable. Ship the SOP; grade against it.

---

## 5. Capability D — the confirm gate

### 5.1 Contract

Every dangerous action is a **pair**. Phase 1 (`*Propose`) validates, stages, and returns a token plus
the exact effect. Phase 2 (`*Post` / `*Commit` / `*Approve` / `*Reject` / `*Reverse`) requires the token.
This is the odoo-ai-agent protocol with our transport: `status: "pending_confirmation"` →
confirm → typed result (`odoo-ai-agent/lib/types.ts:29-62`; governing rule at
`odoo-ai-agent/messages/en.json:1295`).

**Token minting.** `confirm_token = "cg-" + sha256(action ‖ canonical_json(args) ‖ WORLD_NOW ‖ seq)[:8]`,
where `seq = SELECT COUNT(*) FROM erp_confirm_tokens` — the same deterministic counter the form runtime
already uses for `form_id` (`mcp/servers/erp_server.py:244-246`). Deterministic under the frozen clock,
therefore replayable by the oracle.

**Binding.** The token stores `args_hash = sha256(canonical_json(effect_preview))`. Phase 2 recomputes the
effect from current state and compares. If anything changed between propose and execute — the agent
edited a draft line, another action moved the bank balance — the token no longer binds:
`417 "the confirmation token does not match the proposed effect: {field} changed after confirmation was
requested"`. **This is what stops the gate from being ceremonial.** Without it, an agent can propose a
benign effect and execute a different one.

**Single use.** `consumed_at` is stamped on success. Re-spending returns
`409 "confirmation token {t} has already been spent; re-propose to get a new one (do not retry a write
with a spent token)"` — the NetSuite idempotency rule
(`opensuitemcp-netsuite/lib/ai/prompts.ts:105`), and the direct answer to the one structural
retry hazard round-2 row 42 says needs no rate estimate: the retry-induced duplicate post.

**Supersession, not expiry.** Our clock is frozen (`WORLD_NOW`, round-2 Q38), so a wall-clock TTL is
meaningless. Instead: at most one un-consumed token per `(action, actor)`. Proposing again supersedes the
previous token, which is marked `superseded` and thereafter returns
`409 "token {t} was superseded by {t2}"`. This mirrors odoo-ai-agent's single outstanding
`action_proposal` and is checkable by the verifier.

**Trap surface it buys, all sourced**: propose-then-forget (agent proposes and reports success without
executing — the "lying tool" shape, round-2 Q31); execute-without-propose (`417 "no confirmation token"`);
edit-after-confirm (arg-hash mismatch); blind retry (spent token); confirm the *wrong* proposal (token
minted for a different `run_id`).

### 5.2 `erp_confirm_tokens` is not readable

The token table is deliberately **not** in `ENTITIES` and not queryable via `data_find_entities_sql`
(which already refuses non-`erp_*` tables at `mcp/servers/erp_server.py:116-118` — note this filter
would *permit* `erp_confirm_tokens`, so an explicit denylist is required; see §7 edit #14). Round-2 Q39:
the agent's own outstanding proposals are fine to expose through the propose call's return value; the
table would additionally leak *the oracle's* tokens if a task is authored with a pre-seeded proposal.

---

## 6. Schema delta

Append to `world/schema.sql`. **Do not edit that file from this spec** — this block is the source text
for a separate change. Every table stamps `WORLD_NOW`, never wall-clock (see §7 edit #9).

```sql
-- ============ Write-and-approve surface (hard layer M1/M2/M7) ============
-- Chart of accounts (Odoo account.account / ERPNext Account). account_type vocabulary is
-- Odoo's, truncated: asset_receivable, asset_cash, asset_current, liability_payable,
-- liability_current, equity, income, expense, off_balance.
CREATE TABLE erp_main_accounts(
  account_code TEXT PRIMARY KEY, dataareaid TEXT, name TEXT, account_type TEXT,
  currency TEXT, blocked INTEGER DEFAULT 0, reconcilable INTEGER DEFAULT 0,
  requires_dimension TEXT);

-- Fiscal periods / period lock (Odoo company lock dates; mcp-erp close_period/reopen_period).
CREATE TABLE erp_fiscal_periods(
  period_id TEXT PRIMARY KEY, dataareaid TEXT, period_start TEXT, period_end TEXT,
  status TEXT DEFAULT 'open');            -- open | on_hold | closed

-- GL journal header. state: Odoo account.move.state (draft/posted/cancel), one-way draft->posted.
-- voucher_type: ERPNext Journal Entry.voucher_type subset. reversed_entry_id: Odoo
-- account.move.reversed_entry_id / ERPNext Journal Entry.reversal_of.
CREATE TABLE erp_ledger_journals(
  journal_id TEXT PRIMARY KEY, dataareaid TEXT, voucher TEXT, voucher_type TEXT,
  description TEXT, user_remark TEXT, posting_date TEXT, period_id TEXT, currency TEXT,
  total_debit REAL DEFAULT 0, total_credit REAL DEFAULT 0, difference REAL DEFAULT 0,
  state TEXT DEFAULT 'draft',
  reversed_entry_id TEXT, reversal_reason TEXT,
  created_by TEXT, created_at TEXT, posted_by TEXT, posted_at TEXT,
  source_doc_id TEXT);                    -- the docs_documents row the amounts derive from (M4)

-- GL journal lines (Odoo account.move.line debit/credit/balance; mcp-erp PostJournalInput.lines).
CREATE TABLE erp_ledger_journal_lines(
  journal_id TEXT, line INTEGER, account_code TEXT, description TEXT,
  debit REAL DEFAULT 0, credit REAL DEFAULT 0, currency TEXT, fx_rate REAL DEFAULT 1,
  party_type TEXT, party TEXT, dimension_dept TEXT,
  PRIMARY KEY(journal_id, line));

-- Delegation of authority (ERPNext Authorization Rule: transaction/based_on/value/
-- system_role/approving_role/company). company-scoped rules SHADOW global rules.
CREATE TABLE erp_approval_policies(
  policy_id TEXT PRIMARY KEY, dataareaid TEXT, doc_type TEXT,
  based_on TEXT DEFAULT 'Grand Total', threshold_amount REAL, currency TEXT,
  applies_to_role TEXT, approving_role TEXT, approving_user TEXT,
  escalation_policy_id TEXT, active INTEGER DEFAULT 1);

-- Approval inbox (ERPNext AuthorizationControl outcome, materialised as a queue).
CREATE TABLE erp_approval_requests(
  request_id TEXT PRIMARY KEY, dataareaid TEXT, doc_type TEXT, doc_id TEXT,
  amount REAL, currency TEXT, submitted_by TEXT, submitted_at TEXT, note TEXT,
  policy_id TEXT, required_role TEXT,
  status TEXT DEFAULT 'pending',          -- pending | approved | rejected | withdrawn
  decided_by TEXT, decided_at TEXT, decision_reason TEXT);

-- Bank cash position: the constraint that makes M2 bite.
CREATE TABLE erp_bank_accounts(
  bank_account TEXT PRIMARY KEY, dataareaid TEXT, name TEXT, currency TEXT,
  available_balance REAL, as_of TEXT, overdraft_limit REAL DEFAULT 0);

-- Payment run header (ERPNext Payment Order; D365 payment proposal).
-- period_option: D365 method-of-payment Period (Invoice | Date | Total).
CREATE TABLE erp_payment_runs(
  run_id TEXT PRIMARY KEY, dataareaid TEXT, pay_date TEXT, bank_account TEXT, currency TEXT,
  period_option TEXT DEFAULT 'Invoice',
  cash_available REAL, eligible_net REAL, total_paid REAL, total_rejected REAL,
  state TEXT DEFAULT 'proposed',          -- proposed | committed | cancelled
  created_by TEXT, created_at TEXT, approved_by TEXT, committed_at TEXT);

-- Payment run lines: BOTH halves of the partition, one row each.
-- reason_code enum from erpnext/accounts/bulk_payment.py::_partition_payable_invoices
-- plus Vendor On Hold / Discount Window Expired / Awaiting Approval / Insufficient Cash.
CREATE TABLE erp_payment_run_lines(
  run_id TEXT, line INTEGER, invoice TEXT, vendor TEXT, due_date TEXT,
  gross_amount REAL, discount_taken REAL DEFAULT 0, withholding REAL DEFAULT 0,
  net_amount REAL, disposition TEXT, reason_code TEXT, reason TEXT, priority_rank INTEGER,
  PRIMARY KEY(run_id, line));

-- FX rates: without these, M4 cannot re-derive any cross-currency amount
-- (odoo-domain.md §8 gap #15 — we have a currency column and no rate table).
CREATE TABLE erp_fx_rates(
  from_ccy TEXT, to_ccy TEXT, rate_date TEXT, rate REAL,
  PRIMARY KEY(from_ccy, to_ccy, rate_date));

-- Two-phase confirm-gate token store. RUNTIME state: never graded, never readable as an entity.
CREATE TABLE erp_confirm_tokens(
  token TEXT PRIMARY KEY, seq INTEGER, action TEXT, actor TEXT, role TEXT,
  target_id TEXT, args_hash TEXT, effect_preview TEXT, minted_at TEXT,
  consumed_at TEXT, superseded_by TEXT);

-- Audit trail (mcp-erp get_erp_audit_trail; odoo-ai-agent GET /chat/{id}/audit).
-- Derived from the graded writes; excluded from the state veto, assertable by row_count.
CREATE TABLE erp_audit_trail(
  audit_id INTEGER PRIMARY KEY, entity_type TEXT, entity_id TEXT, action TEXT,
  actor TEXT, role TEXT, at TEXT, before_json TEXT, after_json TEXT);
```

New `ENTITIES` registrations in `erp_server.py:36-54` (read surface, so discovery works):
`MainAccounts → erp_main_accounts`, `FiscalPeriods → erp_fiscal_periods`,
`LedgerJournals → erp_ledger_journals`, `LedgerJournalLines → erp_ledger_journal_lines`,
`ApprovalPolicies → erp_approval_policies`, `ApprovalRequests → erp_approval_requests`,
`BankAccounts → erp_bank_accounts`, `PaymentRuns → erp_payment_runs`,
`PaymentRunLines → erp_payment_run_lines`, `ExchangeRates → erp_fx_rates`.
**Not registered**: `erp_confirm_tokens`, `erp_audit_trail`.

New `FORMS` entries (optional, for form-tool depth): `LedgerJournalTable` (menu item
"General journals", grid `journal_id, voucher, posting_date, description, total_debit, total_credit, state`,
tabs General/Lines/Approval, actions `Post`, `Reverse`, `Lines`) — `Post` and `Reverse` must route to
`_deny()` for `analyst`/`collections` exactly as `SettleTransactions` does today
(`erp_server.py:345`), preserving the "governed actions only" story.

---

## 7. Required changes to the existing framework — precise list

| # | File / line | Today | Required change |
|---|---|---|---|
| 1 | `mcp/lib/framework.py:26-29` | `db()` returns a bare connection; every write path re-implements `cx.execute(...); cx.commit()` (see `erp_server.py:423-426, 435-437`) | add `Server.tx()` — a context manager that opens one connection, runs the whole action, commits once, rolls back on exception. Partial writes on a mid-action failure would corrupt the state-diff veto |
| 2 | `mcp/lib/framework.py` (absent) | no audit helper | add `Server.audit(entity_type, entity_id, action, actor, before, after)` writing `erp_audit_trail`, stamped with `self.now`. Grounded in mcp-erp `get_erp_audit_trail` (`src/server.rs:509-512`) |
| 3 | `mcp/lib/framework.py` (absent) | no confirm-token store | add `Server.mint_token(action, target_id, effect_preview)` and `Server.consume_token(token, action, target_id, effect_preview)`. Canonical JSON = `json.dumps(obj, sort_keys=True, separators=(",",":"))`; hash = sha256. Seq from `SELECT COUNT(*) FROM erp_confirm_tokens` (mirrors `form_id` at `erp_server.py:244-246`) |
| 4 | `mcp/servers/erp_server.py:34` | `_role()` reads `WORLD_ROLE`; there is **no user identity** | add `_actor()` reading `WORLD_USER` (default: the role name). Segregation of duties (§3) is unimplementable without it |
| 5 | `mcp/servers/erp_server.py:30-32` | `ROLE_NAME` is a 2-entry dict (`analyst`, `collections`) | extend to 5: `analyst` "Finance analyst (read-only)", `collections` "Collections coordinator", `ap_clerk` "Accounts payable clerk", `controller` "Corporate controller", `cfo` "Chief financial officer". `_deny()` text is unchanged |
| 6 | `mcp/servers/erp_server.py:400-401, 443-445` | `ACTIONS[…]["requires_role"]` is a **single string**, tested with `==` | change to `requires_roles: [..]` with membership. Today a `controller` cannot see `ContosoIssueCollectionLetter` even though a controller outranks a collections coordinator — with 5 roles this is a functional bug, not a nicety |
| 7 | `mcp/lib/framework.py:39-45` | `rows()` pages reads at 25; no write analogue | add `Server.batch_result(details)` returning ECOUNT's partial-success envelope `{SuccessCnt, FailCnt, SlipNos[], ResultDetails[]}` (`mcp-server-ecount/src/tools/register.ts:176-180`) |
| 8 | `mcp/lib/framework.py:64-66` | a result containing `"error"` is traced `ok=False` — so an **authentic denial counts as a failed call** | add a third trace field `denied: true` when the payload carries `role` (the `_deny()` signature). Otherwise `required_servers` / `min_calls` (`verifiers/vcode.py:75-81`) under-count an agent that correctly hit a permission wall, and no task can *require* that it did |
| 9 | `mcp/servers/harness_server.py:20`, all new writers | `submit_answer` stamps `dt.datetime.now(timezone.utc)` — wall-clock | every new write stamps `S.now` (frozen `WORLD_NOW`). Wall-clock in a graded table makes `table_hashes` non-deterministic and breaks the τ-bench gold-replay comparison outright (§9) |
| 10 | `verifiers/vcode.py:21-29` | `table_hashes()` hashes **every column of every table** | add a per-table column-exclusion map (`{"erp_audit_trail": ["at"], …}`) so audit/session noise cannot flip a hash. Keep the default "hash everything" for all business tables |
| 11 | `verifiers/vcode.py:91` | `RUNTIME_TABLES = {"erp_form_sessions"}` | → `{"erp_form_sessions", "erp_confirm_tokens", "erp_audit_trail"}`. Token minting and audit rows are tool-session state; they must not trip `writes_only` |
| 12 | `verifiers/vcode.py:93-111` | `state_checks` supports `writes_only`, `row_count`, `cell_equals` | add four types — see §9 |
| 13 | `sim/oracle.py:26` | `servers[s].call(step["tool"], step.get("args") or {})` — **args are literal**; `solution/walk.json` is a static list | a confirm token is minted at runtime and cannot be written into a static walk. Add a substitution pass: `"$token"` in any arg resolves to the `confirm_token` of the most recent successful `*Propose` result, and `"$last.<key>"` to any field of the previous result (needed for `run_id`, `journal_id`, `request_id` too). **This is the highest-risk edit — see §10** |
| 14 | `mcp/servers/erp_server.py:116-118` | `data_find_entities_sql` allows any table whose name starts with `erp_` | add an explicit denylist `{erp_confirm_tokens, erp_audit_trail, erp_form_sessions}`, returning the existing "table is outside the ERP" `ValueError`. Without it the SQL tool leaks the token store (round-2 Q39) |
| 15 | `sim/prepare.py:58` | env dict sets `WORLD_ROLE` from `meta.get("agent_role","analyst")` | add `"WORLD_USER": meta.get("agent_user", meta.get("agent_role","analyst"))` |
| 16 | `sim/prepare.py:65-66` | `initial_state.json` = `table_hashes(db)` after seeding | unchanged in shape, but it must be written **after** the confirm-token/audit tables exist, and it becomes the baseline for `table_unchanged` (§9) |
| 17 | `research/scenario-registry.json` | 15 families, all read-and-reconcile | register `journal_entry`, `approval_queue`, `payment_run_short`, `confirm_gate` with `agent_role` and `agent_user` fields per scenario |

---

## 8. Money re-derivation rules (M4)

The verifier never reads a written amount back and calls it correct. For every write that carries an
amount, it recomputes from base data. Source posture: ERP-Bench re-prices every purchase line against the
scenario's tier table and flags any fallback to the typed `price_unit`
(`research/erp-bench-deep-dive.md` §1; round-2 Q40).

| Written value | Table.column | Recompute from | Tolerance |
|---|---|---|---|
| journal line amount | `erp_ledger_journal_lines.debit/credit` | the formula named in the source document (`erp_ledger_journals.source_doc_id` → `docs_documents.body`): straight-line accrual `= base × days_elapsed / days_in_period`; prepaid amortisation `= base / months`; FX revaluation `= balance × (rate_close − rate_book)` | ±0.01 |
| journal header totals | `erp_ledger_journals.total_debit/total_credit` | `Σ lines.debit` / `Σ lines.credit` — never the submitted header | ±0.005 |
| journal balance | `erp_ledger_journals.difference` | `round(total_debit − total_credit, 2)`; **must be exactly 0 for `state='posted'`** (ERPNext `journal_entry.py:680` computes it as `flt(total_debit, prec) − flt(total_credit, prec)`) | 0 |
| reversal lines | mirrored `erp_ledger_journal_lines` | for each original line: `debit' = credit`, `credit' = debit`, same `account_code`, same `party` | exact |
| cash discount | `erp_payment_run_lines.discount_taken` | walk the `erp_cash_disc` chain from `erp_vend_trans.cash_disc_code` via `next_code` (D365 `5D10% → 10D5% → 14D2%`, `research/erp-domain.md` §1.2); pick the tier whose window `trans_date + days` contains `pay_date`; `= open_amount × percent / 100`, else 0. Matches the shipped `ContosoCashDiscountForecast` arithmetic (`erp_server.py:476-480`) | ±0.01 |
| net payment | `erp_payment_run_lines.net_amount` | `gross_amount − discount_taken − withholding` | ±0.01 |
| gross | `erp_payment_run_lines.gross_amount` | `erp_vend_trans.amount − erp_vend_trans.settled` **at run time**, not the stored line | ±0.01 |
| run totals | `erp_payment_runs.total_paid/total_rejected` | `Σ net_amount` grouped by `disposition` | ±0.02 |
| cash feasibility | — | `total_paid ≤ erp_bank_accounts.available_balance + overdraft_limit` | strict |
| settlement | `erp_settlements.amount`, `erp_vend_trans.settled` | `settled' = settled + Σ settlements(invoice)`; `closed = 1` iff `settled ≥ amount − 0.005` | ±0.005 |
| approval amount | `erp_approval_requests.amount` | recomputed from the target document (`Σ journal lines` / `run.total_paid`), **not** the value the submitter passed | ±0.01 |
| policy binding | `erp_approval_requests.policy_id` | re-run the two-query cascade (company-scoped, then `coalesce(company,'')=''`) and assert the same policy id | exact |
| FX | any `*_accounting` amount | `amount × erp_fx_rates.rate` at `(currency, company_currency, posting_date)`; **missing rate is a graded refusal, not a 1.0 fallback** | ±0.01 |
| installment due date | `erp_vend_trans.due_date` decoys | per-installment `date_maturity`; the header due date is `max(date_maturity)` and is a decoy (round-2 Q35, `odoo/addons/account/models/account_move.py:1079-1086` via `odoo-domain.md` §7 #2) | exact |

---

## 9. State-diff veto surface (M1 + M7)

### 9.1 The τ-bench recipe, concretely

τ-bench computes reward by hashing the whole data store, reloading a **fresh** store, replaying the gold
action list, re-hashing, and requiring equality — `to_hashable` sorts dict keys and set members
(`tau-bench/tau_bench/envs/base.py:27-36`), `consistent_hash` is sha256 of the string form (`:38-41`),
`get_data_hash` (`:121-122`), and `calculate_reward` sets `reward = 0.0` when
`data_hash != gt_data_hash` (`:124-139`). Our `verifiers/vcode.py:21-29` already hashes every table with
sha256 over sorted repr'd rows — same construction, per table instead of per store, which is *better*
because it localises the diff.

### 9.2 Table classes

| Class | Tables | Rule |
|---|---|---|
| **Graded write targets** | `erp_ledger_journals`, `erp_ledger_journal_lines`, `erp_approval_requests`, `erp_payment_runs`, `erp_payment_run_lines`, `erp_settlements`, `erp_vend_trans`, `erp_cust_trans`, `erp_bank_accounts`, `erp_collection_letters`, `erp_customers` (hold flag only), `answers` | hash must equal the **gold-replay** hash, exactly |
| **Runtime (invisible to grading)** | `erp_form_sessions`, `erp_confirm_tokens`, `erp_audit_trail` | excluded from the veto (`vcode.py:91`); still assertable via explicit `row_count` |
| **Must-not-change (blast radius, M7)** | `erp_vendors`, `erp_companies`, `erp_main_accounts`, `erp_fiscal_periods`, `erp_approval_policies`, `erp_payment_terms`, `erp_cash_disc`, `erp_purch_orders`, `erp_product_receipts`, `erp_sales_orders`, `erp_activities`, `erp_collection_pools`, `erp_customer_pool`, `erp_methods_of_payment`, `erp_aging_snapshot`, `erp_fx_rates`, all `books_*`, `sheet_*`, `email_*`, `filings_*`, `docs_documents` | hash must equal `initial_state.json`, exactly. This is where the decoy vendors and same-name counterparties live |

### 9.3 New `state_checks` types for `verifiers/vcode.py`

```json
{"type":"gold_state_equals","tables":["erp_ledger_journals","erp_ledger_journal_lines"],
 "gold":"solution/gold_state.json"}
{"type":"table_unchanged","tables":["erp_vendors","erp_main_accounts","docs_documents"]}
{"type":"rows_added","table":"erp_ledger_journals","sql":"SELECT COUNT(*) FROM erp_ledger_journals WHERE state='posted'","expect":1}
{"type":"no_rows_matching","name":"decoy vendors untouched",
 "sql":"SELECT COUNT(*) FROM erp_payment_run_lines WHERE vendor IN (SELECT account FROM erp_vendors WHERE vendor_group='DECOY')","expect":0}
```

- `gold_state_equals` reads a `solution/gold_state.json` emitted by the **oracle replay at export time**
  (`sim/oracle.py` on a fresh DB), holding `{table: [nrows, hash]}` for the listed tables. This is the
  literal τ-bench comparison; it is what makes "any incidental write fails" enforceable instead of
  aspirational.
- `table_unchanged` is the M7 blast-radius veto and is *stricter* than the existing `writes_only`
  whitelist: `writes_only` passes if a table isn't listed as dirty, `table_unchanged` names the tables that
  must be byte-identical, so a task author cannot forget one.
- Existing `writes_only` stays as the cheap default for read-only families.

### 9.4 Decoy seeding (M7)

ERP-Bench seeds ~150 adjacent entities per task with opaque namespace tokens so relevance cannot be
pattern-matched — task records read `rD5BD7E1C25_c01`, decoys `r2EF13BB94B_p01`
(`research/erp-bench-deep-dive.md`, round-2 Q20). Our analogue, using the existing name pools
(`research/erp-domain.md` §3): decoy vendors in `vendor_group='DECOY'` with Contoso/Fabrikam-style names
one edit away from the task's vendors, near-duplicate invoice numbers (`PPINV-101` vs `PPINV-1O1`), and
the same counterparty in a second `dataareaid`. A write touching any of them fails via §9.3.

---

## 10. Open risks and unresolved decisions

1. **Oracle replay vs runtime tokens** (edit #13). `solution/walk.json` is a static list replayed with
   literal args (`sim/oracle.py:26`), and the admission rule is "a task ships only if this passes". Every
   two-phase write therefore needs `$token` / `$last.<key>` substitution, and `gold_state.json` must be
   produced by that same replay. If the substitution and the token-minting counter are not *bit*
   deterministic, the gold hash differs run to run and every write task fails spuriously. Highest-risk
   item in this spec.
2. **Non-collapse for the payment run needs an SOP that actually discriminates.** Gate 4 in §4.2 rejects a
   task whose graded set equals greedy-by-largest or greedy-by-due-date; writing seeds that satisfy it
   *and* stay plausible is the real authoring cost, and ERP-Bench needed up to 150 resamples per task
   (`sampler.py:2343`, `:2926-2929`).
3. **Two error vocabularies.** We adopt Frappe's (417 validation / 403 permission / 409 conflict) per the
   census recommendation, while quoting Odoo's message *text*. Odoo's own status map is 422/403/404/409
   (`odoo/odoo/exceptions.py`, via `odoo-domain.md` §5.4). Mixing a Frappe code with an Odoo string is
   defensible for a D365-shaped mock that copies neither, but it should be a recorded decision, not a drift.
4. **Approval escalation is specified but not sourced.** `erp_approval_policies.escalation_policy_id` has
   no counterpart in ERPNext's Authorization Rule (which has no chaining). **(UNVERIFIED — no shipped
   escalation ladder found in the corpus; the closest is D365's collection-letter ladder, which is a
   different object.)** Either drop the column or ground it before a task depends on it.
5. **`erp_fx_rates` has no shipped source in our corpus** for the specific rate-table shape; it is derived
   from Odoo's `amount_currency` vs `balance` + `currency_rate` + `exchange_move_id` triad
   (`odoo-domain.md` §8 gap #15). Shape is inferred, not copied. **(UNVERIFIED at field level.)**
6. **Period lock semantics are simplified.** Odoo ships five company lock dates plus per-user lock
   exceptions (`odoo-domain.md` §6); we ship one `status` per period. Adequate for a "you cannot post into
   a closed period" trap, insufficient for a lock-exception task.
7. **`WORLD_USER` collides with role-only tasks.** All 58 existing tasks set only `agent_role`
   (`sim/prepare.py:58`); defaulting `WORLD_USER` to the role name keeps them green but makes
   "submitter == approver" trivially true whenever a task gives one agent both roles. Task authors must
   set `agent_user` explicitly on every approval-family task.
