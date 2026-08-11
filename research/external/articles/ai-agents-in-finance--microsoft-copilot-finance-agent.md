# Create Custom reconciliation agents with Finance Agent (preview)

- **URL:** https://learn.microsoft.com/en-us/copilot/finance/reconcile/custom-reconciliation-agent
- **Publisher:** Microsoft Learn (Microsoft 365 Copilot Finance documentation)
- **Retrieved:** 2026-08-10
- **Topic:** ai-agents-in-finance

## Summary

This is Microsoft's how-to for building **custom reconciliation agents** with **Finance Agent** in **Microsoft 365 Copilot Studio** — a different product surface from the in-ERP Dynamics 365 Finance Account Reconciliation Agent. Unlike the managed agent, a custom agent is author-controlled across seven documented dimensions: **how you trigger the agent**, **the data sources it accesses**, **data extraction**, **templates** (key mapping), **target location for the report**, **communication to report recipients**, and **post-reconciliation mitigations**.

### Concrete architecture
Custom agents are assembled from Power Platform connectors. The documented connector set is: **Finance Agent** (connects to the Finance Agent backend that provides the Reconciliation Agent and other AI services), **SharePoint**, **Outlook (Office 365)**, **CSV/Data Operations** (the **Create CSV table** action converts ERP JSON into CSV for the Finance Agent connector), and **Teams**. Premium connectors (Finance, Microsoft Fabric) require a new connection with external-system credentials; connections can default to the end user's or the agent author's credentials, and author credentials are described as common for internal scenarios. DLP policies must permit the connectors.

### Two shipped example agents (unmanaged solutions)
- **Finance Agent – ERP Integration Example** (download: aka.ms/fnocustomreconagent). Trigger: **runs once per week**. Data sources: two tables in Finance. Extraction: **Create CSV Table**. Report saved to **SharePoint**; notification by **email with a link to the report**. Backing flow: **PerformReconciliationFromFin&Ops**. Prerequisite: **full-access user license for Finance**.
- **SAP Finance Agent – ERP Integration Example** (download: aka.ms/sapcustomreconagent). Same weekly trigger and CSV extraction; requires an **SAP S/4HANA instance** because it uses the **SAP OData connector** (earlier SAP versions unsupported). Report saved to SharePoint; notification via **Teams**, configured through **Send Success Notification** and **Send Error Notification** actions in the **PerformReconciliationFromSAP** flow.

### Trigger mechanics and the matching-key problem
The trigger is a **Recurring Copilot Trigger** card, weekly by default, editable via **Recurrence**. The instruction the trigger sends the agent is a natural-language template: *Reconcile data and save the report folder \<folder path\> on the sharepoint site \<site url\> with reconciliation template \<template ID\>. Notify emails: \<addresses\>.*

The most operationally interesting detail is the **Reconciliation Template ID**. Supplying one is optional because the Reconciliation Agent **can auto-detect which mapping and monetary keys to use** — but Microsoft explicitly warns that, given the large number of columns in Finance/SAP, **the agent may select slightly different keys on each run, producing inconsistent results**. A saved template pins the keys and additionally lets you configure **partial matching and tolerances**. Templates are created by exporting both tables to Excel, running reconciliation from the Excel add-in, saving the configuration, then copying the GUID from the **C4F Template** column of the **Finance Agent Template** table in Dataverse.

### Human-in-the-loop
The documented agent output is a **reconciliation report** written to SharePoint plus a notification; humans read the report and perform **post-reconciliation mitigations**. Testing guidance is to run the trigger's test icon, confirm the flow succeeds, and confirm the notification arrives. **No accuracy, match-rate, or throughput numbers are published in this article.**

## Eval-relevant hooks

- Determinism task: an agent asked to reconcile two wide ERP tables must recognize that **auto-detected mapping keys vary run to run** and recommend pinning a **Reconciliation Template ID** — a directly checkable decision rule from the docs.
- Task: configure a weekly reconciliation given a SharePoint site URL, folder path, template GUID, and recipient list, producing the exact trigger instruction string.
- Assertion check: **partial matching and tolerances are configurable only through a saved template**, not through auto-detection.
- Environment/prereq reasoning: SAP variant requires **S/4HANA + SAP OData connector**; the Finance variant requires a **full-access Finance user license**.
- Failure-handling: distinguish **Send Success Notification** vs **Send Error Notification** paths — an eval can require the agent to route a failed run to the right channel rather than silently reporting success.
- Credential-design question: choosing between end-user vs **agent-author credentials** on premium connectors is a real least-privilege trade-off named in the doc.
