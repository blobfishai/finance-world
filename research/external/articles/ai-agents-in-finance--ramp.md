# Policy Agent Overview (Ramp)

- **URL:** https://support.ramp.com/hc/en-us/articles/44072387128979-Policy-Agent-Overview
- **Publisher:** Ramp (product support documentation)
- **Retrieved:** 2026-08-10
- **Topic:** ai-agents-in-finance

## Summary

**Policy Agent** is Ramp's AI expense reviewer. It applies the customer's **written expense policy** to **every card transaction and reimbursement**, so the unit of work is a single expense event rather than a batch or a report.

### Decision model — three internal outcomes, two UI buckets
Policy Agent produces one of three internal decisions:
1. **Approval recommended** — the expense clearly complies with policy.
2. **Requires review** — the agent is uncertain, is missing context, or the policy explicitly requires human review.
3. **Rejection recommended** — the agent identifies a clear policy violation.

The UI collapses the second and third into a single **"Review recommended"** bucket. Documented behavior when policy language or submissions are broad, ambiguous, or missing context is that the agent **leans conservative** and routes to **Requires review** rather than approving.

### Autonomy posture and approval gates
Policy Agent **starts in "review-only" mode**, where it only recommends actions. It **does not auto-approve by default**; the customer decides, through workflows, when the agent may automatically approve clearly in-policy expenses. The documentation states plainly that **reviewers always retain final authority**. This is the cleanest published example of a graduated autonomy ladder in corporate finance: recommend-only → workflow-gated auto-approval on the low-risk tail → human decision on everything else.

### Inputs the agent evaluates
The evidence set per expense is enumerated: merchant name, amount, date/time, currency and converted USD amounts; item names and tax; **receipt OCR and itemization**; employee memo, attendees, and trip details (itinerary, name, description); location; custom fields such as department, role, entity, level, and office location; card details (last 4, physical vs. virtual, spend program); fund-level data; and reference data such as **GSA rates**.

### Documented limitations (as important as the capabilities)
- Policy Agent **evaluates each expense individually and cannot look across multiple transactions** — so it cannot detect split-transaction abuse, cumulative-limit breaches, or behavioral patterns.
- It **does not determine whether GL coding is correct**, and it does not rely on employee-entered GL codes.

### Published performance numbers
The one quantitative claim: **early customers reduced manual reviews by about 85% while maintaining 99%+ accuracy**. No denominator, review period, or measurement methodology is published alongside those figures, so they should be treated as vendor-reported.

The overall shape — deterministic policy text as the ground truth, per-transaction evaluation with cited context, conservative escalation on ambiguity, and human final authority — makes Policy Agent a useful reference design for any "policy compliance agent" eval, because the correct answer for an ambiguous case is *escalate*, not *guess*.

## Eval-relevant hooks

- Three-way classification task: given a policy excerpt plus a transaction record, output **Approval recommended / Requires review / Rejection recommended**; ambiguity must map to **Requires review**, not to approval — a directly gradeable escalation rule.
- Trap task: present a split transaction (two same-day charges each under the limit). Correct behavior is to note that per-expense evaluation **cannot** catch this, since the agent cannot look across multiple transactions.
- Trap task: ask the agent to fix or validate a GL code — the documented scope explicitly excludes GL-coding correctness.
- Input-completeness check: score whether the agent uses receipt itemization, attendees, trip details, and reference rates (e.g., **GSA rates**) rather than merchant + amount alone.
- Autonomy-configuration task: describe the correct rollout — start in **review-only**, then enable workflow-gated auto-approval only for clearly in-policy expenses.
- Metric-grounding assertion: the only published figures are **~85% reduction in manual reviews** and **99%+ accuracy**; any other stated number is unsupported.
