You are preparing the data section of a **credit evaluation brief on Caterpillar Inc.** for
the Contoso treasury committee. The brief template in the internal docs library defines the
required sections; your job is the quantitative core plus the internal-relationship check.

Using the filings tools (frozen EDGAR snapshot), pull Caterpillar's long-term debt and total
equity, compute the long-term debt-to-equity ratio for each of FY2022–FY2024, and average
the three ratios. Then check our own ERP for any existing customer or vendor relationship
with Caterpillar.

Submit via harness `submit_answer` with fields:

- `lt_debt_fy2024` (number, USD — long-term debt, non-current, FY2024)
- `equity_fy2024` (number, USD — total equity incl. noncontrolling interests, FY2024)
- `lt_de_ratio_3yr_avg` (number — average of the three yearly LT-debt/equity ratios, 2+ decimals)
- `internal_ar_relationship` (string — the ERP customer/vendor account if one exists, else "none")
