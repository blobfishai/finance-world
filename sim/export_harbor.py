#!/usr/bin/env python3
"""Export every task as a SELF-CONTAINED Harbor task directory.

The authoring repo keeps the MCP servers, the verifier engine and the oracle at repo level
and shares one built world; a shipped Harbor task may assume none of that. This bakes, per
task: the prepared world (core + that task's seed layers), the runtime that serves it, and
rewritten solve/test scripts that reference only paths inside the task directory.

    dist/harbor/<family>__<slug>/
      task.toml  instruction.md
      environment/Dockerfile
      environment/runtime/{mcp,verifiers,sim}   the servers, verifier, oracle
      environment/state/                        world.sqlite + initial_state.json + workdir
      solution/{walk.json,solve.sh}
      tests/{checks.json,test.sh}                writes reward.txt (the Harbor contract)

Export is gated: a task directory is only kept if, in the exported bundle, the oracle walk
replays and the verifier scores 1 (round-2 ledger row 37 — a task ships only with a
certified oracle). Bundles that fail the gate are deleted and reported, never shipped.

    python3 sim/export_harbor.py                    # all tasks
    python3 sim/export_harbor.py --tasks 'tasks/payment_run/*'
    python3 sim/export_harbor.py --no-gate          # export without replaying (fast, unsafe)
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim"))
from prepare import prepare

DIST = ROOT / "dist/harbor"

BOOTSTRAP = '''#!/usr/bin/env python3
"""Point the baked MCP roster at wherever this task directory actually lives."""
import json, sys
from pathlib import Path

task = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
state = task / "environment/state"
runtime = task / "environment/runtime"
meta = json.loads((state / "world_meta.json").read_text())
servers = {}
for name in meta["servers"]:
    servers[name] = {
        "command": sys.executable,
        "args": [str(runtime / "mcp/servers" / f"{name}_server.py")],
        "env": {"WORLD_DB": str(state / "world.sqlite"),
                "WORLD_NOW": meta["world_now"],
                "WORLD_ROLE": meta["world_role"],
                "TRACE_FILE": str(state / "trace.jsonl")},
    }
(state / ".mcp.json").write_text(json.dumps({"mcpServers": servers}, indent=1))
print(f"bootstrapped {len(servers)} servers -> {state/'.mcp.json'}")
'''

SOLVE_SH = '''#!/bin/bash
# Oracle solution: replay solution/walk.json through the baked MCP servers.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
TASK_DIR="$(dirname "$HERE")"
python3 "$TASK_DIR/environment/runtime/bootstrap.py" "$TASK_DIR"
python3 "$TASK_DIR/environment/runtime/sim/oracle.py" "$TASK_DIR" "$TASK_DIR/environment/state"
'''

TEST_SH = '''#!/bin/bash
# Harbor reward contract: write 1/0 to $VERIFIER_LOG_DIR/reward.txt (default /logs/verifier).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TASK_DIR="$(dirname "$HERE")"
LOGDIR="${VERIFIER_LOG_DIR:-/logs/verifier}"
mkdir -p "$LOGDIR" 2>/dev/null || LOGDIR="$TASK_DIR/.verifier"; mkdir -p "$LOGDIR"
python3 "$TASK_DIR/environment/runtime/verifiers/vcode.py" \\
        --task-dir "$TASK_DIR" --run-dir "$TASK_DIR/environment/state" > "$LOGDIR/verify.json"
python3 - "$LOGDIR" <<'PY'
import json, sys
d = json.load(open(sys.argv[1] + "/verify.json"))
open(sys.argv[1] + "/reward.txt", "w").write(str(d["reward"]))
print("reward:", d["reward"], "failed:", d["failed"])
PY
'''

DOCKERFILE = '''# Self-contained finance-world task. The world, the MCP servers that serve it, the
# verifier and the oracle are all baked in; nothing is fetched at run time.
FROM python:3.12-slim
WORKDIR /app/task
COPY . /app/task
RUN python3 /app/task/environment/runtime/bootstrap.py /app/task
CMD ["sleep", "infinity"]
'''


def export_one(task: Path, gate: bool) -> tuple[str, bool, str]:
    name = f"{task.parent.name}__{task.name}"
    out = DIST / name
    if out.exists(): shutil.rmtree(out)
    (out / "environment").mkdir(parents=True)

    # 1. the prepared world for THIS task (core + its seed layers)
    staged = ROOT / ".runs/export" / task.parent.name / task.name
    info = prepare(task, staged)
    state = out / "environment/state"
    state.mkdir()
    shutil.copy(staged / "world.sqlite", state / "world.sqlite")
    shutil.copy(staged / "initial_state.json", state / "initial_state.json")
    if (staged / "workdir").is_dir():
        shutil.copytree(staged / "workdir", state / "workdir")
    (state / "trace.jsonl").write_text("")

    # what bootstrap.py needs to rebuild .mcp.json wherever the task lands
    roster = json.loads((staged / ".mcp.json").read_text())["mcpServers"]
    any_env = next(iter(roster.values()))["env"]
    (state / "world_meta.json").write_text(json.dumps({
        "servers": sorted(roster),
        "world_now": any_env.get("WORLD_NOW", "2026-03-02T12:00:00Z"),
        "world_role": any_env.get("WORLD_ROLE", "analyst"),
    }, indent=1))

    # 2. the runtime that serves it
    rt = out / "environment/runtime"
    rt.mkdir()
    for sub in ("mcp", "verifiers"):
        shutil.copytree(ROOT / sub, rt / sub, ignore=shutil.ignore_patterns("__pycache__"))
    (rt / "sim").mkdir()
    for f in ("oracle.py", "prepare.py"):
        shutil.copy(ROOT / "sim" / f, rt / "sim" / f)
    (rt / "bootstrap.py").write_text(BOOTSTRAP)

    # 3. the Harbor contract files
    shutil.copy(task / "task.toml", out / "task.toml")
    shutil.copy(task / "instruction.md", out / "instruction.md")
    (out / "environment/Dockerfile").write_text(DOCKERFILE)
    for sub, files in (("solution", ["walk.json"]), ("tests", ["checks.json"])):
        (out / sub).mkdir(exist_ok=True)
        for f in files:
            src = task / sub / f
            if src.exists(): shutil.copy(src, out / sub / f)
    if (task / "steps").is_dir():
        shutil.copytree(task / "steps", out / "steps")
    (out / "solution/solve.sh").write_text(SOLVE_SH)
    (out / "tests/test.sh").write_text(TEST_SH)
    for s in (out / "solution/solve.sh", out / "tests/test.sh"):
        s.chmod(0o755)

    if not gate:
        return name, True, "exported (ungated)"

    # 4. the gate: the bundle must solve and verify itself, using only its own contents
    solve = subprocess.run(["bash", str(out / "solution/solve.sh")], capture_output=True, text=True)
    if solve.returncode != 0:
        shutil.rmtree(out)
        return name, False, f"oracle failed: {(solve.stderr or solve.stdout)[-160:].strip()}"
    test = subprocess.run(["bash", str(out / "tests/test.sh")], capture_output=True, text=True)
    reward_file = out / ".verifier/reward.txt"
    reward = reward_file.read_text().strip() if reward_file.exists() else "?"
    if reward != "1":
        shutil.rmtree(out)
        return name, False, f"verifier scored {reward}: {(test.stdout or test.stderr)[-160:].strip()}"
    # leave the bundle pristine: the gate's own run must not ship as the agent's state
    shutil.rmtree(out / ".verifier", ignore_errors=True)
    shutil.copy(staged / "world.sqlite", state / "world.sqlite")
    (state / "trace.jsonl").write_text("")
    return name, True, "oracle-verified"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="tasks/*/*")
    ap.add_argument("--no-gate", action="store_true")
    a = ap.parse_args()
    tasks = sorted(p for p in ROOT.glob(a.tasks) if (p / "task.toml").exists())
    DIST.mkdir(parents=True, exist_ok=True)
    ok, bad = [], []
    for t in tasks:
        name, good, note = export_one(t, gate=not a.no_gate)
        (ok if good else bad).append((name, note))
        print(f"  {'OK  ' if good else 'FAIL'} {name:52} {note}")
    size = subprocess.run(["du", "-sh", str(DIST)], capture_output=True, text=True).stdout.split()[0]
    print(f"\nexported {len(ok)}/{len(tasks)} tasks to {DIST} ({size})")
    if bad:
        print(f"{len(bad)} REJECTED by the export gate (not shipped):")
        for n, note in bad: print(f"  {n}: {note}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
