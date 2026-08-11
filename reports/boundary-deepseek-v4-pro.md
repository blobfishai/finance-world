# Boundary test — deepseek-v4-pro

> 2026-08-11 · 83 tasks · 1 trial each · breadth-first pass.
> Model reached through `sim/agent_openai.py` (OpenAI-compatible transport), graded by
> the same verifier, over the same MCP servers, with the same anti-hack vetoes as the
> Claude path. No grading code is model-specific.

## Headline

| | |
|---|---|
| tasks graded | **81** |
| pass | **62** |
| fail | **19** |
| pass rate | **77%** |
| excluded (budget-starved) | 2 |

A 77% pass rate is a usable calibration point: the world is neither trivially passed
nor uniformly too hard, and 19 tasks produce a reproducible failure to study.

## It separates models

On the 16 tasks both models have valid trials for, the world **discriminates on
7 of 16** — and in both directions, which is what a measurement
instrument has to do. A benchmark every model passes ranks nothing.

| task | deepseek-v4-pro | sonnet |
|---|---|---|
| `bank_rec/ach-return-mar` | PASS | MIXED **←** |
| `bank_rec/statement-divergence-feb` | PASS | PASS |
| `business_brief/brief-caterpillar` | PASS | PASS |
| `business_brief/brief-caterpillar-v2` | PASS | PASS |
| `cash_app/remittance-batch-mar02` | PASS | PASS |
| `cash_forecast/cesp-four-week` | PASS | MIXED **←** |
| `close_mgmt/subledger-tieout-feb` | PASS | PASS |
| `close_mgmt/two-period-close-cesq` | FAIL | PASS **←** |
| `collections_ops/escalate-sparrow-letter3` | PASS | PASS |
| `cross_system/email-invoice-meadow` | PASS | PASS |
| `cross_system/intercompany-tieout-feb` | PASS | PASS |
| `cross_system/total-ar-adventure-group` | FAIL | PASS **←** |
| `cross_system/total-ar-adventure-group-v2` | FAIL | PASS **←** |
| `cross_system/tracker-formula-drift` | FAIL | FAIL |
| `erp_qa/ar-balance-fourthcoffee-east` | PASS | MIXED **←** |
| `erp_qa/cash-disc-fourthcoffee-east` | PASS | FAIL **←** |

## Failure modes

| n | mode |
|---|---|
| 6 | wrong entity / wrong classification |
| 5 | wrong number — aggregation or logic |
| 5 | never submitted / incomplete submission |
| 2 | other |
| 1 | unit / scale error |

## Escalation works

The `doc_mode="buried"` lever (same ground truth, governing policy hidden among the
adjacent-policy library) flipped a task the model had passed:

| base | escalated |
|---|---|
| `business_brief/brief-caterpillar` PASS | `-v2` PASS |
| `cross_system/total-ar-adventure-group` FAIL | `-v2` FAIL |
| `vendor_master/dormant-vendor-review` PASS | `-v2` FAIL |

`vendor_master/dormant-vendor-review` passes at 22 tool calls; burying its SOP among
8 sibling policies fails it on `cutoff_date` — the model no longer derives the 12-month
boundary because it no longer reliably finds the rule that defines it.

## By family

| family | pass | fail | rate |
|---|---|---|---|
| cross_system | 2 | 3 | 40% |
| payment_run | 1 | 1 | 50% |
| cash_app | 1 | 1 | 50% |
| finance_qa | 4 | 3 | 57% |
| expense_audit | 2 | 1 | 67% |
| vendor_master | 3 | 1 | 75% |
| close_mgmt | 3 | 1 | 75% |
| erp_qa_fb | 26 | 8 | 76% |
| anomaly_triage | 1 | 0 | 100% |
| threeway_match | 2 | 0 | 100% |
| cash_forecast | 1 | 0 | 100% |
| pbc | 2 | 0 | 100% |
| business_brief | 2 | 0 | 100% |
| fpna | 2 | 0 | 100% |
| bank_rec | 2 | 0 | 100% |
| journal_entry | 1 | 0 | 100% |
| payment_proposal | 1 | 0 | 100% |
| collections_ops | 1 | 0 | 100% |
| erp_qa | 5 | 0 | 100% |

## Every failure

| task | calls | verdict |
|---|---|---|
| `cash_app/deduction-coding-mar` | 78 | answer:cinv701_reason:missing_terms(['pricing_variance']);answer:cinv701_reason:forbidden_terms(['unauthorized |
| `close_mgmt/two-period-close-cesq` | 11 | 02:answer:feb_erp_ap:missing;02:answer:feb_workbook_ap:missing;02:answer:feb_variance:missing;02:answer:jan_it |
| `cross_system/total-ar-adventure-group` | 32 | answer:erp_open_balance:off(got=1060156.1);answer:combined_exposure:off(got=1079206.1) |
| `cross_system/total-ar-adventure-group-v2` | 52 | answer:erp_open_balance:off(got=755828.79);answer:combined_exposure:off(got=781078.79) |
| `cross_system/tracker-formula-drift` | 56 | answer:erp_live_total:off(got=238195.17) |
| `erp_qa_fb/ap-invoices-1` | 50 | answer:open_invoice_total:mismatch(got=$0.00) |
| `erp_qa_fb/cash-collections-1` | 24 | answer:total_collected_fy:mismatch(got=$0.00) |
| `erp_qa_fb/credit-limit-3` | 29 | answer:credit_limit:not_numeric |
| `erp_qa_fb/credit-notes-1` | 24 | answer:unapplied_credit_total:mismatch(got=$0.00) |
| `erp_qa_fb/discounts-1` | 49 | answer:open_deduction_total:mismatch(got=$0.00) |
| `erp_qa_fb/invoicing-history-1` | 14 | answer:invoice_count:off(got=3.0);answer:invoiced_total:off(got=669832.5) |
| `erp_qa_fb/payment-history-2` | 16 | answer:largest_payment_amount:mismatch(got=46415.07);answer:largest_payment_voucher:mismatch(got=arpm000669) |
| `erp_qa_fb/sales-orders-3` | 16 | answer:order_count:off(got=1.0);answer:sales_order_id:mismatch(got=724) |
| `expense_audit/threshold-shaving-h1` | 22 | answer:detector_triggered:unparseable_yes_no(got=threshold shaving) |
| `finance_qa/scale-trap-lmt` | 4 | answer:revenue:scale_error(got=71.043, want=71043.0, off by /1000);answer:revenue_scale:wrong_scale(got=billio |
| `finance_qa/xom-cat-liquidity-compare` | 3 | answer:larger_company:missing_terms(['ExxonMobil']) |
| `finance_qa/xom-current-assets-followup` | 4 | 02:answer:current_assets_2023:missing;02:answer:pct_change:missing |
| `payment_run/shortfall-mar06` | 40 | answer:shortfall:off(got=62800.0) |
| `vendor_master/dormant-vendor-review-v2` | 21 | answer:cutoff_date:missing_terms(['2025-03-02']) |

## What this run is not

One trial per task cannot separate `flaky` from `solid` — that needs the 3-trial pass,
and flaky is the band the house method actually wants. Breadth came first deliberately:
it identifies *which* tasks discriminate, so depth is spent where it informs.

Before any of this was read as a result, `docs/AUDIT.md` **A9** was found and fixed —
the runner ended episodes on an empty assistant turn, truncating 4 runs at 5–35 turns
against a 40 budget and scoring them as wrong answers. Those trials were discarded and
re-run. Taken at face value the sweep would have overstated difficulty by ~17% of its
failures.

