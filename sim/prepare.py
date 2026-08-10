#!/usr/bin/env python3
"""Materialize one task run: core world + the task's own seed layers.

Task seed layers (all optional, all task-level by design):
  environment/seed/seed.sql        special core data (SQL overlay on any table)
  environment/seed/mcp_seed.json   {table_name: [row dicts]} declarative per-server seeding
  environment/seed/documents/*.md  seeded documents -> docs_documents (docs MCP server)
  environment/seed/inputs/*        input files staged into the agent workdir (container runs)
Produces run_dir/{world.sqlite, .mcp.json, trace.jsonl, initial_state.json, workdir/}.
"""
import json, shutil, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVERS = ["erp", "books", "sheets", "email", "filings", "docs", "harness"]

def prepare(task_dir, run_dir):
    task_dir, run = Path(task_dir), Path(run_dir)
    if run.exists(): shutil.rmtree(run)
    (run / "workdir").mkdir(parents=True)
    db = run / "world.sqlite"
    shutil.copy(ROOT / "world/build/core.sqlite", db)
    cx = sqlite3.connect(db)
    seed = task_dir / "environment/seed"

    sql = seed / "seed.sql"
    if sql.exists(): cx.executescript(sql.read_text())

    mj = seed / "mcp_seed.json"
    if mj.exists():
        for table, rows in json.loads(mj.read_text()).items():
            for row in rows:
                row = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in row.items()}
                cols = ",".join(row); ph = ",".join("?" * len(row))
                cx.execute(f"INSERT OR REPLACE INTO {table}({cols}) VALUES({ph})", list(row.values()))

    docs = seed / "documents"
    if docs.is_dir():
        for p in sorted(docs.glob("*.md")):
            body = p.read_text()
            title = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ")), p.stem)
            dtype = p.stem.split("--")[0] if "--" in p.stem else "doc"
            cx.execute("INSERT OR REPLACE INTO docs_documents VALUES(?,?,?,?,?,?)",
                       (p.stem, title, dtype, "1.0", "2026-01-01", body))

    cx.commit()
    now = cx.execute("SELECT value FROM meta WHERE key='WORLD_NOW'").fetchone()[0]
    cx.close()

    inputs = seed / "inputs"
    if inputs.is_dir():
        for p in inputs.iterdir(): shutil.copy(p, run / "workdir" / p.name)

    trace = run / "trace.jsonl"; trace.touch()
    import tomllib
    meta = tomllib.loads((task_dir / "task.toml").read_text()).get("metadata", {})
    env = {"WORLD_DB": str(db), "WORLD_NOW": now, "TRACE_FILE": str(trace),
           "WORLD_ROLE": meta.get("agent_role", "analyst")}
    mcp = {"mcpServers": {s: {"command": "python3",
                              "args": [str(ROOT / f"mcp/servers/{s}_server.py")],
                              "env": env} for s in SERVERS}}
    (run / ".mcp.json").write_text(json.dumps(mcp, indent=1))

    sys.path.insert(0, str(ROOT / "verifiers"))
    from vcode import table_hashes
    (run / "initial_state.json").write_text(json.dumps(table_hashes(db)))
    return {"db": str(db), "env": env, "mcp_config": str(run / ".mcp.json")}

if __name__ == "__main__":
    print(json.dumps(prepare(sys.argv[1], sys.argv[2])))
