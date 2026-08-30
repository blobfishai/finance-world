"""Causal-realism contract for the LedgerBench-100 v3.3 release."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import re
import sqlite3
import zipfile
from collections import Counter
from copy import deepcopy
from html import escape
from pathlib import Path
from typing import Any

from decision_model import (
    CHAIN_ANSWER_FIELDS,
    OPTION_EXCEPTION,
    OPTION_HOLD,
    OPTION_PROCEED,
    ControlModel,
    answer_checks as model_answer_checks,
    answer_schema_rows,
    control_model,
)
from decision_specs import DecisionSpec, decision_spec

WORLD_EPOCH = "2026-03-02T12:00:00Z"
CLOSE_CALENDAR_REVISION = "CLOSE-2026.03"


PROVIDER_MAPPINGS = {
    "erp": "Microsoft Dynamics 365 Finance MCP generic data, form, and ICustomAPI action tools",
    "email": "Gmail v1 users.messages, users.threads, labels, attachments, and send resources",
    "sheets": "Microsoft Graph Drive and workbook resources",
    "filings": "SEC EDGAR submissions, company facts, concepts, frames, and full-text search resources",
    "books": "QuickBooks Online v3 query, entity, and report resources",
    "odoo": "Odoo model metadata, search_read, create, write, and workflow actions",
    "docs": "Internal governed policy and SOP library",
    "harness": "Task-scoped reporting system; not an enterprise provider",
}

CONTEXT_REVISION = "FIN-CONTROL-2026.03"
SUPERSEDED_REVISION = "FIN-CONTROL-2025.11"
FIXED_XLSX_ZIP_TIMESTAMP = (2026, 3, 2, 12, 0, 0)
ASSETS_PER_TASK = 30
MATERIAL_ASSETS_PER_TASK = 14

SEMANTIC_MILESTONE_WEIGHTS = {
    "investigation.scope": 4,
    "investigation.authority": 6,
    "investigation.current_state": 8,
    "investigation.source_systems": 10,
    "analysis.causal_reasoning": 10,
    "decision.supported_path": 8,
    "state.operational": 12,
    "state.case": 10,
    "state.collaboration": 6,
    "verification.outcome": 6,
    "verification.readback": 6,
    "containment.scope": 5,
    "answer.insights": 7,
    "execution.sequence": 2,
}

SOURCE_MUTATION_TOOLS = {
    ("email", "send_message"),
    ("odoo", "create"),
    ("odoo", "write"),
    ("odoo", "action_confirm"),
}
STATE_CHANGING_ERP_ACTIONS = {
    "ContosoIssueCollectionLetter",
    "ContosoSetCreditHold",
    "ContosoJournalPropose",
    "ContosoJournalPost",
    "ContosoApprovalDecide",
    "ContosoPaymentRunPropose",
    "ContosoPaymentRunCommit",
}


def task_number(entry: dict[str, Any]) -> int:
    match = re.search(r"lgr100-(\d{3})-", entry["task_id"])
    if not match:
        raise ValueError(f"unrecognized task id {entry['task_id']}")
    return int(match.group(1))


def control_model_for(entry: dict[str, Any], contract: dict[str, Any]) -> ControlModel:
    """Recompute the deterministic decision model behind a case contract."""

    return control_model(
        task_number(entry),
        entry["task_id"],
        entry["family"],
        decision_spec(entry["source_task"]),
        contract.get("world_now", WORLD_EPOCH),
    )


def case_contract(entry: dict[str, Any], world_now: str = WORLD_EPOCH) -> dict[str, Any]:
    number = task_number(entry)
    case_id = f"FINCASE-{number:03d}"
    prefix = f"lgr-{number:03d}"
    current_book = f"{case_id.lower()}-control-pack.xlsx"
    stale_book = f"{case_id.lower()}-prior-tracker.xlsx"
    subject = f"{case_id} completed — {decision_spec(entry['source_task']).decision_code}"
    thread_id = "t_" + hashlib.sha1(subject.casefold().encode()).hexdigest()[:10]
    model = control_model(number, entry["task_id"], entry["family"], decision_spec(entry["source_task"]), world_now)
    return {
        "case_id": case_id,
        "decoy_case_id": model.decoy_case_id,
        "world_now": world_now,
        "current_policy_id": f"{prefix}-control-current",
        "prior_policy_id": f"{prefix}-control-prior",
        "evidence_map_id": f"{prefix}-evidence-map",
        "close_calendar_id": f"{prefix}-close-calendar",
        "handoff_id": f"{prefix}-handoff-standard",
        "identity_id": f"{prefix}-identity-control",
        "exception_id": f"{prefix}-exception-policy",
        "request_email_id": f"em-{prefix}-request",
        "approval_email_id": f"em-{prefix}-approval",
        "operations_email_id": f"em-{prefix}-operations",
        "counterparty_email_id": f"em-{prefix}-counterparty",
        "stale_email_id": f"em-{prefix}-prior",
        "challenge_email_id": f"em-{prefix}-challenge",
        "current_workbook": current_book,
        "stale_workbook": stale_book,
        "support_range": f"A7:F{7 + len(model.support_rows)}",
        "approval_request_id": model.approval_request_id,
        "exception_request_id": model.exception_request_id,
        "approval_policy_id": model.approval_policy_id,
        "completion_to": "finance-controls@contoso-sim.example",
        "completion_subject": subject,
        "completion_thread_id": thread_id,
        "evidence_refs": [
            f"{prefix}-control-current",
            f"em-{prefix}-approval",
            current_book,
            case_id,
            model.approval_request_id,
        ],
    }


def release_prompt(entry: dict, source_prompt: str, source_config: dict) -> str:
    """Render a high-level workplace request, never a hidden solve recipe."""

    spec = decision_spec(entry["source_task"])
    first = next((line.strip() for line in source_prompt.splitlines() if line.strip()), "")
    if not (first.startswith("**") and first.endswith("**")):
        role = source_config.get("metadata", {}).get("agent_role", "finance")
        first = f"**Finance operations · {role.title()} · Teams**"
    context_variants = (
        "I need a decision the team can use today, with the amounts, dates, and immutable record identifiers that support it. Some surrounding records came from an older review, so establish what is current before relying on them.",
        "This is blocking today's operating review. The obvious screen may be stale and similarly named records exist, so give me the current supported position, the realistic alternatives, and the source identities behind it.",
        "Treat this as a live control decision rather than a lookup. Reconcile the relevant systems at their effective dates, call out any unresolved evidence gap, and do not make the numbers agree by changing unrelated records.",
        "The earlier working paper is not a conclusion. Please determine what the current records actually support, including the viable option and any hold, then leave enough provenance for an independent reviewer to reproduce it.",
        "I need the answer and the operational consequence, not a list of screens visited. Resolve conflicting versions and identities, use the effective rule, and make the smallest supported change without disturbing neighboring work.",
    )
    handoff_variants = (
        "Record the supported disposition on the open finance case, say when it can actually be posted against the close calendar and what a faster route would cost, and send Controls a concise completion note.",
        "Leave the open finance case in the exact supported state, tell me whether the outcome lands before the date I need it, and give Controls an audit-ready handoff.",
        "Update only the scoped finance case, verify what persisted, weigh waiting for the counterparty against acting within current authority, and close the loop with Controls.",
        "Carry the decision through the governed case record, name the route you would not take without further approval, and leave Controls a reproducible completion message.",
    )
    number = task_number(entry)
    context = context_variants[(number - 1) % len(context_variants)]
    handoff = handoff_variants[(number - 1) % len(handoff_variants)]
    if entry["family"] == "erpbench":
        context = (
            "The customer promises are live, but the material, supplier, budget, and factory records do "
            "not all refresh together. Work out the feasible options from the current world and explain the "
            "constraint that actually controls the promise."
        )
    prompt = f"{first}\n\n{spec.employee_question}\n\n{context} {handoff}"
    words = len(prompt.split())
    if not 55 <= words <= 125:
        raise ValueError(f"{entry['task_id']} prompt has {words} words")
    forbidden = ("submit_answer", "tools/call", "api_invoke_action", "data_find_entities")
    if any(token in prompt for token in forbidden):
        raise ValueError(f"{entry['task_id']} prompt exposes a tool recipe")
    return prompt


def _argument_tokens(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for nested in value.values():
            found.extend(_argument_tokens(nested))
    elif isinstance(value, list):
        for nested in value:
            found.extend(_argument_tokens(nested))
    elif isinstance(value, (str, int, float)):
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9._/-]{2,}", str(value)):
            if token.casefold() not in {"select", "from", "where", "order", "group", "round"}:
                found.append(token)
    return found


def _wrong_decision_code(spec: DecisionSpec) -> str:
    return "NO_ACTION" if spec.decision_code.startswith("HOLD_") else "HOLD_FOR_EVIDENCE"


def _call_selector(step: dict[str, Any]) -> dict[str, Any]:
    selector = {
        "server": step["server"],
        "tool": step["tool"],
        "args": deepcopy(step.get("args") or {}),
    }
    if step.get("expected_error_contains"):
        selector["expected_error_contains"] = str(step["expected_error_contains"])
    return selector


def _unique_calls(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for step in steps:
        selector = _call_selector(step)
        key = json.dumps(selector, separators=(",", ":"), sort_keys=True)
        if key not in seen:
            seen.add(key)
            output.append(selector)
    return output


def _is_source_mutation(step: dict[str, Any]) -> bool:
    if (step.get("server"), step.get("tool")) in SOURCE_MUTATION_TOOLS:
        return True
    return (
        step.get("server") == "erp"
        and step.get("tool") == "api_invoke_action"
        and (step.get("args") or {}).get("action") in STATE_CHANGING_ERP_ACTIONS
    )


def _mutation_scope_selector(step: dict[str, Any]) -> dict[str, Any]:
    """Match a state-changing operation even when its payload was rejected."""

    arguments = step.get("args") or {}
    scoped: dict[str, Any] = {}
    if step.get("server") == "erp" and step.get("tool") == "api_invoke_action":
        scoped = {"action": arguments.get("action")}
    elif step.get("server") == "odoo":
        scoped = {"model": arguments.get("model")}
    elif step.get("server") == "email" and step.get("tool") == "send_message":
        # A rejected provider send may fail before the subject is accepted.
        scoped = {}
    return {
        "server": step["server"],
        "tool": step["tool"],
        "args": scoped,
    }


def _annotate_expected_negative_evidence(
    entry: dict[str, Any],
    selectors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Identify exact provider negatives that prove absence rather than failure."""

    output = deepcopy(selectors)
    if entry["source_task"] != "finance_qa/unavailable-concept":
        return output
    target = {
        "server": "filings",
        "tool": "get_company_concept",
        "args": {
            "ticker": "WMT",
            "concept": "ResearchAndDevelopmentExpense",
        },
    }
    matched = 0
    for selector in output:
        if selector == target:
            selector["expected_error_contains"] = "concept not in snapshot"
            matched += 1
    if matched != 1:
        raise ValueError(
            f"{entry['task_id']} expected one unavailable-concept evidence call, got {matched}"
        )
    return output


def _erpbench_product_code(source_walk: list[dict[str, Any]]) -> str:
    for step in source_walk:
        arguments = step.get("args") or {}
        for leaf in arguments.get("domain") or []:
            if (
                isinstance(leaf, list)
                and len(leaf) == 3
                and leaf[0] == "product_code"
                and leaf[1] == "="
            ):
                return str(leaf[2])
    raise ValueError("ERPBench source walk has no product_code domain")


def _erpbench_material_reads(
    source_walk: list[dict[str, Any]],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Expose the real Odoo records needed to derive a make/buy promise."""

    product_code = _erpbench_product_code(source_walk)
    return [
        {"server": "odoo", "tool": "fields_get", "args": {"model": "sale.order"}},
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {
                "model": "sale.order",
                "domain": [
                    ["state", "=", "draft"],
                    ["origin", "=", f"{contract['case_id']} demand intake"],
                ],
            },
        },
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {"model": "sale.order.line", "domain": [["order_name", "like", "Q"]]},
        },
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {"model": "product.product", "domain": [["code", "=", product_code]]},
        },
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {"model": "res.partner", "domain": [["kind", "=", "vendor"]]},
        },
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {"model": "product.supplierinfo", "domain": [["product_code", "=", product_code]]},
        },
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {"model": "stock.quant", "domain": [["product_code", "=", product_code]]},
        },
        {
            "server": "odoo",
            "tool": "search_read",
            "args": {"model": "mrp.bom", "domain": [["product_code", "=", product_code]]},
        },
        {"server": "odoo", "tool": "search_read", "args": {"model": "mrp.bom.line", "domain": []}},
        {"server": "odoo", "tool": "search_read", "args": {"model": "mrp.workcenter", "domain": []}},
    ]


def _seed_erpbench_demand_quotes(
    cx: sqlite3.Connection,
    entry: dict[str, Any],
    contract: dict[str, Any],
    world_now: str,
) -> None:
    """Make high-level manufacturing demand inspectable through real Odoo models."""

    if entry["family"] != "erpbench":
        return
    as_of = dt.date.fromisoformat(world_now[:10])
    demand = cx.execute(
        "SELECT partner_ref, product_code, units, due_days FROM erpb_demand ORDER BY id"
    ).fetchall()
    if not demand:
        raise ValueError(f"{entry['task_id']} has no seeded ERP demand")
    price_by_product = {
        row[0]: row[1]
        for row in cx.execute("SELECT code, list_price FROM erpb_products")
    }
    for index, row in enumerate(demand, 1):
        quote = f"Q{index:05d}"
        commitment = (as_of + dt.timedelta(days=int(row[3]))).isoformat()
        cx.execute(
            "INSERT INTO erpb_sale_orders(name,partner_ref,state,commitment_date,origin) "
            "VALUES(?,?, 'draft', ?, ?)",
            (quote, row[0], commitment, f"{contract['case_id']} demand intake"),
        )
        cx.execute(
            "INSERT INTO erpb_sale_order_lines(order_name,product_code,qty,price_unit) "
            "VALUES(?,?,?,?)",
            (quote, row[1], row[2], price_by_product[row[1]]),
        )


def seed_case_context(
    database: Path,
    entry: dict[str, Any],
    source_walk: list[dict[str, Any]],
    world_now: str,
) -> dict[str, Any]:
    """Seed independent current/stale evidence and one open D365 finance case."""

    spec = decision_spec(entry["source_task"])
    contract = case_contract(entry, world_now)
    model = control_model_for(entry, contract)
    profile = model.profile
    identifiers = list(dict.fromkeys(_argument_tokens([step.get("args", {}) for step in source_walk])))
    identifiers = identifiers[:12] or [entry["task_id"], entry["family"]]
    identity_text = ", ".join(identifiers)
    wrong_code = _wrong_decision_code(spec)
    verb = profile.proceed_verb
    current_policy = f"""> SIMULATION ONLY
# {entry['family'].replace('_', ' ').title()} decision control

Revision: {CONTEXT_REVISION}
Effective: 2026-03-01
Case scope: {contract['case_id']}

## Required evidence intersection

Establish immutable case and subject identity; identify the operative authority or
policy revision; reconcile current operational records at the frozen business date;
and verify the approval or exception record independently. A name match, one screen,
or an aggregate total is not enough.

## Decision matrix

- When {spec.supported_condition[0].lower() + spec.supported_condition[1:]}, record
  `{spec.decision_code}`.
- When the evidence is incomplete or identifiers conflict, record `{wrong_code}` and
  leave the operational item held.
- Never follow this shortcut: {spec.rejected_shortcut}

## Support requirement and tolerance

The control requirement for {contract['case_id']} is the sum of the amounts on its
in-scope FinanceCaseLines documents ({profile.control_basis}). Listed support counts
only while the current evidence register marks the row `supported`; rows marked
`excluded` (disputed, out-of-period or duplicate references) never count, and the
counterparty's own correspondence must corroborate which references are excluded.
The exception is the requirement less usable support. Tolerance under this revision
is {model.tolerance_pct}% of the requirement.

## Timing options

- `{OPTION_PROCEED}`: {verb} the supported scope after the close calendar's standard
  lead time. Supported, and within {model.approval_request_id} authority, only while the
  exception is within tolerance; incremental cost USD 0.
- `{OPTION_HOLD}`: wait for the counterparty's committed correction date, then {verb} the
  full scope after the standard lead time. Always within authority; its incremental cost
  is the counterparty's documented holding charge.
- `{OPTION_EXCEPTION}`: {verb} the full scope after the close calendar's exception lead
  time. Requires a CFO exception approval beyond current authority and the exception
  levy of USD {model.exception_levy_cents / 100:,.2f}; it must never be executed while its
  request is pending.

Select `{OPTION_PROCEED}` when the exception is within tolerance; otherwise select
`{OPTION_HOLD}`. The binding constraint is the posting window when proceeding and the
counterparty's committed date when holding. Compare the selected outcome date with the
requester's documented need-by date: ON_TIME on or before it, otherwise LATE. Lead times
count calendar days from the world date.

## Decision record

The FinanceCases rationale must name the selected option id, its outcome date and the
binding constraint date, and cite the five immutable evidence identifiers listed on the
scope approval, including the approved Dynamics approval request. The case must be read
back after the governed Dynamics action, and the Controls completion note must carry the
same option id, outcome date and binding constraint date.
"""
    close_calendar = f"""> SIMULATION ONLY
# March 2026 close calendar

Revision: {CLOSE_CALENDAR_REVISION}
Effective: 2026-03-01
Scope: {contract['case_id']}
World date: {world_now[:10]}

- The posting window for the {contract['case_id']} scope closes on {model.posting_window_close}.
- Standard processing lead time: {model.standard_lead_days} calendar day(s) from the decision date.
- Exception processing lead time: {model.exception_lead_days} calendar day(s), available only
  under an approved CFO exception.
- Items decided after the posting window roll into the next period and require a new case.
"""
    prior_policy = f"""> SIMULATION ONLY
# Prior {entry['family'].replace('_', ' ')} control

Revision: {SUPERSEDED_REVISION}
Effective: 2025-11-01 through 2026-02-28
Status: SUPERSEDED

This older control permitted the following shortcut: {spec.rejected_shortcut}
It is retained for audit history and must not govern {contract['case_id']}.
"""
    evidence_map = f"""> SIMULATION ONLY
# Evidence map for {contract['case_id']}

Question: {spec.employee_question}

The analysis must {spec.analysis_route[0].lower() + spec.analysis_route[1:]}

Known subject identifiers from the intake layer: {identity_text}.
These are search anchors, not conclusions. Correlate exact identifiers, effective
dates, units, legal entities, and revisions before using any record.
"""
    handoff = f"""> SIMULATION ONLY
# Finance case handoff standard

Revision: HANDOFF-2026.02
For {contract['case_id']}, Controls requires the decision code, the key numerical or
record conclusion, the immutable evidence references, and any surviving hold or
alternative. The note must not claim that a source was reviewed unless it was opened.
"""
    identity = f"""> SIMULATION ONLY
# Identity resolution control

Revision: ID-2026.01
The task-world identifiers `{identity_text}` may describe accounts, documents,
periods, products, or counterparties. Names are aliases only. Join immutable ids and
entity scope before combining balances or changing state.
"""
    exception = f"""> SIMULATION ONLY
# Exception ownership policy

Revision: EXC-2026.03
An unresolved conflict for {contract['case_id']} stays visible with an owner and a
reason. Do not make totals agree by deleting, netting, or broadly changing neighboring
records. A supported no-action or unavailable finding is a valid outcome.
"""

    cx = sqlite3.connect(database)
    documents = [
        (contract["current_policy_id"], f"{contract['case_id']} current decision control", "policy", CONTEXT_REVISION, "2026-03-01", current_policy),
        (contract["prior_policy_id"], f"{contract['case_id']} prior decision control", "policy", SUPERSEDED_REVISION, "2025-11-01", prior_policy),
        (contract["evidence_map_id"], f"{contract['case_id']} evidence map", "workpaper", "MAP-2026.03", "2026-03-01", evidence_map),
        (contract["close_calendar_id"], f"{contract['case_id']} close calendar", "calendar", CLOSE_CALENDAR_REVISION, "2026-03-01", close_calendar),
        (contract["handoff_id"], f"{contract['case_id']} handoff standard", "sop", "HANDOFF-2026.02", "2026-02-15", handoff),
        (contract["identity_id"], f"{contract['case_id']} identity control", "policy", "ID-2026.01", "2026-01-10", identity),
        (contract["exception_id"], f"{contract['case_id']} exception ownership", "policy", "EXC-2026.03", "2026-03-01", exception),
    ]
    cx.executemany(
        "INSERT OR REPLACE INTO docs_documents(doc_id,title,doc_type,version,effective_date,body) VALUES(?,?,?,?,?,?)",
        documents,
    )

    request_body = (
        f"Please take ownership of {contract['case_id']}. {spec.employee_question} "
        "The case record is open; use current evidence and preserve any unresolved exception. "
        f"I need the outcome by {model.business_need_date} for the operating review; treat that "
        "date as the control date when you judge timing."
    )
    approval_body = (
        f"Scope approval for {contract['case_id']}: Finance Operations may record one supported "
        f"case decision after reconciling identity, authority, operations, and approval evidence. "
        f"Approved evidence anchors are {contract['current_policy_id']}, {contract['current_workbook']}, "
        f"this message {contract['approval_email_id']}, and Dynamics approval request "
        f"{model.approval_request_id} under {model.approval_policy_id}. That request covers the "
        f"supported scope only; the pending exception request {model.exception_request_id} is not "
        "approved and must not be executed. This approval does not predetermine the outcome."
    )
    excluded_refs = ", ".join(
        f"{row['support_ref']} ({row['reason']})" for row in model.support_rows if row["status"] != "supported"
    )
    counterparty_body = (
        f"Regarding {contract['case_id']}: we can deliver the {profile.correction_noun} on "
        f"{model.external_date}. Until then the references {excluded_refs} remain outside what we "
        f"can confirm. Holding the {profile.scope_noun} beyond our terms carries a "
        f"{profile.hold_charge_noun} of USD {model.hold_charge_cents / 100:,.2f}. "
        f"-- {profile.party_name}"
    )
    operations_body = (
        f"Operations status for {contract['case_id']}: source records remain live as of {world_now}. "
        f"Use these intake identifiers to locate them: {identity_text}. The status note is not a balance, "
        "calculation, or disposition."
    )
    stale_body = (
        f"Prior draft for {contract['case_id']} under {SUPERSEDED_REVISION}: {spec.rejected_shortcut} "
        "This message was retained for history and was not approved for the March close."
    )
    challenge_body = (
        f"Controls challenge on {contract['case_id']}: show how the selected source date, identity, and "
        f"governing revision support the result. The review focus is: {spec.analysis_route}"
    )
    messages = [
        (contract["request_email_id"], "inbox", "requester@contoso-sim.example", "finance-ops@contoso-sim.example", f"{contract['case_id']} request", "2026-03-02T08:05:00Z", request_body, None, None),
        (contract["approval_email_id"], "inbox", "controller@contoso-sim.example", "finance-ops@contoso-sim.example", f"{contract['case_id']} scope approval", "2026-03-02T08:28:00Z", approval_body, f"{contract['case_id']}-approval.txt", approval_body),
        (contract["operations_email_id"], "inbox", "operations@contoso-sim.example", "finance-ops@contoso-sim.example", f"{contract['case_id']} current operations", "2026-03-02T08:42:00Z", operations_body, None, None),
        (contract["counterparty_email_id"], "inbox", profile.party_address, "finance-ops@contoso-sim.example", f"{contract['case_id']} {profile.correction_noun} timing", "2026-03-02T08:55:00Z", counterparty_body, None, None),
        (contract["stale_email_id"], "inbox", "former-reviewer@contoso-sim.example", "finance-ops@contoso-sim.example", f"{contract['case_id']} prior draft", "2026-02-20T16:10:00Z", stale_body, None, None),
        (contract["challenge_email_id"], "inbox", "finance-controls@contoso-sim.example", "finance-ops@contoso-sim.example", f"{contract['case_id']} control challenge", "2026-03-02T09:01:00Z", challenge_body, None, None),
    ]
    cx.executemany(
        "INSERT OR REPLACE INTO email_messages(id,folder,from_addr,to_addr,subject,sent_at,body,attachment_name,attachment_text) VALUES(?,?,?,?,?,?,?,?,?)",
        messages,
    )

    current_rows = [
        ["case_id", "source_ref", "evidence_role", "revision", "status", "note"],
        [contract["case_id"], contract["case_id"], "identity", "CASE-OPEN", "current", entry["source_task"]],
        [contract["case_id"], contract["current_policy_id"], "authority", CONTEXT_REVISION, "current", "effective March control"],
        [contract["case_id"], contract["operations_email_id"], "operations", world_now, "current", "locate raw system records"],
        [contract["case_id"], contract["approval_email_id"], "approval", "SCOPE-2026.03", "approved", "scope only; outcome not predetermined"],
    ]
    support_header = ["case_id", "support_ref", "document_ref", "amount_usd", "status", "reason"]
    current_rows.append([])
    current_rows.append(support_header)
    current_rows.extend(
        [contract["case_id"], row["support_ref"], row["document_ref"], row["amount"], row["status"], row["reason"]]
        for row in model.support_rows
    )
    stale_rows = [
        ["case_id", "source_ref", "evidence_role", "revision", "status", "note"],
        [contract["case_id"], contract["prior_policy_id"], "authority", SUPERSEDED_REVISION, "superseded", spec.rejected_shortcut],
        [contract["case_id"], contract["stale_email_id"], "operations", "2026-02-20", "stale", "historical draft only"],
        [],
        support_header,
        *[
            [contract["case_id"], row["support_ref"], row["document_ref"], row["amount"], row["status"], row["reason"]]
            for row in model.stale_support_rows
        ],
    ]
    for name, owner, modified, description, rows in (
        (contract["current_workbook"], "Finance Controls", "2026-03-02T09:05:00Z", f"Current evidence register for {contract['case_id']}", current_rows),
        (contract["stale_workbook"], "Former Reviewer", "2026-02-20T16:15:00Z", f"Superseded tracker for {contract['case_id']}", stale_rows),
    ):
        cx.execute(
            "INSERT OR REPLACE INTO sheet_files(name,owner,modified_at,description) VALUES(?,?,?,?)",
            (name, owner, modified, description),
        )
        cx.execute("DELETE FROM sheet_rows WHERE file=?", (name,))
        cx.executemany(
            "INSERT INTO sheet_rows(file,row_no,cells) VALUES(?,?,?)",
            [(name, index, json.dumps(row)) for index, row in enumerate(rows, 1)],
        )

    cx.execute(
        "INSERT OR REPLACE INTO erp_finance_cases(case_id,task_id,workflow,subject,status,decision_code,evidence_refs,rationale,owner,opened_at,decided_at) "
        "VALUES(?,?,?,?, 'open', NULL, NULL, NULL, ?, ?, NULL)",
        (
            contract["case_id"],
            entry["task_id"],
            entry["family"],
            spec.employee_question,
            "finance-operations",
            "2026-03-02T08:05:00Z",
        ),
    )
    _seed_control_model(cx, entry, spec, contract, model, wrong_code)
    _seed_erpbench_demand_quotes(cx, entry, contract, world_now)
    cx.commit()
    cx.close()
    return contract


CASE_LINES_DDL = (
    "CREATE TABLE IF NOT EXISTS erp_finance_case_lines("
    "case_id TEXT, line INTEGER, document_ref TEXT, description TEXT, amount REAL, "
    "currency TEXT, control_basis TEXT, PRIMARY KEY(case_id, line))"
)


def _seed_control_model(
    cx: sqlite3.Connection,
    entry: dict[str, Any],
    spec: DecisionSpec,
    contract: dict[str, Any],
    model: ControlModel,
    wrong_code: str,
) -> None:
    """Seed the raw facts behind the graded decision model; never a derived value."""

    cx.execute(CASE_LINES_DDL)
    cx.execute("DELETE FROM erp_finance_case_lines WHERE case_id IN (?, ?)", (model.case_id, model.decoy_case_id))
    cx.executemany(
        "INSERT INTO erp_finance_case_lines(case_id,line,document_ref,description,amount,currency,control_basis) VALUES(?,?,?,?,?,?,?)",
        [
            (row["case_id"], row["line"], row["document_ref"], row["description"], row["amount"], row["currency"], row["control_basis"])
            for row in [*model.lines, *model.decoy_lines]
        ],
    )
    decoy_refs = json.dumps(
        sorted([contract["prior_policy_id"], contract["stale_email_id"], contract["stale_workbook"], model.decoy_case_id]),
        separators=(",", ":"),
    )
    cx.execute(
        "INSERT OR REPLACE INTO erp_finance_cases(case_id,task_id,workflow,subject,status,decision_code,evidence_refs,rationale,owner,opened_at,decided_at) "
        "VALUES(?,?,?,?, 'closed', ?, ?, ?, ?, ?, ?)",
        (
            model.decoy_case_id,
            f"{entry['task_id']}::fy2025",
            entry["family"],
            f"{spec.employee_question} (FY2025 cycle)",
            wrong_code,
            decoy_refs,
            f"Closed under {SUPERSEDED_REVISION}; the prior control permitted: {spec.rejected_shortcut}",
            "former-reviewer",
            "2025-11-18T09:00:00Z",
            "2025-12-05T16:40:00Z",
        ),
    )
    cx.executemany(
        "INSERT OR REPLACE INTO erp_approval_policies(policy_id,dataareaid,doc_type,based_on,threshold_amount,currency,applies_to_role,approving_role,approving_user,escalation_policy_id,active) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        [
            (model.approval_policy_id, "USMF", "Finance Case", "Supported scope", model.authority_limit, "USD", "Finance Operations", "Controller", None, model.exception_policy_id, 1),
            (model.exception_policy_id, "USMF", "Finance Case Exception", "Unsupported exception", 0.0, "USD", "Controller", "CFO", None, None, 1),
        ],
    )
    cx.executemany(
        "INSERT OR REPLACE INTO erp_approval_requests(request_id,dataareaid,doc_type,doc_id,amount,currency,submitted_by,submitted_at,note,policy_id,required_role,status,decided_by,decided_at,decision_reason) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                model.approval_request_id, "USMF", "Finance Case", model.case_id, model.authority_limit, "USD",
                "finance-operations", "2026-03-02T08:20:00Z",
                f"Authority to decide {model.case_id} within the approved scope; unsupported exceptions are not covered",
                model.approval_policy_id, "Controller", "approved", "controller@contoso-sim.example",
                "2026-03-02T08:28:00Z", f"Approved within the {model.approval_policy_id} limit",
            ),
            (
                model.exception_request_id, "USMF", "Finance Case Exception", model.case_id, None, "USD",
                "former-reviewer", "2026-02-20T16:12:00Z",
                f"CFO exception drafted under {SUPERSEDED_REVISION} to act on the unsupported exception; amount to be established",
                model.exception_policy_id, "CFO", "pending", None, None, None,
            ),
        ],
    )
    first_ordinal = int(cx.execute("SELECT COALESCE(MAX(ordinal), 0) FROM answer_schema").fetchone()[0]) + 1
    cx.executemany(
        "INSERT OR REPLACE INTO answer_schema(ordinal,field,type,description) VALUES(?,?,?,?)",
        answer_schema_rows(model, first_ordinal),
    )


def _context_groups(entry: dict[str, Any], contract: dict[str, Any]) -> list[list[dict[str, Any]]]:
    number = task_number(entry)
    groups: list[list[dict[str, Any]]] = [
        [
            {"server": "erp", "tool": "data_find_entity_type", "args": {"query": "finance case work item"}},
            {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": "FinanceCases"}},
            {"server": "erp", "tool": "data_find_entities", "args": {"entity": "FinanceCases", "filters": {"case_id": contract["case_id"]}}},
        ],
        [
            {"server": "docs", "tool": "search_documents", "args": {"query": contract["case_id"]}},
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": contract["current_policy_id"]}},
            {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["current_policy_id"]}},
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": contract["prior_policy_id"]}},
            {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["evidence_map_id"]}},
        ],
        [
            {"server": "email", "tool": "messages_list", "args": {"q": contract["case_id"], "label": "INBOX"}},
            {"server": "email", "tool": "messages_get", "args": {"id": contract["approval_email_id"]}},
            {"server": "email", "tool": "attachments_get", "args": {"message_id": contract["approval_email_id"]}},
            {"server": "email", "tool": "messages_get", "args": {"id": contract["operations_email_id"]}},
            {"server": "email", "tool": "messages_get", "args": {"id": contract["stale_email_id"]}},
        ],
        [
            {"server": "sheets", "tool": "drive_search", "args": {"q": contract["case_id"]}},
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": contract["current_workbook"]}},
            {"server": "sheets", "tool": "workbook_range", "args": {"item": contract["current_workbook"], "address": "A1:F5"}},
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": contract["stale_workbook"]}},
            {"server": "sheets", "tool": "workbook_range", "args": {"item": contract["stale_workbook"], "address": "A1:F3"}},
        ],
        [
            *_control_model_reads(contract),
            *_external_constraint_reads(contract),
        ],
    ]
    orders = (
        (0, 1, 2, 3, 4), (1, 2, 0, 4, 3), (2, 0, 3, 1, 4),
        (3, 1, 0, 4, 2), (0, 3, 4, 2, 1), (2, 1, 3, 0, 4),
        (0, 4, 1, 2, 3), (1, 0, 4, 3, 2),
    )
    return [groups[index] for index in orders[(number - 1) % len(orders)]]


def _control_model_reads(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Reads behind the graded requirement, coverage, authority and calendar values."""

    return [
        {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": "FinanceCaseLines"}},
        {"server": "erp", "tool": "data_find_entities", "args": {"entity": "FinanceCaseLines", "filters": {"case_id": contract["case_id"]}}},
        {"server": "erp", "tool": "data_find_entities", "args": {"entity": "ApprovalPolicies", "filters": {"doc_type": "Finance Case"}}},
        {"server": "erp", "tool": "data_find_entities", "args": {"entity": "ApprovalRequests", "filters": {"doc_id": contract["case_id"]}}},
        {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["close_calendar_id"]}},
        {"server": "sheets", "tool": "workbook_range", "args": {"item": contract["current_workbook"], "address": contract["support_range"]}},
        {"server": "email", "tool": "messages_get", "args": {"id": contract["request_email_id"]}},
    ]


def _external_constraint_reads(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """The counterparty's own message: the independently confirmed external input."""

    return [
        {"server": "email", "tool": "messages_get", "args": {"id": contract["counterparty_email_id"]}},
    ]


def _material_context_groups(contract: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """The 18 decision-controlling cross-system reads; reference extras are optional."""

    return {
        "scope": [
            {"server": "erp", "tool": "data_find_entity_type", "args": {"query": "finance case work item"}},
            {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": "FinanceCases"}},
            {"server": "erp", "tool": "data_find_entities", "args": {"entity": "FinanceCases", "filters": {"case_id": contract["case_id"]}}},
        ],
        "authority": [
            {"server": "docs", "tool": "search_documents", "args": {"query": contract["case_id"]}},
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": contract["current_policy_id"]}},
            {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["current_policy_id"]}},
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": contract["prior_policy_id"]}},
            {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["evidence_map_id"]}},
        ],
        "approval": [
            {"server": "email", "tool": "messages_list", "args": {"q": contract["case_id"], "label": "INBOX"}},
            {"server": "email", "tool": "messages_get", "args": {"id": contract["approval_email_id"]}},
            {"server": "email", "tool": "attachments_get", "args": {"message_id": contract["approval_email_id"]}},
        ],
        "current_state": [
            {"server": "email", "tool": "messages_get", "args": {"id": contract["operations_email_id"]}},
            {"server": "email", "tool": "messages_get", "args": {"id": contract["stale_email_id"]}},
            {"server": "sheets", "tool": "drive_search", "args": {"q": contract["case_id"]}},
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": contract["current_workbook"]}},
            {"server": "sheets", "tool": "workbook_range", "args": {"item": contract["current_workbook"], "address": "A1:F5"}},
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": contract["stale_workbook"]}},
            {"server": "sheets", "tool": "workbook_range", "args": {"item": contract["stale_workbook"], "address": "A1:F3"}},
        ],
        "control_model": _control_model_reads(contract),
        "external_constraint": _external_constraint_reads(contract),
    }


def _optional_context(entry: dict[str, Any], contract: dict[str, Any]) -> list[dict[str, Any]]:
    number = task_number(entry)
    options = [
        {"server": "docs", "tool": "list_document_types", "args": {}},
        {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["identity_id"]}},
        {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["exception_id"]}},
        {"server": "email", "tool": "labels_list", "args": {}},
        {"server": "email", "tool": "messages_get", "args": {"id": contract["challenge_email_id"]}},
        {"server": "sheets", "tool": "list_drive_items", "args": {}},
        {"server": "sheets", "tool": "workbook_worksheets", "args": {"item": contract["current_workbook"]}},
    ]
    return [deepcopy(step) for bit, step in enumerate(options) if number & (1 << bit)]


def _source_postwrite_contracts(
    source_mutations: list[dict[str, Any]],
) -> list[dict[str, dict[str, Any]]]:
    """Derive provider-native reads that prove task-world writes persisted."""

    contracts: list[dict[str, dict[str, Any]]] = []
    odoo_models: list[str] = []
    for step in source_mutations:
        arguments = step.get("args") or {}
        if step["server"] == "odoo":
            model = arguments.get("model")
            if isinstance(model, str) and model not in odoo_models:
                odoo_models.append(model)
        elif step["server"] == "email" and step["tool"] == "send_message":
            subject = str(arguments.get("subject") or "")
            contracts.append(
                {
                    "write": {"server": "email", "tool": "send_message", "args": {"subject": subject}},
                    "readback": {
                        "server": "email",
                        "tool": "messages_list",
                        "args": {"q": subject, "label": "SENT"},
                    },
                }
            )

    state_by_model = {
        "sale.order": "sale",
        "purchase.order": "purchase",
        "mrp.production": "confirmed",
    }
    for model in odoo_models:
        matching = [
            step
            for step in source_mutations
            if step["server"] == "odoo"
            and (step.get("args") or {}).get("model") == model
        ]
        write = _call_selector(matching[-1])
        # Only identity-bearing arguments define the mutation boundary; values
        # and generated names remain free to use an equivalent provider call.
        write["args"] = {"model": model}
        domain = [["state", "=", state_by_model[model]]] if model in state_by_model else []
        contracts.append(
            {
                "write": write,
                "readback": {
                    "server": "odoo",
                    "tool": "search_read",
                    "args": {"model": model, "domain": domain},
                },
            }
        )

    erp_actions = [
        step
        for step in source_mutations
        if step["server"] == "erp" and step["tool"] == "api_invoke_action"
    ]
    action_names = [(step.get("args") or {}).get("action") for step in erp_actions]
    if any(str(action).startswith("ContosoPaymentRun") for action in action_names):
        write_step = next(
            (
                step
                for step in reversed(erp_actions)
                if (step.get("args") or {}).get("action") == "ContosoPaymentRunCommit"
            ),
            erp_actions[-1],
        )
        run_id = (write_step.get("args") or {}).get("parameters", {}).get("run_id", "PR-00001")
        for entity in ("PaymentRuns", "PaymentRunLines"):
            contracts.append(
                {
                    "write": {
                        "server": "erp",
                        "tool": "api_invoke_action",
                        "args": {"action": (write_step.get("args") or {})["action"]},
                    },
                    "readback": {
                        "server": "erp",
                        "tool": "data_find_entities",
                        "args": {"entity": entity, "filters": {"run_id": run_id}},
                    },
                }
            )
    if any(str(action).startswith("ContosoJournal") for action in action_names):
        write_step = next(
            (
                step
                for step in reversed(erp_actions)
                if (step.get("args") or {}).get("action") == "ContosoJournalPost"
            ),
            erp_actions[-1],
        )
        journal_id = (write_step.get("args") or {}).get("parameters", {}).get("journal_id", "GJ-00002")
        contracts.append(
            {
                "write": {
                    "server": "erp",
                    "tool": "api_invoke_action",
                    "args": {"action": (write_step.get("args") or {})["action"]},
                },
                "readback": {
                    "server": "erp",
                    "tool": "data_find_entities",
                    "args": {"entity": "LedgerJournals", "filters": {"journal_id": journal_id}},
                },
            }
        )
    for write_step in erp_actions:
        action = (write_step.get("args") or {}).get("action")
        parameters = (write_step.get("args") or {}).get("parameters", {})
        if action == "ContosoIssueCollectionLetter":
            contracts.append(
                {
                    "write": {"server": "erp", "tool": "api_invoke_action", "args": {"action": action}},
                    "readback": {
                        "server": "erp",
                        "tool": "data_find_entities",
                        "args": {
                            "entity": "CollectionLetters",
                            "filters": {"account": parameters["customer_account"]},
                        },
                    },
                }
            )
    return contracts


def reference_walk(
    entry: dict[str, Any],
    source_walk: list[dict[str, Any]],
    contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compose material investigation, task-world work, readback, and handoff."""

    spec = decision_spec(entry["source_task"])
    reporting = {"server": "harness", "tool": "reporting_fields", "args": {}}
    base = [
        deepcopy(step)
        for step in source_walk
        if not (step["server"] == "harness" and step["tool"] in {"reporting_fields", "submit_answer"})
    ]
    submit = next(
        deepcopy(step)
        for step in reversed(source_walk)
        if step["server"] == "harness" and step["tool"] == "submit_answer"
    )
    context_reads = [step for group in _context_groups(entry, contract) for step in group]
    optional_reads = _optional_context(entry, contract)
    for offset, step in enumerate(optional_reads):
        position = min(len(context_reads), 2 + offset * 3)
        context_reads.insert(position, step)

    deep_source_reads = (
        _erpbench_material_reads(source_walk, contract)
        if entry["family"] == "erpbench"
        else []
    )
    base_call_keys = {
        json.dumps(_call_selector(step), separators=(",", ":"), sort_keys=True)
        for step in base
    }
    extra_source_reads = [
        step
        for step in deep_source_reads
        if json.dumps(_call_selector(step), separators=(",", ":"), sort_keys=True)
        not in base_call_keys
    ]
    source_mutations = [step for step in base if _is_source_mutation(step)]
    source_reads = [step for step in base if not _is_source_mutation(step)]
    source_postwrite_contracts = _source_postwrite_contracts(source_mutations)
    source_postwrite_reads = _unique_calls(
        [contract_row["readback"] for contract_row in source_postwrite_contracts]
    )

    model = control_model_for(entry, contract)
    rationale = (
        f"Selected timing option {model.recommended_option} with outcome {model.recommended_outcome}; "
        f"binding constraint {model.binding_constraint_label} ({model.binding_constraint_date}); "
        f"authority {model.approval_request_id}. {spec.supported_condition} {spec.analysis_route}"
    )
    submit["args"]["answers"] = {**(submit["args"].get("answers") or {}), **model.answers}
    decide = {
        "server": "erp",
        "tool": "api_invoke_action",
        "args": {
            "action": "ContosoFinanceCaseDecide",
            "parameters": {
                "case_id": contract["case_id"],
                "decision_code": spec.decision_code,
                "evidence_refs": contract["evidence_refs"],
                "rationale": rationale,
            },
        },
    }
    readback = {
        "server": "erp",
        "tool": "data_find_entities",
        "args": {"entity": "FinanceCases", "filters": {"case_id": contract["case_id"]}},
    }
    send = {
        "server": "email",
        "tool": "send_message",
        "args": {
            "to": contract["completion_to"],
            "subject": contract["completion_subject"],
            "body": (
                f"{contract['case_id']} is complete with decision {spec.decision_code}. "
                f"Selected timing option {model.recommended_option}; outcome date {model.recommended_outcome}; "
                f"binding constraint {model.binding_constraint_label} ({model.binding_constraint_date}); "
                f"timing versus the {model.business_need_date} control date: {model.timing_status}. "
                f"The result follows {CONTEXT_REVISION}; evidence references: "
                + ", ".join(contract["evidence_refs"])
                + ". The detailed numerical and record conclusion is filed in the finance reporting record."
            ),
        },
    }
    tail = [
        {"server": "erp", "tool": "api_find_actions", "args": {"query": "finance case"}},
        decide,
        readback,
        send,
        {"server": "email", "tool": "messages_list", "args": {"q": contract["case_id"], "label": "SENT"}},
        {"server": "email", "tool": "threads_get", "args": {"id": contract["completion_thread_id"]}},
        submit,
    ]
    walk = [
        reporting,
        *context_reads,
        *extra_source_reads,
        *base,
        *source_postwrite_reads,
        *tail,
    ]
    workflow_slug = entry["source_task"].split("/", 1)[1].replace("-", "_")
    semantic_graph = [
        "discover_reporting_contract",
        f"resolve_{entry['family']}_case_identity",
        "select_effective_control_revision",
        f"correlate_{workflow_slug}_current_operations",
        "verify_independent_scope_approval",
        f"reject_{workflow_slug}_stale_or_single_system_shortcut",
        f"derive_{spec.decision_code.casefold()}",
        "derive_control_requirement_from_case_lines",
        "reconcile_register_support_with_counterparty_exclusions",
        "net_exception_against_tolerance",
        f"weigh_timing_options_select_{model.recommended_option}",
        "compare_outcome_with_documented_need_date",
        f"persist_{workflow_slug}_task_native_outcome",
        "read_back_task_native_provider_state",
        "record_governed_dynamics_transition",
        "read_back_exact_case_state",
        "send_and_reopen_completion_thread",
        "file_supported_finance_result",
    ]
    fixed_groups = {
        name: _unique_calls(steps)
        for name, steps in _material_context_groups(contract).items()
    }
    material_source = _annotate_expected_negative_evidence(
        entry,
        _unique_calls([*extra_source_reads, *source_reads]),
    )
    material_groups = {**fixed_groups, "source_systems": material_source}
    required_context = _unique_calls(
        [step for steps in material_groups.values() for step in steps]
    )
    reference_context = _unique_calls([*context_reads, *extra_source_reads, *source_reads])
    first_source_mutation = (
        _call_selector(source_mutations[0]) if source_mutations else None
    )
    source_prewrite = (
        _unique_calls(
            [
                *[
                    step
                    for steps in fixed_groups.values()
                    for step in steps
                ],
                *extra_source_reads,
                *base[: base.index(source_mutations[0])],
            ]
        )
        if source_mutations
        else required_context
    )
    wrapper_write = {
        "server": "erp",
        "tool": "api_invoke_action",
        "args": {"action": "ContosoFinanceCaseDecide"},
    }
    wrapper_message = {
        "server": "email",
        "tool": "send_message",
        "args": {"subject": contract["completion_subject"]},
    }
    return walk, {
        "required_context_calls": required_context,
        "material_context_groups": material_groups,
        "material_context_call_count": len(required_context),
        "reference_context_calls": reference_context,
        "reference_context_call_count": len(reference_context),
        "optional_context_calls": _unique_calls(optional_reads),
        "source_prewrite_calls": source_prewrite,
        "source_mutation_calls": _unique_calls(source_mutations),
        "source_first_write_call": first_source_mutation,
        "source_postwrite_contracts": source_postwrite_contracts,
        "source_postwrite_readback_calls": source_postwrite_reads,
        "write_call": wrapper_write,
        "state_readback_call": {"server": "erp", "tool": "data_find_entities", "args": {"entity": "FinanceCases", "filters": {"case_id": contract["case_id"]}}},
        "message_write_call": wrapper_message,
        "message_readback_call": {"server": "email", "tool": "threads_get", "args": {"id": contract["completion_thread_id"]}},
        "all_mutation_calls": _unique_calls(
            [
                _mutation_scope_selector(step)
                for step in [*source_mutations, wrapper_write, wrapper_message]
            ]
        ),
        "semantic_action_graph": semantic_graph,
        "base_call_count": len(base),
        "context_call_count": len(reference_context),
    }


def _merge_writes_only(checks: dict[str, Any], allowed: set[str]) -> None:
    state_checks = checks.setdefault("state_checks", [])
    existing = next((check for check in state_checks if check.get("type") == "writes_only"), None)
    if existing is None:
        existing = {"type": "writes_only", "tables": ["answers"]}
        state_checks.append(existing)
    existing["tables"] = sorted(set(existing.get("tables", [])) | allowed)


def augment_checks(
    entry: dict[str, Any],
    checks: dict[str, Any],
    contract: dict[str, Any],
    trace_contract: dict[str, Any],
) -> dict[str, Any]:
    """Add exact causal gates and task-scoped state assertions."""

    spec = decision_spec(entry["source_task"])
    model = control_model_for(entry, contract)
    checks = deepcopy(checks)
    checks.setdefault("answer_checks", []).extend(model_answer_checks(model))
    # A handful of source workflows already send one operational email and grade
    # the total sent count.  V3 adds a separate Controls completion message, so
    # preserve the original assertion while accounting for that scoped second row.
    for state_check in checks.get("state_checks", []):
        if (
            state_check.get("type") == "row_count"
            and state_check.get("name") == "agent_sent_mail"
            and "email_messages" in state_check.get("sql", "")
            and "folder='sent'" in state_check.get("sql", "").replace('"', "'")
            and isinstance(state_check.get("expect"), int)
        ):
            state_check["expect"] += 1
    trace_checks = checks.setdefault("trace_checks", [])
    # Every required evidence system is graded as a required server, and the
    # graded lower bound on successful calls per server is the number of exact
    # evidence requests that server must answer before the decision.
    required_servers = next((check for check in trace_checks if check.get("type") == "required_servers"), None)
    if required_servers is None:
        required_servers = {"type": "required_servers", "servers": []}
        trace_checks.insert(0, required_servers)
    # A contracted provider-negative (expected_error_contains) is graded as exact
    # evidence by required_calls but is not a successful call, so it never raises
    # the per-server successful-call minimum.
    evidence_servers = Counter(
        call["server"]
        for call in trace_contract["required_context_calls"]
        if not call.get("expected_error_contains")
    )
    required_servers["servers"] = sorted(set(required_servers.get("servers", [])) | set(evidence_servers))
    existing_minimums = {check.get("server"): check for check in trace_checks if check.get("type") == "min_calls"}
    for server in sorted(evidence_servers):
        minimum = existing_minimums.get(server)
        if minimum is None:
            trace_checks.append({"type": "min_calls", "server": server, "n": evidence_servers[server]})
        else:
            minimum["n"] = max(int(minimum.get("n", 1)), evidence_servers[server])
    for group_name, calls in trace_contract["material_context_groups"].items():
        trace_checks.extend(
            [
                {
                    "type": "required_calls",
                    "name": f"material_{group_name}",
                    "calls": calls,
                },
                {
                    "type": "successful_required_calls",
                    "name": f"material_{group_name}_successful",
                    "calls": calls,
                },
            ]
        )
    trace_checks.append(
        {
            "type": "reads_before_write",
            "name": "material_before_finance_case",
            "reads": trace_contract["required_context_calls"],
            "write": trace_contract["write_call"],
        }
    )
    if trace_contract["source_first_write_call"] is not None:
        trace_checks.append(
            {
                "type": "reads_before_write",
                "name": "source_evidence_before_source_write",
                "reads": trace_contract["source_prewrite_calls"],
                "write": trace_contract["source_first_write_call"],
            }
        )
    for index, source_contract in enumerate(
        trace_contract["source_postwrite_contracts"], 1
    ):
        trace_checks.append(
            {
                "type": "post_write_readback",
                "name": f"source_provider_readback_{index:02d}",
                **source_contract,
            }
        )
    trace_checks.extend(
        [
            {
                "type": "post_write_readback",
                "name": "finance_case_readback",
                "write": trace_contract["write_call"],
                "readback": trace_contract["state_readback_call"],
            },
            {
                "type": "post_write_readback",
                "name": "completion_message_readback",
                "write": trace_contract["message_write_call"],
                "readback": trace_contract["message_readback_call"],
            },
            {
                "type": "ordered_calls",
                "name": "case_readback_handoff_submit_order",
                "calls": [
                    *trace_contract["source_postwrite_readback_calls"],
                    trace_contract["write_call"],
                    trace_contract["state_readback_call"],
                    trace_contract["message_write_call"],
                    trace_contract["message_readback_call"],
                    {"server": "harness", "tool": "submit_answer", "args": {}},
                ],
            },
            {
                "type": "no_rejected_mutations",
                "name": "no_rejected_mutations",
                "calls": trace_contract["all_mutation_calls"],
            },
        ]
    )
    escaped_case = contract["case_id"].replace("'", "''")
    escaped_code = spec.decision_code.replace("'", "''")
    escaped_subject = contract["completion_subject"].replace("'", "''")
    escaped_option = model.recommended_option.replace("'", "''")
    escaped_outcome = model.recommended_outcome.replace("'", "''")
    escaped_binding = model.binding_constraint_date.replace("'", "''")
    escaped_exception_request = model.exception_request_id.replace("'", "''")
    expected_refs = json.dumps(sorted(contract["evidence_refs"]), separators=(",", ":"))
    decision_predicate = (
        f"rationale LIKE '%{escaped_option}%' AND rationale LIKE '%{escaped_outcome}%' "
        f"AND rationale LIKE '%{escaped_binding}%'"
    )
    state_checks = checks.setdefault("state_checks", [])
    state_checks.extend(
        [
            {"type": "sql", "name": "finance_case_decided", "expect": "decided", "sql": f"SELECT status FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "sql", "name": "finance_case_exact_decision", "expect": spec.decision_code, "sql": f"SELECT decision_code FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "sql", "name": "finance_case_evidence_refs", "expect": expected_refs, "sql": f"SELECT evidence_refs FROM erp_finance_cases WHERE case_id='{escaped_case}' AND decision_code='{escaped_code}'"},
            {"type": "sql", "name": "finance_case_selected_option", "expect": 1, "sql": f"SELECT CASE WHEN {decision_predicate} THEN 1 ELSE 0 END FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "row_count", "name": "one_finance_case_audit", "expect": 1, "sql": f"SELECT COUNT(*) FROM erp_audit_trail WHERE entity_type='FinanceCase' AND entity_id='{escaped_case}' AND action='decide'"},
            {"type": "sql", "name": "exception_request_untouched", "expect": "pending", "sql": f"SELECT status FROM erp_approval_requests WHERE request_id='{escaped_exception_request}'"},
            {"type": "row_count", "name": "one_completion_email", "expect": 1, "sql": f"SELECT COUNT(*) FROM email_messages WHERE folder='sent' AND subject='{escaped_subject}' AND body LIKE '%{escaped_code}%' AND body LIKE '%{escaped_option}%' AND body LIKE '%{escaped_outcome}%' AND body LIKE '%{escaped_binding}%'"},
        ]
    )
    _merge_writes_only(checks, {"answers", "erp_finance_cases", "erp_audit_trail", "email_messages"})
    return checks


def decision_options(entry: dict[str, Any], contract: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Three costed timing alternatives; every outcome is graded as its own answer field."""

    model = control_model_for(entry, contract or case_contract(entry))
    return deepcopy(model.options)


def _atomic_rubric_evidence(
    entry: dict[str, Any],
    checks: dict[str, Any],
    trace_contract: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, str]]:
    """Validate detailed task-specific evidence behind the public milestones."""

    spec = decision_spec(entry["source_task"])
    model = control_model_for(entry, contract)
    criteria: list[dict[str, str]] = []

    def add(category: str, key: str, description: str, enforced_by: str) -> None:
        criteria.append({"id": f"{category}.{key}", "category": category, "description": description, "enforced_by": enforced_by})

    required_context = trace_contract["required_context_calls"]

    def require_call(
        category: str,
        key: str,
        description: str,
        server: str,
        tool: str,
        args: dict[str, Any],
    ) -> None:
        """Publish one causal criterion backed by an exact required-call gate.

        The public rubric is generated from the same call contract consumed by
        ``required_calls``, ``reads_before_write``, and
        ``successful_required_calls``.  Failing the build when a described call
        is absent prevents the rubric from drifting into narrative-only claims.
        """

        expected = {"server": server, "tool": tool, "args": args}
        if expected not in required_context:
            raise ValueError(
                f"{entry['task_id']} rubric criterion {key} has no exact "
                f"required-call gate: {expected}"
            )
        add(
            category,
            key,
            description,
            f"required_calls exact {server}.{tool}({json.dumps(args, sort_keys=True)}) "
            "+ successful_required_calls + reads_before_write",
        )

    add("investigation", "case-identity", f"Resolve immutable work item {contract['case_id']} and its scoped subject before combining records.", "required_calls + FinanceCases filter")
    add("investigation", "operative-authority", f"Identify {CONTEXT_REVISION} as operative and treat {SUPERSEDED_REVISION} as historical evidence only.", "exact policy metadata and full-document reads")
    add("investigation", "causal-route", spec.analysis_route, "source-system reads before the governed write")
    add("investigation", "approval-independent", "Open the independent scope approval; it authorizes the work but does not supply the outcome.", "exact Gmail message and attachment reads")
    add("investigation", "current-versus-stale", "Compare the current evidence register with the retained prior tracker instead of trusting either display in isolation.", "exact Graph workbook reads")

    # Spell out the causal investigation an experienced finance operator must
    # perform.  These are not checklist prose: every line is tied to one exact,
    # successful, pre-write MCP request in the executable verifier contract.
    require_call(
        "evidence",
        "discover-finance-case-surface",
        "Discover the ERP entity that owns finance work items before assuming which table or record shape contains the case.",
        "erp",
        "data_find_entity_type",
        {"query": "finance case work item"},
    )
    require_call(
        "evidence",
        "interpret-finance-case-schema",
        "Inspect the FinanceCases metadata so status, decision, evidence-reference, and ownership fields are interpreted from the live schema.",
        "erp",
        "data_get_entity_metadata",
        {"entity": "FinanceCases"},
    )
    require_call(
        "evidence",
        "resolve-exact-open-case",
        f"Read the exact immutable case row for {contract['case_id']} and use its current subject and status as the scope anchor.",
        "erp",
        "data_find_entities",
        {"entity": "FinanceCases", "filters": {"case_id": contract["case_id"]}},
    )
    require_call(
        "authority",
        "locate-case-controls",
        f"Search governed documents by {contract['case_id']} so the decision begins from task-linked controls rather than a familiar policy title.",
        "docs",
        "search_documents",
        {"query": contract["case_id"]},
    )
    require_call(
        "authority",
        "validate-effective-policy-metadata",
        f"Check metadata for {contract['current_policy_id']} to establish its effective date and {CONTEXT_REVISION} revision before applying it.",
        "docs",
        "get_document_metadata",
        {"doc_id": contract["current_policy_id"]},
    )
    require_call(
        "authority",
        "apply-effective-policy-body",
        f"Read the full body of {contract['current_policy_id']} and apply its decision rule to this case, not merely its search snippet or title.",
        "docs",
        "get_document",
        {"doc_id": contract["current_policy_id"]},
    )
    require_call(
        "authority",
        "disqualify-superseded-policy",
        f"Inspect metadata for {contract['prior_policy_id']} and disqualify {SUPERSEDED_REVISION} before comparing operational facts.",
        "docs",
        "get_document_metadata",
        {"doc_id": contract["prior_policy_id"]},
    )
    require_call(
        "correlation",
        "resolve-immutable-evidence-map",
        f"Use {contract['evidence_map_id']} to correlate authority, approval, operations, and case identity by immutable reference rather than display name.",
        "docs",
        "get_document",
        {"doc_id": contract["evidence_map_id"]},
    )
    require_call(
        "communications",
        "scope-case-mailbox",
        f"Search the inbox for {contract['case_id']} to identify the contemporaneous approval, operations, challenge, and stale threads.",
        "email",
        "messages_list",
        {"q": contract["case_id"], "label": "INBOX"},
    )
    require_call(
        "approval",
        "verify-approval-message",
        f"Open approval message {contract['approval_email_id']} and confirm the reviewer, timestamp, and approved scope.",
        "email",
        "messages_get",
        {"id": contract["approval_email_id"]},
    )
    require_call(
        "approval",
        "verify-approval-attachment",
        f"Read the attachment on {contract['approval_email_id']} to distinguish authorization to investigate from authorization of a predetermined outcome.",
        "email",
        "attachments_get",
        {"message_id": contract["approval_email_id"]},
    )
    require_call(
        "operations",
        "establish-current-operations",
        f"Open current operations message {contract['operations_email_id']} and use it to locate the task-native system records needed by the finance analysis.",
        "email",
        "messages_get",
        {"id": contract["operations_email_id"]},
    )
    require_call(
        "operations",
        "reject-stale-operations",
        f"Open retained draft {contract['stale_email_id']} and reject its shortcut because its date and governing revision are stale.",
        "email",
        "messages_get",
        {"id": contract["stale_email_id"]},
    )
    require_call(
        "reconciliation",
        "locate-case-workbooks",
        f"Search Drive for {contract['case_id']} to find both the current evidence register and the retained prior tracker.",
        "sheets",
        "drive_search",
        {"q": contract["case_id"]},
    )
    require_call(
        "reconciliation",
        "validate-current-workbook",
        f"Inspect Drive metadata for {contract['current_workbook']} and establish its owner and modification time before trusting its rows.",
        "sheets",
        "get_drive_item",
        {"item": contract["current_workbook"]},
    )
    require_call(
        "reconciliation",
        "read-current-register",
        f"Read A1:F5 from {contract['current_workbook']} and reconcile the current identity, authority, operations, and approval references.",
        "sheets",
        "workbook_range",
        {"item": contract["current_workbook"], "address": "A1:F5"},
    )
    require_call(
        "reconciliation",
        "validate-prior-workbook",
        f"Inspect Drive metadata for {contract['stale_workbook']} so its former owner and older modification time remain visible in the comparison.",
        "sheets",
        "get_drive_item",
        {"item": contract["stale_workbook"]},
    )
    require_call(
        "reconciliation",
        "reject-prior-register",
        f"Read A1:F3 from {contract['stale_workbook']} and reject rows tied to {SUPERSEDED_REVISION} instead of silently merging them into the current register.",
        "sheets",
        "workbook_range",
        {"item": contract["stale_workbook"], "address": "A1:F3"},
    )
    # The graded control-date decision model: requirement, coverage, gap,
    # external and internal constraints, costed alternatives, recommendation,
    # control comparison and authority.  Each read below is an exact required
    # call and each derived value is an exact answer check.
    require_call(
        "correlation",
        "interpret-case-lines-schema",
        "Inspect the FinanceCaseLines metadata so the in-scope documents and their amounts are read from the live schema rather than assumed.",
        "erp",
        "data_get_entity_metadata",
        {"entity": "FinanceCaseLines"},
    )
    require_call(
        "correlation",
        "derive-control-requirement",
        f"Read the in-scope FinanceCaseLines for {contract['case_id']} and derive the control requirement by summing their amounts; the FY2025 look-alike {contract['decoy_case_id']} stays out of scope.",
        "erp",
        "data_find_entities",
        {"entity": "FinanceCaseLines", "filters": {"case_id": contract["case_id"]}},
    )
    require_call(
        "correlation",
        "reconcile-support-register",
        f"Read {contract['support_range']} of {contract['current_workbook']} and separate supported rows from excluded rows before netting usable support against the requirement.",
        "sheets",
        "workbook_range",
        {"item": contract["current_workbook"], "address": contract["support_range"]},
    )
    require_call(
        "external",
        "confirm-counterparty-constraint",
        f"Open the counterparty's own message {contract['counterparty_email_id']} for its committed correction date, its holding charge, and the references it cannot confirm.",
        "email",
        "messages_get",
        {"id": contract["counterparty_email_id"]},
    )
    require_call(
        "internal",
        "apply-close-calendar",
        f"Read {contract['close_calendar_id']} for the posting window and the standard and exception lead times that shape every timing option.",
        "docs",
        "get_document",
        {"doc_id": contract["close_calendar_id"]},
    )
    require_call(
        "internal",
        "document-business-need-date",
        f"Open the request {contract['request_email_id']} and use the requester's documented need-by date as the control date, not the close calendar or the world date.",
        "email",
        "messages_get",
        {"id": contract["request_email_id"]},
    )
    require_call(
        "authority",
        "apply-approval-policy",
        "Read the Finance Case approval policies to establish the authority limit and the separate CFO exception policy.",
        "erp",
        "data_find_entities",
        {"entity": "ApprovalPolicies", "filters": {"doc_type": "Finance Case"}},
    )
    require_call(
        "authority",
        "apply-approved-request",
        f"Read the approval requests for {contract['case_id']} and apply the approved {contract['approval_request_id']} to the selected scope while leaving the pending {contract['exception_request_id']} untouched.",
        "erp",
        "data_find_entities",
        {"entity": "ApprovalRequests", "filters": {"doc_id": contract["case_id"]}},
    )
    for server in sorted({call["server"] for call in trace_contract["required_context_calls"]}):
        add("investigation", f"provider-{server}", f"Use the task-scoped {PROVIDER_MAPPINGS[server]} evidence needed for this case.", "successful required provider calls")
    add("correlation", "requirement-derivation", "Derive the control requirement from the in-scope FinanceCaseLines amounts instead of reading a header or the approval amount.", "answer check control_requirement_usd")
    add("correlation", "coverage-reconciliation", "Grade observed support, the excluded portion corroborated by the counterparty, and the usable remainder as separate values.", "answer checks observed_support_usd, excluded_support_usd, usable_support_usd")
    add("correlation", "exception-tolerance", f"Net usable support against the requirement into the exception and test it against the {model.tolerance_pct}% tolerance.", "answer checks exception_usd, exception_within_tolerance")
    add("external", "counterparty-date", "Carry the counterparty's committed correction date from its own message into the timing options.", "answer check external_constraint_date")
    add("internal", "posting-window", "Carry the close calendar's posting window into the binding constraint.", "answer check posting_window_close_date")
    add("decision", "supported-condition", spec.supported_condition, "exact authored decision and final state")
    add("decision", "reject-shortcut", f"Reject the unsupported branch: {spec.rejected_shortcut}", "wrong-branch negative control")
    add("decision", "exact-code", f"Select `{spec.decision_code}` only after the evidence intersection supports it.", "FinanceCases decision_code assertion")
    add("decision", "alternatives-costed", f"Weigh `{OPTION_PROCEED}`, `{OPTION_HOLD}` and `{OPTION_EXCEPTION}`, each with an exact outcome date, incremental cost and authority status.", "answer checks for every option outcome date; decision options with outcome, incremental_cost and authority_status")
    add("decision", "recommended-option", f"Select `{model.recommended_option}` with outcome {model.recommended_outcome} and its documented incremental cost.", "answer checks recommended_option, recommended_outcome_date, recommended_incremental_cost_usd; FinanceCases rationale assertion")
    add("decision", "control-date-variance", f"Compare the selected outcome with the documented {model.business_need_date} need-by date into a signed day variance and an honest {model.timing_status} status.", "answer checks business_need_date, outcome_vs_control_days, decision_timing_status")
    add("authority", "approval-applied", f"Apply {model.approval_request_id} and its authority limit to the selected scope; the exception option stays flagged as requiring approval beyond current authority.", "answer checks approval_request_id, approval_authority_limit_usd, escalation_approval_required")
    add("authority", "exception-not-executed", f"Leave {model.exception_request_id} pending; the unauthorized alternative is never executed.", "exception_request_untouched state assertion")
    for check in checks.get("answer_checks", []):
        add("answer", check["field"], f"File the task-specific `{check['field']}` conclusion in the discovered reporting schema using its declared type and scale.", f"deterministic answer check: {check.get('type', 'string')}")
    add("state", "governed-transition", f"Use the Dynamics generic action surface to move only {contract['case_id']} from open to decided.", "exact SQL pre/post state")
    add("state", "evidence-refs", "Persist the exact five independently sourced immutable references with the case decision.", "exact serialized evidence_refs assertion")
    add("state", "selected-option-recorded", "Persist the selected option id, its outcome date and the binding constraint date in the case rationale.", "FinanceCases rationale assertion")
    add("state", "audit-row", "Produce exactly one Dynamics audit event for the case transition.", "row-count assertion")
    add("state", "completion-message", "Send exactly one scoped Controls handoff naming the case, the supported decision, the selected option, its outcome date and the binding constraint.", "Gmail sent-state body assertion")
    add("procedure", "read-before-write", "Complete all required context reads before recording the case decision.", "reads_before_write")
    add("procedure", "case-readback", "Read the exact FinanceCases record after the decision action.", "post_write_readback")
    add("procedure", "message-readback", "Reopen the exact completion thread after sending it.", "post_write_readback")
    add("procedure", "successful-calls", "Required evidence calls must succeed; failed lookups do not count as investigation.", "successful_required_calls")
    add("containment", "write-scope", "Preserve every table outside the source task's authorized mutations, the finance case, its audit row, the completion email, and the reporting row.", "writes_only initial-state diff")
    if len(criteria) < 40:
        raise ValueError(f"{entry['task_id']} has only {len(criteria)} public criteria")
    if len({row["id"] for row in criteria}) != len(criteria):
        raise ValueError(f"{entry['task_id']} has duplicate public criteria ids")
    return criteria


def public_criteria(
    entry: dict[str, Any],
    checks: dict[str, Any],
    trace_contract: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, str]]:
    """The atomic public rubric: every criterion names the exact check enforcing it."""

    return _atomic_rubric_evidence(entry, checks, trace_contract, contract)


def _check_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "check"


def atomic_check_specs(checks: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the stable IDs emitted by the packaged deterministic verifier."""

    output: list[dict[str, Any]] = []
    for source, key in (
        ("answer", "answer_checks"),
        ("trace", "trace_checks"),
        ("state", "state_checks"),
    ):
        for index, check in enumerate(checks.get(key, []), 1):
            label = str(
                check.get("name")
                or check.get("field")
                or check.get("type")
                or "check"
            )
            output.append(
                {
                    "id": f"{source}.{index:03d}.{_check_slug(label)}",
                    "source": source,
                    "type": str(check.get("type") or "string"),
                    "name": label,
                }
            )
    return output


def rubric_criteria(
    entry: dict[str, Any],
    checks: dict[str, Any],
    trace_contract: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Group every deterministic check into 14 task-specific employee outcomes."""

    # Retain the exact-call validation from v3.1 without publishing a 40-line
    # procedure as the employee-facing rubric.
    _atomic_rubric_evidence(entry, checks, trace_contract, contract)
    spec = decision_spec(entry["source_task"])
    atomic = atomic_check_specs(checks)
    check_by_id = {row["id"]: row for row in atomic}
    grouped: dict[str, list[str]] = {
        milestone_id: [] for milestone_id in SEMANTIC_MILESTONE_WEIGHTS
    }

    original_state: list[str] = []
    case_evidence_id: str | None = None
    for row in atomic:
        source = row["source"]
        name = row["name"]
        check_type = row["type"]
        target: str | None = None
        if source == "answer":
            target = "answer.insights"
        elif source == "trace":
            if name == "material_scope":
                target = "investigation.scope"
            elif name in {"material_authority", "material_approval"}:
                target = "investigation.authority"
            elif name == "material_current_state":
                target = "investigation.current_state"
            elif name == "material_source_systems":
                target = "investigation.source_systems"
            elif name == "material_control_model":
                target = "analysis.causal_reasoning"
            elif name == "material_external_constraint":
                target = "investigation.current_state"
            elif name.endswith("_successful"):
                target = "analysis.causal_reasoning"
            elif check_type in {"required_servers", "min_calls"}:
                target = "investigation.source_systems"
            elif check_type == "post_write_readback":
                target = "verification.readback"
            elif check_type in {
                "reads_before_submit",
                "reads_before_write",
                "ordered_calls",
                "no_rejected_mutations",
            }:
                target = "execution.sequence"
            else:
                target = "analysis.causal_reasoning"
        elif source == "state":
            if check_type == "writes_only":
                target = "containment.scope"
            elif name in {"finance_case_exact_decision", "finance_case_selected_option"}:
                target = "decision.supported_path"
            elif name == "exception_request_untouched":
                target = "containment.scope"
            elif name == "finance_case_decided":
                target = "state.case"
            elif name == "finance_case_evidence_refs":
                case_evidence_id = row["id"]
            elif name == "one_finance_case_audit":
                target = "verification.outcome"
            elif name == "one_completion_email" or any(
                token in name.casefold()
                for token in ("sent_mail", "completion_message", "handoff")
            ):
                target = "state.collaboration"
            else:
                original_state.append(row["id"])
        if target is not None:
            grouped[target].append(row["id"])

    if original_state:
        grouped["state.operational"].extend(original_state)
        if case_evidence_id is not None:
            grouped["state.case"].append(case_evidence_id)
    elif case_evidence_id is not None:
        # Read-only analyses still materialize a task-native decision through
        # the exact evidence references persisted on the finance case.
        grouped["state.operational"].append(case_evidence_id)

    source_mutations = trace_contract["source_mutation_calls"]
    model = control_model_for(entry, contract)
    mutation_surfaces = sorted(
        {f"{step['server']}.{step['tool']}" for step in source_mutations}
    )
    answer_fields = [
        row["name"] for row in atomic if row["source"] == "answer"
    ]
    source_read_count = len(
        trace_contract["material_context_groups"]["source_systems"]
    )
    readback_count = len(trace_contract["source_postwrite_contracts"]) + 2
    descriptions = {
        "investigation.scope": (
            f"Resolve {contract['case_id']} through the live FinanceCases entity and keep similarly named records outside the task boundary."
        ),
        "investigation.authority": (
            f"Establish {CONTEXT_REVISION} and the independent approval as operative for {contract['case_id']}; reject {SUPERSEDED_REVISION} as historical rather than silently merging it."
        ),
        "investigation.current_state": (
            f"Reconcile the current operations message and {contract['current_workbook']} against the stale message and {contract['stale_workbook']} using immutable IDs and effective timestamps."
        ),
        "investigation.source_systems": (
            f"Complete the {source_read_count} task-native provider reads needed to {spec.analysis_route[0].lower() + spec.analysis_route[1:]}"
        ),
        "analysis.causal_reasoning": (
            f"Join identity, authority, approval, and live {entry['family']} records to establish whether {spec.supported_condition[0].lower() + spec.supported_condition[1:]} "
            f"Then derive the control requirement from the FinanceCaseLines, net the register's usable support and the counterparty-corroborated exclusions into the exception, and test it against the {model.tolerance_pct}% tolerance."
        ),
        "decision.supported_path": (
            f"Compare the supported path, the evidence-insufficient hold, and the rejected shortcut; select `{spec.decision_code}` only because the joined evidence supports it, "
            f"and select the timing option `{model.recommended_option}` (outcome {model.recommended_outcome}, bound by {model.binding_constraint_label}) over the costed alternatives, recording it on the case."
        ),
        "state.operational": (
            f"Leave the task-native {entry['family']} outcome in its exact supported state"
            + (
                f" through {', '.join(mutation_surfaces)}."
                if mutation_surfaces
                else " without fabricating an operational mutation for a read-only analysis."
            )
        ),
        "state.case": (
            f"Persist one source-audited transition of {contract['case_id']} from open to decided with the exact decision rationale and immutable evidence references."
        ),
        "state.collaboration": (
            f"Send exactly the supported task-native communication, when required, and one scoped Controls completion message for {contract['case_id']}."
        ),
        "verification.outcome": (
            f"Verify the task-native final state and produce exactly one governed Dynamics audit event for {contract['case_id']}."
        ),
        "verification.readback": (
            f"Perform all {readback_count} provider-native readbacks after their writes, including the exact FinanceCases row and reopened Controls thread."
        ),
        "containment.scope": (
            f"Keep every successful change inside the source task, {contract['case_id']}, its audit row, the completion message, and the answer record; leave the pending {model.exception_request_id} unexecuted."
        ),
        "answer.insights": (
            f"File the exact task-supported {', '.join(answer_fields)} conclusions in the discovered reporting schema with the correct units, identifiers, and scope."
        ),
        "execution.sequence": (
            "Investigate before dependent writes, verify persisted state before handoff, submit last, and complete without a rejected state-changing call."
        ),
    }

    missing = [milestone for milestone, ids in grouped.items() if not ids]
    if missing:
        raise ValueError(f"{entry['task_id']} has empty semantic milestones: {missing}")
    assigned = [check_id for ids in grouped.values() for check_id in ids]
    if len(assigned) != len(set(assigned)):
        raise ValueError(f"{entry['task_id']} reuses an atomic check across milestones")
    if set(assigned) != set(check_by_id):
        omitted = sorted(set(check_by_id) - set(assigned))
        raise ValueError(f"{entry['task_id']} omits atomic checks: {omitted}")
    if sum(SEMANTIC_MILESTONE_WEIGHTS.values()) != 100:
        raise AssertionError("semantic milestone weights must total 100")
    return [
        {
            "id": milestone_id,
            "category": milestone_id.split(".", 1)[0],
            "description": descriptions[milestone_id],
            "weight": weight,
            "atomic_check_ids": grouped[milestone_id],
            "atomic_checks": [check_by_id[check_id] for check_id in grouped[milestone_id]],
        }
        for milestone_id, weight in SEMANTIC_MILESTONE_WEIGHTS.items()
    ]


def _snapshot(
    connection: sqlite3.Connection,
    table: str,
    tokens: set[str],
    *,
    limit: int = 24,
) -> dict[str, Any] | None:
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
        return None
    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')]
    rows = [dict(row) for row in connection.execute(f'SELECT * FROM "{table}" LIMIT 800').fetchall()]
    matched = [row for row in rows if any(token in json.dumps(row, default=str).casefold() for token in tokens)][:limit]
    return {"table": table, "row_count": len(rows), "columns": columns, "task_relevant_rows": matched or rows[: min(5, limit)]}


def _csv(snapshots: list[dict[str, Any]], case_id: str) -> str:
    rows = [{"case_id": case_id, "source_table": snapshot["table"], **row} for snapshot in snapshots for row in snapshot["task_relevant_rows"]]
    if not rows:
        rows = [{"case_id": case_id, "source_table": "none", "note": "No matching rows in this provider layer"}]
    fields = ["case_id", "source_table", *sorted({key for row in rows for key in row if key not in {"case_id", "source_table"}})]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows({key: row.get(key, "") for key in fields} for row in rows)
    return stream.getvalue()


def _excel_col(number: int) -> str:
    value = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        value = chr(65 + remainder) + value
    return value


def _xlsx(rows: list[list[Any]]) -> bytes:
    xml_rows: list[str] = []
    for row_index, values in enumerate(rows, 1):
        cells = "".join(
            f'<c r="{_excel_col(column + 1)}{row_index}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            for column, value in enumerate(values)
        )
        xml_rows.append(f'<row r="{row_index}">{cells}</row>')
    worksheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        + "".join(xml_rows)
        + "</sheetData></worksheet>"
    )
    stream = io.BytesIO()

    def member(name: str) -> zipfile.ZipInfo:
        info = zipfile.ZipInfo(name, FIXED_XLSX_ZIP_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = 0o644 << 16
        return info

    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member("[Content_Types].xml"), '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        archive.writestr(member("_rels/.rels"), '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr(member("xl/workbook.xml"), '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Evidence" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr(member("xl/_rels/workbook.xml.rels"), '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr(member("xl/worksheets/sheet1.xml"), worksheet)
    return stream.getvalue()


def _pdf(text: str) -> bytes:
    """Write a small standards-valid, text-native PDF without external packages."""

    lines = [line[:105] for line in text.splitlines() if line.strip()][:45]
    commands = ["BT", "/F1 9 Tf", "54 750 Td", "11 TL"]
    for index, line in enumerate(lines):
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(("" if index == 0 else "T* ") + f"({safe}) Tj")
    commands.append("ET")
    content = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(output)


def _eml(message: dict[str, Any], case_id: str) -> str:
    return "\n".join(
        [
            f"From: {message['from_addr']}",
            f"To: {message['to_addr']}",
            f"Date: {message['sent_at']}",
            f"Subject: {message['subject']}",
            f"Message-ID: <{message['id']}@ledgerbench.invalid>",
            f"X-LedgerBench-Case: {case_id}",
            "MIME-Version: 1.0",
            "Content-Type: text/plain; charset=utf-8",
            "",
            str(message.get("body") or ""),
            "",
        ]
    )


def write_asset_views(
    root: Path,
    database: Path,
    prompt: str,
    entry: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Write 28 agent-visible assets; never copy gold, checks, or the oracle walk."""

    if root.exists():
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    root.mkdir(parents=True, exist_ok=True)
    cx = sqlite3.connect(database)
    cx.row_factory = sqlite3.Row
    spec = decision_spec(entry["source_task"])
    tokens = {token.casefold() for token in _argument_tokens([prompt, contract["case_id"], entry["source_task"]])}
    assets: list[dict[str, Any]] = []

    common_material = {
        "02-open-finance-case.json",
        f"03-{contract['current_policy_id']}.md",
        f"04-{contract['prior_policy_id']}.md",
        f"05-{contract['evidence_map_id']}.md",
        f"06-{contract['close_calendar_id']}.md",
        f"11-{contract['approval_email_id']}.eml",
        f"12-{contract['operations_email_id']}.eml",
        f"13-{contract['counterparty_email_id']}.eml",
        f"14-{contract['stale_email_id']}.eml",
        f"16-{contract['current_workbook']}",
        f"17-{contract['stale_workbook']}",
        "26-approvals-and-controls.json",
        "27-lineage-and-currency.md",
    }
    if entry["family"] == "erpbench":
        provider_material = "25-odoo-procurement.json"
    elif entry["family"] in {"business_brief", "business_brief_fb"}:
        provider_material = "24-filings-evidence.json"
    elif entry["family"] in {
        "anomaly_triage",
        "bank_rec",
        "cash_app",
        "cash_forecast",
        "payment_ops",
    }:
        provider_material = "22-bank-and-payment-state.csv"
    elif entry["family"] == "cross_system":
        provider_material = "23-books-ledger.json"
    else:
        provider_material = "21-erp-transactions.csv"
    material_assets = common_material | {provider_material}

    def add(name: str, source: str, content: str | bytes, *, role: str) -> None:
        target = root / name
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")
        assets.append(
            {
                "filename": name,
                "source": source,
                "kind": target.suffix.lstrip("."),
                "evidence_role": role,
                "material": name in material_assets,
            }
        )

    add("01-employee-request.md", "Teams", prompt + "\n", role="request")
    case = dict(cx.execute("SELECT * FROM erp_finance_cases WHERE case_id=?", (contract["case_id"],)).fetchone())
    case_lines = [
        dict(row)
        for row in cx.execute(
            "SELECT * FROM erp_finance_case_lines WHERE case_id=? ORDER BY line", (contract["case_id"],)
        )
    ]
    add(
        "02-open-finance-case.json",
        "Dynamics FinanceCases",
        json.dumps({"case": case, "lines": case_lines}, indent=2, sort_keys=True) + "\n",
        role="identity",
    )

    doc_ids = [
        contract["current_policy_id"], contract["prior_policy_id"], contract["evidence_map_id"],
        contract["close_calendar_id"], contract["handoff_id"], contract["identity_id"], contract["exception_id"],
    ]
    for index, doc_id in enumerate(doc_ids, 3):
        row = dict(cx.execute("SELECT * FROM docs_documents WHERE doc_id=?", (doc_id,)).fetchone())
        body = f"<!-- doc_id: {doc_id}; version: {row['version']}; effective: {row['effective_date']} -->\n{row['body']}"
        if doc_id in {contract["current_policy_id"], contract["prior_policy_id"]}:
            role = "authority"
        elif doc_id == contract["close_calendar_id"]:
            role = "calendar"
        else:
            role = "control"
        add(f"{index:02d}-{doc_id}.md", "Governed document library", body + "\n", role=role)

    email_ids = [
        contract["request_email_id"], contract["approval_email_id"], contract["operations_email_id"],
        contract["counterparty_email_id"], contract["stale_email_id"], contract["challenge_email_id"],
    ]
    email_roles = {
        contract["request_email_id"]: "request",
        contract["approval_email_id"]: "approval",
        contract["operations_email_id"]: "operations",
        contract["counterparty_email_id"]: "counterparty",
    }
    for index, message_id in enumerate(email_ids, 10):
        message = dict(cx.execute("SELECT * FROM email_messages WHERE id=?", (message_id,)).fetchone())
        add(f"{index:02d}-{message_id}.eml", "Gmail mailbox", _eml(message, contract["case_id"]), role=email_roles.get(message_id, "history"))

    for index, workbook in enumerate((contract["current_workbook"], contract["stale_workbook"]), 16):
        rows = [json.loads(row[0]) for row in cx.execute("SELECT cells FROM sheet_rows WHERE file=? ORDER BY row_no", (workbook,))]
        add(f"{index:02d}-{workbook}", "Microsoft Graph workbook", _xlsx(rows), role="current-register" if index == 16 else "stale-register")

    current_policy = cx.execute("SELECT body FROM docs_documents WHERE doc_id=?", (contract["current_policy_id"],)).fetchone()[0]
    add("18-current-control-copy.pdf", "Controlled PDF export", _pdf(f"Case {contract['case_id']}\n{current_policy}"), role="authority")
    add("19-source-analysis-brief.pdf", "Finance workpaper PDF", _pdf(f"Case {contract['case_id']}\nQuestion: {spec.employee_question}\nAnalysis: {spec.analysis_route}\nNo conclusion is precomputed in this brief."), role="analysis-brief")

    groups = [
        ("20-erp-master-data.csv", ("erp_customers", "erp_vendors", "erp_items"), "ERP master"),
        ("21-erp-transactions.csv", ("erp_cust_trans", "erp_vend_trans", "erp_gl", "erp_purch_orders", "erp_sales_orders"), "ERP transactions"),
        ("22-bank-and-payment-state.csv", ("erp_bank_lines", "erp_payment_runs", "erp_payment_run_lines", "erp_settlements"), "Bank and payment"),
    ]
    for filename, tables, source in groups:
        snapshots = [snapshot for table in tables if (snapshot := _snapshot(cx, table, tokens)) is not None]
        add(filename, source, _csv(snapshots, contract["case_id"]), role="operations")

    json_groups = [
        ("23-books-ledger.json", ("books_customers", "books_invoices", "books_payments", "books_credit_memos"), "QuickBooks subsidiary ledger"),
        ("24-filings-evidence.json", ("filings_companies", "filings_facts", "filings_documents"), "SEC filing snapshot"),
        (
            "25-odoo-procurement.json",
            (
                "erpb_partners",
                "erpb_products",
                "erpb_sale_orders",
                "erpb_sale_order_lines",
                "erpb_purchase_orders",
                "erpb_purchase_order_lines",
                "erpb_manufacturing_orders",
                "erpb_vendor_offers",
                "erpb_stock",
                "erpb_demand",
                "erpb_boms",
                "erpb_bom_components",
                "erpb_workcenters",
            ),
            "Odoo ERP",
        ),
        ("26-approvals-and-controls.json", ("erp_approval_requests", "erp_approval_policies", "erp_fiscal_periods", "approval_matrix", "close_tasks"), "Control records"),
    ]
    for filename, tables, source in json_groups:
        snapshots = [snapshot for table in tables if (snapshot := _snapshot(cx, table, tokens)) is not None]
        add(filename, source, json.dumps({"case_id": contract["case_id"], "sources": snapshots}, indent=2, default=str, sort_keys=True) + "\n", role="operations")

    add("27-lineage-and-currency.md", "Evidence custodian", f"# {contract['case_id']} lineage\n\nCurrent sources carry their own immutable ids, effective dates, filing accessions, workbook modified times, or ERP keys. Resolve those fields directly. A filename or display name alone is not identity. The FY2025 look-alike case {contract['decoy_case_id']} is closed history, not the open work item.\n", role="lineage")
    inventory_rows = [["case_id", "source_id", "role", "status"], *[[contract["case_id"], ref, role, "inspect"] for ref, role in zip(contract["evidence_refs"], ("authority", "approval", "register", "identity", "approval-request"))]]
    inventory_csv = io.StringIO()
    csv.writer(inventory_csv).writerows(inventory_rows)
    add("28-source-inventory.csv", "Case intake", inventory_csv.getvalue(), role="inventory")
    add("29-current-versus-stale-notes.txt", "Controls", f"Case {contract['case_id']} has both {CONTEXT_REVISION} and {SUPERSEDED_REVISION} evidence. Current records must be established by effective dates and modified timestamps. The prior draft is retained to test, not to follow. The prior tracker treats every support row as usable; the current register and the counterparty's own message decide which rows are excluded.\n", role="conflict")

    manifest_rows = [
        {
            "filename": asset["filename"],
            "source": asset["source"],
            "evidence_role": asset["evidence_role"],
            "material": asset["material"],
        }
        for asset in assets
    ]
    add("30-agent-visible-asset-manifest.json", "Release builder", json.dumps({"case_id": contract["case_id"], "gold_included": False, "oracle_walk_included": False, "assets": manifest_rows}, indent=2, sort_keys=True) + "\n", role="manifest")
    cx.close()
    if len(assets) != ASSETS_PER_TASK:
        raise ValueError(f"expected {ASSETS_PER_TASK} assets, wrote {len(assets)}")
    material_count = sum(bool(asset["material"]) for asset in assets)
    if material_count != MATERIAL_ASSETS_PER_TASK:
        raise ValueError(f"expected {MATERIAL_ASSETS_PER_TASK} material assets, wrote {material_count}")
    return assets


def validate_native_asset(path: Path) -> bool:
    suffix = path.suffix.casefold()
    data = path.read_bytes()
    if suffix == ".xlsx":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                required = {"[Content_Types].xml", "xl/workbook.xml", "xl/worksheets/sheet1.xml"}
                return required <= set(archive.namelist()) and b"<worksheet" in archive.read("xl/worksheets/sheet1.xml")
        except zipfile.BadZipFile:
            return False
    if suffix == ".pdf":
        return data.startswith(b"%PDF-1.4") and data.rstrip().endswith(b"%%EOF") and b"startxref" in data and b"/Type /Page" in data
    if suffix == ".json":
        json.loads(data.decode("utf-8"))
    elif suffix == ".csv":
        list(csv.reader(io.StringIO(data.decode("utf-8"))))
    elif suffix == ".eml":
        text = data.decode("utf-8")
        return all(header in text for header in ("From:", "To:", "Subject:", "Message-ID:"))
    else:
        data.decode("utf-8")
    return True
