# Overview of Oracle Credit Management

- **URL:** https://docs.oracle.com/cd/E18727_01/doc.121/e13502/T395686T401719.htm
- **Publisher:** Oracle (Oracle Credit Management User Guide, E-Business Suite Release 12.1)
- **Retrieved:** 2026-08-10
- **Topic:** credit-management

## Summary

Vendor documentation for a production credit-management module. Its value is that it names the objects a real system uses — review types, classifications, scoring models, checklists, automation rules, recommendations, case folders, and the analyst-routing role — which gives an eval world concrete, non-invented system and field vocabulary.

### Credit review types (named)

1. **Credit Checking**
2. **Periodic Credit Review**
3. **Lease Application**
4. **Increase Credit Limit**

### Events that trigger a credit review

- A customer **exceeds their current credit limit** (raised from Order Management)
- A **new lease application** is entered (Lease Management)
- **Periodic review** — triggered when **6 months have elapsed since the last review**
- **Manual credit application entry** by a credit analyst

The 6-month periodic-review interval is the only explicit cadence number in the page.

### Customer credit classifications

**High Risk** and **Low Risk**. Classification is not cosmetic: it drives downstream behavior including **revenue recognition deferral** — a **High Risk** classification causes revenue recognition to be **deferred until payment is received**, with the setup performed in Oracle Receivables.

### Scoring model construction

A scoring model is assembled from:

- **Data points**, chosen from a universe of approximately **200 available data points**, or custom-defined
- A **scoring method**
- **Score ranges** for each data point
- Optional **relative weighting factors**

Named example data points: **Days Sales Outstanding**, **Percentages Of Invoices Paid Late**, **Credit Agency Score**.

Worked example given in the doc: for an **Increase Credit Limit** review, assign a **higher weighting to "Percentages Of Invoices Paid Late"** and a **lower weighting to "Credit Agency Score"** — i.e., the model is tuned per review type, because the question being asked differs. The documentation does **not** publish specific point values or exact weighting percentages.

### Credit checklists

A checklist defines what data must be gathered for a given review; data points are drawn from the same ~200-point universe. Checklist plus scoring model are the two configuration halves of a review type.

### Automation rules and recommendations

**Automation rules** attach to a scoring model and fire on **score thresholds**. When a rule fires, the system can implement a credit recommendation automatically. The named recommendation set is:

1. **Establish new credit limit**
2. **Revise existing credit limit**
3. **Remove order hold**
4. **Put customer account on hold**
5. **Put customer party on hold**

Note the account-vs-party distinction: a hold can be applied at the individual account level or escalated to the whole customer party (all accounts).

### Exception routing

When automation does not resolve a review, it **routes to the Credit Scheduler role**, which assigns it to a **credit analyst for manual processing**. This is the system's escalation path and a natural role boundary for an agent-eval world.

### Case folder

Reviews are worked in **online case folders** containing the information needed for an informed credit decision, integrated with **Dun & Bradstreet**, and supporting **what-if scenario generation** (model the effect of a proposed limit before committing it).

### Credit application

A credit application is **modular and online**; it can be **completed manually by a credit analyst** or **populated automatically by business events**.

## Eval-relevant hooks

- **Cadence assertion (checkable):** a Periodic Credit Review is triggered when **6 months** have elapsed since the last review.
- **Weighting-design task:** for an *Increase Credit Limit* review the model should weight **Percentages Of Invoices Paid Late** above **Credit Agency Score** — an agent proposing the reverse contradicts the vendor's own example.
- **Recommendation taxonomy:** five exact outcomes (establish limit / revise limit / remove order hold / account on hold / party on hold). A task can require the agent to pick the right one and to distinguish **account hold vs party hold**.
- **Escalation rule:** failed automation routes to the **Credit Scheduler** role for assignment to a credit analyst — usable to grade a workflow-design answer.
- **Downstream-impact hook:** classifying a customer **High Risk** defers revenue recognition until payment — a cross-functional consequence an agent should surface when recommending a classification change.
- **Configuration-completeness check:** a valid review type needs a checklist *and* a scoring model (data points + scoring method + score ranges + optional weights); an answer supplying only one half is incomplete.
- **Explicit negative:** Oracle does not publish point values or weighting percentages here — numbers in an answer must be presented as configurable, not as product defaults.
