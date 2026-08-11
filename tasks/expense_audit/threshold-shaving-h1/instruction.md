You are auditing expenses at Contoso. Today is March 2, 2026.

The six-month expense extract (September 2025 – February 2026) is on the shared drive.
Individually every claim is compliant. Apply the **threshold-shaving detector** described
in the expense audit policy and report whether any employee triggers it.

Submit via harness `submit_answer`:

- `shaving_employee` (string — the employee who triggers the detector, or "none")
- `shaving_claim_count` (number — their claims inside the detector's amount band)
- `shaving_total` (number, USD — total of those claims)
- `detector_triggered` ("yes" or "no")
