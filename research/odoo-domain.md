# Odoo Domain Research for finance-world

Research date: 2026-08-11. Source: sparse checkout of `odoo/odoo` at `research/external/repos/odoo` — **Odoo 19.0 final** (`odoo/release.py:15`, `version_info = (19, 0, 0, FINAL, 0, '')`). Modules present: `addons/account`, `addons/purchase`, `addons/sale`, `addons/payment`, `addons/analytic`, `odoo/addons/base`, plus a handful of `odoo/` core files (`http.py`, `exceptions.py`, `sql_db.py`). Everything below cites a path in that checkout unless marked **UNVERIFIED**.

**License note:** `account` and `purchase` are **LGPL-3** (`odoo/addons/account/__manifest__.py:142`, `odoo/addons/purchase/__manifest__.py:61`). Treat this repo as a **fact source, not a code source** — we mirror field names, state machines and semantics; we do not copy implementation.

Companion doc: [`research/erp-domain.md`](erp-domain.md) (Dynamics-365-shaped model our world already ships). Section 8 is the explicit gap analysis against [`world/schema.sql`](../world/schema.sql).

---

## 1. Core accounting models

Odoo has **no separate AR/AP subledger tables**. Everything is one polymorphic journal-entry table (`account.move`) plus its lines (`account.move.line`); "customer invoice", "vendor bill", "payment journal entry" and "misc entry" are all rows in `account_move` discriminated by `move_type`. This is the **NetSuite pattern**, and the opposite of D365's `CustTrans`/`VendTrans` split that our world copies.

| Model | Table | Role | Evidence |
|---|---|---|---|
| `account.move` | `account_move` | Journal entry / invoice / bill / credit note header | `odoo/addons/account/models/account_move.py:74-76` |
| `account.move.line` | `account_move_line` | Journal item (the double-entry line **and** the invoice line **and** the receivable/payable open item) | `odoo/addons/account/models/account_move_line.py:32+` |
| `account.payment` | `account_payment` | Payment document; owns/points at its own `account.move` | `odoo/addons/account/models/account_payment.py:8-10` |
| `account.partial.reconcile` | `account_partial_reconcile` | One settlement link: debit line ↔ credit line, amount | `odoo/addons/account/models/account_partial_reconcile.py:10-56` |
| `account.full.reconcile` | `account_full_reconcile` | Closure marker when a set of partials nets to zero | `odoo/addons/account/models/account_full_reconcile.py:5-10` |
| `account.payment.term` (+ `.line`) | `account_payment_term(_line)` | Due-date schedule **and** early-payment discount | `odoo/addons/account/models/account_payment_term.py:11-46, 281-308` |
| `account.journal` | `account_journal` | Sale / purchase / cash / bank / credit / general | `odoo/addons/account/models/account_journal.py:43,106-113` |
| `account.account` | `account_account` | Chart of accounts; `account_type` drives everything | `odoo/addons/account/models/account_account.py:44-65` |
| `account.tax` (+ `.group`, repartition lines) | `account_tax` | Tax computation & repartition | `odoo/addons/account/models/account_tax.py:26,72-205` |
| `res.partner` | `res_partner` | Customer **and** vendor in one record (Xero-style) | `odoo/addons/account/models/partner.py:513-624` |
| `account.bank.statement.line` | `account_bank_statement_line` | Raw bank feed row awaiting cash application | `odoo/addons/account/models/account_bank_statement_line.py:25-149` |
| `account.reconcile.model` | `account_reconcile_model` | Auto-matching rules for the bank widget | `odoo/addons/account/models/account_reconcile_model.py:92-147` |
| `purchase.order` (+ `.line`) | `purchase_order(_line)` | PO header/lines with `qty_received` / `qty_invoiced` | `odoo/addons/purchase/models/purchase_order.py:22-131`, `purchase_order_line.py:59-82` |
| `purchase.bill.line.match` | *(SQL view, `_auto=False`)* | The 3-way-match workbench | `odoo/addons/purchase/models/purchase_bill_line_match.py:9-13,133-135` |
| `purchase.bill.union` | *(SQL view)* | Posted bills ∪ un-billed POs, for "create bill from" | `odoo/addons/purchase/report/purchase_bill.py:8-43` |

### 1.1 `account.move` — the fields that matter

| Field | Type / values | Notes | Evidence |
|---|---|---|---|
| `state` | `draft` / `posted` / `cancel` | Only three. Required, readonly, tracked, default `draft` | `account_move.py:130-142` |
| `move_type` | `entry`, `out_invoice`, `out_refund`, `in_invoice`, `in_refund`, `out_receipt`, `in_receipt` | Required, indexed, default `entry` | `account_move.py:143-160` |
| `payment_state` | `not_paid`, `in_payment`, `paid`, `partial`, `reversed`, `blocked`, `invoicing_legacy` | Stored compute, tracked | `account_move.py:49-57, 601-607` |
| `status_in_payment` | `payment_state` ∪ `draft`/`posted`/`sent`/`cancel` | UI-facing merged status; has a raw-SQL search override | `account_move.py:608-617, 1331-1339` |
| `name` | Char, "Number" | Computed sequence, unique per journal when posted | `account_move.py:109-115`, index `account_move.py:786-789` |
| `ref` | Char, "Reference" | Vendor's own bill number → duplicate detection key | `account_move.py:117-122` |
| `date` | accounting date (required) vs `invoice_date` (document date) vs `invoice_date_due` | Three distinct dates | `account_move.py:123-129, 375-385` |
| `invoice_date_due` | Date | **Derived**: `max(date_maturity)` over the payment-term lines | `account_move.py:380-385, 1079-1086` |
| `invoice_payment_term_id` | → `account.payment.term` | Defaults from `partner.property_payment_term_id` / `property_supplier_payment_term_id` | `account_move.py:406-412, 1070-1077` |
| `amount_untaxed` / `amount_tax` / `amount_total` / `amount_residual` | Monetary, stored computes | `amount_residual` = Σ residual of `display_type='payment_term'` lines | `account_move.py:546-593, 1168-1202` |
| `*_signed` variants | Monetary | AR/AP sign normalisation via `direction_sign` (+1 for `entry`/outbound, −1 otherwise) | `account_move.py:542-545, 1145-1151` |
| `reversed_entry_id` / `reversal_move_ids` | → `account.move` | Credit-note ↔ original link | `account_move.py:624-632` |
| `matched_payment_ids` / `reconciled_payment_ids` | M2M `account.payment` | The "payments on this invoice" widget | `account_move.py:214-227` |
| `commercial_partner_id` | → `res.partner` | Roll-up to the parent company of a contact | `account_move.py:431-437` |
| `duplicated_ref_ids` | M2M compute | Duplicate-bill detector (see §7.4) | `account_move.py:754, 2065-2069`; query `_fetch_duplicate_reference` `:2071-2171` |
| `partner_credit_warning` | Text | Credit-limit banner, group-restricted | `account_move.py:750-753, 1984-1998` |
| `auto_post` / `auto_post_until` | Selection + Date | Future-dated moves auto-post on their date | `account_move.py:294-309` |
| `checked` / `restrict_mode_hash_table` / `inalterable_hash` / `secure_sequence_number` | audit-trail machinery | Hash-chained posted entries | `account_move.py:317, 353-365` |
| `next_payment_date` | Date compute+search | min payment date over unpaid lines (installments) | `account_move.py:773-778` |

Postgres indexes worth copying for realism (they encode the real query patterns): `_payment_idx (journal_id, state, payment_state, move_type, date)`, `_duplicate_bills_idx (ref) WHERE move_type IN ('in_invoice','in_refund')`, `_unique_name (name, journal_id) WHERE state='posted' AND name != '/'` with message *"Another entry with the same name already exists."* — `account_move.py:784-793`.

### 1.2 `account.move.line` — one table, five jobs

`display_type` tells you what a line *is*: `product`, `cogs`, `tax`, `discount`, `rounding`, **`payment_term`**, `line_section`, `line_subsection`, `line_note`, `epd`, `non_deductible_*` (`account_move_line.py:329-347`).

The **`payment_term` lines are the AR/AP open items** — one per installment. Key fields:

| Field | Meaning | Evidence |
|---|---|---|
| `debit` / `credit` / `balance` (company ccy), `amount_currency` (+`currency_id`) | double entry | `account_move_line.py:115-150` |
| `amount_residual` / `amount_residual_currency` | **stored** open remainder | `account_move_line.py:242-253` |
| `reconciled` (bool), `full_reconcile_id`, `matching_number` | closure state; `matching_number` is `'P<n>'` while only partially matched, `'I*'` for import-marked | `account_move_line.py:254-261, 300-306, 3150-3159` |
| `matched_debit_ids` / `matched_credit_ids` | → `account.partial.reconcile` both ways | `account_move_line.py:262-273` |
| `date_maturity` | **per-line** due date (indexed, tracked) | `account_move_line.py:386-392` |
| `discount_date`, `discount_amount_currency`, `discount_balance` | early-payment-discount snapshot, stored on the line | `account_move_line.py:440-457` |
| `payment_date` | compute+search: min(`discount_date`, `date_maturity`) | `account_move_line.py:461-465`; search impl `account_move.py:2415` uses `('line_ids','any',[...])` |
| `account_id` → `account_type` | `asset_receivable` / `liability_payable` gate everything | `account_move_line.py:93-107, 313-316` |
| `purchase_line_id` | → `purchase.order.line` (added by `purchase`) | `odoo/addons/purchase/models/account_invoice.py:528-529` |

**Balance invariant**: `_check_balanced` raises `UserError("The entry is not balanced.")`; the SQL groups by move and `HAVING ROUND(SUM(balance), decimal_places) != 0` (`account_move.py:2767-2806`).

---

## 2. AR/AP lifecycle state machines

### 2.1 Invoice/bill: draft → posted → (cancel)

```
draft --action_post()/_post(soft=False)--> posted --button_draft()--> draft
posted --button_cancel()--> (button_draft first) --> cancel
cancel --button_draft()--> draft
```

- `action_post` → `_post(soft=False)` (`account_move.py:6147-6168, 5557+`). Requires group `account.group_account_invoice`, else `AccessError("You don't have the access rights to post an invoice.")` (`:5571-5572`).
- Validation failures collected into **one** `UserError` joined by newlines (`:5669-5671`). Exact shipped messages include: *"The field 'Vendor' is required, please complete it to validate the Vendor Bill."*, *"The Bill/Refund date is required to validate this document."*, *"You cannot validate an invoice with a negative total amount…"*, *"Even magicians can't post nothing!"*, *"You cannot post an entry in an archived journal (%(journal)s)"*, *"A line of this move is using a archived account, you cannot post it."* (`:5612-5659`).
- `soft=True` (the default of `_post`) does **not** post future-dated moves; it sets `auto_post='at_date'` and chatters *"This move will be posted at the accounting date: %(date)s"* (`:5679-5686`).
- `button_draft` refuses non-posted/cancelled, refuses when `need_cancel_request`, deletes analytic lines, detaches attachments (`:6236-6251`). Lock-date guard raises *"You cannot reset to draft a locked journal entry."* (`:6340`).
- `button_cancel` = draft-then-cancel; it **breaks reconciliation** (`self.line_ids.remove_move_reconcile()`) and cancels linked payments (`:6351-6363`).
- Numbering happens at post via `sequence.mixin`: sale/bank/cash/credit journals get `CODE/YYYY/00000` (annual), others `CODE/YYYY/MM/0000` (monthly); refund sequence prefixes `R`, payment sequence prefixes `P` (`account_move.py:4254-4292`; regexes at `sequence_mixin.py:43-45`).

### 2.2 `payment_state` — how it is actually computed

`_compute_payment_state` (`account_move.py:1222-1314`) runs a UNION query over `account_partial_reconcile` joined both directions, restricted to counterpart lines whose account is `asset_receivable`/`liability_payable`, then:

| Condition | Resulting `payment_state` |
|---|---|
| not an invoice, or draft with zero total | `not_paid` |
| `amount_residual == 0` and a payment/statement line is involved and **all** linked payments `is_matched` | `paid` |
| `amount_residual == 0`, payment involved, some payment not bank-matched | `_get_invoice_in_payment_state()` |
| `amount_residual == 0`, **no** payment involved, counterpart move types are purely the reverse kind (`out_invoice` ← `out_refund`, `in_invoice` ← `in_refund`, `entry` ← `entry`) | `reversed` |
| `amount_residual == 0`, no payment, other counterparts | `paid` |
| residual ≠ 0 and a matched payment sits in `in_process` | `_get_invoice_in_payment_state()` |
| residual ≠ 0 and any partial exists | `partial` |
| manual toggle | `blocked` (sticky; skipped by the recompute) |
| legacy import flag | `invoicing_legacy` (sticky) |

**Shipped-behaviour finding (docs vs code):** `_get_invoice_in_payment_state()` returns **`'paid'`** in the community `account` module. Its docstring says the `in_payment` state is only enabled *"in the accountant module"* (`account_move.py:7333-7338`). So in a stock community DB, **`in_payment` is a selectable value that is never produced**. Same for `invoicing_legacy` (only set by migration). This is a first-class trap for an eval.

`blocked` is set/cleared by `action_toggle_block_payment`, which refuses on paid/in_payment: *"You can't block a paid invoice."* (`account_move.py:6365-6373`).

### 2.3 Reconciliation (payment matching)

Everything goes through `account.move.line.reconcile()` → `_reconcile_plan([self])` (`account_move_line.py:3135-3137`); undo is `remove_move_reconcile()` = unlink the partials (`:3139-3141`).

1. **Eligibility** (`_check_amls_exigibility_for_reconciliation`, `:2644-2679`) — exact `UserError` strings: *"You are trying to reconcile some entries that are already reconciled."*, *"You can not reconcile cancelled entries."*, *"Entries are not from the same account: %s"*, *"Entries don't belong to the same company: %s"*, *"Account %s does not allow reconciliation…"*.
2. **Ordering = FIFO by due date.** `_optimize_reconciliation_plan` sorts lines by `(date_maturity or date, currency_id, amount_currency, balance)` and splits the plan into per-currency sub-nodes (`:2705-2730`). Under `reduced_line_sorting` context only `(date_maturity or date, currency)`.
3. **Pairing loop** walks debit and credit generators, calling `_prepare_reconciliation_single_partial` for each pair; a line drops out when it has nothing left (`:2567-2602`). Each pair yields one `account.partial.reconcile` and optionally an exchange-difference move.
4. **Partial row** = `debit_move_id`, `credit_move_id`, `amount` (always positive, company ccy), `debit_amount_currency`, `credit_amount_currency`, `max_date` (= max of the two line dates — *"used to determine at which date this reconciliation needs to be shown on the aged receivable/payable reports"*), `exchange_move_id`, `full_reconcile_id` (`account_partial_reconcile.py:15-68, 84-90`).
5. **Full reconcile** is created when a set nets to zero; `create()` bulk-UPDATEs `full_reconcile_id` on lines and partials and refreshes `matching_number` (`account_full_reconcile.py:26-45`).
6. The invoice-form widget calls `js_assign_outstanding_line(line_id)` / `js_remove_outstanding_partial(partial_id)` (`account_move.py:6206-6224`) — these are the "apply this open credit to this invoice" / "unapply" verbs.

### 2.4 `account.payment`

| Field | Values | Evidence |
|---|---|---|
| `state` | `draft`, `in_process`, `paid`, `canceled`, `rejected` | `account_payment.py:36-49` |
| `payment_type` | `outbound` ("Send") / `inbound` ("Receive") | `:99-102` |
| `partner_type` | `customer` / `supplier` | `:103-106` |
| `is_reconciled`, `is_matched` | stored computes; `is_matched` = liquidity line cleared against the bank | `:50-53, 469-497` |
| `move_id`, `outstanding_account_id`, `destination_account_id` | payment JE + outstanding-receipts/payments account | `:17-22, 123-138` |
| `payment_method_line_id` / `payment_method_id` | manual, check, batch deposit, SEPA CT/DD, US ISO20022 | `:74-92` |
| `reconciled_invoice_ids` / `reconciled_bill_ids` (+ counts) | derived | `:147-163` |

`_compute_state` (`:453-467`): a payment moves `in_process → paid` when its liquidity lines have zero residual (or the liquidity account isn't reconcilable), or when **all** reconciled invoices/bills reach `payment_state == 'paid'`. So a payment can be created and reconciled to an invoice while both sit in an intermediate state until the bank line clears — the Odoo analogue of "in transit".

**Registering a payment** is a wizard, `account.payment.register` (`odoo/addons/account/wizard/account_payment_register.py:13`), and it is where most AR/AP friction lives:

- `payment_difference` + `payment_difference_handling` ∈ {`open` ("Keep open"), `reconcile` ("Mark as fully paid")} + `writeoff_account_id` / `writeoff_label` (default `'Write-Off'`) (`:134-153`).
- `installments_mode` ∈ {`next`, `overdue`, `before_date`, `full`} (`:63-74`) — driven by `account.move.line._get_installments_data`, which tags each payment-term line `early_payment_discount` / `overdue` / `next` / `before_date` / `other` (`account_move_line.py:3320-3380`).
- `group_payment`, `can_group_payments`, `duplicate_payment_ids`, and a trust/bank-account gate (`untrusted_bank_ids`, `missing_account_partners`) (`:25-27, 162-169`).
- `early_payment_discount_mode` forces `payment_difference_handling='reconcile'` and hides the write-off section (`:861-872`).

### 2.5 Mapping to our three-layer subledger (explicit)

| finance-world layer (D365 shape) | our table | D365 artifact | Odoo equivalent |
|---|---|---|---|
| Posted subledger transaction | `erp_cust_trans` / `erp_vend_trans` | `CustTrans` / `VendTrans` | `account.move` (header, `move_type`+`state='posted'`) **+** its `account.move.line` rows with `display_type='payment_term'` on an `asset_receivable`/`liability_payable` account |
| Open remainder | `amount - settled WHERE closed=0` | `CustTransOpen.AmountCur` | `account.move.line.amount_residual` / `amount_residual_currency` (**stored**, not derived at read time) |
| Settlement link | `erp_settlements(payment_id, invoice_id, amount, cash_disc_taken)` | `CustSettlement` | `account.partial.reconcile(debit_move_id, credit_move_id, amount, *_amount_currency, max_date)` |
| Closed flag | `erp_cust_trans.closed` | `CustTrans.Closed` (date) | `account.move.line.reconciled` (bool) + `full_reconcile_id` + `matching_number` |
| Header payment status | *(absent)* | *(absent — D365 has no header status)* | `account.move.payment_state` (7 values) |
| Due date | `erp_cust_trans.due_date` (one per txn) | `CustTransOpen.DueDate` | **`account.move.line.date_maturity`, one per installment**; `move.invoice_date_due` is only `max()` of them |
| Discount date | derived from `erp_cash_disc.days` | `CashDisc` code + Days | `account.move.line.discount_date` (stored) + `discount_amount_currency` / `discount_balance` |
| Aging bucket source | live open rows + `erp_aging_snapshot` | `CustTransOpen` + aging snapshot | residual lines bucketed by `date_maturity`; historical accuracy needs `partial.max_date` |

Three structural mismatches to be aware of when porting:

1. **Odoo splits one invoice into N open items** (one per payment-term installment). Our schema and D365 keep one open row per transaction. Any "30% now / 70% in 60 days" scenario is unrepresentable in `erp_cust_trans` today.
2. **Odoo has no AR/AP split.** One `account_move` table + `move_type` + one `res.partner` for customer *and* vendor (`supplier_rank` / `customer_rank` are just counters — `partner.py:606-607`). Our `erp_customers`/`erp_vendors`/`erp_cust_trans`/`erp_vend_trans` split is the D365 shape.
3. **Odoo's settled amount lives on the line, not the header.** `settled` in our schema is a header-level running total; Odoo recomputes `amount_residual` per line from the partials.

---

## 3. Payment terms & early payment discount vs D365 CashDisc

### 3.1 The Odoo model

`account.payment.term` (`account_payment_term.py:11-46`):

| Field | Meaning |
|---|---|
| `line_ids` → `account.payment.term.line` | the installment schedule; percents must total exactly 100 |
| `early_discount` (bool), `discount_percentage` (default **2.0**), `discount_days` (default **10**) | the entire cash-discount configuration, **on the term itself** |
| `early_pay_discount_computation` | `included` ("On early payment"), `excluded` ("Never"), `mixed` ("Always (upon invoice)") — tax-reduction treatment |
| `display_on_invoice`, `note`, `sequence`, `company_id` | presentation |

`account.payment.term.line` (`:281-308`): `value` ∈ {`percent`, `fixed`}, `value_amount`, `nb_days`, and `delay_type` ∈ **`days_after`, `days_after_end_of_month`, `days_after_end_of_next_month`, `days_end_of_month_on_the`** (+ `days_next_month`, a 2-char string 0–31).

Due-date arithmetic, `_get_due_date` (`:310-327`):
- `days_after` → `date_ref + nb_days`
- `days_after_end_of_month` → `end_of(month) + nb_days`
- `days_after_end_of_next_month` → `end_of(next month) + nb_days`
- `days_end_of_month_on_the` → `date_ref + nb_days + relativedelta(months=1, day=days_next_month)`; if `days_next_month == 0`, `end_of(date_ref + nb_days, 'month')`

Constraints (`_check_lines`, `:156-169`) — all raise `ValidationError` with these exact strings: *"The Payment Term must have at least one percent line and the sum of the percent must be 100%."*; *"The Early Payment Discount functionality can only be used with payment terms using a single 100% line."*; *"The Early Payment Discount must be strictly positive."*; *"The Early Payment Discount days must be strictly positive."*

Discount amount, `_get_amount_due_after_discount` (`:61-79`) and `_compute_terms` (`:200-214`):
- `included` → discount on the **whole** total: `total * (1 - pct)`
- `excluded` / `mixed` → the discount base is the **untaxed** amount, so the tax is never reduced: `total - untaxed * pct` (`:203-205`). **Naming trap:** the signature is `_get_amount_due_after_discount(total_amount, untaxed_amount)` and its body computes `(total_amount - untaxed_amount) * pct` (`:65-66`), but **both shipped call sites pass `amount_tax` into the `untaxed_amount` parameter** (`odoo/addons/account/views/report_invoice.xml:454`; `odoo/addons/account/tests/test_account_move_out_invoice.py:4974-4977`), so it evaluates to the same `total − untaxed*pct`. Read the parameter name and you get the formula backwards.
- default per country: BE → `mixed`, NL → `excluded`, everyone else → `included` (`:81-90`)
- `discount_date = invoice_date + discount_days` (`:195, 263-267`)

Eligibility at payment time, `account.move._is_eligible_for_early_payment_discount` (`account_move.py:3016-3028`): same currency **and** eligible `move_type` **and** `payment_term.early_discount` **and** `reference_date <= line.discount_date`.

Shipped defaults (`odoo/addons/account/data/account_data.xml:36-105`): `Immediate Payment`, `15 Days`, `21 Days`, `30 Days`, `45 Days`, `End of Following Month`, `10 Days after End of Next Month`, **`30% Now, Balance 60 Days`** (two lines: 30% @ 0d, 70% @ 60d), **`2/7 Net 30`** (`early_discount=True`, 2%, 7 days, single 100%/30d line), `90 days, on the 10th`.

### 3.2 Comparison table

| Dimension | **D365 / our world** (`research/erp-domain.md` §1.2, `world/schema.sql:8-9`) | **Odoo 19** |
|---|---|---|
| Where the discount lives | Separate `CashDisc` object, independent of terms of payment; our `erp_cash_disc(code, percent, days, next_code)` | On the payment term itself (`early_discount`/`discount_percentage`/`discount_days`) |
| Multiple discount tiers | **Yes** — `next_discount_code` chains (docs example `5D10%` → `10D5%` → `14D2%`) | **No** — exactly one tier; and it is *rejected* on multi-line terms |
| Installments | Not modelled (one due date per txn) | **Yes** — N lines, percent or fixed, each with its own `delay_type`/`nb_days` |
| Due-date rules | Net + N days, COD, current-month | 4 `delay_type` variants incl. end-of-next-month and "on the Nth of next month" |
| Tax treatment of the discount | Not modelled | 3-way `early_pay_discount_computation` (`included`/`excluded`/`mixed`), country-defaulted |
| Discount date storage | Derived (`invoice_date + CashDisc.Days`) | **Materialised** on the open item: `aml.discount_date`, `discount_amount_currency`, `discount_balance` |
| Discount posting | `CashDisc` main account for customer/vendor discounts | Dedicated `account_journal_early_pay_discount_gain/loss_account_id` on the company; write-off lines with `display_type='epd'` |
| Capture at payment | Settlement records `cash_disc_taken` | Wizard flips into `early_payment_discount_mode`, forces `payment_difference_handling='reconcile'` |
| Classic "2/10 Net 30" | Term `Net30` + discount code `Days=10, 2%` (two objects) | One term, e.g. shipped **`2/7 Net 30`** (one object) |

Porting verdict: our D365-shaped `erp_cash_disc` chain is **richer** on tiers and **poorer** on installments and tax treatment. If we want Odoo-flavoured tasks we need (a) a term-lines table, (b) a `discount_date` column on the open item.

---

## 4. Purchase side / three-way match (directly relevant to the parked `threeway_match` family)

### 4.1 `purchase.order`

| Field | Values | Evidence |
|---|---|---|
| `state` | `draft` ("RFQ"), `sent` ("RFQ Sent"), `to approve`, `purchase` ("Purchase Order"), `cancel` | `purchase_order.py:105-111` |
| `invoice_status` | `no` ("Nothing to Bill"), `to invoice` ("Waiting Bills"), `invoiced` ("Fully Billed") | `:127-131` |
| `locked` (bool), `lock_confirmed_po` | locked POs can't be cancelled/modified | `:112-118` |
| `partner_ref` | **vendor's own reference** — a second matching key | `:83` |
| `date_order`, `date_approve`, `date_planned` | order / confirmation / expected arrival | `:88-90, 132-134` |
| `invoice_ids`, `invoice_count` | stored computes | `:125-126` |
| `payment_term_id`, `incoterm_id`, `fiscal_position_id`, `currency_rate` | commercial terms | `:143-170` |
| `acknowledged` | vendor confirmed receipt of the PO | `:119-121` |

Transitions (`:611-655`): `print_quotation()` draft→sent; `button_confirm()` → `_confirmation_error_message()` guard → either `button_approve()` (→ `purchase`, stamps `date_approve`, optionally `locked`) or → `to approve` (double validation); `button_cancel()` refuses locked POs and refuses POs with non-draft/non-cancelled bills — *"Unable to cancel purchase order(s): %s. You must first cancel their related vendor bills."*; `button_draft()`; `button_lock()`/`button_unlock()`.

`invoice_status` is derived, not stored by hand (`_get_invoiced`, `:46-68`): `no` unless `state == 'purchase'`; `to invoice` if any non-display line has `qty_to_invoice != 0`; `invoiced` if all are zero **and** `invoice_ids` is non-empty.

### 4.2 `purchase.order.line` — the match quantities

| Field | Definition | Evidence |
|---|---|---|
| `product_qty` | ordered qty | `purchase_order_line.py:23` |
| `qty_received` (+ `qty_received_manual`, `qty_received_method`) | received qty; `qty_received_method` selection in this module is only `('manual','Manual')`, help text names a "Stock Moves" method that comes *"from confirmed pickings"* | `:61-66, 219-248` |
| `qty_invoiced` | Σ over `invoice_lines`, **excluding `state='cancel'` moves**, `+` for `in_invoice`, `−` for `in_refund`, UoM-converted | `:59, 165-200` |
| `qty_to_invoice` | **the whole 3-way-match rule** (see below) | `:67-68, 165-177` |
| `qty_received_at_date` / `qty_invoiced_at_date` | as-of-date recomputation via `accrual_entry_date` context | `:71-80, 181-242` |
| `invoice_lines` | O2M of `account.move.line` via `purchase_line_id` | `:56` |

```
if order.state == 'purchase':
    if product.purchase_method == 'purchase':   # "On ordered quantities"
        qty_to_invoice = product_qty  - qty_invoiced
    else:                                       # 'receive' = "On received quantities"
        qty_to_invoice = qty_received - qty_invoiced
else:
    qty_to_invoice = 0
```
(`purchase_order_line.py:171-177`)

**Bill-control policy** lives on the product: `product.template.purchase_method` ∈ {`purchase` "On ordered quantities", `receive` "On received quantities"}; services default to `purchase`, everything else to the company default (`odoo/addons/purchase/models/product.py:14-29`). This single field is the difference between a 2-way and a 3-way match, per product line.

### 4.3 Bill ↔ PO linkage

- `account.move.line.purchase_line_id` → `purchase.order.line` (`ondelete='set null'`, indexed) and `purchase_order_id` related through it (`odoo/addons/purchase/models/account_invoice.py:528-529`).
- `account.move.is_purchase_matched` = every `display_type='product'` invoice line has a `purchase_line_id` (`:102-108`).
- `account.move.purchase_id` / `purchase_vendor_bill_id` are **`store=False`** onchange helpers (`:19-23`) — a real RPC trap (see §7.5).

**Auto-matching a bill to POs**, `_match_purchase_orders` (`:349-448`), returns one of five verdicts:

| Verdict | Rule |
|---|---|
| `total_match` | PO name (or `partner_ref`) matches a reference on the bill **and** Σ remaining `amount_to_invoice` is within **±0.02** of the bill total; or (fallback) exactly one open PO for that vendor whose `amount_total` is within ±0.02 |
| `subset_total_match` | OCR only: a subset of PO lines sums to the bill total |
| `po_match` | OCR only: PO reference matched but no amount match |
| `subset_match` | EDI only: subset of PO lines matches subset of bill lines by unit price |
| `no_match` | nothing |

`TOLERANCE = 0.02` (`odoo/addons/purchase/models/account_invoice.py:13`). Candidate POs are filtered by `state='purchase'` **and** `invoice_status in ('to invoice','no')`; the vendor fallback uses `('partner_id','child_of',[partner_id])`.

`amount_to_invoice` per line = `(1 - qty_invoiced/product_qty) * price_total` (`:397`) — note this is **tax-inclusive** `price_total`, unlike the workbench which shows `price_subtotal`.

### 4.4 The 3-way-match workbench: `purchase.bill.line.match`

A **read-only SQL view** (`_auto = False`, `_table_query` = UNION ALL) over two selects (`purchase_bill_line_match.py:82-135`):

- **PO side** (`_select_po_line`, `:83-105`): `purchase_order_line` joined to `purchase_order` `WHERE po.state = 'purchase' AND (pol.product_qty > pol.qty_invoiced OR pol.qty_to_invoice != 0) OR ((pol.display_type = '' OR pol.display_type IS NULL) AND pol.is_downpayment AND pol.qty_invoiced > 0)` (`:102-104`) — exposes `line_qty` (=`product_qty`), `qty_invoiced`, `qty_to_invoice`, `line_amount_untaxed` (=`price_subtotal`). **SQL-precedence trap:** the third disjunct is un-parenthesised, so `AND` binds tighter than `OR` and the `po.state = 'purchase'` filter does **not** constrain the down-payment branch — fully-billed down-payment lines on POs in *any* state surface in the view.
- **Bill side**: `account_move_line` `WHERE display_type='product' AND move_type IN ('in_invoice','in_refund') AND parent_state IN ('draft','posted') AND purchase_line_id IS NULL` — i.e. **only unmatched bill lines**, with negative `id` to avoid collision.

Actions: `action_match_lines()` pairs POL↔AML per product (zip, then dump the remainder onto the last POL, then delete unmatched AMLs and append remaining POLs to the bill); `_action_create_bill_from_po_lines()` creates a draft `in_invoice` and calls `_add_purchase_order_lines`; `action_add_to_po()` opens `bill.to.po.wizard`, refusing multi-vendor (*"Please select bill lines with the same vendor."*) or multi-PO (*"Vendor Bill lines can only be added to one Purchase Order."*) (`:146-224`).

### 4.5 What is **not** in this checkout

The **goods-receipt layer**. `purchase/__manifest__.py:11` shows `'depends': ['account']` only; there is no `stock` addon in the checkout (`ls addons/` → account, analytic, payment, purchase, sale). So `stock.picking` / `stock.move` / the `purchase_stock` bridge that populates `qty_received` from confirmed receipts is **UNVERIFIED** here — only the `qty_received_method` help text (*"Stock Moves: the quantity comes from confirmed pickings"*, `purchase_order_line.py:62-64`) attests to it. Our world's `erp_product_receipts` table already stands in for it.

---

## 5. External API surface

### 5.1 Transport

- Core dispatcher `dispatch_rpc(service_name, method, params)` with services **`common`**, **`db`**, **`object`** (`odoo/http.py:428-449`). The `object` service is where `execute_kw` lives (`odoo.service.model.dispatch`) — **that module is not in this sparse checkout**, so the exact `execute_kw` signature is UNVERIFIED here and taken from docs below.
- JSON-RPC 2.0 over HTTP is the web transport: request `{"jsonrpc":"2.0","method":"call","params":{...},"id":null}`, success `{"jsonrpc":"2.0","result":{...},"id":null}`, error `{"jsonrpc":"2.0","error":{"code":1,"message":"…","data":{"code":"…","debug":"traceback"}},"id":null}` (`odoo/http.py:2558-2629`). In 19.0 `type='json'` is a deprecated alias for `type='jsonrpc'` (`:815-819`).
- Fetched docs (2026-08-11): <https://www.odoo.com/documentation/18.0/developer/reference/external_api.html> confirms endpoints **`/xmlrpc/2/common`** (unauthenticated meta-calls incl. `authenticate()` → `uid`) and **`/xmlrpc/2/object`** (authenticated `execute_kw`), API keys as password replacement (since 14.0), and domain examples of the form `[['is_company','=',true]]`. <https://www.odoo.com/documentation/19.0/developer/reference/external_api.html> shows 19.0 reorganised this into an **"External JSON-2 API"** with sections for Request/Response, API keys (creation/revocation/rotation), Access Rights, Transactions, and a **migration guide from XML-RPC/JSON-RPC** — the concrete 19.0 endpoint path and body schema were not recoverable from the fetch and are **UNVERIFIED**.

### 5.2 Model methods (the tool surface to mock)

Documented on both doc pages: `search`, `search_count`, `read`, `search_read`, `fields_get`, `create`, `write`, `unlink`, `check_access_rights` / `has_access`. Kwargs: `fields`, `offset`, `limit`, `order`, `context`. Plus (verified in-repo) `name_search(name, domain, operator='ilike', limit=100)` (`odoo/addons/base/models/res_country.py:90`, `res_users.py:663`), `fields_get(allfields, attributes)` (`res_users.py:1322`), and `_read_group(domain, groupby, aggregates)` used server-side with aggregate strings like `'invoice_date:min'`, `'amount_total_signed:sum'` (`odoo/addons/account/models/partner.py:482-491`).

### 5.3 Domain syntax

Polish-prefix list of `(field, operator, value)` triples with `'&'` (implicit), `'|'`, `'!'`. Operators actually exercised in `addons/account/models/` (frequency by grep):

`'='` (300), `'in'` (181), `'!='` (45), **`'child_of'`** (25), `'not in'` (24), `'<='` (13), `'>='` (11), `'<'` (11), **`'any'`** (10), `'>'` (8), `'ilike'` (7), **`'parent_of'`** (6), `'like'` (5), `'=like'` (5), `'=ilike'` (5), **`'not any'`** (4), `'=?'` (2), `'not ilike'` (1).

Exact command these figures come from (re-run per operator, from the checkout root; other plausible patterns give different totals, so this one is load-bearing): `grep -oF "'<OP>'," addons/account/models/*.py | wc -l`.

Concrete shipped examples worth copying verbatim into a mock's test suite:
- `domain="[('account_type', '=', 'asset_receivable')]"` (`partner.py:551`)
- `domain="[('id', 'in', suitable_journal_ids)]"` (`account_move.py:168`)
- `[('parent_state','=','posted'), ('company_id','child_of', root_id)]` (`partner.py:377-380`)
- `('partner_id', 'child_of', [partner_id])` (`purchase/models/account_invoice.py:437`)
- nested relational: `[('line_ids', 'any', [('reconciled','=',False), ('payment_date', operator, value)])]` (`account_move.py:2415`)
- prefix OR: `['|', *move._check_company_domain(...), ('company_id','child_of', ...)]` (`account_move.py:1469`); prefix NOT: `['!', ('id','child_of', ids)]` (`account/models/product.py:189`)

### 5.4 Errors and access control

`odoo/exceptions.py` gives every exception an HTTP status — this is exactly the error taxonomy a mock should emit:

| Exception | `http_status` | When |
|---|---|---|
| `UserError` | **422** | business-rule violation ("no sense given the current state of a record") |
| `AccessDenied` (⊂ UserError) | **403** | bad login/password; traceback suppressed |
| `AccessError` (⊂ UserError) | **403** | ACL/record-rule denial |
| `MissingError` (⊂ UserError) | **404** | write on a deleted record |
| `LockError` (⊂ UserError) | **409** | record could not be locked |
| `ValidationError` (⊂ UserError) | (inherits 422) | Python `@api.constrains` violation |
| `RedirectWarning` | — | warning + an action to jump to (e.g. untrusted bank account, `account_move.py:5601-5608`) |
| `ConcurrencyError` | — | retry-after-delay signal |

Anything else bubbling to the RPC layer becomes a "Server error" (`odoo/exceptions.py:1-5`). Serialised as `{name, message, arguments, context, debug}` (`odoo/http.py:469-479`).

**ACL model**: `ir.model.access` rows carry `model_id`, `group_id`, `perm_read/write/create/unlink`, `active` (`odoo/addons/base/models/ir_model.py:2080-2093`). Denial message is assembled from three constants (`ir_model.py:26-34`):

```
You are not allowed to access '<Model Label>' (<model.name>) records.

This operation is allowed for the following groups:
	- <Privilege>/<Group>
	...

Contact your administrator to request access if necessary.
```
(`read`/`write`/`create`/`unlink` swap "access"/"modify"/"create"/"delete"; if no group grants it, the middle block becomes *"No group currently allows this operation."* — `ir_model.py:2178-2196`.)

Accounting groups shipped: `group_account_readonly`, `group_account_invoice`, `group_account_basic`, `group_account_user`, `group_account_manager`, `group_account_secured`, plus feature groups `group_cash_rounding`, `group_partial_purchase_deductibility`, `group_validate_bank_account` (`odoo/addons/account/security/account_security.xml:46-101`).

**Field-level restriction** is the subtler one: `res.partner.credit`, `debit`, `credit_limit`, `total_invoiced`, `account_move_count` all carry `groups='account.group_account_invoice,account.group_account_readonly'` (`partner.py:514-539, 568`). A low-privilege RPC user does not get an error — the field simply isn't there.

---

## 6. Reference data & reports available in-repo

- **Chart-of-account types** (19 values) — `asset_receivable`, `asset_cash`, `asset_current`, `asset_non_current`, `asset_prepayments`, `asset_fixed`, `liability_payable`, `liability_credit_card`, `liability_current`, `liability_non_current`, `equity`, `equity_unaffected`, `income`, `income_other`, `expense`, `expense_other`, `expense_depreciation`, `expense_direct_cost`, `off_balance` (`account_account.py:44-65`).
- **Journal types** — `sale`, `purchase`, `cash`, `bank`, `credit`, `general`; `code` is a **5-char** sequence prefix (`account_journal.py:97-113`).
- **Lock dates** — five company-level dates: `fiscalyear_lock_date`, `tax_lock_date`, `sale_lock_date`, `purchase_lock_date`, `hard_lock_date`, each with a per-user computed variant honouring `account.lock.exception` (`odoo/addons/account/models/company.py:58-112`). Violation message: *"You cannot add/modify entries prior to and inclusive of: %(lock_date_info)s."* (`account_move.py:2808-2824`).
- **Partner credit** — `credit` ("Total Receivable"), `debit` ("Total Payable") computed as `SUM(amount_residual)` over posted, unreconciled lines on `asset_receivable`/`liability_payable` (`partner.py:372-402`); `credit_limit` (company-dependent), `use_partner_credit_limit`, `trust` ∈ {`good`,`normal`,`bad`}, and `days_sales_outstanding` = `(credit / total_invoiced_incl_tax) * days_since_oldest_invoice` (`partner.py:479-496, 521-534, 572`). Warning banner only fires on **draft `out_invoice`** when `company.account_use_credit_limit` (`account_move.py:1984-1998`).
- **Autopost bills** — `res.partner.autopost_bills` ∈ {`always`, `ask` ("Ask after 3 validations without edits"), `never`}, default `ask` (`partner.py:608-614`).
- **Sale side** (for symmetry): `sale.order.state` ∈ `draft`/`sent`/`sale`/`cancel`; `invoice_status` ∈ `upselling`/`invoiced`/`to invoice`/`no` (`odoo/addons/sale/models/sale_order.py:19-31`).
- **Payment providers**: `payment.transaction.state` ∈ `draft`/`pending`/`authorized`/`done`/`cancel`/`error` (`odoo/addons/payment/models/payment_transaction.py:65-69`).
- **Analytic**: `account.analytic.plan` (hierarchical) → `account.analytic.account` → `account.analytic.line`; distribution is a **JSON** field `analytic_distribution` on move lines (`odoo/addons/analytic/models/analytic_plan.py:14`, `analytic_account.py:12`, `analytic_line.py:164,227`; `account_move_line.py:434-437`).
- **Demo names** (canonical Odoo texture, contrast with our Contoso/Fabrikam set): **Wood Corner**, **Acme Corporation**, **Gemini Furniture**, **Ready Mat**, **OpenWood**, **Azure Interior** (`odoo/addons/base/data/res_partner_demo.xml:44-150`); demo invoices in `odoo/addons/account/demo/account_demo.py:184-260` use `End of Following Month` / `Immediate Payment` terms and back-date 2/3/15/40 days.
- **Not in this checkout** (enterprise `account_reports` / `account_followup` / `accountant`): the Aged Receivable/Payable report definition, the dunning/follow-up state machine, and the `in_payment` override. All **UNVERIFIED**.

---

## 7. Friction / chaos patterns worth stealing

1. **Selection values that never occur.** `payment_state` advertises `in_payment` and `invoicing_legacy`; community code produces neither (`account_move.py:7333-7338`). An agent that trusts `fields_get` over the data gets it wrong.
2. **Header due date lies under installments.** `invoice_date_due = max(date_maturity)` (`account_move.py:1079-1086`). With `30% Now, Balance 60 Days` the invoice is 30% overdue on day 1 while the header due date is 60 days out.
3. **Read-only virtual tables.** `purchase.bill.line.match` and `purchase.bill.union` are SQL views (`_auto=False`) — `create`/`write` on them is meaningless; you must call `action_match_lines()` / `_action_create_bill_from_po_lines()` (`purchase_bill_line_match.py:12,133-135`; `purchase_bill.py:10,25-43`).
4. **Duplicate detection asymmetry.** `_fetch_duplicate_reference` (`account_move.py:2071-2171`) ANDs a per-side condition onto one shared JOIN. Vendor side (`in_invoice`/`in_refund`, `:2117-2140`) is a **two-case OR**: *case 1* same `ref` **and** (either `invoice_date` NULL **or** equal `date_part('year', invoice_date)`); **or** *case 2* — the one that is easy to miss — **different** refs but same `commercial_partner_id` + same `amount_total` + `amount_total != 0.0` + same `invoice_date`. Customer side (`out_invoice`/`out_refund`, `:2106-2115`) is a single case: same `amount_total` **and** same `invoice_date`. Both sides then AND the shared JOIN predicates (`:2149-2159`): same `company_id`, `move.id != duplicate_move.id`, counterpart `state IN ('draft','posted')`, same `move_type`, same `currency_id`, and same `commercial_partner_id` (**or** a NULL partner matched against a *draft* counterpart). So the asymmetry is real, but neither side is keyed on `ref` alone and both are company/currency/type-scoped.
5. **`store=False` fields that look writable.** `account.move.purchase_id` / `purchase_vendor_bill_id` appear in `fields_get` but are onchange-only helpers (`purchase/models/account_invoice.py:19-23`). Writing them over RPC silently does nothing.
6. **Silently-missing fields, not errors.** Group-restricted `partner.credit`/`debit`/`credit_limit` vanish for under-privileged users rather than raising (`partner.py:514-539`).
7. **Five different reasons a post fails** — archived journal, archived account, inactive currency, negative total, missing bill date, unbalanced, plus five distinct lock dates and per-user lock exceptions (`account_move.py:5612-5671, 2808-2824`).
8. **Contact vs commercial entity.** Invoices hang off a child contact but `credit`/DSO roll up to `commercial_partner_id` (`account_move.py:431-437`, `partner.py:479-496`) — an intra-system version of our cross-system ID drift.
9. **Two references per PO.** `purchase_order.name` (ours) and `partner_ref` (theirs); the bill matcher tries both (`purchase/models/account_invoice.py:382-390`).
10. **Tolerance and unit mismatches.** PO matching uses tax-**inclusive** `price_total` within ±0.02 while the match workbench displays tax-**exclusive** `price_subtotal`; quantities are UoM-converted before comparison (`account_invoice.py:13,397`; `purchase_bill_line_match.py:97`; `purchase_order_line.py:197`).
11. **Sequence gaps and hash chains.** `made_sequence_gap`, `_made_gaps` index, `restrict_mode_hash_table`, `inalterable_hash`, `secure_sequence_number` — posted entries can be immutable and gap-audited (`account_move.py:328, 353-365, 791-792`).
12. **Cancel destroys reconciliation.** `button_cancel` calls `remove_move_reconcile()` and cancels linked payments (`account_move.py:6351-6363`) — a plausible "how did this invoice reopen?" mystery.
13. **`max_date` on partials** determines which reconciliations count in an as-of-date aged report (`account_partial_reconcile.py:64-68`). Aged balances as of a past date ≠ today's residuals.

---

## 8. Gap analysis vs `world/schema.sql`

Read at `world/schema.sql` (106 lines). Our ERP namespace is D365-shaped and **header-only**. Odoo concepts that are missing and that a credible three-way-match or reconciliation task needs:

| # | Missing concept | Odoo anchor | Why it blocks a task | Priority |
|---|---|---|---|---|
| 1 | **Vendor-bill / customer-invoice LINES** | `account.move.line` with `display_type='product'`, `quantity`, `price_unit`, `product_uom_id` | `erp_vend_trans` has only `amount`. You cannot compare billed qty/price to PO qty/price without bill lines. **This is the single blocker for `threeway_match`.** | P0 |
| 2 | **bill-line → PO-line link** | `account.move.line.purchase_line_id`; `move.is_purchase_matched` | No way to express "this bill line covers PO line 3", hence no matched/unmatched partition | P0 |
| 3 | **`qty_invoiced` / `qty_to_invoice` on PO lines** | `purchase_order_line.py:59-68,165-177` | `erp_purch_orders` has `qty_ordered` and `erp_product_receipts` has `qty_received`, but nothing tracks billed qty → no over-billing detection | P0 |
| 4 | **Bill-control policy per product** | `product.template.purchase_method` ∈ `purchase`/`receive` | Without it, every line is 3-way and services generate false exceptions | P0 |
| 5 | **PO `invoice_status` + real state machine** | `state` (5 values), `invoice_status` (3 values), `locked` | `erp_purch_orders.status` is free text; "which POs are ready to bill" has no ground truth | P0 |
| 6 | **Draft vs posted** | `account.move.state` | All our transactions are implicitly posted. "The bill is still in draft, that's why the aging is short" is one of the most realistic AP questions and is currently unaskable | P1 |
| 7 | **Payment-term installment lines** | `account.payment.term.line` (`value`, `nb_days`, `delay_type`) | `erp_payment_terms(code, days)` cannot express `30% Now, Balance 60 Days` or end-of-next-month | P1 |
| 8 | **Per-open-item due date** | `aml.date_maturity` | One `due_date` per transaction ⇒ installment aging impossible | P1 |
| 9 | **Materialised discount date on the open item** | `aml.discount_date`, `discount_amount_currency`, `discount_balance` | Our discount date is derivable from `erp_cash_disc.days`, so no "stored value disagrees with the rule" trap | P2 |
| 10 | **Tax split** | `amount_untaxed` / `amount_tax` / `amount_total`; `account.tax`; `early_pay_discount_computation` | Price-variance matching and discount-on-net-vs-gross questions need a tax column | P1 |
| 11 | **GL / double entry** | `account.move.line.debit/credit/balance`, `_check_balanced`, `account.account.account_type` | We ship no chart of accounts and no journal entries — any "post the accrual / where did it hit the GL" task is out of reach | P2 (large) |
| 12 | **Credit-note ↔ invoice link** | `reversed_entry_id` / `reversal_move_ids`; `payment_state='reversed'` | `txn_type='CreditNote'` exists but is unlinked ⇒ can't distinguish "reversed" from "paid" | P1 |
| 13 | **Reconciliation identity + undo** | `matching_number` (`P<n>`), `full_reconcile_id`, `remove_move_reconcile()` | `erp_settlements` is close but has no matching id and no unapply verb | P2 |
| 14 | **Bank statement lines** | `account.bank.statement.line` (`payment_ref`, `partner_name`, `amount`, `is_reconciled`, `amount_residual`) + `account.reconcile.model` | Payments already exist inside our ERP, so cash-application (match a bank line to an invoice) cannot be asked | P1 |
| 15 | **Multi-currency mechanics** | `amount_currency` vs `balance`, `currency_rate`, `exchange_move_id` on partials | We have a `currency` column but no rate table and no FX gain/loss | P2 |
| 16 | **Lock dates / period close** | 5 company lock dates + `account.lock.exception` | No "you cannot post into a closed period" friction | P2 |
| 17 | **Analytic dimensions** | `analytic_distribution` JSON on lines | No cost-centre/project questions | P3 |
| 18 | **Duplicate-bill surface** | `duplicated_ref_ids` + `_duplicate_bills_idx` | AP-controls task ("is this a duplicate?") has no supporting structure | P2 |

**Minimum schema delta to unpark `threeway_match`** (items 1–5): add `erp_vend_invoice_lines(invoice_id, line, item, description, qty, unit_price, uom, tax_amount, po_number, po_line)`, add `qty_invoiced` to `erp_purch_orders` (or derive it), add `bill_control` (`ordered`|`received`) per PO line or per item, and give `erp_purch_orders.status` a closed vocabulary plus an `invoice_status`.

---

## 9. Portable eval tasks (with ground-truth mechanisms)

| Task | What it tests | Ground truth | Anchor |
|---|---|---|---|
| **PO billing readiness** | derive `invoice_status` rather than trusting a stored status | recompute `qty_to_invoice` per line; `to invoice` iff any ≠ 0 | `purchase_order.py:46-68` |
| **3-way match exception report** | qty over-billing + price variance with tolerance | per line: `qty_billed > qty_received` (policy `receive`) or `> qty_ordered` (policy `purchase`); `|bill price − PO price| > 0.02` | `purchase_order_line.py:171-177`; `account_invoice.py:13` |
| **Bill-control policy trap** | not flagging a service line as over-received | `product.purchase_method == 'purchase'` ⇒ compare to ordered, not received | `purchase/models/product.py:14-29` |
| **Match the orphan bill lines** | fuzzy line pairing | AMLs with `purchase_line_id IS NULL` on draft/posted `in_invoice`; correct POL per product | `purchase_bill_line_match.py:107-131, 163-200` |
| **Which PO does this bill belong to?** | reference-vs-amount matching hierarchy | `total_match` if Σ remaining `amount_to_invoice` within ±0.02 else vendor+total fallback else `no_match` | `account_invoice.py:349-448` |
| **Duplicate vendor bill** | AP control | bills: same `ref` + (null date or same year) **OR** *different* ref + same `amount_total` (≠ 0) + same `invoice_date`; customer invoices: same `amount_total` + same `invoice_date`. Both sides additionally require same `company_id`, `move_type`, `currency_id`, `commercial_partner_id` (or null partner vs a draft counterpart) and counterpart `state IN ('draft','posted')` | `account_move.py:2106-2115` (out), `:2117-2140` (in), `:2149-2159` (shared JOIN) |
| **Why is this invoice not paid?** | payment ≠ reconciliation | payment exists in `in_process` / partials absent ⇒ `payment_state` stays `not_paid`/`partial` | `account_move.py:1222-1314`; `account_payment.py:453-467` |
| **Residual after payment + credit note** | multi-source settlement | residual = amount − Σ partials (payment) − Σ partials (refund); state `partial` | `account_move_line.py:242-253`; `account_move.py:1310-1311` |
| **Reversed vs paid** | credit-note-only offset | residual 0 **and** counterpart move types ⊆ {refund, entry} ⇒ `reversed`, not `paid` | `account_move.py:1295-1307` |
| **Early-payment-discount decision** | date + tax-treatment arithmetic | eligible iff `pay_date <= invoice_date + discount_days` and same currency; amount = `total*(1−p)` (`included`) vs `total − untaxed*p` (`excluded`/`mixed`) | `account_payment_term.py:61-79, 200-214`; `account_move.py:3016-3028` |
| **Installment aging** | per-line due dates | bucket each `payment_term` line's residual by its own `date_maturity`; header `invoice_date_due` is a decoy | `account_move.py:1079-1086`; `account_move_line.py:3320-3380` |
| **Exotic due dates** | date arithmetic | `End of Following Month`, `10 Days after End of Next Month`, `90 days, on the 10th` via `_get_due_date` | `account_payment_term.py:310-327`; `account_data.xml:66-105` |
| **FIFO cash application** | which invoices a lump payment clears | sort open lines by `(date_maturity or date, currency, amount_currency, balance)`, consume greedily | `account_move_line.py:2705-2730, 2567-2602` |
| **Aged balance as of a past date** | snapshot vs live | reconciliations only count from `partial.max_date` onward | `account_partial_reconcile.py:64-68` |
| **Reconciliation refusals** | negative testing | different accounts / different companies / already reconciled / cancelled / non-reconcilable account | `account_move_line.py:2644-2679` |
| **Post-failure diagnosis** | multi-cause friction | one of: no partner, no bill date, negative total, archived journal/account, inactive currency, unbalanced, lock date | `account_move.py:5612-5671, 2808-2824` |
| **`in_payment` doc-vs-reality** | trusting metadata over data | `fields_get` lists `in_payment`; no record can hold it in community | `account_move.py:7333-7338` |
| **DSO for a customer** | formula fidelity | `(credit / Σ amount_total_signed) × (today − min(invoice_date))`, where the `_read_group` domain is `state not in ('draft','cancel')` (cancelled excluded too, not just draft) **and** `move_type in get_sale_types(include_receipts=True)` **and** `company_id = env.company` **and** `commercial_partner_id in …`; result is `0` when the sum is falsy, and a missing partner defaults `oldest_invoice_date` to today | `partner.py:479-496`, domain at `:483-488` |
| **Credit-limit gate** | conditional warning | only draft `out_invoice`, only when `company.account_use_credit_limit`; limit from partner or company | `account_move.py:1984-1998`; `partner.py:521-528` |
| **Blocked payment** | sticky manual state | `action_toggle_block_payment` refuses when `paid`/`in_payment` | `account_move.py:6365-6373` |

---

## 10. Open questions

1. The Odoo 19 **External JSON-2 API** request/response envelope and endpoint path — the docs page reorganised away from the classic `execute_kw` description and the fetch did not surface the concrete shapes. Need a second fetch of the sub-pages (`.../external_api/*`) or a live server.
2. `odoo/service/model.py` (the real `execute_kw` dispatcher, `retrying`, `ConcurrencyError` handling) is **not** in this sparse checkout — argument order and the `@api.model` vs record-method calling convention are docs-only here.
3. `odoo/osv/expression.py` / `odoo/fields.py` are absent, so the **authoritative operator list** and `search_read` kwargs semantics are inferred from usage + docs, not from the parser.
4. `purchase_stock` / `stock` are absent ⇒ the **goods-receipt object** (`stock.picking`, `stock.move`, backorders, over-receipt tolerance) is entirely unverified. This matters because it is the third leg of the three-way match.
5. `account_reports` / `account_followup` / `accountant` (enterprise) are absent ⇒ the **Aged Partner Balance report definition**, the **follow-up (dunning) state machine** (Odoo's analogue of D365 collection letters), and the **`in_payment` override** are unverified.
6. Whether Odoo's `matching_number` (`P<n>` / full-reconcile name) is worth porting as a user-visible identifier, or whether our `erp_settlements.id` is sufficient.
7. Whether to model Odoo's polymorphic `account_move` at all, or keep the D365 Cust/Vend split and treat Odoo purely as a second mockable system (an "Odoo-shaped subsidiary book" alongside the QBO-shaped `books_*` namespace) for cross-system reconciliation chaos.
8. Company-level defaults referenced but not read this pass: `company.account_use_credit_limit`, `account_journal_early_pay_discount_gain/loss_account_id`, `po_lock`, `po_double_validation` thresholds.

---

## Sources

**In-repo (all paths relative to `research/external/repos/`)**
- `odoo/release.py` (version 19.0 final), `odoo/addons/account/__manifest__.py:142`, `odoo/addons/purchase/__manifest__.py:11,61` (LGPL-3, deps)
- `odoo/addons/account/models/`: `account_move.py`, `account_move_line.py`, `account_payment.py`, `account_payment_term.py`, `account_partial_reconcile.py`, `account_full_reconcile.py`, `account_journal.py`, `account_account.py`, `account_tax.py`, `account_bank_statement_line.py`, `account_reconcile_model.py`, `partner.py`, `company.py`, `sequence_mixin.py`
- `odoo/addons/account/wizard/`: `account_payment_register.py`, `account_move_reversal.py`
- `odoo/addons/account/data/account_data.xml`, `odoo/addons/account/demo/account_demo.py`, `odoo/addons/account/security/account_security.xml`
- `odoo/addons/purchase/models/`: `purchase_order.py`, `purchase_order_line.py`, `purchase_bill_line_match.py`, `account_invoice.py`, `product.py`; `odoo/addons/purchase/report/purchase_bill.py`
- `odoo/addons/sale/models/sale_order.py`, `odoo/addons/payment/models/payment_transaction.py`, `odoo/addons/analytic/models/*`
- `odoo/odoo/http.py`, `odoo/odoo/exceptions.py`, `odoo/odoo/addons/base/models/ir_model.py`, `odoo/odoo/addons/base/data/res_partner_demo.xml`

**Fetched 2026-08-11**
- <https://www.odoo.com/documentation/19.0/developer/reference/external_api.html> (External JSON-2 API: request/response, API keys, access rights, transactions, migration guide from XML-RPC/JSON-RPC)
- <https://www.odoo.com/documentation/18.0/developer/reference/external_api.html> (`/xmlrpc/2/common`, `/xmlrpc/2/object`, `authenticate()` → uid, `execute_kw()`, API keys since 14.0, domain example `[['is_company','=',true]]`)

**Cross-reference**
- `research/erp-domain.md` (D365/USMF model our world ships), `world/schema.sql` (current mock schema)
