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

## Why a finance person opens each tool (persona scenarios)

Each scenario comes from the researched workflows (`research/domain-workflows.md`) and maps
to a shipped task where one exists.

**erp** — the system of record, opened dozens of times a day:
- *AR analyst, Monday morning*: "who went past due over the weekend?" → aged balances →
  prioritized collections worklist. (task: ar-balance-fourthcoffee-east)
- *Credit manager*: sales begs to release a blocked order → credit limit vs open balance vs
  oldest past-due → release or hold. (task: credit-limit-adatum)
- *Collections analyst*: before escalating Sparrow Retail, what letter level are they at and
  have they paid since? (task: collections-sparrow)
- *AP manager, cash call*: how much AP is overdue right now; what comes due this week?
  (tasks: ap-overdue-usmf, due-next-week-adventure)
- *AP specialist*: vendor phones "where's my payment?" → vendor transactions + settlement.
- *Controller at close*: does the subledger tie to the GL?

**books** — because the subsidiary never migrated (documented post-acquisition pattern):
- *Controller, group roll-up*: consolidated AR exposure must include CES Direct's invoices,
  which exist only in QBO. (task: total-ar-adventure-group)
- *AR analyst, dispute*: customer says "we returned that batch" — the credit memo lives in
  the subsidiary's books, not the ERP. (same task, the credit-memo trap)

**sheets** — Excel is the real close system (94% close in Excel — Ledge):
- *AR analyst*: promise-to-pay notes live in the collections tracker, not the ERP — and the
  tracker can be a letter-level stale (version drift).
- *AP specialist*: manual invoice log for counterparties whose ERP entity setup is pending
  with master data. (tasks: email-invoice-meadow, total-ar-adventure-group-v2 side-log)
- *Controller*: month-end summary snapshots — knowing which file is stale is part of the
  job (get_spreadsheet_metadata exists for exactly this).

**email** — where paper actually arrives (68% of invoices manually keyed from email):
- *AP specialist*: the vendor's February statement with negotiated discount terms is an
  attachment in the AP mailbox. (task: cash-disc-fourthcoffee-east)
- *AR analyst*: remittance advice decoupled from the wire (46% cite unapplied cash) — the
  email says which invoices a payment covers.
- *Anyone pre-audit*: "who approved this?" — approvals live in threads. (task:
  email-invoice-meadow — the invoice exists only here)

**filings** — grounded counterparty research, never from memory:
- *Credit manager*: credit evaluation of a large prospect → leverage ratios from 10-Ks per
  the 5-C's memo structure. (tasks: brief-caterpillar, brief-caterpillar-v2)
- *FP&A / treasury*: figures for the committee brief with period + form cited. (task:
  xom-current-assets)
- *Procurement*: supplier-viability screen (Z-score inputs) on critical vendors.

**docs** — policies are consult-don't-know knowledge:
- *Collections analyst mid-escalation*: what day threshold triggers letter 3 and what fee
  posts? → dunning runbook. (task: collections-sparrow)
- *AP specialist*: is a 2/10 net 30 worth taking this week? → discount-capture policy
  (~36% annualized: always). (task: cash-disc-fourthcoffee-east)
- *Credit manager*: which band is a 1.40 D/E? → credit policy thresholds. (task:
  brief-caterpillar-v2)
- *Any analyst writing a brief*: the required section structure. (template doc)

**harness** — not a finance tool: the eval-only submission surface that turns the agent's
answer into verifiable state.

## Change control

Adding a server requires: evidence row here + at least one task whose checks require it +
an entry in `mcp/mcp-servers.json` with `shaped_after`. PR/commit message must cite the
research doc. Same bar applies to *tables*: schema additions must name the workflow that
reads them.
