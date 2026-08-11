# Credit Management Operations in SAP SD (SAP ERP)

- **URL:** https://blog.sap-press.com/credit-management-operations-in-sap-sd-sap-erp
- **Publisher:** SAP PRESS (Rheinwerk Publishing) blog
- **Retrieved:** 2026-08-10
- **Topic:** credit-management

## Summary

Operational walkthrough of day-to-day credit management in SAP SD: which transaction codes a credit analyst actually runs, what the system checks, and how blocked sales documents get released. This is the best source in the set for **blocked-order / credit-hold mechanics with real system and field names**.

### Transaction codes (as described by this source)

**Blocked-document handling and review**

- **VKM1** — release or reject **blocked sales documents**. Menu path: *Logistics → Sales and Distribution → Credit Management → Exceptions*. From VKM1 the analyst can reach the customer master record, the credit master record, and open-sales-value reports through the **Environment** menu, so the release decision can be made without leaving the screen.
- **VKM3** — review the credit status of **multiple customers** simultaneously.
- **S_ALR_87012218** — generate the **credit master sheet** report for individual customer credit analysis.

**Credit master record maintenance**

- **FD32** — maintain the **individual customer credit master record**; modify **credit limits** and **risk categories**.
- **F.31** — **credit overview** transaction, for reviewing large numbers of customers at once.
- **F.34** — **mass change** of customer credit master record fields (the example given is **Next Review Date**) using selection criteria.

**Mass/technical field maintenance**

- **MASS** — object **KNA1**; modifies fields in tables **KNKK** and **KNKA**. Named fields: **risk category = KNKK-CTLPC**, **customer credit group = KNKK-GRUPP**, **individual limit = KNKA-KLIME**.
- **SE16N** — edit the credit limit field **KNKK-KLIMK** using the **SAP_EDIT** function.

### The credit checks SAP can perform (named check taxonomy)

The credit check configuration can subject a document to any combination of:

1. **Static credit limit** check
2. **Dynamic credit limit** check
3. **Document value** check
4. **Critical fields** check
5. **Next check date** check
6. **Maximum dunning level** check
7. **Open items** check
8. **Oldest open item** check

Plus **user exits 1, 2, and 3**, which are optional.

This is an exception-type taxonomy: a blocked order can be blocked for any of these reasons, **not only for exceeding the credit limit**. A credit analyst diagnosing a block must identify *which* check failed before deciding on release.

### Credit exposure components

The system tracks exposure across **open orders, open deliveries, open billing documents, and open accounts receivable**. The credit master record holds customer credit account data organized by **credit control area**.

### Credit review metrics

Named review metrics in the credit master sheet context: **total sales**, **days sales outstanding (DSO)**, and **credit utilized**.

### Practical implications for policy design

- Because **risk category** (KNKK-CTLPC) sits on the credit master record per credit control area, risk-tiering is a master-data attribute, not a report — changing a customer's tier changes which check configuration applies to their orders.
- Because **Next Review Date** is a mass-maintainable field (F.34), review cadence is enforced as data on the record rather than as a calendar reminder; a "next check date" check can itself block an order when the review is overdue.
- Release authority is operationally defined by who has access to **VKM1**, which is the natural place to encode a two-person or dollar-threshold approval rule.

## Eval-relevant hooks

- **Exception-taxonomy task:** given a blocked sales order, determine which of the eight named checks caused the block (static limit, dynamic limit, document value, critical fields, next check date, max dunning level, open items, oldest open item). An agent that assumes "credit limit exceeded" by default fails when the true cause is e.g. **maximum dunning level** or **oldest open item**.
- **Transaction-code assertions (checkable):** VKM1 = release/reject blocked SD documents; FD32 = maintain individual credit master (limit + risk category); F.31 = credit overview; F.34 = mass change of credit master fields such as Next Review Date; S_ALR_87012218 = credit master sheet.
- **Field-level assertions:** risk category = **KNKK-CTLPC**; customer credit group = **KNKK-GRUPP**; individual limit = **KNKA-KLIME**; credit limit = **KNKK-KLIMK**.
- **Exposure-calculation rule:** credit exposure = open orders + open deliveries + open billing documents + open AR — an agent computing exposure from AR alone understates it.
- **Cadence-enforcement hook:** an overdue **next check date** can itself block orders; the remediation is a documented credit review, not a limit increase.
- **Segregation-of-duties hook:** VKM1 release authority is the control point for who may free a held order; a policy answer should tie release authority to role and dollar threshold.
