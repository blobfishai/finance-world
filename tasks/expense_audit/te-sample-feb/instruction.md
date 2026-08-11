You are auditing travel & expense claims at Contoso. Today is March 2, 2026.

The February expense export is on the shared drive. Test every line against the T&E policy
in the docs library and report the exceptions.

Submit via harness `submit_answer`:

- `violation_count` (number of expense lines that breach the policy)
- `violating_report_ids` (string — comma-separated report ids with violations)
- `out_of_policy_amount` (number, USD — total amount of the violating lines)
- `worst_violation_rule` (string — the policy rule broken by the largest violating line)
