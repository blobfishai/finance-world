"""Causal-realism contract for the LedgerBench-100 v3 release."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sqlite3
import zipfile
from copy import deepcopy
from html import escape
from pathlib import Path
from typing import Any

from decision_specs import DecisionSpec, decision_spec


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


def task_number(entry: dict[str, Any]) -> int:
    match = re.search(r"lgr100-(\d{3})-", entry["task_id"])
    if not match:
        raise ValueError(f"unrecognized task id {entry['task_id']}")
    return int(match.group(1))


def case_contract(entry: dict[str, Any]) -> dict[str, Any]:
    number = task_number(entry)
    case_id = f"FINCASE-{number:03d}"
    prefix = f"lgr-{number:03d}"
    current_book = f"{case_id.lower()}-control-pack.xlsx"
    stale_book = f"{case_id.lower()}-prior-tracker.xlsx"
    subject = f"{case_id} completed — {decision_spec(entry['source_task']).decision_code}"
    thread_id = "t_" + hashlib.sha1(subject.casefold().encode()).hexdigest()[:10]
    return {
        "case_id": case_id,
        "current_policy_id": f"{prefix}-control-current",
        "prior_policy_id": f"{prefix}-control-prior",
        "evidence_map_id": f"{prefix}-evidence-map",
        "handoff_id": f"{prefix}-handoff-standard",
        "identity_id": f"{prefix}-identity-control",
        "exception_id": f"{prefix}-exception-policy",
        "request_email_id": f"em-{prefix}-request",
        "approval_email_id": f"em-{prefix}-approval",
        "operations_email_id": f"em-{prefix}-operations",
        "stale_email_id": f"em-{prefix}-prior",
        "challenge_email_id": f"em-{prefix}-challenge",
        "current_workbook": current_book,
        "stale_workbook": stale_book,
        "completion_to": "finance-controls@contoso-sim.example",
        "completion_subject": subject,
        "completion_thread_id": thread_id,
        "evidence_refs": [
            f"{prefix}-control-current",
            f"em-{prefix}-approval",
            current_book,
            case_id,
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
        "Record the supported disposition on the open finance case and send Controls a concise completion note.",
        "Leave the open finance case in the exact supported state and give Controls an audit-ready handoff.",
        "Update only the scoped finance case, verify what persisted, and close the loop with Controls.",
        "Carry the decision through the governed case record and leave Controls a reproducible completion message.",
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


def seed_case_context(
    database: Path,
    entry: dict[str, Any],
    source_walk: list[dict[str, Any]],
    world_now: str,
) -> dict[str, Any]:
    """Seed independent current/stale evidence and one open D365 finance case."""

    spec = decision_spec(entry["source_task"])
    contract = case_contract(entry)
    identifiers = list(dict.fromkeys(_argument_tokens([step.get("args", {}) for step in source_walk])))
    identifiers = identifiers[:12] or [entry["task_id"], entry["family"]]
    identity_text = ", ".join(identifiers)
    wrong_code = _wrong_decision_code(spec)
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

The decision rationale must cite at least four immutable evidence identifiers and the
case must be read back after the governed Dynamics action.
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
        "The case record is open; use current evidence and preserve any unresolved exception."
    )
    approval_body = (
        f"Scope approval for {contract['case_id']}: Finance Operations may record one supported "
        f"case decision after reconciling identity, authority, operations, and approval evidence. "
        f"Approved evidence anchors are {contract['current_policy_id']}, {contract['current_workbook']}, "
        f"and this message {contract['approval_email_id']}. This approval does not predetermine the outcome."
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
    stale_rows = [
        ["case_id", "source_ref", "evidence_role", "revision", "status", "note"],
        [contract["case_id"], contract["prior_policy_id"], "authority", SUPERSEDED_REVISION, "superseded", spec.rejected_shortcut],
        [contract["case_id"], contract["stale_email_id"], "operations", "2026-02-20", "stale", "historical draft only"],
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
    cx.commit()
    cx.close()
    return contract


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
    ]
    orders = (
        (0, 1, 2, 3), (1, 2, 0, 3), (2, 0, 3, 1),
        (3, 1, 0, 2), (0, 3, 2, 1), (2, 1, 3, 0),
    )
    return [groups[index] for index in orders[(number - 1) % len(orders)]]


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


def reference_walk(
    entry: dict[str, Any],
    source_walk: list[dict[str, Any]],
    contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compose discovery, source investigation, governed write, and readback."""

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
    rationale = f"{spec.supported_condition} {spec.analysis_route}"
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
    walk = [reporting, *context_reads, *base, *tail]
    workflow_slug = entry["source_task"].split("/", 1)[1].replace("-", "_")
    semantic_graph = [
        "discover_reporting_contract",
        f"resolve_{entry['family']}_case_identity",
        "select_effective_control_revision",
        f"correlate_{workflow_slug}_current_operations",
        "verify_independent_scope_approval",
        f"reject_{workflow_slug}_stale_or_single_system_shortcut",
        f"derive_{spec.decision_code.casefold()}",
        "record_governed_dynamics_transition",
        "read_back_exact_case_state",
        "send_and_reopen_completion_thread",
        "file_supported_finance_result",
    ]
    required_context = [
        {"server": step["server"], "tool": step["tool"], "args": step.get("args") or {}}
        for step in context_reads
    ]
    return walk, {
        "required_context_calls": required_context,
        "write_call": {"server": "erp", "tool": "api_invoke_action", "args": {"action": "ContosoFinanceCaseDecide"}},
        "state_readback_call": {"server": "erp", "tool": "data_find_entities", "args": {"entity": "FinanceCases", "filters": {"case_id": contract["case_id"]}}},
        "message_write_call": {"server": "email", "tool": "send_message", "args": {"subject": contract["completion_subject"]}},
        "message_readback_call": {"server": "email", "tool": "threads_get", "args": {"id": contract["completion_thread_id"]}},
        "semantic_action_graph": semantic_graph,
        "base_call_count": len(base),
        "context_call_count": len(context_reads),
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
    checks = deepcopy(checks)
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
    trace_checks.extend(
        [
            {"type": "required_calls", "calls": trace_contract["required_context_calls"]},
            {
                "type": "reads_before_write",
                "reads": trace_contract["required_context_calls"],
                "write": trace_contract["write_call"],
            },
            {
                "type": "post_write_readback",
                "write": trace_contract["write_call"],
                "readback": trace_contract["state_readback_call"],
            },
            {
                "type": "post_write_readback",
                "write": trace_contract["message_write_call"],
                "readback": trace_contract["message_readback_call"],
            },
            {
                "type": "ordered_calls",
                "calls": [
                    trace_contract["write_call"],
                    trace_contract["state_readback_call"],
                    trace_contract["message_write_call"],
                    trace_contract["message_readback_call"],
                    {"server": "harness", "tool": "submit_answer", "args": {}},
                ],
            },
            {"type": "successful_required_calls", "calls": trace_contract["required_context_calls"]},
        ]
    )
    escaped_case = contract["case_id"].replace("'", "''")
    escaped_code = spec.decision_code.replace("'", "''")
    escaped_subject = contract["completion_subject"].replace("'", "''")
    expected_refs = json.dumps(sorted(contract["evidence_refs"]), separators=(",", ":"))
    state_checks = checks.setdefault("state_checks", [])
    state_checks.extend(
        [
            {"type": "sql", "name": "finance_case_decided", "expect": "decided", "sql": f"SELECT status FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "sql", "name": "finance_case_exact_decision", "expect": spec.decision_code, "sql": f"SELECT decision_code FROM erp_finance_cases WHERE case_id='{escaped_case}'"},
            {"type": "sql", "name": "finance_case_evidence_refs", "expect": expected_refs, "sql": f"SELECT evidence_refs FROM erp_finance_cases WHERE case_id='{escaped_case}' AND decision_code='{escaped_code}'"},
            {"type": "row_count", "name": "one_finance_case_audit", "expect": 1, "sql": f"SELECT COUNT(*) FROM erp_audit_trail WHERE entity_type='FinanceCase' AND entity_id='{escaped_case}' AND action='decide'"},
            {"type": "row_count", "name": "one_completion_email", "expect": 1, "sql": f"SELECT COUNT(*) FROM email_messages WHERE folder='sent' AND subject='{escaped_subject}' AND body LIKE '%{escaped_code}%'"},
        ]
    )
    _merge_writes_only(checks, {"answers", "erp_finance_cases", "erp_audit_trail", "email_messages"})
    return checks


def decision_options(entry: dict[str, Any]) -> list[dict[str, Any]]:
    spec = decision_spec(entry["source_task"])
    return [
        {
            "id": spec.decision_code.casefold().replace("_", "-"),
            "label": spec.decision_code.replace("_", " ").title(),
            "selected": True,
            "reason": spec.supported_condition,
        },
        {
            "id": _wrong_decision_code(spec).casefold().replace("_", "-"),
            "label": _wrong_decision_code(spec).replace("_", " ").title(),
            "selected": False,
            "reason": "Use only when the required evidence intersection is incomplete or conflicting.",
        },
        {
            "id": "unsupported-shortcut",
            "label": "Unsupported Shortcut",
            "selected": False,
            "reason": spec.rejected_shortcut,
        },
    ]


def rubric_criteria(
    entry: dict[str, Any],
    checks: dict[str, Any],
    trace_contract: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, str]]:
    """Explain the actual causal test in task-specific workplace language."""

    spec = decision_spec(entry["source_task"])
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
    for server in sorted({call["server"] for call in trace_contract["required_context_calls"]}):
        add("investigation", f"provider-{server}", f"Use the task-scoped {PROVIDER_MAPPINGS[server]} evidence needed for this case.", "successful required provider calls")
    add("decision", "supported-condition", spec.supported_condition, "exact authored decision and final state")
    add("decision", "reject-shortcut", f"Reject the unsupported branch: {spec.rejected_shortcut}", "wrong-branch negative control")
    add("decision", "exact-code", f"Select `{spec.decision_code}` only after the evidence intersection supports it.", "FinanceCases decision_code assertion")
    add("decision", "alternatives", "Keep evidence-insufficient or conflicting alternatives visible rather than forcing a clean answer.", "decision options and state containment")
    for check in checks.get("answer_checks", []):
        add("answer", check["field"], f"File the task-specific `{check['field']}` conclusion in the discovered reporting schema using its declared type and scale.", f"deterministic answer check: {check.get('type', 'string')}")
    add("state", "governed-transition", f"Use the Dynamics generic action surface to move only {contract['case_id']} from open to decided.", "exact SQL pre/post state")
    add("state", "evidence-refs", "Persist the exact four independently sourced immutable references with the case decision.", "exact serialized evidence_refs assertion")
    add("state", "audit-row", "Produce exactly one Dynamics audit event for the case transition.", "row-count assertion")
    add("state", "completion-message", "Send exactly one scoped Controls handoff naming the case and supported decision.", "Gmail sent-state assertion")
    add("procedure", "read-before-write", "Complete all required context reads before recording the case decision.", "reads_before_write")
    add("procedure", "case-readback", "Read the exact FinanceCases record after the decision action.", "post_write_readback")
    add("procedure", "message-readback", "Reopen the exact completion thread after sending it.", "post_write_readback")
    add("procedure", "successful-calls", "Required evidence calls must succeed; failed lookups do not count as investigation.", "successful_required_calls")
    add("containment", "write-scope", "Preserve every table outside the source task's authorized mutations, the finance case, its audit row, the completion email, and the reporting row.", "writes_only initial-state diff")
    if len(criteria) < 40:
        raise ValueError(f"{entry['task_id']} has only {len(criteria)} public criteria")
    return criteria


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
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Evidence" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)
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
) -> list[dict[str, str]]:
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
    assets: list[dict[str, str]] = []

    def add(name: str, source: str, content: str | bytes, *, role: str) -> None:
        target = root / name
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")
        assets.append({"filename": name, "source": source, "kind": target.suffix.lstrip("."), "evidence_role": role})

    add("01-employee-request.md", "Teams", prompt + "\n", role="request")
    case = dict(cx.execute("SELECT * FROM erp_finance_cases WHERE case_id=?", (contract["case_id"],)).fetchone())
    add("02-open-finance-case.json", "Dynamics FinanceCases", json.dumps(case, indent=2, sort_keys=True) + "\n", role="identity")

    doc_ids = [
        contract["current_policy_id"], contract["prior_policy_id"], contract["evidence_map_id"],
        contract["handoff_id"], contract["identity_id"], contract["exception_id"],
    ]
    for index, doc_id in enumerate(doc_ids, 3):
        row = dict(cx.execute("SELECT * FROM docs_documents WHERE doc_id=?", (doc_id,)).fetchone())
        body = f"<!-- doc_id: {doc_id}; version: {row['version']}; effective: {row['effective_date']} -->\n{row['body']}"
        role = "authority" if doc_id in {contract["current_policy_id"], contract["prior_policy_id"]} else "control"
        add(f"{index:02d}-{doc_id}.md", "Governed document library", body + "\n", role=role)

    email_ids = [
        contract["request_email_id"], contract["approval_email_id"], contract["operations_email_id"],
        contract["stale_email_id"], contract["challenge_email_id"],
    ]
    for index, message_id in enumerate(email_ids, 9):
        message = dict(cx.execute("SELECT * FROM email_messages WHERE id=?", (message_id,)).fetchone())
        role = "approval" if message_id == contract["approval_email_id"] else "operations" if message_id == contract["operations_email_id"] else "history"
        add(f"{index:02d}-{message_id}.eml", "Gmail mailbox", _eml(message, contract["case_id"]), role=role)

    for index, workbook in enumerate((contract["current_workbook"], contract["stale_workbook"]), 14):
        rows = [json.loads(row[0]) for row in cx.execute("SELECT cells FROM sheet_rows WHERE file=? ORDER BY row_no", (workbook,))]
        add(f"{index:02d}-{workbook}", "Microsoft Graph workbook", _xlsx(rows), role="current-register" if index == 14 else "stale-register")

    current_policy = cx.execute("SELECT body FROM docs_documents WHERE doc_id=?", (contract["current_policy_id"],)).fetchone()[0]
    add("16-current-control-copy.pdf", "Controlled PDF export", _pdf(f"Case {contract['case_id']}\n{current_policy}"), role="authority")
    add("17-source-analysis-brief.pdf", "Finance workpaper PDF", _pdf(f"Case {contract['case_id']}\nQuestion: {spec.employee_question}\nAnalysis: {spec.analysis_route}\nNo conclusion is precomputed in this brief."), role="analysis-brief")

    groups = [
        ("18-erp-master-data.csv", ("erp_customers", "erp_vendors", "erp_items"), "ERP master"),
        ("19-erp-transactions.csv", ("erp_cust_trans", "erp_vend_trans", "erp_gl", "erp_purch_orders", "erp_sales_orders"), "ERP transactions"),
        ("20-bank-and-payment-state.csv", ("erp_bank_lines", "erp_payment_runs", "erp_payment_run_lines", "erp_settlements"), "Bank and payment"),
    ]
    for filename, tables, source in groups:
        snapshots = [snapshot for table in tables if (snapshot := _snapshot(cx, table, tokens)) is not None]
        add(filename, source, _csv(snapshots, contract["case_id"]), role="operations")

    json_groups = [
        ("21-books-ledger.json", ("books_customers", "books_invoices", "books_payments", "books_credit_memos"), "QuickBooks subsidiary ledger"),
        ("22-filings-evidence.json", ("filings_companies", "filings_facts", "filings_documents"), "SEC filing snapshot"),
        ("23-odoo-procurement.json", ("erpb_partners", "erpb_products", "erpb_sale_orders", "erpb_purchase_orders", "erpb_manufacturing_orders"), "Odoo ERP"),
        ("24-approvals-and-controls.json", ("erp_approval_requests", "erp_approval_policies", "approval_matrix", "close_tasks"), "Control records"),
    ]
    for filename, tables, source in json_groups:
        snapshots = [snapshot for table in tables if (snapshot := _snapshot(cx, table, tokens)) is not None]
        add(filename, source, json.dumps({"case_id": contract["case_id"], "sources": snapshots}, indent=2, default=str, sort_keys=True) + "\n", role="operations")

    add("25-lineage-and-currency.md", "Evidence custodian", f"# {contract['case_id']} lineage\n\nCurrent sources carry their own immutable ids, effective dates, filing accessions, workbook modified times, or ERP keys. Resolve those fields directly. A filename or display name alone is not identity.\n", role="lineage")
    inventory_rows = [["case_id", "source_id", "role", "status"], *[[contract["case_id"], ref, role, "inspect"] for ref, role in zip(contract["evidence_refs"], ("authority", "approval", "register", "identity"))]]
    inventory_csv = io.StringIO()
    csv.writer(inventory_csv).writerows(inventory_rows)
    add("26-source-inventory.csv", "Case intake", inventory_csv.getvalue(), role="inventory")
    add("27-current-versus-stale-notes.txt", "Controls", f"Case {contract['case_id']} has both {CONTEXT_REVISION} and {SUPERSEDED_REVISION} evidence. Current records must be established by effective dates and modified timestamps. The prior draft is retained to test, not to follow.\n", role="conflict")

    manifest_rows = [{"filename": asset["filename"], "source": asset["source"], "evidence_role": asset["evidence_role"]} for asset in assets]
    add("28-agent-visible-asset-manifest.json", "Release builder", json.dumps({"case_id": contract["case_id"], "gold_included": False, "oracle_walk_included": False, "assets": manifest_rows}, indent=2, sort_keys=True) + "\n", role="manifest")
    cx.close()
    if len(assets) != 28:
        raise ValueError(f"expected 28 assets, wrote {len(assets)}")
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
