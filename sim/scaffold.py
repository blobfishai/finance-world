#!/usr/bin/env python3
"""Stamp Harbor boilerplate (tests/test.sh, solution/solve.sh, environment/Dockerfile)
into every task dir. Task-specific files (task.toml, instruction.md, checks.json,
walk.json, seed/*) are authored by hand and never touched here."""
import stat, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEST_SH = """#!/bin/bash
# Harbor reward contract: write 1/0 to $VERIFIER_LOG_DIR/reward.txt (default /logs/verifier).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TASK_DIR="${TASK_DIR:-$(dirname "$HERE")}"
REPO_ROOT="${REPO_ROOT:-$(cd "$TASK_DIR/../../.." && pwd)}"
RUN_DIR="${RUN_DIR:-/app/run}"
LOGDIR="${VERIFIER_LOG_DIR:-/logs/verifier}"
mkdir -p "$LOGDIR"
python3 "$REPO_ROOT/verifiers/vcode.py" --task-dir "$TASK_DIR" --run-dir "$RUN_DIR" > "$LOGDIR/verify.json"
python3 - "$LOGDIR" <<'PY'
import json, sys
d = json.load(open(sys.argv[1] + "/verify.json"))
open(sys.argv[1] + "/reward.txt", "w").write(str(d["reward"]))
print("reward:", d["reward"], "failed:", d["failed"])
PY
"""

SOLVE_SH = """#!/bin/bash
# Oracle solution: replay solution/walk.json through the real MCP tool handlers.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
TASK_DIR="$(dirname "$HERE")"
REPO_ROOT="${REPO_ROOT:-$(cd "$TASK_DIR/../../.." && pwd)}"
RUN_DIR="${RUN_DIR:-/app/run}"
python3 "$REPO_ROOT/sim/oracle.py" "$TASK_DIR" "$RUN_DIR"
"""

DOCKERFILE = """# Materialized fully by the Stage-6 Harbor exporter, which bakes into the image:
#   /app/run/world.sqlite   (core + this task's seed layers, via sim/prepare.py)
#   /app/mcp/, /app/verifiers/, /app/sim/   (servers, verifier engine, oracle)
# Local calibration runs use sim/run_task.py directly and do not need Docker.
FROM python:3.12-slim
WORKDIR /app
COPY . /app/task
CMD ["sleep", "infinity"]
"""

def main():
    stamped = 0
    for task in sorted(ROOT.glob("tasks/*/*")):
        if not (task / "task.toml").exists(): continue
        for rel, content in [("tests/test.sh", TEST_SH),
                             ("solution/solve.sh", SOLVE_SH),
                             ("environment/Dockerfile", DOCKERFILE)]:
            p = task / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            if rel.endswith(".sh"): p.chmod(p.stat().st_mode | stat.S_IEXEC)
        stamped += 1
    print(f"stamped boilerplate into {stamped} task dirs")

if __name__ == "__main__":
    main()
