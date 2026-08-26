#!/usr/bin/env python3
"""World-correctness validator — proves the world executes correctly, without any model.

Checks per task (all deterministic, all offline):
  S1 structure      required files present; task.name matches its directory
  S2 metadata       family matches dir; acceptance_label present; walk_len == len(walk)
  S3 tools exist    every walk step names a tool that the server actually registers
  S4 drift guard    every answer_check field is mentioned in instruction.md
                    (prompt/verifier drift = the lawfirm AUDIT.md bug class)
  S5 servers        checks' required_servers are all visited by the oracle walk
  S6 seeds          mcp_seed.json tables exist in schema; seed.sql applies cleanly
  S7 determinism    prepare() twice -> identical table hashes
  S8 oracle         the reference walk scores reward 1
  S9 negative       an idle run (no tool calls) scores reward 0  [task is not free]
  S10 no-submit     replaying the walk WITHOUT the final submit scores 0
  S11 gt freshness  any check carrying `gt_sql` still matches what the world computes
  S12 non-collapse  a task declaring naive_answer/graded_answer is not solvable by the
                    naive heuristic (M3; ERP-Bench's objective-certification gate)
                    (catches expected-value drift when the ledger is regenerated)
                    [answer must come from the agent, not from side effects]
Exit 0 iff every check passes. Run before trusting any model score.
"""
import importlib.util, json, shutil, sqlite3, subprocess, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim")); sys.path.insert(0, str(ROOT / "verifiers"))
from prepare import prepare
from vcode import verify_all as verify, table_hashes, steps_of

FAIL = []
def check(ok, task, code, msg):
    if not ok: FAIL.append(f"{task}: [{code}] {msg}")
    return ok

def server_tools():
    out = {}
    for f in sorted((ROOT / "mcp/servers").glob("*_server.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        out[m.S.name] = set(m.S.tools)
    return out

def schema_tables():
    cx = sqlite3.connect(":memory:")
    cx.executescript((ROOT / "world/schema.sql").read_text())
    return {r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def replay(task_dir, run_dir, steps):
    """Replay explicit walk steps in-process (same handlers, same trace)."""
    import os
    env = json.loads((Path(run_dir) / ".mcp.json").read_text())["mcpServers"]["erp"]["env"]
    os.environ.update(env)
    servers = {}
    for st in steps:
        name = st["server"]
        if name not in servers:
            spec = importlib.util.spec_from_file_location(f"{name}_srv_{Path(run_dir).name}",
                                                          ROOT / f"mcp/servers/{name}_server.py")
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            servers[name] = m.S
        try: servers[name].call(st["tool"], st.get("args") or {})
        except Exception: pass

def main():
    tools = server_tools()
    tables = schema_tables()
    tasks = sorted(p for p in ROOT.glob("tasks/*/*") if (p / "task.toml").exists())
    import argparse as _ap
    _a, _ = _ap.ArgumentParser(add_help=False).parse_known_args()
    import sys as _sys
    if "--sample" in _sys.argv:
        import random as _rnd
        n = int(_sys.argv[_sys.argv.index("--sample") + 1])
        _rnd.Random(0).shuffle(tasks); tasks = sorted(tasks[:n])
        print(f"(sampling {len(tasks)} tasks — full gate is `python3 sim/validate.py`)")
    print(f"validating {len(tasks)} tasks against {sum(len(v) for v in tools.values())} tools "
          f"in {len(tools)} servers, {len(tables)} tables\n")

    for t in tasks:
        name = f"{t.parent.name}/{t.name}"
        # S1 structure
        for rel in ["task.toml", "instruction.md", "tests/checks.json", "tests/test.sh",
                    "solution/walk.json", "solution/solve.sh", "environment/Dockerfile"]:
            check((t / rel).exists(), name, "S1", f"missing {rel}")
        cfg = tomllib.loads((t / "task.toml").read_text())
        check(cfg["task"]["name"] == name, name, "S1", f"task.name={cfg['task']['name']!r} != dir")

        # S2 metadata
        meta = cfg.get("metadata", {})
        check(meta.get("family") == t.parent.name, name, "S2", "metadata.family != directory")
        check(bool(meta.get("acceptance_label")), name, "S2", "missing acceptance_label")
        walk = json.loads((t / "solution/walk.json").read_text())
        for sd in steps_of(t):
            if (sd / "walk.json").exists(): walk += json.loads((sd / "walk.json").read_text())
        check(meta.get("walk_len") == len(walk), name, "S2",
              f"walk_len={meta.get('walk_len')} != actual {len(walk)}")

        # S3 tools exist
        for st in walk:
            srv, tool = st["server"], st["tool"]
            if not check(srv in tools, name, "S3", f"unknown server {srv!r}"): continue
            check(tool in tools[srv], name, "S3", f"{srv} has no tool {tool!r}")

        # S4 contract/verifier drift + S5 required servers
        #
        # The invariant is "the agent is told, somewhere it can see, every field it will be
        # graded on". That used to mean the instruction text, because the field list was
        # stapled to the prompt. The contract now lives on the reporting tool
        # (`answer_schema` -> harness `reporting_fields`), so the guard reads the schema —
        # repointed, not relaxed. A graded field absent from the schema is ungradeable in
        # practice: nothing would ever tell the agent to file it.
        checks = json.loads((t / "tests/checks.json").read_text())
        seed = t / "environment/seed/mcp_seed.json"
        schema = set()
        if seed.exists():
            try:
                schema = {r["field"].lower()
                          for r in json.loads(seed.read_text()).get("answer_schema", [])}
            except Exception:
                schema = set()
        instr = (t / "instruction.md").read_text().lower()
        for c in checks.get("answer_checks", []):
            f = c["field"].lower()
            check(f in schema or f in instr, name, "S4",
                  f"answer field {c['field']!r} is graded but appears in neither the task's "
                  f"answer_schema nor its instruction — nothing would tell the agent to file it")
        for sd in steps_of(t):                      # each later turn states its own fields
            sc = json.loads((sd / "checks.json").read_text())
            si = (sd / "instruction.md").read_text().lower() if (sd / "instruction.md").exists() else ""
            for c in sc.get("answer_checks", []):
                f = c["field"].lower()
                check(f in schema or f in si, name, "S4",
                      f"step {sd.name}: field {c['field']!r} in neither answer_schema nor "
                      f"its instruction")
            checks.setdefault("trace_checks", []).extend(sc.get("trace_checks", []))
        walk_servers = {s["server"] for s in walk}
        for c in checks.get("trace_checks", []):
            if c["type"] == "required_servers":
                for s in c["servers"]:
                    check(s in walk_servers, name, "S5", f"required server {s!r} not in oracle walk")

        # S6 seeds
        seed = t / "environment/seed"
        mj = seed / "mcp_seed.json"
        if mj.exists():
            for tbl in json.loads(mj.read_text()):
                check(tbl in tables, name, "S6", f"mcp_seed table {tbl!r} not in schema")

        # S7 determinism (prepare twice)
        a = prepare(t, ROOT / ".runs/validate" / t.name / "a")
        h1 = table_hashes(a["db"])
        b = prepare(t, ROOT / ".runs/validate" / t.name / "b")
        check(h1 == table_hashes(b["db"]), name, "S7", "prepare() is not deterministic")

        # S8 oracle green
        run_o = ROOT / ".runs/validate" / t.name / "oracle"
        prepare(t, run_o); replay(t, run_o, walk)
        check(verify(t, run_o)["reward"] == 1, name, "S8", "oracle walk does not score 1")

        # S12 objective non-collapse (docs/HARD-LAYER-DESIGN.md M3, ported from ERP-Bench's
        # _objective_family_certified): a task that declares a naive baseline must not be
        # solvable by it. Declaring the two and having them agree is the failure mode.
        naive, graded = meta.get("naive_answer"), meta.get("graded_answer")
        if naive is not None or graded is not None:
            check(naive is not None and graded is not None, name, "S12",
                  "declare both naive_answer and graded_answer, or neither")
            if naive is not None and graded is not None:
                norm_ = lambda s: sorted(x.strip().lower() for x in str(s).split(",") if x.strip())
                check(norm_(naive) != norm_(graded), name, "S12",
                      f"naive answer equals the graded answer ({graded!r}) - the task collapses "
                      f"to the naive heuristic and cannot measure the stated objective")

        # S11 ground-truth freshness: a check with gt_sql must still equal the world
        cxv = sqlite3.connect(run_o / "world.sqlite")
        for d in [t] + list(steps_of(t)):
            cp = (d / "tests/checks.json") if (d / "tests/checks.json").exists() else (d / "checks.json")
            for c in json.loads(cp.read_text()).get("answer_checks", []):
                if "gt_sql" not in c: continue
                _row = cxv.execute(c["gt_sql"]).fetchone()
                live = _row[0] if _row else None
                if live is None:
                    continue      # write-task output: not derivable pre-episode (A13)
                tol = max(float(c.get("tol_abs", 0.01)), abs(float(c["expect"])) * float(c.get("tol_rel", 0)))
                check(abs(float(live) - float(c["expect"])) <= tol, name, "S11",
                      f"stale ground truth for {c['field']}: expects {c['expect']}, world says {live}")
        cxv.close()
        # the three world copies this task just used are scratch; at ~1.2k tasks keeping
        # them costs several GB (docs/AUDIT.md A12)
        shutil.rmtree(ROOT / ".runs/validate" / t.name, ignore_errors=True)

        # S9 negative control: idle run must fail
        run_n = ROOT / ".runs/validate" / t.name / "idle"
        prepare(t, run_n)
        check(verify(t, run_n)["reward"] == 0, name, "S9", "idle run scores 1 — task is free")

        # S10 walk without the final submit must fail
        submitless = [s for s in walk if not (s["server"] == "harness" and s["tool"] == "submit_answer")]
        if len(submitless) < len(walk):
            run_s = ROOT / ".runs/validate" / t.name / "nosubmit"
            prepare(t, run_s); replay(t, run_s, submitless)
            check(verify(t, run_s)["reward"] == 0, name, "S10",
                  "scores 1 without submitting — answer leaks from side effects")
        else:
            check(False, name, "S10", "walk has no harness.submit_answer step")

        # the S9/S10 worlds are created AFTER the mid-loop cleanup above; without this
        # second sweep a full run leaks ~21MB per task (~32GB across the task tree)
        shutil.rmtree(ROOT / ".runs/validate" / t.name, ignore_errors=True)

        print(f"  {'ok ' if not any(f.startswith(name + ':') for f in FAIL) else 'FAIL'} {name}")

    print()
    if FAIL:
        print(f"VALIDATION FAILED — {len(FAIL)} finding(s):")
        for f in FAIL: print("  -", f)
        return 1
    print(f"VALIDATION PASSED — {len(tasks)} tasks, 10/10 checks each.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
