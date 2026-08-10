# Tool census — every server must earn its place

Guard against the fixed-vendor-roster anti-pattern (salesforce-grok packages ship
`salesforce, stripe, email, slack, calendar, erp, jira, github, notion, pagerduty` into
every world regardless of domain — a sales world showing pagerduty/github is how you know a
roster was copied, not chosen). **Rule: a server exists here iff (a) research evidence says
this team uses that system class, and (b) at least one shipped task requires it.** A server
that no task requires gets deleted, not kept "for realism".

| Server | Why it exists (evidence) | Task families that require it |
|---|---|---|
| `erp` | The buyer workload is D365 ERP QA; FinanceBenchmark runs against D365 USMF and ships its demo data (`research/evals-and-benchmarks.md`, `research/erp-domain.md`) | erp_qa, cross_system, business_brief (internal-relationship check) |
| `books` | Subsidiary AR outside the main ERP is a documented fragmentation pattern; QBO has the richest documented MCP surface to imitate (`research/domain-workflows.md` §3, `research/erp-domain.md`) | cross_system |
| `sheets` | Excel is the shadow system: 94% close in Excel, 89% run half their workflows in it (`research/domain-workflows.md` §3) | cross_system |
| `email` | 68% of invoices are manually keyed from email; approvals/remittance live in threads (`research/domain-workflows.md` §3) | erp_qa (statements), cross_system |
| `filings` | Public-entity research is a named workload; EDGAR is the ground-truth source; frozen real XBRL facts keep it deterministic (`research/domain-workflows.md` §4) | finance_qa, business_brief |
| `docs` | Policies are consult-don't-know knowledge (dunning runbook, discount policy, brief template); house anchor pattern (`research/domain-workflows.md` §2) | erp_qa, business_brief |
| `harness` | Eval-only answer submission; off the business surface (house rule) | all |

## Deliberately excluded (and why)

- **slack/jira/github/pagerduty/notion/calendar** — engineering/ops tools; no finance
  workflow in our research touches them. Their presence would be roster-copying.
- **stripe / payment rails** — payments *execution* is out of scope for wave 0-1 (read-only
  world); revisit only if a researched collections_ops task needs a payment-status read.
- **bank portal** — in the research (timing-gap chaos) but not yet required by a shipped
  task; add together with the bank-reconciliation task, not before.
- **CRM (salesforce/hubspot)** — that's the *sales* world's spine, not finance's.

## Change control

Adding a server requires: evidence row here + at least one task whose checks require it +
an entry in `mcp/mcp-servers.json` with `shaped_after`. PR/commit message must cite the
research doc. Same bar applies to *tables*: schema additions must name the workflow that
reads them.
