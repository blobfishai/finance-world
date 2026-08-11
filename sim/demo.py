#!/usr/bin/env python3
"""Exercise EVERY tool on EVERY server against a real seeded world and write docs/DEMO.md.

Proof-of-life for the world: real calls, real SQL-backed responses, plus an inventory of
every seeded document and input file across all tasks. No models involved.
"""
import importlib.util, json, os, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim"))
from prepare import prepare

# (server, tool, args) — one realistic call per tool, on the task world named below.
DEMO_TASK = "tasks/erp_qa/collections-sparrow"
EXTRA = {  # tools needing a different task's seed to be meaningful
    "tasks/erp_qa/cash-disc-fourthcoffee-east": [
        ("erp", "api_find_actions", {"query": "discount"}),
        ("erp", "api_invoke_action", {"action": "ContosoCashDiscountForecast", "parameters": {"vendor_account": "SYNVEN-0069"}}),
        ("email", "messages_list", {"q": "fourth coffee"}),
        ("email", "messages_get", {"id": "em-0090"}),
        ("email", "attachments_get", {"message_id": "em-0090"}),
        ("email", "threads_get", {"id": "em-0090"}),
        ("email", "labels_list", {}),
        ("docs", "list_documents", {}),
        ("docs", "search_documents", {"query": "discount"}),
        ("docs", "get_document", {"doc_id": "policy--cash-discount-capture"}),
        ("docs", "get_document_metadata", {"doc_id": "policy--cash-discount-capture"}),
        ("docs", "list_document_types", {}),
    ],
    "tasks/cross_system/total-ar-adventure-group-v2": [
        ("books", "get_company_info", {}),
        ("books", "query", {"q": "SELECT * FROM Customer WHERE DisplayName LIKE '%adventure%'"}),
        ("books", "get_customer", {"customer_id": "BC-114"}),
        ("books", "get_invoice", {"invoice": "CD-1041"}),
        ("books", "get_creditmemo", {"creditmemo": "CM-2007"}),
        ("books", "get_payment", {"payment_id": "none"}),
        ("books", "report_aged_receivables", {}),
        ("books", "report_customer_balance", {}),
        ("books", "report_transaction_list", {"date_from": "2026-01-01", "date_to": "2026-03-02"}),
        ("books", "create_invoice", {"invoice": {"CustomerRef": "BC-114", "TotalAmt": 1}}),
        ("books", "update_invoice", {"invoice": {"Id": "bi-1041"}}),
        ("books", "void_invoice", {"invoice_id": "bi-1041"}),
        ("sheets", "list_drive_items", {}),
        ("sheets", "get_drive_item", {"item": "CES-migration-side-log.xlsx"}),
        ("sheets", "workbook_worksheets", {"item": "CES-migration-side-log.xlsx"}),
        ("sheets", "workbook_range", {"item": "CES-migration-side-log.xlsx", "address": "A1:D3"}),
        ("sheets", "workbook_used_range", {"item": "CES-migration-side-log.xlsx"}),
        ("sheets", "drive_search", {"q": "adventure"}),
    ],
    "tasks/business_brief/brief-caterpillar": [
        ("filings", "lookup_company", {"query": "Caterpillar"}),
        ("filings", "list_available_concepts", {"ticker": "CAT"}),
        ("filings", "get_company_concept", {"ticker": "CAT", "concept": "LongTermDebtNoncurrent"}),
        ("filings", "get_company_facts", {"ticker": "CAT"}),
        ("filings", "get_xbrl_frames", {"concept": "LongTermDebtNoncurrent", "fy": "2024"}),
        ("filings", "get_submissions", {"ticker": "CAT"}),
        ("filings", "full_text_search", {"q": "balance sheet"}),
    ],
    "tasks/vendor_master/missing-po-inquiry": [
        ("email", "send_message", {"to": "ap@wingtip-sim.example",
                                   "subject": "PO reference needed for invoice TWINV-303",
                                   "body": "Please confirm the purchase order this invoice was raised against."}),
    ],
    "tasks/collections_ops/escalate-sparrow-letter3": [
        ("erp", "api_invoke_action", {"action": "ContosoIssueCollectionLetter", "parameters": {"customer_account": "US-008"}}),
        ("erp", "api_invoke_action", {"action": "ContosoSetCreditHold", "parameters": {"customer_account": "US-008", "on_hold": "Open", "reason": "demo"}}),
    ],
}
BASE = [
    ("erp", "data_find_entity_type", {"query": "customer invoices"}),
    ("erp", "data_get_entity_metadata", {"entity": "CustomerTransactions"}),
    ("erp", "data_find_entities", {"entity": "Customers", "filters": {"account": "US-008"}}),
    ("erp", "data_find_entities_sql", {"sql": "SELECT invoice, due_date, ROUND(amount-settled,2) AS open FROM erp_cust_trans WHERE account='US-008' AND closed=0"}),
    ("erp", "data_create_entities", {"entity": "Customers", "records": [{"account": "X"}]}),
    ("erp", "data_update_entities", {"entity": "Customers", "updates": [{"account": "US-008"}]}),
    ("erp", "data_delete_entities", {"entity": "Customers", "keys": ["US-008"]}),
    ("erp", "form_find_menu_item", {"query": "customers"}),
    ("erp", "form_open_menu_item", {"menu_item": "All customers"}),
    ("erp", "form_filter_grid", {"form_id": "fh-1", "column": "name", "value": "Sparrow"}),
    ("erp", "form_find_controls", {"form_id": "fh-1", "search": "credit"}),
    ("erp", "form_select_grid_row", {"form_id": "fh-1", "row": "AUTO"}),
    ("erp", "form_open_or_close_tab", {"form_id": "fh-1", "tab": "Credit and collections"}),
    ("erp", "form_click_control", {"form_id": "fh-1", "control": "Collections"}),
    ("erp", "form_open_lookup", {"form_id": "fh-1", "control": "payment_term"}),
    ("erp", "form_sort_grid_column", {"form_id": "fh-1", "column": "account"}),
    ("erp", "form_filter_form", {"form_id": "fh-1", "value": "Sparrow"}),
    ("erp", "form_set_control_values", {"form_id": "fh-1", "values": {"credit_max": 1}}),
    ("erp", "form_save_form", {"form_id": "fh-1"}),
    ("erp", "form_close_form", {"form_id": "fh-1"}),
    ("erp", "api_find_actions", {}),
    ("erp", "api_invoke_action", {"action": "ContosoCollectionStatus", "parameters": {"customer_account": "US-008"}}),
    ("harness", "submit_answer", {"answers": {"demo_field": "demo value"}}),
    ("harness", "list_submitted", {}),
]

def load(name, tag):
    spec = importlib.util.spec_from_file_location(f"{name}_{tag}", ROOT / f"mcp/servers/{name}_server.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.S

def run_group(task, calls, out, tag, covered):
    env = prepare(ROOT / task, ROOT / f".runs/demo/{tag}")["env"]
    os.environ.update(env)
    servers, row_hint = {}, None
    out.append(f"\n### World: `{task}`\n")
    for srv, tool, args in calls:
        if srv not in servers: servers[srv] = load(srv, tag)
        a = dict(args)
        if a.get("row") == "AUTO": a["row"] = row_hint or 1
        try:
            res = servers[srv].call(tool, a)
        except Exception as e:
            res = {"exception": repr(e)}
        covered.add((srv, tool))
        if tool == "form_filter_grid" and isinstance(res, dict):
            rows = res.get("grid", {}).get("rows") or []
            if rows: row_hint = rows[0]["_row"]
        s = json.dumps(res, default=str)
        s = s if len(s) <= 520 else s[:520] + " …"
        out.append(f"**`{srv}.{tool}`**  `{json.dumps(a, default=str)[:150]}`\n")
        out.append(f"```json\n{s}\n```\n")

def main():
    out = ["# Live tool & document demo", "",
           "Generated by `python3 sim/demo.py` — every tool called for real against seeded",
           "task worlds, every response computed from SQLite at call time. SIMULATION ONLY.", ""]
    covered = set()
    out.append("## Tools")
    run_group(DEMO_TASK, BASE, out, "base", covered)
    for task, calls in EXTRA.items():
        run_group(task, calls, out, task.split("/")[-1], covered)

    # coverage
    all_tools = set()
    for f in sorted((ROOT / "mcp/servers").glob("*_server.py")):
        S = load(f.stem.replace("_server", ""), "cov")
        for t in S.tools: all_tools.add((S.name, t))
    missing = sorted(all_tools - covered)
    out.insert(4, f"**Coverage: {len(covered)}/{len(all_tools)} tools exercised**"
                  + (f" — not shown: {missing}" if missing else " (100%)") + "\n")

    # seeded documents + inputs inventory
    out.append("\n## Seeded documents and input files\n")
    out.append("| Task | Kind | File | First line |")
    out.append("|---|---|---|---|")
    n_docs = n_inputs = 0
    for t in sorted(ROOT.glob("tasks/*/*")):
        seed = t / "environment/seed"
        for p in sorted(seed.glob("documents/*.md")):
            head = next((l for l in p.read_text().splitlines() if l.strip()), "")
            out.append(f"| {t.parent.name}/{t.name} | policy/SOP | `{p.name}` | {head[:60]} |"); n_docs += 1
        for p in sorted((seed / "inputs").glob("*")) if (seed / "inputs").is_dir() else []:
            head = p.read_text().splitlines()[0][:60]
            out.append(f"| {t.parent.name}/{t.name} | input file | `{p.name}` | {head} |"); n_inputs += 1
    out.insert(len(out) - (n_docs + n_inputs + 3),
               f"{n_docs} seeded policy/SOP documents, {n_inputs} staged input files.\n")
    (ROOT / "docs/DEMO.md").write_text("\n".join(out) + "\n")
    print(f"wrote docs/DEMO.md — {len(covered)}/{len(all_tools)} tools, {n_docs} documents, {n_inputs} inputs")
    if missing: print("not exercised:", missing)

if __name__ == "__main__":
    main()
