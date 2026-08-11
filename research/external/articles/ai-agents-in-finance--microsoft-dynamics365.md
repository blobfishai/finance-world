# Account Reconciliation Agent (production ready preview) — Dynamics 365 Finance

- **URL:** https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/acct-rec-agent
- **Publisher:** Microsoft Learn (Dynamics 365 Finance documentation)
- **Retrieved:** 2026-08-10
- **Topic:** ai-agents-in-finance

## Summary

Microsoft's **Account Reconciliation Agent** is a prerelease ("production ready preview") agent inside Dynamics 365 Finance. Its stated purpose is to move reconciliation away from a reactive, SSRS-report-driven process toward a continuous close: the **Account reconciliation** workspace raises exceptions, and the agent evaluates each exception and proposes a mitigation. At the time of retrieval Microsoft itself must activate the agent for a customer (activation is requested via a Microsoft Forms link), pending changes to give "more configuration flexibility and predictable credit consumption."

### Setup and operating parameters (from the overview article)
1. Enable the **(Preview) Account reconciliation agent** feature in the **Feature management** workspace.
2. Go to **Modules > Agents**, find the **Account reconciliation** template, and enable it.
3. Specify the **start date** for the reconciliation process.
4. Add the modules that participate in reconciliation and **rank them in priority order**.
5. Specify **exception limits** to apply during processing — either **daily** or **monthly**.
6. Optional alerts: **Enable balance alert** (fires when balance falls below a user-set threshold); **Enable daily/monthly limit alert** (fires at **50%, 75%, or 90%** of the chosen limit); **Notify if a run is skipped due to limit**.
7. Review and confirm settings — the agent does not run until settings are confirmed — then activate.

### What the agent does vs. what stays human
The agent **processes two exception types**: **Voucher amount mismatch** and **Pending accounting transferred to general ledger**. Critically, it only **recommends actions for voucher amount mismatch exceptions**. For such an exception the documented example recommendation is **Create journal entry**; the human can accept it or choose from the alternatives **Reverse**, **Link transactions**, or **Accept without change**. So the agent's output is a suggestion plus rationale, and the accept/override decision is the human approval gate. A localization caveat is documented: **Suggested action** shows a summary only when the user language is **EN-US**; otherwise it shows a recommended action.

Auditability is explicit: every exception is logged with the history of actions taken by users, automation, or agents. In the **Activity** pane, agent output appears as **Fix suggested by agent**, and each addressed exception gets a **Reconciled** activity with an **undo** option that returns the exception to an unmitigated state. The **Account reconciliation agent** card in the workspace shows the count of agent suggestions for the selected period.

### Companion setup article
The setup article (https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/configure-acct-recon-agent) adds hard prerequisites: **Dynamics 365 Finance version 10.0.46 or later**; features **Immersive Home**, **Agent management**, and **(Production ready preview) Account reconciliation agent**; Power Platform packages **Copilot for finance and operations apps v1.0.3048.2+** and **Copilot in Microsoft Dynamics 365 Finance v1.0.3049.1+**. The agent runs under a **dedicated agent identity user** in both Dataverse and Finance, with Dataverse roles **Finance and Operations basic user**, **Account reconciliation agent role**, **Environment maker**, and Finance roles **Account reconciliation agent** and **System user**. Four Power Automate flows must be activated: *Complete agent activity request*, *Determine work to be done*, *Generate and log recommended action*, and *Agent execution is triggered*.

**No accuracy, match-rate, or throughput percentages are published in either article.** Microsoft also warns that it may automatically swap the underlying AI model, so the model producing responses may differ from the one shown in the UI.

## Eval-relevant hooks

- Task: given a **Voucher amount mismatch** exception, choose among the exact four actions (**Create journal entry / Reverse / Link transactions / Accept without change**) and justify — an agent that invents a fifth action fails.
- Checkable assertion: the agent recommends actions for **voucher amount mismatch only**, not for **Pending accounting transferred to general ledger** — a good trap for over-claiming automation scope.
- Decision rule: alert thresholds are exactly **50% / 75% / 90%** of the daily or monthly exception limit; a run can be **skipped** once the limit is hit.
- Governance task: enumerate the exact Dataverse vs. Finance role split for an agent identity (5 named roles) as a least-privilege review exercise.
- Reversibility check: every reconciled exception has an **undo** that returns it to unmitigated state — an eval can require the agent to state how to roll back a wrong auto-fix.
- Negative assertion for grounding tests: this documentation publishes **no accuracy percentage**; any confident "X% accurate" claim about this agent is unsupported.
