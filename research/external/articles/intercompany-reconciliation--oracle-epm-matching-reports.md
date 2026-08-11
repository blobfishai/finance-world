# Setting Up Intercompany Matching Reports (Oracle EPM Financial Consolidation and Close)

- **URL:** https://docs.oracle.com/en/cloud/saas/financial-consolidation-cloud/usfcc/setting_up_intercompany_matching_reports.html
- **Publisher:** Oracle (Working with Financial Consolidation and Close, Oracle Cloud EPM)
- **Retrieved:** 2026-08-10
- **Topic:** intercompany-reconciliation

## Summary

This page is the most operationally explicit source found on **intercompany matching tolerances** — how a tolerance is defined as an amount versus a percentage, exactly how the percentage is computed, and how the two interact when both are set. It documents the report that a group controller uses to see entity-versus-partner balances and decide which differences are worth chasing.

### Report point of view and account selection

The report POV requires one member each from **Scenario, Year, Period, View, Consolidation, and Currency** — the Currency member must be a **Reporting Currency**. POV members accept substitution variables so the report re-points at runtime.

Accounts can be selected two ways:

- **Specific Accounts** — pick an account plus its matching accounts to be matched against each other.
- **Plug Accounts** — system-defined accounts that store elimination differences. Each plug account section gets its own **Grand Total** row; associated accounts must share an account-type pairing (**Asset with Expense**; **Liability, Revenue, or Equity** together). Without plug accounts the report shows a single Grand Total for the whole report.

The intercompany partner can be drawn from either the **Intercompany dimension** or the **Entity dimension** (in which case non-Intercompany entities are filtered out).

### Tolerance mechanics — the core operational content

**Tolerance Value (amount-based).** Enter a positive number; the **default is 0**. If the absolute variance is **less than or equal to** the tolerance value, the variance and the data cells are suppressed. Oracle's worked example: Entity = 299, Partner = 200, difference = 99. With Tolerance = 100 the row is **suppressed** (99 < 100); with Tolerance = 50 it is **not suppressed** (99 > 50).

**Tolerance Percent (percentage-based).** Enter a positive number **not greater than 100**. The computation is specified step by step:
1. Take the absolute value of the variance portion contributed by the **Accounts**.
2. Take the absolute value of the variance portion contributed by the **Matching Accounts**.
3. Take the **minimum** of those two values.
4. Tolerance Percent Value = that minimum × (Tolerance Percent ÷ 100).
5. If the Tolerance Percent Value is **greater than** the absolute variance, suppress the variance and the data cells.

If there are no Matching Accounts, only the Accounts portion is used.

**Both set.** When a Tolerance Value *and* a Tolerance Percent are supplied, take the **minimum of the two tolerance calculations**; if that minimum exceeds the absolute variance, suppress.

**Automatic suppression.** Rows with no data on both transactions are suppressed automatically, regardless of tolerance settings.

### Suppression dimensions and grouping

Suppression Dimensions are **Data Source, Movement, and custom-defined dimensions**; members are chosen via the Member Selector or a comma-delimited list. Each has three options:

- **Not Suppressed** (default) — the dimension appears as a Report Grid column, one row per outer-dimension combination.
- **Suppressed** — the dimension is excluded from the grid and each row implies a summation over all selected members (treated as the right-most inner dimension).
- **Group** — as Not Suppressed plus summation rows per group; limited to base members only. The Intercompany Partner dimension auto-groups.

Two further display controls: **Reversals** (exclude reversal Entity/Partner rows) and **Blank Columns** (exclude columns with no values across the entire column, applied per plug account or per matching set).

### Display options

**Scale Factor** 0–9 (default 0) multiplies unsuppressed data cells; **Decimal Override** 0–6 digits (default 0); **Member Display** as Name, Description, or Both; **Report Title** defaults to "Intercompany Report"; **Report Type** HTML, PDF, or XLSX; an option to show or hide the ICP prefix on the intercompany member; and an **Accounts in Rows** yes/no orientation toggle. The substitution variable **`EnableExcelNumberFormat=True`** forces numeric display in Excel, overriding user preferences.

Not covered on this page: currency/rate conversion detail, drill-down behavior, and the specific entity-versus-partner column layout in the rendered output.

## Eval-relevant hooks

- Direct computation task: given Entity 299 / Partner 200 and a tolerance of 100 versus 50, decide whether the difference is suppressed (99 < 100 → suppressed; 99 > 50 → shown). Reusable as a tolerance decision rule.
- Percentage-tolerance task: compute Tolerance Percent Value = min(|Accounts portion|, |Matching Accounts portion|) × (Tolerance Percent / 100) and compare it to the absolute variance — a common wrong answer is applying the percentage to the larger side or to the variance itself.
- Combined-tolerance rule: when both an amount and a percent are configured, the **minimum** of the two governs, not the maximum.
- Configuration assertion: matched account pairs must be type-compatible (Asset↔Expense; Liability/Revenue/Equity) — a mismatched pairing is a setup error an agent can be asked to flag.
- Reporting-integrity trap: a difference can disappear from the report because of tolerance suppression, automatic empty-row suppression, or the Blank Columns option — an agent claiming "no intercompany differences" must first verify the tolerance settings were 0/none.
- Report defaults worth asserting: Tolerance Value default 0, Tolerance Percent capped at 100, Scale Factor 0–9, Decimal Override 0–6.
