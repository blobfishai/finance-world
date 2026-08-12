#!/bin/bash
# Oracle solution: replay solution/walk.json through the real MCP tool handlers.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
TASK_DIR="$(dirname "$HERE")"
REPO_ROOT="${REPO_ROOT:-$(cd "$TASK_DIR/../../.." && pwd)}"
RUN_DIR="${RUN_DIR:-/app/run}"
python3 "$REPO_ROOT/sim/oracle.py" "$TASK_DIR" "$RUN_DIR"
