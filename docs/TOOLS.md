# Mock tools — inventory, APIs, real-service comparison, SQL backing

**61 tools across 7 MCP servers**, all in `mcp/servers/*_server.py` (one stdio MCP server
per product, JSON-RPC framework in `mcp/lib/framework.py`, per-call tracing). Quality bar:
grafana/mcp-grafana (98 tools, live-state-backed, category organization) — we match its
density philosophy at the surface our domain actually has, and every tool is backed by
state, not canned text.

**Every tool is SQL-backed.** Each handler opens the run's `world.sqlite`
(`world/build/core.sqlite` + the task's `environment/seed/` overlays via `sim/prepare.py`)
and computes results with live queries. Even the ERP *form tools* keep their view-model
session state in a table (`erp_form_sessions`). Proof of consistency: the
`ContosoCashDiscountForecast` action computes $437.11 for the cash-disc task's seed — the
same figure its verifier pins. Change a seed row and tool output + ground truth move
together.

## Inventory (generated from the live registry — snippet at bottom)

| Server | Tools | Backing tables |
|---|---|---|
| `erp` | **23** | `erp_*` (11 tables incl. `erp_form_sessions` runtime state) |
| `books` | **14** | `books_customers, books_invoices, books_credit_memos, books_payments` |
| `filings` | **7** | `filings_companies, filings_facts, filings_documents` |
| `email` | **5** | `email_messages` |
| `sheets` | **5** | `sheet_files, sheet_rows` |
| `docs` | **5** | `docs_documents` |
| `harness` | **2** | `answers` (the graded state) |

### `erp` — 23 tools — **1:1 with Microsoft's Dynamics 365 ERP MCP server (22/22 + 1 alias)**

Mirrors learn.microsoft.com/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp exactly:

- **Data tools 7/7**: `data_find_entity_type`, `data_get_entity_metadata`,
  `data_find_entities` (25-row pages), `data_find_entities_sql` (read-only SELECT, the
  10.0.48+ replacement), `data_create_entities`, `data_update_entities`,
  `data_delete_entities` — the three writes exist and respond with **authentic role-based
  rejections** (agent role: "Finance analyst (read-only)"), matching the real server's
  RBAC contract ("the system rejects calls to actions or objects the user role cannot access").
- **Form tools 13/13**: `form_find_menu_item`, `form_open_menu_item`, `form_close_form`,
  `form_find_controls` (one search term per call, per the real doc), `form_open_or_close_tab`,
  `form_filter_form`, `form_filter_grid`, `form_sort_grid_column`, `form_select_grid_row`,
  `form_click_control`, `form_open_lookup`, `form_set_control_values`, `form_save_form`.
  Real view-model runtime over 8 registered forms (CustTable, VendTable, CustTrans,
  VendTrans, CustCollectionLetterJour, CustAgedBalances, PaymTerm, CashDisc) with the
  documented behaviors: **tabs closed by default**, grid **filters support only the
  "matches" operator**, ISO dates, 25-row pages, runtime-calculated fields on row select,
  action controls that execute business logic (Collections → letters + aging;
  OpenTransactions), writes RBAC-denied.
- **Action tools 2/2**: `api_find_actions`, `api_invoke_action` over an ICustomAPI-style
  registry (environment-specific by design, like the real server): `ContosoCustAgedBalancesLive`,
  `ContosoCashDiscountForecast`, `ContosoCollectionStatus`.
- **+1 convenience alias**: `get_customer_aged_balances` (the live "Customer aged balances"
  view; kept stable for oracle walks).

Not mocked, deliberately: Entra ID auth handshake, environment servicing downtime,
Copilot-credit billing — outside eval scope.

### `books` — 14 tools — QBO-shaped (AR slice of Intuit's 144-tool MCP, ~10%)

`get_company_info` · **`query`** (QBO-style query language: `SELECT * FROM Invoice WHERE
CustomerRef = 'BC-114'`, entities Customer/Invoice/CreditMemo/Payment) · `list_customers` ·
`get_customer` · `query_invoices` · `get_invoice` · `query_credit_memos` · `query_payments` ·
**reports 3**: `report_aged_receivables` (QBO behavior: credit memos NOT netted),
`report_customer_balance`, `report_transaction_list` · **writes 3** (`create_invoice`,
`update_invoice`, `void_invoice`) — exist, respond with authentic `insufficient scope:
accounting.read` denials.

### `filings` — 7 tools — **EDGAR data-API 1:1 at the endpoint level**

`lookup_company` (ticker→CIK) · `get_company_concept` (≈ `api/xbrl/companyconcept`) ·
`get_company_facts` (≈ `api/xbrl/companyfacts`, large payload like the real one) ·
`get_xbrl_frames` (≈ `api/xbrl/frames`: one concept, one period, all companies) ·
`get_submissions` (≈ `data.sec.gov/submissions`) · `full_text_search` (≈ EDGAR FTS) ·
`list_available_concepts` (snapshot index). Facts are **real XBRL values** captured from
data.sec.gov (XOM, CAT; 2026-08-10), frozen for determinism. Rate-limit/User-Agent/CIK-padding
friction not reproduced by default (ledger Q12: escalation lever).

### `email` (5) · `sheets` (5) · `docs` (5) — the fragmentation surfaces

email: `search_messages`, `get_message`, `list_folders`, `get_thread`, `get_attachment`.
sheets: `list_spreadsheets`, `read_sheet`, `read_range`, `get_spreadsheet_metadata`
(staleness checks — chaos mechanic), `search_content` (cross-file grep).
docs: `list_documents`, `search_documents`, `get_document`, `get_document_metadata`
(version/effective-date checks), `list_document_types`.

### `harness` (2) — eval-only

`submit_answer` (answers-as-state; literal "none" for empty-answer traps) · `list_submitted`.

## Coverage summary vs real services

| Mock | Real surface | Verdict |
|---|---|---|
| erp | D365 ERP MCP: 22 tools | **22/22 — 1:1 by name and behavior contract** |
| filings | EDGAR data APIs: 5 endpoints + FTS | **6/6 endpoint-level 1:1** (+ index helper) |
| books | Intuit QBO MCP: 144 tools | 14 (~10%) — full AR read slice + query language + reports; writes scope-denied |
| email / sheets / docs | Gmail / Drive-Excel / SharePoint-class | minimal-but-honest read surfaces sized to their evidence class |

## Error & security semantics

Application errors are informative payloads (`{"error", "available_entities"/"hint"}`),
never raw stack traces; the framework marks them `ok:false` in the trace so
`required_servers` verification still demands a *successful* call. Write tools are present
(1:1 with reality) but return authentic authorization denials — the agent's role is
read-only, exactly how the real servers scope agents; denials are traceable, and the
verifier `writes_only` veto independently guarantees no state mutation outside `answers`.

## Research anchoring chain

Real-service research (`research/erp-domain.md`, `research/domain-workflows.md`; Microsoft
copilot-mcp doc fetched 2026-08-10 for the verbatim 22-tool list) → census + exclusion list
(`docs/TOOL-CENSUS.md`) → roster with `shaped_after` (`mcp/mcp-servers.json`) → tasks whose
`required_servers` checks demand the server. Excluded: slack/jira/github/pagerduty/notion —
see the fixed-roster anti-pattern bug (`~/dev/blobfish-0/docs/BUG-TOOL-ROSTER-INFERENCE.md`).

## Regenerating the inventory

```bash
python3 - <<'EOF'
import importlib.util
from pathlib import Path
total = 0
for f in sorted(Path("mcp/servers").glob("*_server.py")):
    spec = importlib.util.spec_from_file_location(f.stem, f); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); total += len(m.S.tools)
    print(f"{m.S.name}: {len(m.S.tools)} tools — {', '.join(m.S.tools)}")
print("TOTAL:", total)
EOF
```
