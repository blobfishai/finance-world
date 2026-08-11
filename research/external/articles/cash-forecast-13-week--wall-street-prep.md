# 13-Week Cash Flow Model (TWCF)

- **URL:** https://www.wallstreetprep.com/knowledge/demystifying-the-13-week-cash-flow-model-in-excel/
- **Publisher:** Wall Street Prep
- **Retrieved:** 2026-08-10
- **Topic:** cash-forecast-13-week

## Summary

A restructuring-practitioner explanation of the thirteen-week cash flow model (**TWCF**), defined as **"a near-term oriented weekly cash flow forecast used in the context of corporate restructuring."** This is the source that best establishes *why the model exists*, *who builds it*, and *what supporting schedules it requires*.

### Method and horizon

- The model uses the **direct method** to forecast **weekly cash receipts less cash disbursements** — it is built from actual cash movements, not from accrual revenue and expense.
- The 13-week horizon gives immediate visibility into liquidity needs during financial distress (one fiscal quarter).
- The model is **updated weekly** and typically carries **one week of actual historical data** alongside the forecast weeks.
- A distinguishing feature versus generic forecasting: the TWCF **reconciles the weekly cash forecast to the EBITDA forecast**, tying profit projections to short-term liquidity constraints.

### Receipts line items

- **Cash collections from accounts receivable** — driven by **Days Sales Outstanding (DSO)**
- **Asset liquidation proceeds**
- **DIP or revolver borrowings**

### Disbursements line items

- **Inventory purchases** (routed through accounts payable)
- **Accrued wages and benefits** — described as **"often the largest disbursement"**
- **Vendor payments**
- **Debt service**
- **Operating expenses**

### The four supporting roll-forward schedules

The TWCF is not a standalone tab; it integrates four roll-forwards, each with its own driver:

| Roll-forward | Driver / inputs |
|---|---|
| **Accounts Receivable** | AR aging data plus **DSO** assumptions |
| **Inventory** | Historical ledger plus **COGS** forecasts and **turnover** projections |
| **Accounts Payable** | Tied to inventory purchases and **DPO** assumptions |
| **Accrued Wages** | Income-statement expense projections with **payroll timing** |

This structure is the answer to "where do the numbers come from": collections come off the AR roll-forward, vendor payments off the AP roll-forward, and payroll off the accrued-wages roll-forward with its own calendar.

### Borrowing base

The TWCF quantifies **actual revolver availability** against the **"complicated borrowing base formulas"** that constrain credit facilities, so that the model identifies **unmet funding needs** rather than just a cash balance. In distress, the constraint is frequently availability under the borrowing base, not the raw cash number.

### Ownership and audience

**Restructuring professionals** prepare the TWCF for **management, creditors, and other stakeholders**. In **Chapter 11**, it supports **DIP financing requests** and influences court-approved reorganization outcomes — which is why DIP lenders condition financing on it.

### Model-integrity caution

Because weekly updating is required, the source warns that the Excel architecture must be robust enough to prevent **model error** under frequent changes. Fragility is treated as a first-order risk of the format, not an afterthought.

### Explicit gap

This source does **not** publish acceptable variance thresholds, a reporting weekday, or a line-item count. Those come from the Zone & Co and Eightx sources in this set.

## Eval-relevant hooks

- **Method assertion (checkable):** the TWCF uses the **direct method**; an agent that builds it by adjusting net income (indirect method) is wrong for this artifact.
- **Structural task:** name the four required roll-forwards (AR, Inventory, AP, Accrued Wages) and their drivers (DSO, COGS/turnover, DPO, payroll timing). A model missing the accrued-wages roll-forward mis-times the single largest disbursement.
- **Liquidity-constraint hook:** the binding constraint in distress is often **borrowing base availability**, not cash balance — a task can supply a borrowing base formula and ask for true available liquidity.
- **Reconciliation hook:** the TWCF should **reconcile to the EBITDA forecast**; a checkable requirement that the cash model and the P&L forecast are not independent artifacts.
- **Stakeholder hook:** the audience is management, creditors, and (in Chapter 11) the DIP lender and court — an agent producing an internal-only management view misses the lender reporting obligation.
- **Receipts-composition check:** **DIP or revolver borrowings** are receipts in this model; treating draws as non-cash or as financing-only omissions breaks the ending-cash roll.
