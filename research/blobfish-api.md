# Blobfish API — the world factory service

> Researched 2026-08-10 from https://blobfish.ai/api-docs. The local mirror
> `~/dev/bf-apidocs` contains only website test scaffolding, not docs — use the live site.

## What it is

Blobfish is Nario's RL-environment factory: it turns natural-language prompts + evidence into
executable synthetic worlds — SQLite databases, Python tools, grounded tasks, deterministic
verifiers ("no LLM judge in the reward path"). Worlds download as **Harbor tar archives**.

- Base URL `https://blobfish.ai`; auth `X-API-Key: bf_...` or `Authorization: Bearer bf_...`
  (`POST /api/v1/auth/keys`); anonymous tier 10 generations/day, 60 calls/hour.
- Session isolation: `X-Blobfish-Session` / `Mcp-Session-Id`; `Idempotency-Key` on compute calls.

## Endpoints that matter for finance-world

| Purpose | Endpoint |
|---|---|
| Create world from prompt | `POST /api/v1/environments` · async: `POST /api/v1/sandbox/jobs` (+ `GET .../jobs/{id}`, SSE `/stream`) |
| Quick preview | `POST /api/v1/sandbox/generate` |
| Per-rollout state isolation | `POST /api/v1/environments/{env_id}/sessions` |
| Execute a mock tool | `POST /api/v1/environments/{env_id}/tools/{tool_name}` |
| Score with verifier | `POST /api/v1/environments/{env_id}/verify` · `POST /api/v1/worlds/{worldId}/tasks/{taskId}/evaluate` |
| MCP (streamable HTTP) | `POST /api/v1/worlds/{worldId}/mcp` |
| Import a hand-built world | `POST /api/v1/worlds/import` (canonical executable) · `POST /api/v1/sandbox/worlds/import` (declarative preview) |
| Inspect / QA | `GET /api/v1/sandbox/worlds/{worldId}` · `GET .../quality` |
| Ship | `GET /api/v1/sandbox/worlds/{worldId}/download` (**Harbor tar**) · `POST .../deploy` (RunPod/local) · Customer Release group (9 endpoints, versioned "company gyms") |

World anatomy in responses mirrors the house pattern: **Thesis** (company, domain, vertical,
personas) · **Tables** (SQLite schema + sample rows) · **Tools** (executable, with
OpenAI/Anthropic schemas) · **Tasks** (grounded prompts + required tool calls) · **Verifiers**
(executable VCode assertions).

## Role in finance-world

1. **Format compatibility target**: our hand-built world should satisfy
   `POST /api/v1/worlds/import` (canonical executable world), so it can ride blobfish's
   hosting/MCP/release rails. The import schema = the `world.json` format_version 4 shape seen
   in salesforce-grok.
2. **Optional bootstrap**: `sandbox/jobs` with our finance prompt can generate a draft world to
   mine for table/tool ideas — but our thesis, data chaos, and tasks stay hand-governed
   (grounding beats generation for a customer engagement; blobfish-0's own README concedes
   prompt-grounding is weak).
3. **Serving path for the customer**: Customer Release endpoints + hosted MCP are how xAI would
   consume the finished gym without cloning this repo.

## Sources

- https://blobfish.ai/api-docs (fetched 2026-08-10; 63 endpoints across 11 groups)
- Local: `~/dev/blobfish-0/demo/frontier-lab-eval/README.md` (BlobfishClient usage)
