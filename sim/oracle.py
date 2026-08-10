#!/usr/bin/env python3
"""Oracle agent: replays a task's solution/walk.json through the real MCP tool handlers
in-process (same trace, same verifier). Admission rule: a task ships only if this passes."""
import importlib.util, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_server(name):
    spec = importlib.util.spec_from_file_location(f"{name}_server", ROOT / f"mcp/servers/{name}_server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.S

def replay(task_dir, run_dir):
    env = json.loads((Path(run_dir) / ".mcp.json").read_text())["mcpServers"]["erp"]["env"]
    os.environ.update(env)
    walk = json.loads((Path(task_dir) / "solution/walk.json").read_text())
    servers = {}
    for i, step in enumerate(walk):
        s = step["server"]
        if s not in servers: servers[s] = load_server(s)
        out = servers[s].call(step["tool"], step.get("args") or {})
        if isinstance(out, dict) and "error" in out:
            print(f"step {i} {s}.{step['tool']} -> error: {out['error']}", file=sys.stderr)
    return len(walk)

if __name__ == "__main__":
    n = replay(sys.argv[1], sys.argv[2])
    print(json.dumps({"walk_steps": n}))
