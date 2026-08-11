#!/bin/bash
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
