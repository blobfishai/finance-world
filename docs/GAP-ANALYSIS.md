# Gap analysis — why each tool was mocked, its evidence, and measured distance from the real product

> Verified 2026-08-10 against vendor documentation (sources at bottom). Companion to
> `docs/TOOLS.md` (inventory) and `docs/TOOL-CENSUS.md` (selection rule + persona scenarios).

## The selection method (why these tools and not others)

A server was mocked iff all three held:
1. **Workflow evidence** — `research/domain-workflows.md` shows a finance persona using
   that system class routinely (e.g., 94% close in Excel; 68% of invoices keyed from email).
2. **Benchmark grounding** — the primary eval (microsoft/FinanceBenchmark) or a researched
   scenario requires it (its 100 erp_qa tasks run against D365 USMF; its briefs require an
   internal AR/AP section).
3. **A shipped task's verifier demands it** (`required_servers`) — no task, no server.

Anything failing the test went on the exclusion list (slack/jira/github/pagerduty/notion —
the fixed-roster anti-pattern tripwires), including two systems analyzed below that we
*deliberately* did not mock.

## Distance from the four real products asked about

### 1. Real Microsoft finance tool — Dynamics 365 Finance ERP MCP → our `erp`

Verified surface (learn.microsoft.com copilot-mcp, fetched 2026-08-10): 22 tools —
7 data + 13 form + 2 action; RBAC-scoped dynamic context; 25-row pages; tabs closed by
default; "matches"-only grid filters; static 13-tool server retiring 2026-10-01.

| Dimension | Real | Ours | Distance |
|---|---|---|---|
| Tool surface | 22 tools | 22/22 same names + behavior contracts (+1 alias) | **≈0 — 1:1** |
| Write semantics | RBAC per role | writes present, authentic denial for read-only analyst role | matches contract; no writable role yet (wave-2 lever) |
| Data model | thousands of entities | 10 AP/AR entities (the benchmark's task surface) | deep on AR/AP, narrow elsewhere — intentional |
| Forms | thousands | 8 registered forms | same |
| Actions | env-specific ICustomAPI | 3 Contoso actions | faithful *mechanism*; small registry |
| Auth/ops | Entra ID, servicing downtime, credit billing | none | out of eval scope, documented |

**Verdict: tool-level 1:1; content breadth deliberately scoped to the benchmark's domain.**

### 2. Real sheet tool — Microsoft Graph Excel API (and Google Sheets) → our `sheets`

Verified surface (Graph `workbook` resource): worksheets CRUD, `range(address='A1:B2')`
with **values + formulas + formulasR1C1 + numberFormat + text + valueTypes**, tables with
rows/columns/**sort/filter**, charts (+ image render), named items, **workbook functions**
(e.g. `functions/pmt`), and three session modes (`workbook-session-id`, persistent /
non-persistent / sessionless).

| Dimension | Real | Ours | Distance |
|---|---|---|---|
| Addressing | A1 ranges, worksheets | flat row list per file | **large** — no A1, no multi-sheet |
| Cell model | values+formulas+formats | values only | **large** — no formulas |
| Operations | ~dozens incl. sort/filter/charts/functions/write | 5 read tools | **~10% of read surface, 0% write** |
| Metadata | drive item props | owner/modified/description (staleness checks) | adequate for the chaos mechanic |

**Verdict: our biggest honesty gap.** It is sized to current tasks (small trackers read
whole), but a 1:1-minded upgrade is well-defined: worksheet model + A1 `read_range` +
formula cells (**formula-drift chaos** — a tracker whose stale SUM disagrees with its rows
— is a researched-worthy escalation), table sort/filter, and session semantics. Queued as
the next densification target.

### 3. Real Salesforce tool → not in finance-world (by evidence), pending 1:1 in the sales world

Verified surface: Salesforce's official **hosted MCP servers** — "SObject All" (full CRUD +
query + search across all objects), "Headless 360" (Discover/Describe/Dispatch), plus DX
MCP (60+ dev tools) and Marketing Cloud MCP; every tool call respects field-level security,
object permissions, and sharing rules.

- **Finance-world**: correctly absent — no researched finance workflow touches CRM
  (`docs/TOOL-CENSUS.md` exclusion list). Distance is not applicable; adding it would be
  the roster-copying mistake.
- **Sales world**: the existing generated mock is *not* 1:1 (regex-bucketed roster —
  `~/dev/blobfish-0/docs/BUG-TOOL-ROSTER-INFERENCE.md`). The rebuild target is the SObject
  discovery-first pattern (Discover/Describe → query/search → CRUD under role security),
  which is structurally the same shape we already proved with the D365 mock.
  Plan: `~/dev/salesforce-grok/docs/SALES-WORLD-DESIGN.md`.

### 4. Real Oracle ERP tools → deliberately not mocked; portability assessed

Verified surface: Oracle Fusion Cloud Financials REST — resources under
`/fscmRestApi/resources/latest/` (`invoices` for payables incl. lines/distributions/
installments/attachments; `receivablesInvoices` with installments/distributions children),
query params `q`/`fields`/`expand`/`limit`/`offset`, standard HTTP verbs.

- Why absent: the world's thesis is a **D365 shop** (the benchmark ships D365 demo data);
  a second full ERP has no evidence-backed workflow here. Our second system is
  QBO-shaped subsidiary books — the researched pattern (small-entity books never migrated).
- Concept portability if ever needed: Oracle's `receivablesInvoices` + installments maps
  onto our three-layer model (posted transaction → open remainder/due dates → settlement);
  the mock would differ mainly in surface style (REST resources + `q` syntax vs MCP
  discovery tools). Census rule applies: no Oracle server until a researched task requires
  an Oracle-shop scenario.

## Summary table

| Real product | Our mock | Tool-surface distance | Backed by |
|---|---|---|---|
| D365 ERP MCP (22 tools) | `erp` (23) | **1:1** | SQL incl. form-session state |
| Intuit QBO MCP (144) | `books` (14) | AR slice ~10%, query language + reports faithful | SQL |
| SEC EDGAR data APIs | `filings` (7) | endpoint-level 1:1, real XBRL values | SQL |
| Graph Excel API | `sheets` (5) | **~10% read / 0% write — biggest gap, upgrade queued** | SQL |
| Gmail-class mail | `email` (5) | read-surface subset (search/read/thread/attachment) | SQL |
| SharePoint-class docs | `docs` (5) | consult surface | SQL |
| Salesforce hosted MCP | — (excluded here; sales world pending) | n/a by evidence | — |
| Oracle Fusion Financials REST | — (excluded; portability documented) | n/a by evidence | — |

## Sources

- https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp (D365 ERP MCP, 22 tools)
- https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0 (Graph workbook API)
- https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/hosted-mcp-servers-overview.html · https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/servers-reference.html · https://developer.salesforce.com/blogs/2025/06/introducing-mcp-support-across-salesforce
- https://docs.oracle.com/en/cloud/saas/financials/26a/farfa/api-invoices.html · https://docs.oracle.com/en/cloud/saas/financials/25d/farfa/api-receivables-invoices.html
- Prior research: `research/erp-domain.md`, `research/domain-workflows.md`, `research/evals-and-benchmarks.md`
