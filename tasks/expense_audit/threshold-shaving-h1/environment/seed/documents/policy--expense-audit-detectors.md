# Expense Audit Detectors (FIN-POL-021)

> SIMULATION ONLY

**Owner:** Controller · **Version:** 1.1 · **Effective:** 2026-01-01

Receipts are required for any single claim **over USD 500**. Compliant-looking claims can
still indicate avoidance behaviour, so the following pattern detectors run each period.

**Threshold shaving.** Flag any employee with **more than 5 claims in the USD 450–499.99
band within a rolling 6-month window**. Each such claim is individually within policy;
the pattern is the finding. Report the employee, the count, and the banded total, and
route to the Controller — do not accuse in the report, state the pattern.

**Duplicate claims.** Two claims sharing Amount + Date + Currency + Expense type +
Merchant are duplicates regardless of report id.

**Split claims.** Two or more same-day claims by one employee in one category that sum to
more than the receipt threshold.
