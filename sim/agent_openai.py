#!/usr/bin/env python3
"""Run a task with any OpenAI-compatible chat-completions model (DeepSeek, Qwen, Kimi, xAI, …).

The Claude path (`claude -p --mcp-config`) speaks MCP over stdio. Rather than reimplement an
MCP client, this loads the same server modules in-process exactly as `sim/oracle.py` does and
exposes their tool registries as OpenAI function specs. That matters for verification: the
servers write TRACE_FILE themselves on every call, so a run through this path produces the
same trace the verifier's trace_checks read — required_servers, min_calls and
reads_before_submit all work unchanged, and no grading code is model-specific.

Tool names are namespaced `<server>__<tool>` (mirroring the `mcp__erp__…` convention the
Claude path sees), so the two paths present the same surface under different syntax.

Config, in precedence order — CLI flag, then env:
    --base-url / OPENAI_BASE_URL     default https://api.deepseek.com
    --api-key  / DEEPSEEK_API_KEY | OPENAI_API_KEY
    --model    (required)            e.g. deepseek-chat, deepseek-reasoner
"""
import argparse, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim"))
from oracle import load_server

SERVERS = ["erp", "books", "sheets", "email", "filings", "docs", "harness"]

SYSTEM = """You are a finance analyst working inside a company's real systems. Answer only \
from what the tools return — never from memory, and never by guessing a plausible figure.

Rules that are graded:
- Every number you report must come from a tool call you actually made.
- "I found none" is a valid and expected answer when the data says so; say it plainly rather \
than inventing a record.
- Consult the policy and contract documents rather than assuming the rule; where a document \
and a field disagree, read the document's effective date before relying on it.
- Finish by calling harness__submit_answer with every field the task asks for. A task is not \
complete until you have submitted."""


def build_tools(servers):
    """OpenAI function specs from the MCP tool registries, namespaced by server."""
    specs, route = [], {}
    for sname, srv in servers.items():
        for tname, (_fn, schema) in srv.tools.items():
            full = f"{sname}__{tname}"
            route[full] = (srv, tname)
            specs.append({"type": "function", "function": {
                "name": full,
                "description": f"[{sname}] {schema['description']}",
                "parameters": schema.get("inputSchema") or {"type": "object", "properties": {}},
            }})
    return specs, route


def run(task_dir, run_dir, model, base_url, api_key, budget, timeout_s=900):
    from openai import OpenAI
    task_dir, run_dir = Path(task_dir), Path(run_dir)
    env = json.loads((run_dir / ".mcp.json").read_text())["mcpServers"]["erp"]["env"]
    os.environ.update(env)

    servers = {s: load_server(s) for s in SERVERS}
    specs, route = build_tools(servers)
    client = OpenAI(api_key=api_key, base_url=base_url)

    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": (task_dir / "instruction.md").read_text()}]
    t0, turns, final, err = time.time(), 0, "", None

    while turns < budget:
        if time.time() - t0 > timeout_s:
            err = f"AGENT_TIMEOUT({timeout_s}s)"; break
        turns += 1
        try:
            r = client.chat.completions.create(model=model, messages=msgs,
                                               tools=specs, tool_choice="auto")
        except Exception as e:
            err = f"api error: {e!r}"; break
        m = r.choices[0].message
        msgs.append({"role": "assistant", "content": m.content or "",
                     "tool_calls": [tc.model_dump() for tc in (m.tool_calls or [])] or None})
        if not m.tool_calls:
            final = m.content or ""
            break
        for tc in m.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            if name not in route:
                out = {"error": f"unknown tool {name}"}
            else:
                srv, tool = route[name]
                try:
                    out = srv.call(tool, args)          # traces itself, like every other path
                except Exception as e:
                    out = {"error": repr(e)}
            msgs.append({"role": "tool", "tool_call_id": tc.id,
                         "content": json.dumps(out, default=str)[:12000]})

    return {"final_text": (final or err or "")[:2000], "num_turns": turns,
            "agent_error": bool(err), "error": err}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True); ap.add_argument("--run-dir", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com"))
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    ap.add_argument("--budget", type=int, default=40)
    a = ap.parse_args()
    if not a.api_key:
        sys.exit("no API key: set DEEPSEEK_API_KEY (or pass --api-key)")
    print(json.dumps(run(a.task, a.run_dir, a.model, a.base_url, a.api_key, a.budget)))
