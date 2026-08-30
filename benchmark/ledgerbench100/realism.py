"""Causal-realism contract for the LedgerBench-100 v3.4 release."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from html import escape
from pathlib import Path
from typing import Any

from decision_model import (
    CHAIN_ANSWER_FIELDS,
    CHAIN_FIELDS,
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
PLANNING_WINDOW_REVISION = "PLAN-2026.03"
DECISION_ENTITY = "DecisionWorkItems"
DECISION_LINE_ENTITY = "DecisionScopeLines"
DECISION_ACTION = "ContosoDecisionWorkItemDecide"


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
CONTEXTUAL_ASSETS_PER_TASK = 30
MIN_MATERIAL_ASSETS_PER_TASK = 19

SEMANTIC_MILESTONE_WEIGHTS = {
    "investigation.scope": 3,
    "investigation.authority": 3,
    "investigation.current_state": 3,
    "investigation.source_systems": 12,
    "analysis.task_native_reasoning": 12,
    "analysis.operating_plan": 8,
    "decision.supported_path": 10,
    "decision.options": 4,
    "state.operational": 15,
    "state.case": 3,
    "state.collaboration": 3,
    "verification.outcome": 4,
    "verification.readback": 4,
    "containment.scope": 4,
    "answer.insights": 9,
    "execution.sequence": 3,
}

TASK_NATIVE_MILESTONES = {
    "investigation.source_systems",
    "analysis.task_native_reasoning",
    "decision.supported_path",
    "state.operational",
    "answer.insights",
}
MIN_TASK_NATIVE_POINTS = 58

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


def _erpbench_plan_facts(entry: dict[str, Any]) -> dict[str, Any]:
    """Derive employee-facing planning facts from the source oracle contract.

    These are not task-number decorations. Dates come from the exact Odoo writes,
    totals come from the source answer/state checks, and the constraint vocabulary
    comes from the curated scenario archetype.
    """

    source = Path(__file__).resolve().parents[2] / "tasks" / entry["source_task"]
    walk = json.loads((source / "solution" / "walk.json").read_text())
    checks = json.loads((source / "tests" / "checks.json").read_text())
    submitted = next(
        step for step in reversed(walk)
        if step["server"] == "harness" and step["tool"] == "submit_answer"
    )["args"]["answers"]
    state_by_name = {
        check.get("name"): check for check in checks.get("state_checks", [])
    }
    sales_dates: list[str] = []
    purchase_dates: list[str] = []
    production_dates: list[str] = []
    calculated_purchase_spend = 0.0
    for step in walk:
        arguments = step.get("args") or {}
        model = arguments.get("model")
        values = arguments.get("values") or {}
        if model == "sale.order" and values.get("commitment_date"):
            sales_dates.append(str(values["commitment_date"]))
        elif model == "purchase.order" and values.get("date_planned"):
            purchase_dates.append(str(values["date_planned"]))
        elif model == "mrp.production" and values.get("date_planned"):
            production_dates.append(str(values["date_planned"]))
        if model == "purchase.order.line" and step.get("tool") == "create":
            calculated_purchase_spend += float(values.get("qty") or 0) * float(
                values.get("price_unit") or 0
            )
    if not sales_dates:
        raise ValueError(f"{entry['task_id']} has no source-supported customer completion date")

    purchased = float(submitted["units_purchased"])
    manufactured = float(submitted["units_manufactured"])
    if purchased and manufactured:
        supply_mode = "MAKE_AND_BUY"
    elif purchased:
        supply_mode = "BUY_ONLY"
    elif manufactured:
        supply_mode = "MANUFACTURE_ONLY"
    else:
        supply_mode = "EXISTING_COVERAGE_ONLY"

    slug = entry["source_task"].split("/", 1)[1]
    if "repair-plan-hard" in slug:
        constraint = "FAILED_WORKCENTER_AND_QUALIFIED_RECOVERY_CAPACITY"
        alternative = "AUTHORIZE_OVERTIME_OR_EXTERNAL_SUBCONTRACTING"
    elif "repair-plan" in slug:
        constraint = "FAILED_SUPPLY_ROUTE_AND_LEAST_DISRUPTIVE_REPLACEMENT"
        alternative = "FULL_PORTFOLIO_REPLAN_OR_CUSTOMER_DATE_EXCEPTION"
    elif "restricted-subassembly" in slug:
        constraint = "RESTRICTED_SUBASSEMBLY_ROUTING_QUALIFICATION"
        alternative = "UNQUALIFIED_ROUTING_EXCEPTION"
    elif "shared-component" in slug:
        constraint = "SHARED_COMPONENT_ALLOCATION_ACROSS_DEPENDENT_BRANCHES"
        alternative = "EXPEDITE_SHARED_COMPONENT_WITH_PLANT_APPROVAL"
    elif "serial-subassemblies" in slug:
        constraint = "SERIAL_SUBASSEMBLY_CRITICAL_PATH"
        alternative = "COMPRESS_SERIAL_ROUTING_WITH_OVERTIME"
    elif "parallel-subassemblies" in slug:
        constraint = "PARALLEL_BRANCH_SYNCHRONIZATION"
        alternative = "OUTSOURCE_ONE_BRANCH_WITH_PLANT_APPROVAL"
    elif "shared-overflow-capacity" in slug or "split-by-capacity" in slug:
        constraint = "QUALIFIED_PRIMARY_AND_OVERFLOW_CAPACITY"
        alternative = "AUTHORIZE_OVERTIME_OR_ADDITIONAL_OVERFLOW"
    elif "single-workcenter" in slug or "qualified-workcenters" in slug:
        constraint = "QUALIFIED_WORKCENTER_CAPACITY"
        alternative = "AUTHORIZE_OVERTIME_OR_ALTERNATE_ROUTING"
    elif "manufacture-only" in slug:
        constraint = "MANUFACTURE_ONLY_POLICY_AND_COMPONENT_AVAILABILITY"
        alternative = "FINISHED_GOODS_BUY_POLICY_EXCEPTION"
    elif "lowest-cost" in slug:
        constraint = "LOWEST_COST_FEASIBLE_MAKE_OR_BUY_PATH"
        alternative = "HIGHER_COST_EXPEDITED_SUPPLY"
    elif "net-30" in slug:
        constraint = "QUALIFIED_NET_30_SUPPLIER_CAPACITY"
        alternative = "PAYMENT_TERMS_EXCEPTION"
    elif "buy-only" in slug:
        constraint = "QUALIFIED_SUPPLIER_CAPACITY_AND_DELIVERY"
        alternative = "BUDGET_OR_SUPPLIER_TERMS_EXCEPTION"
    else:
        constraint = "MATERIAL_CAPACITY_AND_CUSTOMER_PROMISE_ALIGNMENT"
        alternative = "EXPEDITED_SUPPLY_OR_OVERTIME_APPROVAL"

    spend_check = state_by_name.get("purchase_spend_matches_optimal") or {}
    purchase_spend = float(
        spend_check.get("expect", round(calculated_purchase_spend, 2))
    )
    confirmed_sales = float(
        (state_by_name.get("confirmed_sale_units") or {}).get("expect", 0)
    )
    feasibility = (
        "ALL_COMMITMENTS_FEASIBLE"
        if float(submitted["orders_rejected"]) == 0
        else "PARTIAL_COMMITMENT_SET"
    )
    answers = {
        "source_plan_completion_date": max(sales_dates),
        "latest_material_arrival_date": max(purchase_dates) if purchase_dates else "NOT_REQUIRED",
        "latest_production_date": max(production_dates) if production_dates else "NOT_REQUIRED",
        "new_purchase_spend_usd": round(purchase_spend, 2),
        "confirmed_sales_units": confirmed_sales,
        "supply_mode": supply_mode,
        "plan_feasibility": feasibility,
        "binding_operational_constraint": constraint,
        "alternative_requiring_approval": alternative,
    }
    return {
        "answers": answers,
        "sales_dates": sorted(set(sales_dates)),
        "purchase_dates": sorted(set(purchase_dates)),
        "production_dates": sorted(set(production_dates)),
    }


def _erpbench_plan_answer_checks(entry: dict[str, Any]) -> list[dict[str, Any]]:
    answers = _erpbench_plan_facts(entry)["answers"]
    numeric = {"new_purchase_spend_usd", "confirmed_sales_units"}
    natural_language = {
        "supply_mode",
        "plan_feasibility",
        "binding_operational_constraint",
        "alternative_requiring_approval",
    }
    ignored_words = {"and", "or", "with", "the"}
    return [
        (
            {
                "field": field,
                "type": "number",
                "expect": value,
                "tol_abs": 0.01,
            }
            if field in numeric
            else (
                {
                    "field": field,
                    "type": "contains_all",
                    "expect": [
                        token.casefold()
                        for token in str(value).split("_")
                        if token.casefold() not in ignored_words
                    ],
                }
                if field in natural_language
                else {"field": field, "type": "string", "expect": value}
            )
        )
        for field, value in answers.items()
    ]


def _erpbench_plan_schema_rows(
    entry: dict[str, Any], first_ordinal: int
) -> list[tuple[int, str, str, str]]:
    descriptions = {
        "source_plan_completion_date": "latest customer commitment date in the persisted source-supported plan",
        "latest_material_arrival_date": "latest planned arrival of newly purchased material, or NOT_REQUIRED",
        "latest_production_date": "latest planned production completion, or NOT_REQUIRED",
        "new_purchase_spend_usd": "new purchasing spend in the persisted feasible plan",
        "confirmed_sales_units": "units on confirmed customer sales orders after the plan is applied",
        "supply_mode": "whether feasible coverage is buy, make, both, or existing coverage only",
        "plan_feasibility": "whether every requested commitment is feasible or only a screened subset",
        "binding_operational_constraint": "task-native material, supplier, routing, or capacity constraint controlling the plan",
        "alternative_requiring_approval": "specific faster or broader route that current authority does not permit",
    }
    answers = _erpbench_plan_facts(entry)["answers"]
    return [
        (
            first_ordinal + offset,
            field,
            "number" if isinstance(value, (int, float)) else "text",
            descriptions[field],
        )
        for offset, (field, value) in enumerate(answers.items())
    ]


def _align_erpbench_control_model(
    model: ControlModel, facts: dict[str, Any]
) -> ControlModel:
    """Make the shared decision envelope use the source production plan's dates/cost."""

    answers = facts["answers"]
    completion = dt.date.fromisoformat(answers["source_plan_completion_date"])
    material = (
        dt.date.fromisoformat(answers["latest_material_arrival_date"])
        if answers["latest_material_arrival_date"] != "NOT_REQUIRED"
        else None
    )
    production = (
        dt.date.fromisoformat(answers["latest_production_date"])
        if answers["latest_production_date"] != "NOT_REQUIRED"
        else None
    )
    external = material or production or completion
    hold_outcome = max(completion, external) + dt.timedelta(days=3)
    exception_outcome = max(
        dt.date.fromisoformat(WORLD_EPOCH[:10]), completion - dt.timedelta(days=1)
    )
    planning_window = completion + dt.timedelta(days=2)
    binding = max([date for date in (material, production) if date is not None], default=completion)
    new_spend_cents = int(round(float(answers["new_purchase_spend_usd"]) * 100))
    authority_limit_cents = max(
        model.authority_limit_cents,
        ((new_spend_cents // 100_000_000) + 2) * 100_000_000,
    )
    outcomes = {
        OPTION_PROCEED: completion.isoformat(),
        OPTION_HOLD: hold_outcome.isoformat(),
        OPTION_EXCEPTION: exception_outcome.isoformat(),
    }
    costs = {
        OPTION_PROCEED: round(new_spend_cents / 100, 2),
        OPTION_HOLD: round(model.hold_charge_cents / 100, 2),
        OPTION_EXCEPTION: round(model.exception_levy_cents / 100, 2),
    }
    options = [
        {
            "id": OPTION_PROCEED,
            "label": "Commit the source-supported production and procurement plan",
            "reason": (
                f"The Odoo plan reaches the customer commitments by {completion.isoformat()} "
                f"with {answers['confirmed_sales_units']:g} confirmed sales units, "
                f"{answers['supply_mode']} coverage, and {answers['new_purchase_spend_usd']:,.2f} USD of new purchasing."
            ),
            "selected": True,
            "recommended": True,
            "outcome": outcomes[OPTION_PROCEED],
            "outcome_field": f"{OPTION_PROCEED}_outcome_date",
            "incremental_cost": costs[OPTION_PROCEED],
            "authority_status": "WITHIN_AUTHORITY",
        },
        {
            "id": OPTION_HOLD,
            "label": "Hold the affected commitments and replan after the limiting input",
            "reason": (
                f"Wait beyond the source-supported plan to {hold_outcome.isoformat()}; "
                "feasible but later than the current customer promise."
            ),
            "selected": False,
            "recommended": False,
            "outcome": outcomes[OPTION_HOLD],
            "outcome_field": f"{OPTION_HOLD}_outcome_date",
            "incremental_cost": costs[OPTION_HOLD],
            "authority_status": "AVAILABLE_NOT_RECOMMENDED",
        },
        {
            "id": OPTION_EXCEPTION,
            "label": answers["alternative_requiring_approval"].replace("_", " ").title(),
            "reason": (
                f"Target {exception_outcome.isoformat()} only through the documented "
                f"{answers['alternative_requiring_approval']} exception, which is outside current authority."
            ),
            "selected": False,
            "recommended": False,
            "outcome": outcomes[OPTION_EXCEPTION],
            "outcome_field": f"{OPTION_EXCEPTION}_outcome_date",
            "incremental_cost": costs[OPTION_EXCEPTION],
            "authority_status": "ADDITIONAL_APPROVAL_REQUIRED",
        },
    ]
    aligned_answers = {
        **model.answers,
        "external_constraint_date": external.isoformat(),
        "posting_window_close_date": planning_window.isoformat(),
        f"{OPTION_PROCEED}_outcome_date": outcomes[OPTION_PROCEED],
        f"{OPTION_HOLD}_outcome_date": outcomes[OPTION_HOLD],
        f"{OPTION_EXCEPTION}_outcome_date": outcomes[OPTION_EXCEPTION],
        "recommended_option": OPTION_PROCEED,
        "recommended_outcome_date": outcomes[OPTION_PROCEED],
        "recommended_incremental_cost_usd": costs[OPTION_PROCEED],
        "business_need_date": completion.isoformat(),
        "outcome_vs_control_days": 0,
        "decision_timing_status": "ON_TIME",
        "approval_authority_limit_usd": round(authority_limit_cents / 100, 2),
        "binding_constraint_date": binding.isoformat(),
    }
    return replace(
        model,
        external_date=external.isoformat(),
        posting_window_close=planning_window.isoformat(),
        business_need_date=completion.isoformat(),
        authority_limit_cents=authority_limit_cents,
        options=options,
        recommended_option=OPTION_PROCEED,
        recommended_outcome=completion.isoformat(),
        recommended_cost_cents=new_spend_cents,
        binding_constraint_date=binding.isoformat(),
        binding_constraint_label=answers["binding_operational_constraint"].replace("_", " ").casefold(),
        outcome_vs_control_days=0,
        timing_status="ON_TIME",
        answers=aligned_answers,
    )


def control_model_for(entry: dict[str, Any], contract: dict[str, Any]) -> ControlModel:
    """Recompute the deterministic decision model behind a case contract."""

    model = control_model(
        task_number(entry),
        entry["task_id"],
        entry["family"],
        decision_spec(entry["source_task"]),
        contract.get("world_now", WORLD_EPOCH),
    )
    if entry["family"] == "erpbench":
        return _align_erpbench_control_model(model, _erpbench_plan_facts(entry))
    return model


def case_contract(entry: dict[str, Any], world_now: str = WORLD_EPOCH) -> dict[str, Any]:
    number = task_number(entry)
    case_id = f"WORKITEM-{number:03d}"
    prefix = f"lgr-{number:03d}"
    current_book = f"{case_id.lower()}-control-pack.xlsx"
    stale_book = f"{case_id.lower()}-prior-tracker.xlsx"
    spec = decision_spec(entry["source_task"])
    subject = f"{case_id} completed — {spec.decision_code}"
    thread_id = "t_" + hashlib.sha1(subject.casefold().encode()).hexdigest()[:10]
    model = control_model_for(entry, {"world_now": world_now})
    approval_document_type = (
        "Production Planning Decision"
        if entry["family"] == "erpbench"
        else "Operational Decision Work Item"
    )
    return {
        "case_id": case_id,
        "decoy_case_id": model.decoy_case_id,
        "world_now": world_now,
        "current_policy_id": f"{prefix}-control-current",
        "prior_policy_id": f"{prefix}-control-prior",
        "evidence_map_id": f"{prefix}-evidence-map",
        "close_calendar_id": f"{prefix}-close-calendar",
        "internal_window_revision": (
            PLANNING_WINDOW_REVISION
            if entry["family"] == "erpbench"
            else CLOSE_CALENDAR_REVISION
        ),
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
        "approval_document_type": approval_document_type,
        "exception_document_type": f"{approval_document_type} Exception",
        "completion_to": (
            "operations-control@contoso-sim.example"
            if entry["family"] == "erpbench"
            else "finance-controls@contoso-sim.example"
        ),
        "completion_subject": subject,
        "completion_thread_id": thread_id,
        "completion_required_tokens": [
            case_id,
            spec.decision_code,
            model.recommended_option,
            model.recommended_outcome,
            model.binding_constraint_date,
        ],
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
        "This is needed for today's operating review. There was an earlier draft and several teams have touched the records, so please work out what is current before you commit to a position.",
        "The first number I saw does not explain the operational consequence. Investigate what the records really support, what would change the answer, and what we should do next.",
        "I need a decision the team can act on, not a data dump. Give me the strongest supported course, the meaningful alternative, and the realistic date and cost trade-off.",
        "Someone has already circulated a working paper, but it is not a conclusion. Recheck the live position, surface any evidence gap that still matters, and make the smallest defensible change.",
        "Please own this through to a usable answer. There are similar and older records around, so be careful about scope and tell me plainly if the supported result is later or narrower than requested.",
        "This has become a blocker for the team. Work from the live records, explain the constraint that truly drives the outcome, and keep any unresolved exception visible rather than forcing agreement.",
        "I want the practical answer and the reasoning an independent reviewer would need to reproduce it. Include the option you considered but would not take without more support.",
        "Treat the requested date as real. Find the best course we can support today, quantify the consequence of waiting, and avoid changing anything outside this piece of work.",
    )
    handoff_variants = (
        "When the conclusion is supported, leave the open review in that state, confirm it saved correctly, and send Controls a short handoff with the answer and timing.",
        "Carry the supported disposition through the review record, verify the result, and close the loop with Controls only after the operational state agrees.",
        "Leave a reproducible decision on the open review, including the route that would need additional authority, then confirm the completion message can be reopened.",
        "Make only the scoped change the evidence supports, check the resulting state, and give Controls a concise note covering the answer, constraint, and realistic completion.",
        "Record the decision and its alternatives in the open review, verify what persisted, and tell Controls whether it meets the date the business asked for.",
    )
    number = task_number(entry)
    context = context_variants[(number - 1) % len(context_variants)]
    handoff = handoff_variants[(number - 1) % len(handoff_variants)]
    if entry["family"] == "erpbench":
        context = (
            "The customer promises are live, and the current plan may not survive the actual material, supplier, "
            "budget, and factory constraints. Work out the feasible choices and the constraint that truly controls the promise."
        )
        handoff = (
            "If the existing plan cannot hold, make the smallest supported repair in the planning system. Confirm what "
            "persisted, then give Operations the realistic completion, the cost or margin trade-off, and the alternative "
            "that would need more authority."
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
    entry: dict[str, Any],
    source_walk: list[dict[str, Any]],
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Expose the real Odoo records needed to derive a make/buy promise."""

    product_code = _erpbench_product_code(source_walk)
    reads = [
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
    slug = entry["source_task"].split("/", 1)[1]
    if "repair-plan" in slug:
        # Recovery work must inspect commitments already left in the ERP before
        # cancelling or replacing the outage-exposed portion of the plan.
        reads.extend(
            [
                {"server": "odoo", "tool": "fields_get", "args": {"model": "purchase.order"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.production"}},
                {"server": "odoo", "tool": "search_read", "args": {"model": "sale.order", "domain": [["state", "=", "sale"]]}},
                {"server": "odoo", "tool": "search_read", "args": {"model": "purchase.order", "domain": [["state", "=", "purchase"]]}},
                {"server": "odoo", "tool": "search_read", "args": {"model": "mrp.production", "domain": [["state", "=", "confirmed"]]}},
            ]
        )
    elif "invoicing" in slug:
        reads.extend(
            [
                {"server": "odoo", "tool": "fields_get", "args": {"model": "sale.order.line"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "purchase.order.line"}},
                {"server": "odoo", "tool": "search_read", "args": {"model": "sale.order", "domain": [["state", "=", "sale"]]}},
                {"server": "sheets", "tool": "workbook_used_range", "args": {"item": contract["current_workbook"]}},
            ]
        )
    elif "capacity" in slug or "workcenter" in slug:
        reads.extend(
            [
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.workcenter"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.production"}},
            ]
        )
    elif "subassembl" in slug or "shared-component" in slug:
        reads.extend(
            [
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.bom.line"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.production"}},
            ]
        )
    elif "buy-only" in slug:
        reads.extend(
            [
                {"server": "odoo", "tool": "fields_get", "args": {"model": "product.supplierinfo"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "purchase.order"}},
            ]
        )
    elif "manufacture-only" in slug:
        reads.extend(
            [
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.bom"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.workcenter"}},
                {"server": "odoo", "tool": "fields_get", "args": {"model": "mrp.production"}},
            ]
        )
    return reads


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
    """Seed independent current/stale evidence and one open D365 decision work item."""

    spec = decision_spec(entry["source_task"])
    contract = case_contract(entry, world_now)
    model = control_model_for(entry, contract)
    profile = model.profile
    identifiers = list(dict.fromkeys(_argument_tokens([step.get("args", {}) for step in source_walk])))
    identifiers = identifiers[:12] or [entry["task_id"], entry["family"]]
    identity_text = ", ".join(identifiers)
    wrong_code = _wrong_decision_code(spec)
    verb = profile.proceed_verb
    factory_job = entry["family"] == "erpbench"
    decision_control_title = (
        "Production planning decision control"
        if factory_job
        else f"{entry['family'].replace('_', ' ').title()} decision control"
    )
    internal_window_name = (
        "production planning window" if factory_job else "close calendar"
    )
    binding_window_name = (
        "factory release window" if factory_job else "posting window"
    )
    excluded_examples = (
        "unqualified, late, capacity-constrained, or double-booked supply"
        if factory_job
        else "disputed, out-of-period, or duplicate references"
    )
    exception_approver = "Plant VP" if factory_job else "CFO"
    controls_team = "Operations Control" if factory_job else "Finance Controls"
    work_item_owner = "supply-planning" if factory_job else "finance-operations"
    operating_team = "Supply Planning" if factory_job else "Finance Operations"
    operating_inbox = (
        "supply-planning@contoso-sim.example"
        if factory_job
        else "finance-ops@contoso-sim.example"
    )
    approver_address = (
        "plant-controller@contoso-sim.example"
        if factory_job
        else "controller@contoso-sim.example"
    )
    options_by_id = {option["id"]: option for option in model.options}
    proceed_cost = options_by_id[OPTION_PROCEED]["incremental_cost"]
    hold_cost = options_by_id[OPTION_HOLD]["incremental_cost"]
    binding_description = (
        f"{model.binding_constraint_label} on {model.binding_constraint_date}"
        if factory_job
        else f"the {binding_window_name} when proceeding"
    )
    proceed_timing = (
        f"on {options_by_id[OPTION_PROCEED]['outcome']} after the source-supported material, routing, and capacity path"
        if factory_job
        else f"after the {internal_window_name}'s standard lead time"
    )
    hold_timing = (
        f"then use the feasible delayed plan finishing {options_by_id[OPTION_HOLD]['outcome']}"
        if factory_job
        else f"then {verb} the full scope after the standard lead time"
    )
    exception_timing = (
        f"target {options_by_id[OPTION_EXCEPTION]['outcome']} through the task-specific expedited route"
        if factory_job
        else f"{verb} the full scope after the {internal_window_name}'s exception lead time"
    )
    current_policy = f"""> SIMULATION ONLY
# {decision_control_title}

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
in-scope DecisionScopeLines records ({profile.control_basis}). Listed support counts
only while the current evidence register marks the row `supported`; rows marked
`excluded` ({excluded_examples}) never count, and the
counterparty's own correspondence must corroborate which references are excluded.
The exception is the requirement less usable support. Tolerance under this revision
is {model.tolerance_pct}% of the requirement.

## Timing options

- `{OPTION_PROCEED}`: {verb} the supported scope {proceed_timing}. Supported, and within
  {model.approval_request_id} authority, only while the
  exception is within tolerance; source-supported incremental cost USD {proceed_cost:,.2f}.
- `{OPTION_HOLD}`: wait for the counterparty's committed correction date, {hold_timing}.
  Always within authority; its incremental cost
  is the counterparty's documented holding charge of USD {hold_cost:,.2f}.
- `{OPTION_EXCEPTION}`: {exception_timing}. Requires a {exception_approver} exception
  approval beyond current authority and the exception
  levy of USD {model.exception_levy_cents / 100:,.2f}; it must never be executed while its
  request is pending.

Select `{OPTION_PROCEED}` when the exception is within tolerance; otherwise select
`{OPTION_HOLD}`. The binding constraint is {binding_description} and the
counterparty's committed date when holding. Compare the selected outcome date with the
requester's documented need-by date: ON_TIME on or before it, otherwise LATE. Lead times
count calendar days from the world date.

## Decision record

The DecisionWorkItems rationale must name the selected option id, its outcome date and the
binding constraint date, and cite the five immutable evidence identifiers listed on the
scope approval, including the approved Dynamics approval request. The case must be read
back after the governed Dynamics action, and the Controls completion note must carry the
same option id, outcome date and binding constraint date.
"""
    close_calendar = f"""> SIMULATION ONLY
# March 2026 {internal_window_name}

Revision: {contract['internal_window_revision']}
Effective: 2026-03-01
Scope: {contract['case_id']}
World date: {world_now[:10]}

- The {binding_window_name} for the {contract['case_id']} scope closes on {model.posting_window_close}.
- Standard processing lead time: {model.standard_lead_days} calendar day(s) from the decision date.
- Exception processing lead time: {model.exception_lead_days} calendar day(s), available only
  under an approved {exception_approver} exception.
- Items decided after the {binding_window_name} roll into the next operating cycle and require a new review.
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
# {controls_team} decision handoff standard

Revision: HANDOFF-2026.02
For {contract['case_id']}, {controls_team} requires the decision code, the key numerical or
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
        (contract["close_calendar_id"], f"{contract['case_id']} {internal_window_name}", "calendar", contract["internal_window_revision"], "2026-03-01", close_calendar),
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
        f"Scope approval for {contract['case_id']}: {operating_team} may record one supported "
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
        f"This message was retained for history and was not approved for the March {internal_window_name}."
    )
    challenge_body = (
        f"Controls challenge on {contract['case_id']}: show how the selected source date, identity, and "
        f"governing revision support the result. The review focus is: {spec.analysis_route}"
    )
    messages = [
        (contract["request_email_id"], "inbox", "requester@contoso-sim.example", operating_inbox, f"{contract['case_id']} request", "2026-03-02T08:05:00Z", request_body, None, None),
        (contract["approval_email_id"], "inbox", approver_address, operating_inbox, f"{contract['case_id']} scope approval", "2026-03-02T08:28:00Z", approval_body, f"{contract['case_id']}-approval.txt", approval_body),
        (contract["operations_email_id"], "inbox", "operations@contoso-sim.example", operating_inbox, f"{contract['case_id']} current operations", "2026-03-02T08:42:00Z", operations_body, None, None),
        (contract["counterparty_email_id"], "inbox", profile.party_address, operating_inbox, f"{contract['case_id']} {profile.correction_noun} timing", "2026-03-02T08:55:00Z", counterparty_body, None, None),
        (contract["stale_email_id"], "inbox", "former-reviewer@contoso-sim.example", operating_inbox, f"{contract['case_id']} prior draft", "2026-02-20T16:10:00Z", stale_body, None, None),
        (contract["challenge_email_id"], "inbox", contract["completion_to"], operating_inbox, f"{contract['case_id']} control challenge", "2026-03-02T09:01:00Z", challenge_body, None, None),
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
        (contract["current_workbook"], controls_team, "2026-03-02T09:05:00Z", f"Current evidence register for {contract['case_id']}", current_rows),
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
            work_item_owner,
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

    factory_job = entry["family"] == "erpbench"
    operating_role = "Supply Planning" if factory_job else "Finance Operations"
    approving_role = "Plant Controller" if factory_job else "Controller"
    exception_role = "Plant VP" if factory_job else "CFO"
    submitter = "supply-planning" if factory_job else "finance-operations"
    approver = (
        "plant-controller@contoso-sim.example"
        if factory_job
        else "controller@contoso-sim.example"
    )
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
            (model.approval_policy_id, "USMF", contract["approval_document_type"], "Supported scope", model.authority_limit, "USD", operating_role, approving_role, None, model.exception_policy_id, 1),
            (model.exception_policy_id, "USMF", contract["exception_document_type"], "Unsupported exception", 0.0, "USD", approving_role, exception_role, None, None, 1),
        ],
    )
    cx.executemany(
        "INSERT OR REPLACE INTO erp_approval_requests(request_id,dataareaid,doc_type,doc_id,amount,currency,submitted_by,submitted_at,note,policy_id,required_role,status,decided_by,decided_at,decision_reason) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                model.approval_request_id, "USMF", contract["approval_document_type"], model.case_id, model.authority_limit, "USD",
                submitter, "2026-03-02T08:20:00Z",
                f"Authority to decide {model.case_id} within the approved scope; unsupported exceptions are not covered",
                model.approval_policy_id, approving_role, "approved", approver,
                "2026-03-02T08:28:00Z", f"Approved within the {model.approval_policy_id} limit",
            ),
            (
                model.exception_request_id, "USMF", contract["exception_document_type"], model.case_id, None, "USD",
                "former-reviewer", "2026-02-20T16:12:00Z",
                f"{exception_role} exception drafted under {SUPERSEDED_REVISION} to act on the unsupported exception; amount to be established",
                model.exception_policy_id, exception_role, "pending", None, None, None,
            ),
        ],
    )
    first_ordinal = int(cx.execute("SELECT COALESCE(MAX(ordinal), 0) FROM answer_schema").fetchone()[0]) + 1
    cx.executemany(
        "INSERT OR REPLACE INTO answer_schema(ordinal,field,type,description) VALUES(?,?,?,?)",
        answer_schema_rows(model, first_ordinal),
    )
    if entry["family"] == "erpbench":
        next_ordinal = first_ordinal + len(CHAIN_ANSWER_FIELDS)
        cx.executemany(
            "INSERT OR REPLACE INTO answer_schema(ordinal,field,type,description) VALUES(?,?,?,?)",
            _erpbench_plan_schema_rows(entry, next_ordinal),
        )


def _context_groups(entry: dict[str, Any], contract: dict[str, Any]) -> list[list[dict[str, Any]]]:
    number = task_number(entry)
    groups: list[list[dict[str, Any]]] = [
        [
            {"server": "erp", "tool": "data_find_entity_type", "args": {"query": "decision work item"}},
            {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": DECISION_ENTITY}},
            {"server": "erp", "tool": "data_find_entities", "args": {"entity": DECISION_ENTITY, "filters": {"case_id": contract["case_id"]}}},
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
        {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": DECISION_LINE_ENTITY}},
        {"server": "erp", "tool": "data_find_entities", "args": {"entity": DECISION_LINE_ENTITY, "filters": {"case_id": contract["case_id"]}}},
        {"server": "erp", "tool": "data_find_entities", "args": {"entity": "ApprovalPolicies", "filters": {"doc_type": contract["approval_document_type"]}}},
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
            {"server": "erp", "tool": "data_find_entity_type", "args": {"query": "decision work item"}},
            {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": DECISION_ENTITY}},
            {"server": "erp", "tool": "data_find_entities", "args": {"entity": DECISION_ENTITY, "filters": {"case_id": contract["case_id"]}}},
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


def _workflow_material_reads(
    entry: dict[str, Any], contract: dict[str, Any]
) -> list[dict[str, Any]]:
    """Task-native discovery paths for the short ERP question sources.

    FinanceBenchmark's source walks often jump straight to one SQL query. A real
    operator first resolves the entity, schema, adjacent control object, and the
    source that can invalidate the apparent answer. These routes are authored by
    employee job; they are not task-number permutations.
    """

    def discover(query: str) -> dict[str, Any]:
        return {"server": "erp", "tool": "data_find_entity_type", "args": {"query": query}}

    def metadata(entity: str) -> dict[str, Any]:
        return {"server": "erp", "tool": "data_get_entity_metadata", "args": {"entity": entity}}

    def actions(query: str) -> dict[str, Any]:
        return {"server": "erp", "tool": "api_find_actions", "args": {"query": query}}

    identity = {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["identity_id"]}}
    exception = {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["exception_id"]}}
    handoff = {"server": "docs", "tool": "get_document", "args": {"doc_id": contract["handoff_id"]}}
    challenge = {"server": "email", "tool": "messages_get", "args": {"id": contract["challenge_email_id"]}}
    counterparty = {"server": "email", "tool": "messages_get", "args": {"id": contract["counterparty_email_id"]}}
    labels = {"server": "email", "tool": "labels_list", "args": {}}
    worksheets = {"server": "sheets", "tool": "workbook_worksheets", "args": {"item": contract["current_workbook"]}}
    drive = {"server": "sheets", "tool": "list_drive_items", "args": {}}

    authored_routes: dict[str, list[dict[str, Any]]] = {
        "close_mgmt/subledger-tieout-feb": [
            metadata("CustomerTransactions"),
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": "CESP-close-recon-2026-02.xlsx"}},
            metadata("VendorTransactions"),
            {"server": "sheets", "tool": "workbook_worksheets", "args": {"item": "CESP-close-recon-2026-02.xlsx"}},
            metadata("MainAccounts"), handoff,
        ],
        "expense_audit/te-sample-feb": [
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": "policy--travel-and-expense"}},
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": "expense-export-2026-02.xlsx"}},
            {"server": "sheets", "tool": "workbook_worksheets", "args": {"item": "expense-export-2026-02.xlsx"}},
            challenge, identity,
        ],
        "expense_audit/threshold-shaving-h1": [
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": "policy--expense-audit-detectors"}},
            challenge, metadata("ApprovalPolicies"), exception,
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": "expense-extract-6mo.xlsx"}},
            {"server": "sheets", "tool": "workbook_worksheets", "args": {"item": "expense-extract-6mo.xlsx"}},
            labels,
        ],
        "pbc/sampling-projection-q1": [
            drive,
            {"server": "sheets", "tool": "get_drive_item", "args": {"item": "audit-sample-results-q1.xlsx"}},
            {"server": "docs", "tool": "get_document_metadata", "args": {"doc_id": "sop--audit-sampling-method"}},
            metadata("FiscalPeriods"), handoff,
            {"server": "sheets", "tool": "workbook_worksheets", "args": {"item": "audit-sample-results-q1.xlsx"}},
        ],
    }
    if entry["family"] != "erp_qa_fb":
        return deepcopy(authored_routes.get(entry["source_task"], []))

    routes: dict[str, list[dict[str, Any]]] = {
        "erp_qa_fb/aged-balance-12": [
            discover("customer aging transactions and snapshot"), metadata("CustomerTransactions"),
            metadata("AgedBalancesSnapshot"), worksheets, metadata("Customers"), challenge,
        ],
        "erp_qa_fb/ap-invoices-1": [
            {"server": "erp", "tool": "form_find_menu_item", "args": {"query": "vendor invoices"}},
            actions("vendor invoice approval"), discover("vendor invoice approval queue"),
            metadata("VendorTransactions"), metadata("ApprovalRequests"), challenge,
            metadata("FiscalPeriods"), labels, exception,
        ],
        "erp_qa_fb/ap-invoices-5": [
            metadata("Vendors"), discover("purchase order receipt invoice match"),
            metadata("PurchaseOrders"), metadata("ProductReceipts"), worksheets, identity,
        ],
        "erp_qa_fb/ap-payments-1": [
            metadata("MethodsOfPayment"), identity, discover("vendor payment method bank account mapping"),
            metadata("BankAccounts"), handoff, labels,
        ],
        "erp_qa_fb/ap-payments-2": [
            actions("vendor payment run proposal"), metadata("PaymentRuns"), worksheets,
            metadata("PaymentRunLines"), discover("payment proposal vendor invoices"), challenge,
        ],
        "erp_qa_fb/ap-purchase-orders-1": [
            discover("supplier open purchase orders and receipts"), metadata("PurchaseOrders"),
            counterparty, metadata("ProductReceipts"), metadata("Vendors"), identity,
        ],
        "erp_qa_fb/cash-collections-1": [
            metadata("CustomerTransactions"), metadata("CustomerSettlements"), counterparty,
            discover("posted customer cash collections fiscal year"), metadata("FiscalPeriods"), worksheets,
        ],
        "erp_qa_fb/cash-disocunts-1": [
            discover("customer settlement cash discount timing"), metadata("CustomerSettlements"),
            metadata("CashDiscounts"), identity, metadata("Customers"), counterparty,
        ],
        "erp_qa_fb/collections-1": [
            metadata("CollectionPools"), metadata("CustomerPools"), actions("collections pool assignment"),
            discover("customers with open receivables and no collection owner"), metadata("Customers"), exception,
        ],
        "erp_qa_fb/collections-tasks-2": [
            actions("collections agent dated worklist"), discover("collections activities due by date"),
            metadata("Activities"), drive, metadata("Customers"), metadata("CustomerPools"),
            counterparty, handoff,
        ],
        "erp_qa_fb/credit-limit-3": [
            metadata("Customers"), worksheets, metadata("CustomerTransactions"),
            discover("customer group credit exposure above limit"), challenge, identity,
        ],
        "erp_qa_fb/credit-notes-1": [
            discover("unapplied customer credit notes"), metadata("CustomerTransactions"),
            counterparty, metadata("CustomerSettlements"), drive, exception,
        ],
        "erp_qa_fb/credit-rating-1": [
            metadata("Customers"), identity, discover("customer credit rating and hold"),
            worksheets, metadata("ApprovalRequests"), labels,
        ],
        "erp_qa_fb/customer-setup-1": [
            metadata("Customers"), metadata("PaymentTerms"), handoff,
            discover("customer payment terms effective setup"), drive, identity,
        ],
        "erp_qa_fb/customer-setup-6": [
            discover("customer group membership by legal entity"), metadata("Companies"),
            worksheets, metadata("Customers"), identity, challenge,
        ],
        "erp_qa_fb/discounts-1": [
            metadata("DeductionReasons"), discover("open customer deductions and owners"),
            metadata("CustomerTransactions"), actions("collections deduction disposition"),
            metadata("Activities"), exception,
        ],
        "erp_qa_fb/dispute-1": [
            challenge, metadata("CustomerTransactions"), discover("customer disputed transactions and cases"),
            metadata("Activities"), metadata("ApprovalRequests"), exception,
        ],
        "erp_qa_fb/invoicing-history-3": [
            metadata("ExchangeRates"), metadata("CustomerTransactions"), worksheets,
            discover("largest posted customer invoice common currency"), metadata("Companies"), identity,
        ],
        "erp_qa_fb/other-2": [
            discover("supplier fiscal year posted spend and credits"), metadata("Vendors"),
            metadata("VendorTransactions"), metadata("FiscalPeriods"), drive, metadata("ExchangeRates"),
        ],
        "erp_qa_fb/payment-history-1": [
            metadata("CustomerTransactions"), counterparty, metadata("CustomerSettlements"),
            discover("largest posted customer payment and settlement"), worksheets, metadata("ExchangeRates"),
        ],
        "erp_qa_fb/sales-orders-1": [
            actions("release blocked sales order"), metadata("SalesOrders"), exception,
            discover("sales orders do not process hold"), metadata("Customers"), challenge,
        ],
        "erp_qa_fb/vendor-balance-4": [
            metadata("Vendors"), metadata("ExchangeRates"), worksheets,
            metadata("VendorTransactions"), discover("open AP liability by vendor group"), metadata("Companies"),
        ],
        "erp_qa_fb/vendors-3": [
            discover("vendors on effective payment hold"), metadata("Vendors"), actions("vendor payment hold"),
            metadata("VendorTransactions"), challenge, metadata("ApprovalRequests"), exception,
        ],
    }
    try:
        return deepcopy(routes[entry["source_task"]])
    except KeyError as error:
        raise KeyError(f"no task-native ERP evidence route for {entry['source_task']}") from error


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
        _erpbench_material_reads(entry, source_walk, contract)
        if entry["family"] == "erpbench"
        else []
    )
    workflow_reads = _workflow_material_reads(entry, contract)
    base_call_keys = {
        json.dumps(_call_selector(step), separators=(",", ":"), sort_keys=True)
        for step in base
    }
    context_call_keys = {
        json.dumps(_call_selector(step), separators=(",", ":"), sort_keys=True)
        for step in context_reads
    }
    extra_workflow_reads = [
        step
        for step in _unique_calls(workflow_reads)
        if json.dumps(_call_selector(step), separators=(",", ":"), sort_keys=True)
        not in base_call_keys | context_call_keys
    ]
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
    plan_answers = (
        _erpbench_plan_facts(entry)["answers"]
        if entry["family"] == "erpbench"
        else {}
    )
    submit["args"]["answers"] = {
        **(submit["args"].get("answers") or {}),
        **model.answers,
        **plan_answers,
    }
    decide = {
        "server": "erp",
        "tool": "api_invoke_action",
        "args": {
            "action": DECISION_ACTION,
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
        "args": {"entity": DECISION_ENTITY, "filters": {"case_id": contract["case_id"]}},
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
        {"server": "erp", "tool": "api_find_actions", "args": {"query": "decision work item"}},
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
        *extra_workflow_reads,
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
        _unique_calls([*extra_workflow_reads, *extra_source_reads, *source_reads]),
    )
    material_groups = {**fixed_groups, "source_systems": material_source}
    required_context = _unique_calls(
        [step for steps in material_groups.values() for step in steps]
    )
    reference_context = _unique_calls(
        [*context_reads, *extra_workflow_reads, *extra_source_reads, *source_reads]
    )
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
                *extra_workflow_reads,
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
        "args": {"action": DECISION_ACTION},
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
        "state_readback_call": {"server": "erp", "tool": "data_find_entities", "args": {"entity": DECISION_ENTITY, "filters": {"case_id": contract["case_id"]}}},
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
    if entry["family"] == "erpbench":
        checks["answer_checks"].extend(_erpbench_plan_answer_checks(entry))
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
            "name": "material_before_decision_work_item",
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
                "name": "decision_work_item_readback",
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
    escaped_to = contract["completion_to"].replace("'", "''")
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
            {"type": "sql", "name": "decision_work_item_decided", "expect": "decided", "sql": f"SELECT status FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "sql", "name": "decision_work_item_exact_decision", "expect": spec.decision_code, "sql": f"SELECT decision_code FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "sql", "name": "decision_work_item_evidence_refs", "expect": expected_refs, "sql": f"SELECT evidence_refs FROM erp_finance_cases WHERE case_id='{escaped_case}' AND decision_code='{escaped_code}'"},
            {"type": "sql", "name": "decision_work_item_selected_option", "expect": 1, "sql": f"SELECT CASE WHEN {decision_predicate} THEN 1 ELSE 0 END FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "row_count", "name": "one_decision_work_item_audit", "expect": 1, "sql": f"SELECT COUNT(*) FROM erp_audit_trail WHERE entity_type='DecisionWorkItem' AND entity_id='{escaped_case}' AND action='decide'"},
            {"type": "sql", "name": "exception_request_untouched", "expect": "pending", "sql": f"SELECT status FROM erp_approval_requests WHERE request_id='{escaped_exception_request}'"},
            {
                "type": "row_count",
                "name": "one_completion_email",
                "expect": 1,
                "sql": (
                    "SELECT COUNT(*) FROM email_messages "
                    f"WHERE folder='sent' AND to_addr='{escaped_to}' AND subject='{escaped_subject}' "
                    f"AND body LIKE '%{escaped_case}%' AND body LIKE '%{escaped_code}%' "
                    f"AND body LIKE '%{escaped_option}%' AND body LIKE '%{escaped_outcome}%' "
                    f"AND body LIKE '%{escaped_binding}%' "
                    "AND (length(trim(body)) - length(replace(trim(body), ' ', ''))) >= 29 "
                    "AND ((length(body) - length(replace(body, '.', ''))) "
                    "+ (length(body) - length(replace(body, ';', ''))) "
                    "+ (length(body) - length(replace(body, ':', '')))) >= 2 "
                    "AND ltrim(body) NOT LIKE '{%' AND ltrim(body) NOT LIKE '[%'"
                ),
            },
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
    factory_job = entry["family"] == "erpbench"
    internal_window_name = (
        "production planning window" if factory_job else "close calendar"
    )
    binding_window_name = (
        "factory release window" if factory_job else "posting window"
    )
    exception_approver = "Plant VP" if factory_job else "CFO"
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

    add("investigation", "case-identity", f"Resolve immutable work item {contract['case_id']} and its scoped subject before combining records.", f"required_calls + {DECISION_ENTITY} filter")
    add("investigation", "operative-authority", f"Identify {CONTEXT_REVISION} as operative and treat {SUPERSEDED_REVISION} as historical evidence only.", "exact policy metadata and full-document reads")
    add("investigation", "causal-route", spec.analysis_route, "source-system reads before the governed write")
    add("investigation", "approval-independent", "Open the independent scope approval; it authorizes the work but does not supply the outcome.", "exact Gmail message and attachment reads")
    add("investigation", "current-versus-stale", "Compare the current evidence register with the retained prior tracker instead of trusting either display in isolation.", "exact Graph workbook reads")

    # Spell out the causal investigation an experienced finance operator must
    # perform.  These are not checklist prose: every line is tied to one exact,
    # successful, pre-write MCP request in the executable verifier contract.
    require_call(
        "evidence",
        "discover-decision-work-item-surface",
        "Discover the ERP entity that owns decision work items before assuming which table or record shape contains the case.",
        "erp",
        "data_find_entity_type",
        {"query": "decision work item"},
    )
    require_call(
        "evidence",
        "interpret-decision-work-item-schema",
        "Inspect the DecisionWorkItems metadata so status, decision, evidence-reference, and ownership fields are interpreted from the live schema.",
        "erp",
        "data_get_entity_metadata",
        {"entity": DECISION_ENTITY},
    )
    require_call(
        "evidence",
        "resolve-exact-open-case",
        f"Read the exact immutable case row for {contract['case_id']} and use its current subject and status as the scope anchor.",
        "erp",
        "data_find_entities",
        {"entity": DECISION_ENTITY, "filters": {"case_id": contract["case_id"]}},
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
        "interpret-decision-scope-schema",
        "Inspect the DecisionScopeLines metadata so the in-scope documents or commitments and their amounts are read from the live schema rather than assumed.",
        "erp",
        "data_get_entity_metadata",
        {"entity": DECISION_LINE_ENTITY},
    )
    require_call(
        "correlation",
        "derive-control-requirement",
        f"Read the in-scope DecisionScopeLines for {contract['case_id']} and derive the control requirement by summing their amounts; the FY2025 look-alike {contract['decoy_case_id']} stays out of scope.",
        "erp",
        "data_find_entities",
        {"entity": DECISION_LINE_ENTITY, "filters": {"case_id": contract["case_id"]}},
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
        f"Read {contract['close_calendar_id']} for the {binding_window_name} and the standard and exception lead times that shape every timing option.",
        "docs",
        "get_document",
        {"doc_id": contract["close_calendar_id"]},
    )
    require_call(
        "internal",
        "document-business-need-date",
        f"Open the request {contract['request_email_id']} and use the requester's documented need-by date as the control date, not the {internal_window_name} or the world date.",
        "email",
        "messages_get",
        {"id": contract["request_email_id"]},
    )
    require_call(
        "authority",
        "apply-approval-policy",
        f"Read the {contract['approval_document_type']} approval policies to establish the authority limit and the separate {exception_approver} exception policy.",
        "erp",
        "data_find_entities",
        {"entity": "ApprovalPolicies", "filters": {"doc_type": contract["approval_document_type"]}},
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
    add("correlation", "requirement-derivation", "Derive the control requirement from the in-scope DecisionScopeLines amounts instead of reading a header or the approval amount.", "answer check control_requirement_usd")
    add("correlation", "coverage-reconciliation", "Grade observed support, the excluded portion corroborated by the counterparty, and the usable remainder as separate values.", "answer checks observed_support_usd, excluded_support_usd, usable_support_usd")
    add("correlation", "exception-tolerance", f"Net usable support against the requirement into the exception and test it against the {model.tolerance_pct}% tolerance.", "answer checks exception_usd, exception_within_tolerance")
    add("external", "counterparty-date", "Carry the counterparty's committed correction date from its own message into the timing options.", "answer check external_constraint_date")
    add("internal", "posting-window", f"Carry the {internal_window_name}'s {binding_window_name} into the binding constraint.", "answer check posting_window_close_date")
    add("decision", "supported-condition", spec.supported_condition, "exact authored decision and final state")
    add("decision", "reject-shortcut", f"Reject the unsupported branch: {spec.rejected_shortcut}", "wrong-branch negative control")
    add("decision", "exact-code", f"Select `{spec.decision_code}` only after the evidence intersection supports it.", "DecisionWorkItems decision_code assertion")
    add("decision", "alternatives-costed", f"Weigh `{OPTION_PROCEED}`, `{OPTION_HOLD}` and `{OPTION_EXCEPTION}`, each with an exact outcome date, incremental cost and authority status.", "answer checks for every option outcome date; decision options with outcome, incremental_cost and authority_status")
    add("decision", "recommended-option", f"Select `{model.recommended_option}` with outcome {model.recommended_outcome} and its documented incremental cost.", "answer checks recommended_option, recommended_outcome_date, recommended_incremental_cost_usd; DecisionWorkItems rationale assertion")
    add("decision", "control-date-variance", f"Compare the selected outcome with the documented {model.business_need_date} need-by date into a signed day variance and an honest {model.timing_status} status.", "answer checks business_need_date, outcome_vs_control_days, decision_timing_status")
    add("authority", "approval-applied", f"Apply {model.approval_request_id} and its authority limit to the selected scope; the exception option stays flagged as requiring approval beyond current authority.", "answer checks approval_request_id, approval_authority_limit_usd, escalation_approval_required")
    add("authority", "exception-not-executed", f"Leave {model.exception_request_id} pending; the unauthorized alternative is never executed.", "exception_request_untouched state assertion")
    for check in checks.get("answer_checks", []):
        add("answer", check["field"], f"File the task-specific `{check['field']}` conclusion in the discovered reporting schema using its declared type and scale.", f"deterministic answer check: {check.get('type', 'string')}")
    add("state", "governed-transition", f"Use the Dynamics generic action surface to move only {contract['case_id']} from open to decided.", "exact SQL pre/post state")
    add("state", "evidence-refs", "Persist the exact five independently sourced immutable references with the case decision.", "exact serialized evidence_refs assertion")
    add("state", "selected-option-recorded", "Persist the selected option id, its outcome date and the binding constraint date in the work-item rationale.", "DecisionWorkItems rationale assertion")
    add("state", "audit-row", "Produce exactly one Dynamics audit event for the case transition.", "row-count assertion")
    add("state", "completion-message", "Send exactly one scoped Controls handoff naming the case, the supported decision, the selected option, its outcome date and the binding constraint.", "Gmail sent-state body assertion")
    add("procedure", "read-before-write", "Complete all required context reads before recording the case decision.", "reads_before_write")
    add("procedure", "case-readback", "Read the exact DecisionWorkItems record after the decision action.", "post_write_readback")
    add("procedure", "message-readback", "Reopen the exact completion thread after sending it.", "post_write_readback")
    add("procedure", "successful-calls", "Required evidence calls must succeed; failed lookups do not count as investigation.", "successful_required_calls")
    add("containment", "write-scope", "Preserve every table outside the source task's authorized mutations, the decision work item, its audit row, the completion email, and the reporting row.", "writes_only initial-state diff")
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
    """Group every deterministic check into 16 task-specific employee outcomes."""

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
    causal_answer_fields = set(CHAIN_FIELDS["H2"] + CHAIN_FIELDS["H3"] + CHAIN_FIELDS["H4"] + CHAIN_FIELDS["H5"])
    control_date_fields = set(CHAIN_FIELDS["H6"] + CHAIN_FIELDS["H9"] + CHAIN_FIELDS["H12"])
    option_answer_fields = set(CHAIN_FIELDS["H7"] + CHAIN_FIELDS["H8"] + CHAIN_FIELDS["H10"])
    for row in atomic:
        source = row["source"]
        name = row["name"]
        check_type = row["type"]
        target: str | None = None
        if source == "answer":
            if name in CHAIN_FIELDS["H1"]:
                target = "investigation.scope"
            elif name in causal_answer_fields:
                target = "analysis.operating_plan"
            elif name in control_date_fields:
                target = "analysis.operating_plan"
            elif name in option_answer_fields:
                target = "decision.options"
            else:
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
            elif name == "material_source_systems_successful":
                target = "analysis.task_native_reasoning"
            elif name == "material_control_model":
                target = "analysis.operating_plan"
            elif name in {"material_external_constraint", "material_external_constraint_successful"}:
                target = "analysis.operating_plan"
            elif name.endswith("_successful"):
                if name in {"material_scope_successful"}:
                    target = "investigation.scope"
                elif name in {"material_authority_successful", "material_approval_successful"}:
                    target = "investigation.authority"
                elif name == "material_current_state_successful":
                    target = "investigation.current_state"
                else:
                    target = "analysis.operating_plan"
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
                target = "analysis.task_native_reasoning"
        elif source == "state":
            if check_type == "writes_only":
                target = "containment.scope"
            elif name == "decision_work_item_exact_decision":
                target = "decision.supported_path"
            elif name == "decision_work_item_selected_option":
                target = "decision.options"
            elif name == "exception_request_untouched":
                target = "containment.scope"
            elif name == "decision_work_item_decided":
                target = "state.case"
            elif name == "decision_work_item_evidence_refs":
                case_evidence_id = row["id"]
            elif name == "one_decision_work_item_audit":
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
    answer_fields = [
        row["name"] for row in atomic if row["source"] == "answer"
    ]
    task_answer_fields = [
        field for field in answer_fields if field not in CHAIN_ANSWER_FIELDS
    ]
    task_answer_checks = [
        deepcopy(check)
        for check in checks.get("answer_checks", [])
        if check.get("field") in task_answer_fields
    ]
    wrapper_state_names = {
        "decision_work_item_decided",
        "decision_work_item_exact_decision",
        "decision_work_item_evidence_refs",
        "decision_work_item_selected_option",
        "one_decision_work_item_audit",
        "exception_request_untouched",
        "one_completion_email",
    }
    task_state_checks = [
        deepcopy(check)
        for check in checks.get("state_checks", [])
        if check.get("type") != "writes_only"
        and check.get("name") not in wrapper_state_names
    ]
    mutation_surfaces: list[dict[str, str]] = []
    for step in source_mutations:
        arguments = step.get("args") or {}
        surface = {
            "server": str(step["server"]),
            "tool": str(step["tool"]),
            **(
                {"model": str(arguments["model"])}
                if arguments.get("model")
                else {}
            ),
            **(
                {"action": str(arguments["action"])}
                if arguments.get("action")
                else {}
            ),
        }
        if surface not in mutation_surfaces:
            mutation_surfaces.append(surface)
    operational_outcomes = [
        check_by_id[check_id]["name"].replace("_", " ")
        for check_id in original_state
    ]
    source_read_count = len(
        trace_contract["material_context_groups"]["source_systems"]
    )
    readback_count = len(trace_contract["source_postwrite_contracts"]) + 2
    descriptions = {
        "investigation.scope": (
            f"Identify the live work item behind “{spec.employee_question}” by immutable subject and scope, and keep similarly named historical records out of the analysis."
        ),
        "investigation.authority": (
            f"Determine that {CONTEXT_REVISION} and the independent scope approval govern this work; recognize {SUPERSEDED_REVISION} as retained history rather than silently applying it."
        ),
        "investigation.current_state": (
            "Compare the current operations message and evidence register with their stale counterparts, resolving conflicts by immutable IDs, effective dates, and modified timestamps."
        ),
        "investigation.source_systems": (
            f"Use the {source_read_count} exact task-native evidence reads needed to {spec.analysis_route[0].lower() + spec.analysis_route[1:]}"
        ),
        "analysis.task_native_reasoning": (
            f"Work through the job's actual causal chain: {spec.analysis_route} "
            f"Show from successful task-native reads whether {spec.supported_condition[0].lower() + spec.supported_condition[1:]} "
            f"Do not substitute this shortcut: {spec.rejected_shortcut}"
        ),
        "analysis.operating_plan": (
            f"Reconcile the requester's {model.business_need_date} need-by date, the counterparty's {model.external_date} correction date, and the {model.posting_window_close} internal window. "
            f"Derive the in-scope {model.profile.scope_noun}, usable {model.profile.support_noun}, exception, signed timing variance, and the constraint that actually determines each feasible outcome."
        ),
        "decision.supported_path": (
            f"Select `{spec.decision_code}` only because the evidence supports the authored condition. Explicitly reject this tempting shortcut: {spec.rejected_shortcut}"
        ),
        "decision.options": (
            f"Compare acting within authority, waiting for the documented correction, and requesting an exception. Preserve each option's outcome date, incremental cost, and authority status; choose `{model.recommended_option}` for {model.recommended_outcome}, bound by {model.binding_constraint_label}."
        ),
        "state.operational": (
            (
                f"Carry the supported {entry['family']} result through {len(source_mutations)} scoped task-native writes and leave these independently checked outcomes: {', '.join(operational_outcomes)}."
                if source_mutations
                else f"Preserve the read-only source systems while materializing the supported {entry['family']} disposition; the checked outcome is {', '.join(operational_outcomes) or 'the exact evidence-linked case result'}."
            )
        ),
        "state.case": (
            "Create exactly one source-audited DecisionWorkItems transition from open to decided, carrying the supported decision, selected option, rationale, and the five independently resolved evidence references."
        ),
        "state.collaboration": (
            "Send only the task-native communication the job requires, plus one concise Controls handoff that states the supported result, timing, constraint, and provenance."
        ),
        "verification.outcome": (
            "Verify that the task-native final state matches the derived result and that exactly one governed audit event records the case transition."
        ),
        "verification.readback": (
            f"After writing, perform all {readback_count} provider-native readbacks, including the exact case row and reopened completion thread, before claiming success."
        ),
        "containment.scope": (
            "Keep every change inside the selected task records, case, audit event, completion message, and reporting row. Leave the unapproved exception pending and every neighboring record unchanged."
        ),
        "answer.insights": (
            f"Return the task's exact employee-facing conclusions ({', '.join(task_answer_fields)}) together with the supported amounts, dates, alternative, cost, authority, and timing variance, using the declared units and scope."
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
    milestone_details = {
        "investigation.source_systems": {
            "expected_investigation": spec.analysis_route,
        },
        "analysis.task_native_reasoning": {
            "reasoning_path": spec.analysis_route,
            "success_condition": spec.supported_condition,
            "rejected_shortcut": spec.rejected_shortcut,
        },
        "analysis.operating_plan": {
            "need_by_date": model.business_need_date,
            "external_constraint_date": model.external_date,
            "internal_window_close": model.posting_window_close,
        },
        "decision.supported_path": {
            "decision_code": spec.decision_code,
            "rejected_shortcut": spec.rejected_shortcut,
        },
        "decision.options": {
            "options": [
                {
                    "id": option["id"],
                    "outcome": option["outcome"],
                    "incremental_cost": option["incremental_cost"],
                    "authority_status": option["authority_status"],
                    "selected": option["selected"],
                }
                for option in model.options
            ],
        },
        "state.operational": {
            "checked_outcomes": operational_outcomes,
            "task_native_write_count": len(source_mutations),
            "task_native_mutation_surfaces": mutation_surfaces,
            "deterministic_state_contract": task_state_checks,
        },
        "answer.insights": {
            "expected_answer_fields": task_answer_fields,
            "deterministic_answer_contract": task_answer_checks,
        },
    }
    task_native_points = sum(
        SEMANTIC_MILESTONE_WEIGHTS[milestone]
        for milestone in TASK_NATIVE_MILESTONES
    )
    if task_native_points < MIN_TASK_NATIVE_POINTS:
        raise AssertionError(
            f"task-native rubric weight {task_native_points} is below "
            f"{MIN_TASK_NATIVE_POINTS}"
        )
    return [
        {
            "id": milestone_id,
            "category": milestone_id.split(".", 1)[0],
            "description": descriptions[milestone_id],
            "weight": weight,
            "atomic_check_ids": grouped[milestone_id],
            "atomic_checks": [check_by_id[check_id] for check_id in grouped[milestone_id]],
            "task_native_core": milestone_id in TASK_NATIVE_MILESTONES,
            **milestone_details.get(milestone_id, {}),
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


def _provider_error(value: Any) -> str | None:
    """Return a provider error without treating ordinary evidence fields as errors."""

    if isinstance(value, dict) and value.get("error"):
        error = value["error"]
        if isinstance(error, dict):
            return str(error.get("message") or json.dumps(error, sort_keys=True))
        return str(error)
    return None


def _execute_material_reads(
    database: Path,
    calls: list[dict[str, Any]],
    server_root: Path,
    *,
    task_id: str,
    world_now: str,
    world_role: str,
) -> list[dict[str, Any]]:
    """Execute every material selector on the packaged read-only MCP surface.

    The evidence room therefore contains provider responses from the exact frozen
    world, not SQL summaries that merely resemble what an agent might have seen.
    Expected provider negatives (for example an absent filing concept) are retained
    as affirmative absence evidence only when the contracted error text matches.
    """

    lib_path = str(server_root / "lib")
    servers_path = server_root / "servers"
    if not Path(lib_path).is_dir() or not servers_path.is_dir():
        raise ValueError(f"invalid MCP runtime root: {server_root}")

    environment = {
        "WORLD_DB": str(database),
        "WORLD_NOW": world_now,
        "WORLD_ROLE": world_role,
    }
    previous = {key: os.environ.get(key) for key in (*environment, "TRACE_FILE")}
    loaded_modules: list[str] = []
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="ledgerbench-material-") as temporary:
        environment["TRACE_FILE"] = str(Path(temporary) / "reads.jsonl")
        os.environ.update(environment)
        sys.path.insert(0, lib_path)
        try:
            servers: dict[str, Any] = {}
            for index, call in enumerate(calls, 1):
                server = call["server"]
                if server not in servers:
                    module_path = servers_path / f"{server}_server.py"
                    if not module_path.is_file():
                        raise ValueError(f"missing packaged MCP server: {module_path}")
                    module_name = (
                        f"ledgerbench_asset_{_check_slug(task_id)}_{server}_{index}"
                    )
                    module_spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    module = importlib.util.module_from_spec(module_spec)
                    if module_spec.loader is None:
                        raise ValueError(f"cannot load MCP server: {module_path}")
                    module_spec.loader.exec_module(module)
                    loaded_modules.append(module_name)
                    servers[server] = module.S

                expected_error = str(call.get("expected_error_contains") or "")
                response: Any = None
                observed_error: str | None = None
                try:
                    response = servers[server].call(call["tool"], call.get("args") or {})
                    observed_error = _provider_error(response)
                except Exception as error:  # provider negatives are evidence when exact
                    observed_error = str(error)

                if expected_error:
                    if not observed_error or expected_error.casefold() not in observed_error.casefold():
                        raise ValueError(
                            f"{task_id} material call {index} expected {expected_error!r}, "
                            f"observed {observed_error!r}"
                        )
                    response = {
                        "verified_absence": True,
                        "contracted_error_contains": expected_error,
                        "provider_error": observed_error,
                    }
                elif observed_error:
                    raise ValueError(
                        f"{task_id} material call {index} failed: {observed_error}"
                    )
                results.append(response)
        finally:
            while lib_path in sys.path:
                sys.path.remove(lib_path)
            for module_name in loaded_modules:
                sys.modules.pop(module_name, None)
            sys.modules.pop("framework", None)
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    return results


def write_asset_views(
    root: Path,
    database: Path,
    prompt: str,
    entry: dict[str, Any],
    contract: dict[str, Any],
    trace_contract: dict[str, Any],
    *,
    server_root: Path | None = None,
    world_now: str = WORLD_EPOCH,
    world_role: str = "finance_operations",
) -> list[dict[str, Any]]:
    """Write context plus one exact MCP response per material evidence read."""

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

    def add(
        name: str,
        source: str,
        content: str | bytes,
        *,
        role: str,
        material: bool = False,
        query_scope: dict[str, Any] | None = None,
        material_reason: str | None = None,
    ) -> None:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")
        data = target.read_bytes()
        record = {
            "filename": name,
            "source": source,
            "kind": target.suffix.lstrip("."),
            "evidence_role": role,
            "material": material,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        if material:
            if query_scope is None or not material_reason:
                raise ValueError(f"material asset lacks scope or reason: {name}")
            record["query_scope"] = query_scope
            record["material_reason"] = material_reason
        assets.append(record)

    add("01-employee-request.md", "Teams", prompt + "\n", role="request")
    case = dict(cx.execute("SELECT * FROM erp_finance_cases WHERE case_id=?", (contract["case_id"],)).fetchone())
    case_lines = [
        dict(row)
        for row in cx.execute(
            "SELECT * FROM erp_finance_case_lines WHERE case_id=? ORDER BY line", (contract["case_id"],)
        )
    ]
    add(
        "02-open-decision-work-item.json",
        "Dynamics DecisionWorkItems",
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

    material_calls = trace_contract["required_context_calls"]
    if len(material_calls) < MIN_MATERIAL_ASSETS_PER_TASK:
        raise ValueError(
            f"{entry['task_id']} has only {len(material_calls)} material evidence reads"
        )
    call_groups: dict[str, str] = {}
    for group, calls in trace_contract["material_context_groups"].items():
        for call in calls:
            key = json.dumps(call, separators=(",", ":"), sort_keys=True)
            call_groups[key] = group
    responses = _execute_material_reads(
        database,
        material_calls,
        server_root or (Path(__file__).resolve().parents[2] / "mcp"),
        task_id=entry["task_id"],
        world_now=world_now,
        world_role=world_role,
    )
    group_reasons = {
        "scope": "Resolves the exact live work-item identity and schema before records are correlated.",
        "authority": "Establishes which control revision governs and which retained document is superseded.",
        "approval": "Proves the independent approval scope without using the approval as the answer.",
        "current_state": "Distinguishes current operational evidence from stale look-alike records.",
        "control_model": "Supplies a required input to the amount, tolerance, authority, or control-date derivation.",
        "external_constraint": "Supplies the counterparty-owned date or cost that constrains the feasible options.",
        "source_systems": f"Provides task-native evidence needed to {spec.analysis_route[0].lower() + spec.analysis_route[1:]}",
    }
    for index, (call, response) in enumerate(zip(material_calls, responses), 1):
        key = json.dumps(call, separators=(",", ":"), sort_keys=True)
        group = call_groups.get(key)
        if group is None:
            raise ValueError(f"material call is not assigned to an evidence group: {call}")
        safe_server = _check_slug(call["server"])
        safe_tool = _check_slug(call["tool"])
        expected_absence = bool(call.get("expected_error_contains"))
        payload = {
            "schema_version": "ledgerbench.material-evidence.v1",
            "task_id": entry["task_id"],
            "world_as_of": world_now,
            "provider": call["server"],
            "tool": call["tool"],
            "request": call.get("args") or {},
            "expected_absence": expected_absence,
            "response": response,
            "evidence_group": group,
            "material_reason": group_reasons[group],
        }
        add(
            f"material/{index:02d}-{safe_server}-{safe_tool}.json",
            PROVIDER_MAPPINGS[call["server"]],
            json.dumps(payload, indent=2, default=str, sort_keys=True) + "\n",
            role=f"material-{group}",
            material=True,
            query_scope={
                "server": call["server"],
                "tool": call["tool"],
                "args": call.get("args") or {},
                "expected_error_contains": call.get("expected_error_contains"),
            },
            material_reason=group_reasons[group],
        )

    manifest_rows = [
        {
            "filename": asset["filename"],
            "source": asset["source"],
            "kind": asset["kind"],
            "evidence_role": asset["evidence_role"],
            "material": asset["material"],
            "bytes": asset["bytes"],
            "sha256": asset["sha256"],
            **(
                {
                    "query_scope": asset["query_scope"],
                    "material_reason": asset["material_reason"],
                }
                if asset["material"]
                else {}
            ),
        }
        for asset in assets
    ]
    add(
        "30-agent-visible-asset-manifest.json",
        "Release builder",
        json.dumps(
            {
                "case_id": contract["case_id"],
                "gold_included": False,
                "oracle_walk_included": False,
                "ordering_semantics": False,
                "material_contract": "one executed MCP response for every verifier-required pre-write evidence selector",
                "assets": manifest_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        role="manifest",
    )
    cx.close()
    material_count = sum(bool(asset["material"]) for asset in assets)
    contextual_count = len(assets) - material_count
    if contextual_count != CONTEXTUAL_ASSETS_PER_TASK:
        raise ValueError(
            f"expected {CONTEXTUAL_ASSETS_PER_TASK} contextual assets, wrote {contextual_count}"
        )
    if material_count != len(material_calls):
        raise ValueError(
            f"expected one material asset per required read ({len(material_calls)}), "
            f"wrote {material_count}"
        )
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
