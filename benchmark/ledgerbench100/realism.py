"""Shared realism contract for the LedgerBench-100 v2 release."""

from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import zipfile
from copy import deepcopy
from html import escape
from pathlib import Path
from typing import Any


PROVIDER_MAPPINGS = {
    "erp": "Microsoft Dynamics 365 Finance & Operations OData, custom API, and form patterns",
    "email": "Gmail v1 users.messages, users.threads, labels, attachments, and send shapes",
    "sheets": "Microsoft Graph Drive and workbook resource shapes",
    "filings": "SEC EDGAR submissions, company facts, concepts, frames, and full-text search shapes",
    "books": "QuickBooks Online v3 query, entity, and report shapes",
    "odoo": "Odoo model metadata, search_read, create, write, and workflow action shapes",
    "docs": "Internal governed policy and SOP library",
    "harness": "Task-scoped reporting system; not an enterprise provider",
}

SAFE_CONTEXT_STEPS = (
    {"server": "docs", "tool": "list_document_types", "args": {}},
    {"server": "email", "tool": "labels_list", "args": {}},
    {"server": "sheets", "tool": "list_drive_items", "args": {}},
    {"server": "harness", "tool": "list_submitted", "args": {}},
    {"server": "erp", "tool": "api_find_actions", "args": {}},
    {"server": "docs", "tool": "list_documents", "args": {}},
)


def release_prompt(entry: dict, source_prompt: str, source_config: dict) -> str:
    """Render an ordinary employee request without embedding the solve recipe."""

    prompt = source_prompt.strip()
    if entry["source_task"].startswith("erpbench/"):
        persona = prompt.splitlines()[0].strip()
        description = source_config["task"].get("description", "the open procurement portfolio")
        product = description.split("—", 1)[-1].strip().rstrip(".")
        quantities = [
            int(value)
            for value in re.findall(r"^-[^\n]*?:\s*(\d+) units", prompt, re.MULTILINE)
        ]
        portfolio = (
            f"The {len(quantities)} open customer orders ({sum(quantities)} units total) for {product}"
            if quantities
            else f"The open customer-order portfolio for {product}"
        )
        prompt = (
            f"{persona}\n\n{portfolio} needs supply coverage before "
            "the committed dates. Work out a feasible plan from the live ERP, current stock, bills of "
            "material, supplier terms, workcenter capacity, customer budgets, and the governed operating "
            "policies. Commit only the supported sales, purchase, and manufacturing records, preserve "
            "traceability between them, and leave the portfolio in a state the fulfillment team can execute."
        )
    prompt = re.sub(
        r"Submit (?:the )?(?:answer|number|finding) with submit_answer\([^\n]*\)\.?",
        "Give the team the supported result and cite the records used.",
        prompt,
        flags=re.IGNORECASE,
    )
    prompt = re.sub(
        r"submit_answer\([^\n]*\)",
        "the finance reporting record",
        prompt,
        flags=re.IGNORECASE,
    )
    if entry.get("provenance") == "variant":
        prompt += (
            f"\n\nA controls reviewer reopened this {entry['family'].replace('_', ' ')} item before "
            "sign-off because the governed rule may sit outside the obvious record. Re-establish the "
            "answer from the current source systems, keep unsupported changes out, and leave a reproducible "
            "audit trail for the reviewer."
        )
    if len(prompt.split()) < 45:
        prompt += (
            " Reconcile the live systems instead of trusting a single screen, keep unrelated records "
            "unchanged, and leave enough source detail for another finance operator to reproduce the result."
        )
    return prompt


def distinct_walk(
    entry: dict,
    source_walk: list[dict],
    seen_sequences: set[tuple[tuple[str, str], ...]],
) -> list[dict]:
    """Add contract/policy discovery and disambiguate repeated family walks."""

    walk = deepcopy(source_walk)
    if not any(
        step["server"] == "harness" and step["tool"] == "reporting_fields"
        for step in walk
    ):
        walk.insert(0, {"server": "harness", "tool": "reporting_fields", "args": {}})
    if entry.get("provenance") == "variant" and not any(
        step["server"] == "docs" for step in walk
    ):
        walk.insert(1, {"server": "docs", "tool": "list_documents", "args": {}})

    def signature(value: list[dict]) -> tuple[tuple[str, str], ...]:
        return tuple((step["server"], step["tool"]) for step in value)

    if signature(walk) not in seen_sequences:
        seen_sequences.add(signature(walk))
        return walk
    for marker in SAFE_CONTEXT_STEPS:
        candidate = [walk[0], deepcopy(marker), *walk[1:]]
        if signature(candidate) not in seen_sequences:
            seen_sequences.add(signature(candidate))
            return candidate
    raise ValueError(f"could not make {entry['task_id']} reference walk distinct")


def decision_options(entry: dict, walk: list[dict]) -> list[dict[str, Any]]:
    sources = list(dict.fromkeys(step["server"] for step in walk if step["server"] != "harness"))
    state_tools = [
        f"{step['server']}.{step['tool']}"
        for step in walk
        if step["tool"].startswith(
            ("create", "write", "send", "api_invoke", "data_create", "data_update", "action_")
        )
    ]
    return [
        {
            "id": "corroborated-current-records",
            "label": "Use corroborated current records",
            "selected": True,
            "reason": (
                f"The {entry['family']} conclusion is supported across {', '.join(sources) or 'the task world'}"
                + (f" before the scoped transitions {', '.join(dict.fromkeys(state_tools))}." if state_tools else ".")
            ),
        },
        {
            "id": "single-system-shortcut",
            "label": "Trust the first matching system",
            "selected": False,
            "reason": "The benchmark deliberately includes stale, incomplete, or differently timed records across systems.",
        },
        {
            "id": "broad-ledger-correction",
            "label": "Apply a broad ledger correction",
            "selected": False,
            "reason": "A broad correction exceeds the supported scope and would alter protected neighboring records or control tables.",
        },
    ]


def rubric_criteria(
    entry: dict,
    checks: dict,
    walk: list[dict],
    initial_hashes: dict[str, str],
) -> list[dict[str, str]]:
    """Expand verifier checks into exact, inspectable task-specific criteria."""

    rows: list[dict[str, str]] = []

    def add(category: str, criterion_id: str, description: str, enforced_by: str) -> None:
        rows.append(
            {
                "id": f"{category}.{criterion_id}",
                "category": category,
                "description": description,
                "enforced_by": enforced_by,
            }
        )

    for check in checks.get("answer_checks", []):
        field = check["field"]
        detail = {key: value for key, value in check.items() if key != "field"}
        add(
            "answer",
            field,
            f"File {field} using the released type, expectation, and tolerance contract {detail!r}.",
            f"vcode:answer_checks[{field}]",
        )
    for index, check in enumerate(checks.get("trace_checks", []), 1):
        label = check.get("name") or check.get("type") or f"trace-{index}"
        add(
            "investigation",
            f"{index:02d}.{label}",
            f"Satisfy the evidence prerequisite {check!r}; relevant reads must precede the filed result, but no exact call order is graded.",
            f"vcode:trace_checks[{index - 1}]",
        )
    allowed_tables = {"answers"}
    for index, check in enumerate(checks.get("state_checks", []), 1):
        label = check.get("name") or check.get("type") or f"state-{index}"
        if check.get("type") == "writes_only":
            allowed_tables.update(check.get("tables", []))
        add(
            "state",
            f"{index:02d}.{label}",
            f"Leave the task world satisfying the exact state assertion {check!r}.",
            f"vcode:state_checks[{index - 1}]",
        )
    observed: set[tuple[str, str, str]] = set()
    for step in walk:
        if step["server"] == "harness" and step["tool"] == "submit_answer":
            continue
        arguments = step.get("args") or {}
        key = (step["server"], step["tool"], json.dumps(arguments, sort_keys=True))
        if key in observed:
            continue
        observed.add(key)
        add(
            "evidence",
            f"{len(observed):02d}.{step['server']}.{step['tool']}",
            f"Establish the task-relevant {step['server']} evidence through {step['tool']} with scope {arguments!r}.",
            "vcode:trace requirements and answer/state derivation",
        )
    for table, digest in sorted(initial_hashes.items()):
        if table in allowed_tables:
            continue
        add(
            "containment",
            f"{table}.digest",
            f"Preserve unrelated table {table} at its seeded digest {digest}; writes_only rejects drift outside {sorted(allowed_tables)!r}.",
            "vcode:writes_only initial-state hash comparison",
        )
    if len(rows) < 40:
        raise ValueError(f"{entry['task_id']} exposes only {len(rows)} verifier criteria")
    return rows


ASSET_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("03-erp-master-data.csv", ("erp_customers", "erp_vendors", "erp_items")),
    ("04-erp-transactions.csv", ("erp_cust_trans", "erp_vend_trans", "erp_gl")),
    ("07-governing-documents.md", ("docs_documents",)),
    ("08-bank-and-payment-state.csv", ("erp_bank_lines", "erp_payment_runs", "erp_payment_run_lines", "erp_settlements")),
    ("09-books-ledger.json", ("books_customers", "books_invoices", "books_payments", "books_credit_memos")),
    ("10-filings-evidence.json", ("filing_companies", "filing_facts", "filing_submissions")),
    ("11-odoo-procurement.json", ("erpb_partners", "erpb_products", "erpb_sale_orders", "erpb_purchase_orders", "erpb_manufacturing_orders")),
    ("12-approvals-and-controls.md", ("erp_approvals", "erp_audit_trail", "approval_matrix", "close_tasks")),
)


def _tokens(prompt: str, walk: list[dict]) -> set[str]:
    values: list[str] = re.findall(r"\b[A-Za-z]+[-_/][A-Za-z0-9._/-]+\b", prompt)

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, list):
            for nested in value:
                collect(nested)
        elif isinstance(value, (str, int, float)):
            values.append(str(value))

    collect([step.get("args", {}) for step in walk])
    return {value.casefold() for value in values if len(value) >= 3}


def _snapshot(
    connection: sqlite3.Connection,
    table: str,
    tokens: set[str],
    *,
    limit: int = 20,
) -> dict[str, Any] | None:
    if not connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone():
        return None
    total = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')]
    candidates = [
        dict(row)
        for row in connection.execute(f'SELECT * FROM "{table}" LIMIT 500').fetchall()
    ]
    matched = [
        row
        for row in candidates
        if any(token in json.dumps(row, default=str).casefold() for token in tokens)
    ][:limit]
    return {
        "table": table,
        "row_count": total,
        "columns": columns,
        "task_relevant_rows": matched or candidates[: min(4, limit)],
    }


def _csv(snapshots: list[dict[str, Any]]) -> str:
    rows = [
        {"source_table": snapshot["table"], **row}
        for snapshot in snapshots
        for row in snapshot["task_relevant_rows"]
    ]
    fields = ["source_table", *sorted({key for row in rows for key in row if key != "source_table"})]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fields})
    return stream.getvalue()


def _markdown(title: str, snapshots: list[dict[str, Any]]) -> str:
    parts = [f"# {title}"]
    for snapshot in snapshots:
        parts.extend(
            [
                "",
                f"## {snapshot['table']} ({snapshot['row_count']} rows)",
                "",
                "```json",
                json.dumps(snapshot["task_relevant_rows"], indent=2, default=str),
                "```",
            ]
        )
    return "\n".join(parts) + "\n"


def _xlsx(sheet_rows: list[dict[str, Any]]) -> bytes:
    rows: list[list[Any]] = []
    for row in sheet_rows:
        cells = row.get("cells")
        if isinstance(cells, str):
            try:
                cells = json.loads(cells)
            except json.JSONDecodeError:
                cells = [cells]
        rows.append([row.get("file", ""), *(cells or [])])
    if not rows:
        rows = [["No task-matched workbook rows"]]
    xml_rows: list[str] = []
    for row_index, values in enumerate(rows, 1):
        cells = "".join(
            f'<c r="{chr(65 + min(column, 25))}{row_index}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
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
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        )
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Task evidence" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        )
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)
    return stream.getvalue()


def write_asset_views(
    root: Path,
    database: Path,
    prompt: str,
    walk: list[dict],
    checks: dict,
    initial_hashes: dict[str, str],
) -> list[dict[str, str]]:
    """Write 14 inspectable, task-scoped views of the exact initial world."""

    root.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    tokens = _tokens(prompt, walk)
    assets: list[dict[str, str]] = []

    def add(name: str, source: str, content: str | bytes) -> None:
        target = root / name
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8", newline="\n")
        assets.append({"filename": name, "source": source, "kind": target.suffix.lstrip(".")})

    add("01-employee-request.md", "Teams", prompt + "\n")
    answer_schema = _snapshot(connection, "answer_schema", tokens)
    add(
        "02-reporting-contract.json",
        "Finance reporting system",
        json.dumps(
            {
                "answer_schema": answer_schema,
                "answer_checks": checks.get("answer_checks", []),
            },
            indent=2,
            default=str,
            sort_keys=True,
        )
        + "\n",
    )
    for filename, tables in ASSET_GROUPS:
        snapshots = [
            snapshot
            for table in tables
            if (snapshot := _snapshot(connection, table, tokens)) is not None
        ]
        suffix = Path(filename).suffix
        if suffix == ".csv":
            content = _csv(snapshots)
        elif suffix == ".md":
            content = _markdown(Path(filename).stem.replace("-", " ").title(), snapshots)
        else:
            content = json.dumps({"sources": snapshots}, indent=2, default=str, sort_keys=True) + "\n"
        add(filename, ", ".join(tables), content)

    sheet_snapshot = _snapshot(connection, "sheet_rows", tokens, limit=100)
    sheet_rows = sheet_snapshot["task_relevant_rows"] if sheet_snapshot else []
    add("05-finance-drive.xlsx", "Microsoft Graph workbook mirror", _xlsx(sheet_rows))
    mail_snapshot = _snapshot(connection, "email_messages", tokens, limit=12)
    messages = mail_snapshot["task_relevant_rows"] if mail_snapshot else []
    eml = "\n\n".join(
        "\n".join(
            [
                f"From: {message.get('from_addr', '')}",
                f"To: {message.get('to_addr', '')}",
                f"Date: {message.get('sent_at', '')}",
                f"Subject: {message.get('subject', '')}",
                f"Message-ID: <{message.get('id', 'unknown')}@ledgerbench.invalid>",
                "",
                str(message.get("body", "")),
            ]
        )
        for message in messages
    ) or "Subject: No task-matched message\n\nThe mailbox contains no identifier-matched message for this task."
    add("06-mailbox-thread.eml", "Gmail v1 mailbox mirror", eml + "\n")
    add(
        "13-initial-state-manifest.json",
        "Verifier initial-state hashes",
        json.dumps({"table_hashes": initial_hashes}, indent=2, sort_keys=True) + "\n",
    )
    used = list(dict.fromkeys(step["server"] for step in walk))
    add(
        "14-tool-contract-map.json",
        "Provider contract mapping",
        json.dumps(
            {
                "servers": [
                    {"server": server, "mapping": PROVIDER_MAPPINGS[server]}
                    for server in used
                ],
                "used_tools": [
                    {"server": step["server"], "tool": step["tool"]}
                    for step in walk
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    connection.close()
    if len(assets) != 14:
        raise ValueError(f"expected 14 assets, wrote {len(assets)}")
    return assets
