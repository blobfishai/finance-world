You are preparing the quantitative core of a **credit evaluation brief on Caterpillar Inc.**
for the Contoso treasury committee. Today is March 2, 2026.

Follow the team's brief template and credit policy — both live in the internal docs
library, and the committee will reject numbers that don't follow them. Compute the
leverage picture the template requires for each of FY2022–FY2024 from the filings
snapshot, classify Caterpillar's leverage using the credit policy's bands, and run the
standard internal-relationship check in our ERP.

Submit via harness `submit_answer` with fields:

- `lt_de_2022`, `lt_de_2023`, `lt_de_2024` (numbers — long-term-debt-to-equity per fiscal year, 2 decimals)
- `lt_de_ratio_3yr_avg` (number — average of the three yearly ratios)
- `leverage_classification` (string — the band name the credit policy assigns to the FY2024 ratio)
- `internal_relationship` (string — ERP account id if we already trade with them, else "none")
