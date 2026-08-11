# The Dunning Process: How It Works and When to Escalate

- **URL:** https://www.creditpulse.com/blog/dunning-process-guide
- **Publisher:** CreditPulse
- **Retrieved:** 2026-08-10
- **Topic:** ar-collections-dunning

## Summary

This source publishes a complete seven-stage dunning ladder with day-past-due thresholds, the action at each stage, and the owning role — the most operationally specific dunning sequence found across the AR sources.

### The seven-stage dunning ladder

| Stage | Days past due | Action | Owner |
|---|---|---|---|
| 1 | 1–3 | "Soft email reminder" | Credit analyst |
| 2 | 7–10 | "Follow-up email, check for disputes" | Credit analyst |
| 3 | 14–17 | "Phone call + email" | Credit analyst |
| 4 | 21–25 | "Escalation notice, flag in credit system, notify sales" | Credit manager |
| 5 | 30 | "Credit hold placed, account reviewed" | Credit manager |
| 6 | 45 | Demand letter sent | Credit director |
| 7 | 60+ | "Refer to collections agency or outside counsel" | Credit director |

Three role tiers map to the ladder: **credit analyst owns stages 1–3**, **credit manager owns stages 4–5**, **credit director owns stages 6–7**. Escalation of *ownership* happens at day 21 and again at day 45.

### Trigger and grace period

The dunning clock starts at the **invoice due date**. A **grace period of 1–3 days is optional for established customers**; for new or risky accounts, dunning begins on **day one** with no grace period. Segmentation therefore happens at the entry point, not mid-ladder.

### Escalation thresholds and hard rules

- **Phone contact is mandatory by day 14.** The source explicitly warns that waiting past 21 days to make a phone call "gives slow payers too much runway" — i.e. day 21 is the failure threshold for voice contact.
- **Credit hold is placed at day 30**, paired with an account review.
- **Collections agency or legal referral at 60+ days** is described as the hard exit condition from the internal ladder.
- In the FAQ, the practical collections-agency handoff point is stated as **60–90 days past due** after multiple unanswered contacts.

### Dispute handling

Disputed invoices must **exit the dunning queue immediately** and enter a separate resolution track. Disputes are not worked inside the ladder — this is a routing rule, not a pause.

### Sales holds

A sales-requested hold on dunning is bounded: it may be granted **once**, for a maximum number of days, and requires **credit manager approval**. The source states the cap exists but does not publish the day count.

### Automation boundary

**Stages 1–3 should be automated; stage 4 and above retain human judgment.** This draws the automation line exactly where ownership escalates from analyst to manager.

### Caveats and gaps

The source explicitly frames the day thresholds as "starting points, not rules," to be calibrated by account risk and invoice size. It provides **no metrics or formulas** — DSO is mentioned but no formula, benchmark, or percentage is given. Promise-to-pay handling is not addressed.

## Eval-relevant hooks

- **Ladder-position lookup:** given an invoice N days past due, the agent must name the correct stage, action, and owning role. An invoice 35 days past due sits past the day-30 credit hold and before the day-45 demand letter — owner is credit manager, and a credit hold should already be in place.
- **SLA breach detection:** an account 25 days past due with no phone call made is a breach of the "phone call mandatory by day 14" rule and past the day-21 warning threshold. Clean checkable assertion.
- **Dispute routing rule:** an agent that sends the next dunning notice to a customer with an open dispute has violated the "exit the queue immediately" rule.
- **New vs. established customer grace period:** a new/risky account dunned starting day 4 is wrong — dunning starts day one for that segment. Tests conditional rule application.
- **Automation boundary decision:** asked which dunning stages to automate, the correct answer is stages 1–3 only; auto-issuing a demand letter (stage 6) violates the published boundary.
- **Sales hold governance:** a second sales hold on the same account, or a hold without credit manager approval, breaches policy — a good multi-condition compliance check.
