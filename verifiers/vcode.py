#!/usr/bin/env python3
"""Deterministic verifier engine. No LLM in the reward path.

Reads tests/checks.json from a task dir and a run dir (world.sqlite, trace.jsonl,
initial_state.json). Emits {"reward": 0|1, "failed": [...]} on stdout; always exits 0.

checks.json:
  answer_checks: [{field, type: number|string|contains_all, expect, tol_abs?, tol_rel?}]
      number: value parsed from "$1,234.56", "1234.56", 1234.56; pass if within
              max(tol_abs, |expect|*tol_rel); default exact to 0.01.
      string: case/space-insensitive equality (use expect "none" for empty-answer traps).
      contains_all: every listed substring appears (case-insensitive) in the value.
  trace_checks: [{type: required_servers, servers: [...]},
                 {type: min_calls, server, n},
                 {type: reads_before_submit}]
  state_checks: [{type: writes_only, tables: ["answers"]}]  # anti-hack veto
"""
import json, re, sqlite3, hashlib, sys
from pathlib import Path

def table_hashes(db):
    cx = sqlite3.connect(db)
    out = {}
    for (t,) in cx.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        rows = cx.execute(f"SELECT * FROM {t}").fetchall()
        h = hashlib.sha256(repr(sorted(map(repr, rows))).encode()).hexdigest()[:16]
        out[t] = [len(rows), h]
    cx.close()
    return out

def parse_number(v):
    if isinstance(v, (int, float)): return float(v)
    s = re.sub(r"[,$\s]|USD", "", str(v), flags=re.I).rstrip("%")
    m = re.match(r"^-?\d+(\.\d+)?$", s)
    return float(s) if m else None

def norm(v): return re.sub(r"\s+", " ", str(v)).strip().lower()

def verify(task_dir, run_dir):
    """Verify one step. `task_dir` is a task root (tests/checks.json) or a step dir (checks.json)."""
    p = Path(task_dir) / "tests/checks.json"
    checks = json.loads((p if p.exists() else Path(task_dir) / "checks.json").read_text())
    db = Path(run_dir) / "world.sqlite"
    failed = []

    cx = sqlite3.connect(db)
    answers = {f: json.loads(v) for f, v in cx.execute("SELECT field, value FROM answers")}
    cx.close()

    for c in checks.get("answer_checks", []):
        fld, typ = c["field"], c.get("type", "string")
        name = f"answer:{fld}"
        if fld not in answers:
            failed.append(name + ":missing"); continue
        got = answers[fld]
        if typ == "number":
            g = parse_number(got)
            if g is None: failed.append(name + ":not_numeric"); continue
            exp = float(c["expect"])
            tol = max(float(c.get("tol_abs", 0.01)), abs(exp) * float(c.get("tol_rel", 0)))
            if abs(g - exp) > tol: failed.append(name + f":off(got={g})")
        elif typ == "contains_all":
            g = norm(got)
            missing = [s for s in c["expect"] if norm(s) not in g]
            if missing: failed.append(name + f":missing_terms({missing})")
        else:
            if norm(got) != norm(c["expect"]): failed.append(name + f":mismatch(got={norm(got)[:60]})")

    trace = []
    tf = Path(run_dir) / "trace.jsonl"
    if tf.exists():
        trace = [json.loads(l) for l in tf.read_text().splitlines() if l.strip()]
    for c in checks.get("trace_checks", []):
        t = c["type"]
        if t == "required_servers":
            used = {r["server"] for r in trace if r.get("ok")}
            miss = [s for s in c["servers"] if s not in used]
            if miss: failed.append(f"trace:required_servers_missing({miss})")
        elif t == "min_calls":
            n = sum(1 for r in trace if r["server"] == c["server"] and r.get("ok"))
            if n < c["n"]: failed.append(f"trace:min_calls({c['server']}<{c['n']})")
        elif t == "reads_before_submit":
            first_submit = next((i for i, r in enumerate(trace)
                                 if r["server"] == "harness" and r["tool"] == "submit_answer"), None)
            reads_before = any(r["server"] != "harness" and r.get("ok") for r in trace[:first_submit or 0])
            if first_submit is None or not reads_before:
                failed.append("trace:no_reads_before_submit")

    init = json.loads((Path(run_dir) / "initial_state.json").read_text())
    final = table_hashes(db)
    RUNTIME_TABLES = {"erp_form_sessions"}  # tool-session state, never an off-task write
    cx = sqlite3.connect(db)
    for c in checks.get("state_checks", []):
        t = c["type"]
        if t == "writes_only":
            allowed = set(c.get("tables", ["answers"])) | RUNTIME_TABLES
            dirty = [x for x in final if x not in allowed and final[x] != init.get(x)]
            if dirty: failed.append(f"state:off_task_writes({dirty})")
        elif t == "row_count":
            n = cx.execute(c["sql"]).fetchone()[0]
            if n != c["expect"]:
                failed.append(f"state:row_count({c.get('name', c['sql'][:40])}: got {n}, want {c['expect']})")
        elif t == "cell_equals":
            row = cx.execute(c["sql"]).fetchone()
            got = row[0] if row else None
            exp = c["expect"]
            ok = (abs(float(got) - float(exp)) <= float(c.get("tol_abs", 0))
                  if isinstance(exp, (int, float)) and got is not None
                  else norm(got) == norm(exp))
            if not ok:
                failed.append(f"state:cell_equals({c.get('name', c['sql'][:40])}: got {got!r}, want {exp!r})")
    cx.close()

    return {"reward": 1 if not failed else 0, "failed": failed,
            "n_tool_calls": len(trace),
            "servers_used": sorted({r['server'] for r in trace})}

def steps_of(task_dir):
    """Multi-step tasks (Harbor [[steps]] shape): steps/NN/{instruction.md,checks.json,walk.json}.
    Step 0 is the task root; later steps run in the SAME world, so state carries across turns."""
    d = Path(task_dir) / "steps"
    return sorted(p for p in d.glob("*") if (p / "checks.json").exists()) if d.is_dir() else []

def verify_all(task_dir, run_dir):
    """Verify the root step plus every later step; reward 1 only if all pass."""
    res = verify(task_dir, run_dir)
    out = {"reward": res["reward"], "failed": list(res["failed"]),
           "n_tool_calls": res["n_tool_calls"], "servers_used": res["servers_used"], "steps": 1}
    for s in steps_of(task_dir):
        r = verify(s, run_dir)
        out["steps"] += 1
        out["failed"] += [f"{s.name}:{f}" for f in r["failed"]]
        out["reward"] = min(out["reward"], r["reward"])
    return out

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True); ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    print(json.dumps(verify_all(a.task_dir, a.run_dir)))
