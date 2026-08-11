# How to Build a 13-Week Cash Flow Forecast (Template + Real Benchmarks)

- **URL:** https://eightx.co/blog/build-13-week-cash-flow-forecast
- **Publisher:** Eightx
- **Retrieved:** 2026-08-10
- **Topic:** cash-forecast-13-week

## Summary

A fractional-CFO build guide written from a direct-to-consumer / ecommerce operating context. Its distinguishing contributions to this topic set are (a) an explicit **weekly roll-forward ritual with a named weekday**, (b) a **minimum-cash trigger expressed as a percentage of burn**, and (c) **channel-specific settlement timing** for receipts. Note the DTC framing when generalizing: the settlement mechanics are channel-specific, but the roll-forward discipline and trigger logic are not.

### Horizon and roll-forward ritual

- Rolling **13-week** model — one fiscal quarter plus a buffer week.
- **Updated every Monday.** The published sequence is: **drop Week 1 → shift Weeks 2–13 forward → add a fresh Week 13 at the back → document the variance between forecast and actuals.**
- Template shape: **one spreadsheet, 13 weekly columns, five line-item groups plus a summary block.**

### The five line-item groups and their timing rules

| Group | Items | Timing rule |
|---|---|---|
| **Receipts** | Shopify, Amazon, wholesale, financing draws | Cash lands per channel: **Shopify 2–5 business days**; **Amazon ~14-day cycle**; wholesale per **AR-aging-adjusted** terms |
| **Inventory POs** | Deposits, balances, freight, duty | Mapped to the **PO schedule and supplier terms** |
| **Ad spend** | Meta, Google, TikTok | **Trailing 4-week average**, adjusted for scale-ups |
| **Payroll** | Salaries, contractors | **Exact amounts on exact pay dates** |
| **Taxes & fixed** | Estimated taxes, rent, software, 3PL | The **week each actually drafts** |

The governing principle across all five: schedule cash on the week it **actually moves**, not the week it is earned, invoiced, or contractually due.

### Data sources named

- **AR aging** — for actual wholesale payment timing rather than stated terms
- **PO schedule** — for exact deposit and balance draft weeks by supplier
- **Payroll calendar** — for exact pay-date amounts
- **Channel settlement documentation** — Shopify Help Center (2–5 business day US payout), Amazon Seller Central (14-day cycle plus reserve)
- **Seasonal reserve terms** — peak-season processor holds, e.g. **10% of peak sales delayed 90–120 days**

### Calculations

> **Net cash flow (each week) = Receipts − Outflows**
> **Ending balance = prior week's ending balance + current week's net cash flow**

The **trough** is the lowest point across the 13-week curve; identifying it is the model's primary output.

### Thresholds and benchmarks published

- **Minimum cash threshold: 20–30% of monthly burn** — flag any week that breaches it.
- **Median small-business cash buffer: 27 days.**
- **Scaled DTC inventory days: 117–221 days**, against a **91-day forecast window** — i.e., the cash cycle can exceed the forecast horizon.
- **Typical DTC cash conversion cycle: ~130 days.**
- **Bank prime rate (May 2026): 6.75%**; typical DTC line of credit at **prime + 1–3% = 8–10%**.

### Action triggers and variance discipline

- Act **2–3 weeks before the trough**, not at it. Named levers, in order of flexibility: **movable items (inventory POs, ad spend)**, then **pull-forward tactics (early-payment discounts)**, then a **pre-arranged line draw**.
- Write **1–2 lines of variance commentary weekly** — e.g., "consistently overestimate collections" or "inventory costs exceed projections" — so the model recalibrates rather than merely records.

### Ownership

Not explicitly assigned; framed as a leadership/CFO function reviewed on a weekly cadence with variance notes for discussion.

## Eval-relevant hooks

- **Roll-forward assertion (checkable):** every **Monday**, drop Week 1, shift Weeks 2–13 forward, append a new Week 13, document variance. An agent that rebuilds the forecast from scratch or extends without dropping Week 1 fails the rolling-forecast definition.
- **Trigger rule:** minimum cash threshold set at **20–30% of monthly burn**; flag any breaching week. A task can supply monthly burn and a 13-week balance series and require the agent to identify breach weeks and the trough.
- **Lead-time rule:** remediation must begin **2–3 weeks before the trough**, and the lever hierarchy is movable spend → pull-forward tactics → line draw. Grading an agent that waits until the trough week is straightforward.
- **Timing-mechanics task:** given Shopify (2–5 business days), Amazon (~14 days plus reserve) and wholesale terms, place receipts in the correct weeks — a checkable arithmetic exercise.
- **Horizon-limitation insight:** with inventory days of **117–221** against a **91-day** window, the forecast cannot see a full inventory cycle; an agent should flag the need for a longer-horizon complement.
- **Seasonal-reserve trap:** a **10% processor hold on peak sales released in 90–120 days** falls outside or at the edge of the window and is a classic omitted receipt.
- **Formula assertions:** net cash flow = receipts − outflows; ending balance = prior ending + current net.
