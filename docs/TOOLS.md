# Mock tools — inventory, APIs, real-service comparison, SQL backing

All 23 mock tools live in **`mcp/servers/*_server.py`** — one stdio MCP server per product,
built on `mcp/lib/framework.py` (JSON-RPC `initialize` / `tools/list` / `tools/call`, tool
schemas in MCP `inputSchema` form, per-call tracing to `TRACE_FILE`). The roster with
`shaped_after` provenance is `mcp/mcp-servers.json`; the evidence rule ("a server exists
iff research says the team uses that system class AND ≥1 task requires it") is
`docs/TOOL-CENSUS.md`.

**Every tool is SQL-backed.** There are no canned responses: each tool handler opens the
run's SQLite state (`WORLD_DB` → `world.sqlite` = `world/build/core.sqlite` + the task's
`environment/seed/` overlays, materialized by `sim/prepare.py`) and computes its answer
with live queries at call time. Change a row in the seed and every tool's answer changes
with it — that's what makes verifier ground truths and tool responses provably consistent.
Table namespaces are per-server, so each MCP server sees only its slice of one state file.

## Inventory (generated from the live tool registry — regenerate with the snippet at bottom)

| Server | Tools | Backing tables (world/schema.sql) |
|---|---|---|
| `erp` | 5 | `erp_companies, erp_payment_terms, erp_cash_disc, erp_customers, erp_vendors, erp_cust_trans, erp_vend_trans, erp_settlements, erp_collection_letters, erp_aging_snapshot` |
| `books` | 5 | `books_customers, books_invoices, books_credit_memos` |
| `sheets` | 2 | `sheet_files, sheet_rows` |
| `email` | 2 | `email_messages` |
| `filings` | 4 | `filings_companies, filings_facts, filings_documents` |
| `docs` | 3 | `docs_documents` |
| `harness` | 2 | `answers` (the graded state) |

### `erp` — 5 tools (`mcp/servers/erp_server.py`)
- **`data_find_entity_type`**(`query`*) — find entity types from a natural-language query
- **`data_get_entity_metadata`**(`entity`*) — field list (via `PRAGMA table_info`); unknown entity → informative error + available list
- **`data_find_entities`**(`entity`*, `filters`, `page`) — filtered query, **25-row pages**
- **`data_find_entities_sql`**(`sql`*) — read-only single SELECT over `erp_*` only, LIMIT 200
- **`get_customer_aged_balances`**(`as_of`, `customer_account`, `customer_group`, `page`) — LIVE aging computed from open transactions (deliberately distinct from the batch `AgedBalancesSnapshot` entity — the dual-truth mechanic)

### `books` — 5 tools (`mcp/servers/books_server.py`)
`list_customers`(`query`) · `get_customer`(`customer_id`*, returns open-balance + unapplied-credit-memo summary) · `query_invoices`(`customer_id`, `status`) · `get_invoice`(`invoice`*) · `query_credit_memos`(`customer_id`)

### `sheets` — 2 tools · `email` — 2 tools · `docs` — 3 tools
`list_spreadsheets` · `read_sheet`(`name`*, `max_rows`) — rows as JSON cells
`search_messages`(`query`*, `folder`) · `get_message`(`message_id`*, incl. attachment text)
`list_documents`(`doc_type`) · `search_documents`(`query`*) · `get_document`(`doc_id`*)

### `filings` — 4 tools (`mcp/servers/filings_server.py`)
`lookup_company`(`query`*) → CIK · `list_available_concepts`(`ticker`*) · `get_company_concept`(`ticker`*, `concept`*) · `get_submissions`(`ticker`*)

### `harness` — 2 tools (`mcp/servers/harness_server.py`)
`submit_answer`(`answers`* object → `answers` table; "none" for empty-answer traps) · `list_submitted`()

## Mock vs. real service — how much are we mocking?

| Mock | Real surface (researched) | Coverage & deliberate gaps |
|---|---|---|
| `erp` | **Microsoft Dynamics 365 ERP MCP server** (dynamic, 2025): `data_find_entity_type`, `data_get_entity_metadata`, `data_find_entities`, `data_find_entities_sql`, ~13 form tools (25-row pages), `api_find_actions`, `api_invoke_action`. Static 13-tool server retires 2026-10-01. FinanceBenchmark ships an `erp-mcp-sqlite` localhost stand-in — Microsoft's own precedent for exactly our mock. (`research/erp-domain.md` §3, `research/evals-and-benchmarks.md`) | **Discovery spine 4/4 tools, same names and call pattern.** Form tools 1/13 (aged balances — the one erp_qa tasks need; page size 25 matches). `api_*` write actions 0/2 — world is read-only until `collections_ops` (wave 2). Auth (Entra OAuth) not mocked — out of eval scope. |
| `books` | **Intuit QuickBooks Online official MCP: 144 tools** across accounting objects. (`research/erp-domain.md` §4) | ~3% by tool count, on purpose: the 5 AR-read tools the subsidiary fragmentation mechanic needs (customers, invoices, credit memos). Entities/fields mirror QBO shapes (`DocNumber`, `Balance`, `TxnDate`, credit-memo `remaining`). |
| `filings` | **SEC EDGAR**: `submissions`, `companyfacts`, `companyconcept`, `frames`, full-text search; 10 req/s + User-Agent friction. Community MCPs: sec-edgar-mcp, financial-datasets (9 tools). (`research/domain-workflows.md` §4) | `companyconcept` ≈ 1:1 (`get_company_concept`), `submissions` ≈ `get_submissions`, `companyfacts` index ≈ `list_available_concepts`, ticker→CIK ≈ `lookup_company`. **Facts are real XBRL values** captured from data.sec.gov (XOM CIK 0000034088, CAT CIK 0000018230; captured 2026-08-10) and frozen for determinism. Not mocked: `frames`, full-text, rate-limit/CIK-padding friction (ledger Q12: escalation lever, off by default). |
| `email` | Gmail/Graph mail APIs (search + read). | Minimal 2-tool read surface — evidence class is "invoices arrive by email" (68% manual keying), which needs search+read only. No send (read-only world). |
| `sheets` | Excel/Drive file listing + range reads. | 2-tool shadow-drive surface for the 94%-close-in-Excel mechanic; no write, no formulas. |
| `docs` | SharePoint/Notion-class doc store. | 3-tool consult surface for the anchor-document pattern (dunning runbook, discount policy, brief template, credit policy). |
| `harness` | (no real counterpart — eval-only) | House pattern: answers-as-state so verification stays deterministic; kept off the business surface. |

## Research anchoring chain (tool → evidence → task)

Every server traces: **real-service research** (`research/erp-domain.md`,
`research/domain-workflows.md`) → **census justification + exclusion list**
(`docs/TOOL-CENSUS.md`) → **roster entry with `shaped_after`** (`mcp/mcp-servers.json`) →
**tasks whose `tests/checks.json` require it** (`required_servers`). Excluded-by-evidence:
slack/jira/github/pagerduty/notion/calendar (no finance workflow touches them — see the
fixed-roster anti-pattern bug, `~/dev/blobfish-0/docs/BUG-TOOL-ROSTER-INFERENCE.md`).

## Error semantics (audit A2)

Tools return informative application errors (`{"error": ..., "available_entities": [...]}`)
instead of raw exceptions; the framework marks any error payload `ok:false` in the trace, so
`required_servers` verification still demands at least one *successful* call — an agent
cannot claim "not in the ERP" off a failed query, but it recovers from a readable error,
not a stack trace.

## Regenerating the inventory

```bash
python3 - <<'EOF'
import importlib.util
from pathlib import Path
for f in sorted(Path("mcp/servers").glob("*_server.py")):
    spec = importlib.util.spec_from_file_location(f.stem, f); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print(f"{m.S.name}: {len(m.S.tools)} tools — {', '.join(m.S.tools)}")
EOF
```
