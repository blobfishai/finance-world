# Credit Basics: Setting Credit Limits

- **URL:** https://nacm.org/pdfs/articles/CreditBasicsSettingCreditLimits.pdf
- **Publisher:** NACM — National Association of Credit Management (NACM-National)
- **Retrieved:** 2026-08-10
- **Topic:** credit-management

## Summary

A short NACM-National reference article that enumerates the methods trade-credit departments actually use to set a customer credit limit. Its framing is that **"no two companies are alike when it comes to actually setting a customer's credit limit"** and that doing so is **"often more art than science."** Its value for eval purposes is the named taxonomy of nine methods, each with a stated mechanism and stated organizational trade-off. It contains **no numeric thresholds, no percentages, and no worked formulas** — this is stated explicitly here so the absence is not mistaken for omission.

### The nine named credit-limit-setting methods

**1. Payment Record.** Works only where the customer already has payment history with your company. Pay on time or early and the credit limit goes up; pay late or not at all and a **credit review process is triggered**. NACM notes this is the **sales department's favorite** method because it incentivizes better-paying buyers to buy more.

**2. Competition.** Set the limit relative to what competitors are extending, so that a lower limit does not box the company out of potential sales. NACM flags this as **difficult to evaluate** when your company is much smaller or larger than competitors, or plays a different role in the supply chain than other suppliers.

**3. Security.** The presence of **lien rights** in certain transactions makes it substantially easier to justify higher credit limits.

**4. Payment Performance.** Suited to a company with a **conservative risk appetite that still wants new customers**. New buyers with little payment history start at a **lower credit limit** and are **rewarded with increases as they pay**. NACM notes sales is **less of a fan** because it slows sales growth.

**5. Period of Time.** The amount a customer can purchase **over a designated period** — a week, a month, or another interval — cannot exceed the established credit limit. NACM notes this **speeds up order approval** because anything fitting within the threshold for the period can be approved without further review.

**6. Agency Rating.** Build a **matrix** in which a given credit-agency rating on a credit report maps to a specific credit limit.

**7. By Formula.** Take a number of different calculations suited to the company's needs and establish a way to **combine them, divide them, and average them** into a limit. NACM's caveats: it **depends on data availability** (key figures on a new customer may not exist), and companies using a formula **tend to rely on it as a preliminary tool** that is then extrapolated using other methods into the actual appropriate limit.

**8. Expectation of Use.** Take the **expected dollar volume of credit sales over a period of time**, **divide by the number of expected orders over the same period**, and use the result as the basis for a **preliminary credit limit estimate**. This is the one method in the article with an explicit arithmetic structure:

> preliminary limit basis = expected credit sales volume over period ÷ expected number of orders over that period

**9. Collection.** Described as "like a secured investment with slightly less security": the more confident the company is that a receivable **can be collected**, the easier it is to justify a higher limit, since sales made are expected to be collected.

### Structural reading

The nine methods sort into three families that are useful for scenario design: (a) **behavior-based** — Payment Record, Payment Performance, Collection; (b) **third-party/data-based** — Agency Rating, By Formula; (c) **commercial/structural** — Competition, Security, Period of Time, Expectation of Use. A realistic corporate credit policy typically composes several: e.g., Agency Rating to set the initial band, Expectation of Use to size it against actual order flow, Payment Performance to govern increases.

## Eval-relevant hooks

- **Formula assertion (checkable):** Expectation of Use = expected credit sales volume over a period ÷ expected number of orders in that period, yielding a *preliminary* limit — an agent that treats the output as the final limit contradicts the source.
- **Method-identification task:** given a described policy ("new customers start low and earn increases as they pay"), name the method — the correct answer is **Payment Performance**, not Payment Record (which requires existing history with your company).
- **Trade-off assertion:** Payment Record is sales-favored; Payment Performance is sales-disfavored because it slows growth. Usable in a stakeholder-conflict scenario between Credit and Sales.
- **Precondition rule:** the **By Formula** method is data-dependent and NACM positions it as preliminary only — a good trap for an agent that proposes a formula-only limit for a brand-new customer with no financials.
- **Structural hook:** Agency Rating implies a **rating-to-limit matrix**; a task can ask the agent to construct that matrix and defend the mapping.
- **Security hook:** presence of **lien rights** is an explicit justification for a higher limit — checkable in a construction/materials scenario.
- **Explicit negative:** this source publishes no percentages, multipliers, or approval-authority dollar levels; any such numbers in a candidate answer must be sourced elsewhere.
