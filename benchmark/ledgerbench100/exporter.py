#!/usr/bin/env python3
"""Build the LedgerBench-100 release: official Harbor 1.4 task packs + dataset.toml.

Extends sim/export_harbor.py's discipline (self-contained bundles, self-replay
gate) to the CounselBench-100 release shape:

  dist/ledgerbench-100/harbor/tasks/lgr100-NNN-<slug>/
    task.toml                      schema 1.4, name = "blobfishai/lgr100-NNN-<slug>",
                                   [[environment.mcp_servers]] streamable-http entries
    instruction.md                 the authored persona chat message, unchanged
    environment/Dockerfile         agent image: digest-pinned python:3.12-slim + tool CLI
    environment/docker-compose.yaml  main + world services (healthchecked)
    environment/tool               stdlib HTTP JSON-RPC CLI for shell agents
    environment/world/             the world image source: server.py bridge,
                                   spec.json, gzipped prepared world, taskspec
                                   (checks.json), and the mcp/verifier runtime
    solution/{walk.json,solve.py,solve.sh}  oracle replay over the LIVE MCP surface
    tests/test.sh                  POSTs token-gated /verify; writes report.json,
                                   reward.json, reward.txt; prints {"passed","reward"}

  dist/ledgerbench-100/harbor/dataset/dataset.toml
    one [[tasks]] entry per task with the registry sha256 content digest
    (the exact Packager.compute_content_hash algorithm from harbor 0.21).

Gate: a pack ships only if, using ONLY its own contents (its world.sqlite.gz, its
runtime modules, its walk.json), the oracle replay scores reward 1. Failures are
deleted and reported, never shipped.

Deterministic: no network, no clock in any shipped byte (gzip mtime pinned to 0).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import shutil
import stat
import sys
import tempfile
import tomllib
from pathlib import Path

from realism import decision_options, distinct_walk, release_prompt, rubric_criteria

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "sim"))
from prepare import prepare  # noqa: E402

RELEASE_NAME = "LedgerBench-100"
RELEASE_SLUG = "ledgerbench-100"
RELEASE_VERSION = "2.0.0"
HARBOR_ORG = "blobfishai"
DATA_LICENSE = "CC-BY-4.0"
CODE_LICENSE = "Apache-2.0"
WORLD_PORT = 8974
# The same digest-pinned public base image CounselBench-100 shipped and proved
# pullable in its Dockerized trials.
BASE_IMAGE = "python:3.12-slim@sha256:7a8b475003c4fe15a2cd4e55e5cfc2f3560bdc9333d624f24cdd6d4340fd7a17"
SERVERS = ["books", "docs", "email", "erp", "filings", "harness", "odoo", "sheets"]
IGNORED_SUFFIXES = (".pyc", ".swp", ".swo", ".DS_Store")


def verification_token(task_id: str) -> str:
    """Capability token pattern (CounselBench-100): the world stores only the digest."""
    return hashlib.sha256(
        f"LedgerBench-100 verifier capability::{task_id}".encode()
    ).hexdigest()


def write_text(path: Path, value: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_json(path: Path, value) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def task_toml(entry: dict, source_meta: dict, description: str) -> str:
    task_name = f"{HARBOR_ORG}/{entry['task_id']}"
    keywords = ["finance", "erp", "mcp", "deterministic", entry["family"]]
    mcp_blocks = "\n".join(
        f'''[[environment.mcp_servers]]
name = "{server}"
transport = "streamable-http"
url = "http://world:{WORLD_PORT}/mcp/{server}"
'''
        for server in SERVERS
    )
    origin = str(source_meta.get("origin", "")).replace('"', "'")
    return f'''schema_version = "1.4"

[task]
name = "{task_name}"
version = "{RELEASE_VERSION}"
description = "{description}"
authors = []
keywords = {json.dumps(keywords)}

[metadata]
benchmark = "{RELEASE_NAME}"
benchmark_version = "{RELEASE_VERSION}"
task_id = "{entry['task_id']}"
source_task = "{entry['source_task']}"
family = "{entry['family']}"
provenance = "{entry['provenance']}"
difficulty = "{entry['difficulty']}"
origin = "{origin}"
walk_len = {entry['walk_len']}
public_criteria = {entry.get('criteria_count', 0)}
n_answer_checks = {entry['n_answer_checks']}
n_state_checks = {entry['n_state_checks']}
n_trace_checks = {entry['n_trace_checks']}
mcp_servers = {len(SERVERS)}
mcp_tools = 66
deterministic_verifier = true
high_level_employee_request = true
llm_judge = false
data_license = "{DATA_LICENSE}"
code_license = "{CODE_LICENSE}"

[verifier]
timeout_sec = 180.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 900.0
cpus = 1
memory_mb = 2048
storage_mb = 4096
gpus = 0

{mcp_blocks}'''


def compose_yaml(has_inputs: bool) -> str:
    inputs_block = """    volumes:
      - type: bind
        source: ./inputs
        target: /workspace/inputs
        read_only: true
""" if has_inputs else ""
    return f"""services:
  main:
    depends_on:
      world:
        condition: service_healthy
    environment:
      LEDGERBENCH_MCP_BASE: http://world:{WORLD_PORT}
{inputs_block}
  world:
    build:
      context: ./world
      dockerfile: Dockerfile
    expose:
      - "{WORLD_PORT}"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:{WORLD_PORT}/health', timeout=2)"]
      interval: 2s
      timeout: 5s
      retries: 60
      start_period: 2s
"""


def main_dockerfile(has_inputs: bool) -> str:
    inputs_line = "COPY inputs /workspace/inputs\n" if has_inputs else ""
    return f"""FROM {BASE_IMAGE}
WORKDIR /workspace
COPY tool /usr/local/bin/tool
{inputs_line}RUN chmod 0755 /usr/local/bin/tool
CMD ["sleep", "infinity"]
"""


def world_dockerfile() -> str:
    return f"""FROM {BASE_IMAGE}
WORKDIR /opt/world
COPY . /opt/world/
RUN python3 -c "import gzip, shutil; shutil.copyfileobj(gzip.open('/opt/world/state/world.sqlite.gz'), open('/opt/world/state/world.sqlite', 'wb'))"
EXPOSE {WORLD_PORT}
CMD ["python3", "/opt/world/server.py"]
"""


def tool_cli() -> str:
    return r'''#!/usr/bin/env python3
"""LedgerBench tool CLI: call the world's MCP servers over Streamable HTTP.

    tool servers
    tool list <server>
    tool call <server> <tool_name> '{"argument": "value"}'
"""
import json
import os
import sys
import urllib.request

BASE = os.environ.get("LEDGERBENCH_MCP_BASE", "http://world:8974")
SERVERS = ["books", "docs", "email", "erp", "filings", "harness", "odoo", "sheets"]


def request(server, method, params=None, request_id=1):
    value = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        value["params"] = params
    req = urllib.request.Request(f"{BASE}/mcp/{server}", method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    with urllib.request.urlopen(req, json.dumps(value).encode("utf-8"), timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise SystemExit(json.dumps(payload["error"]))
    return payload["result"]


if len(sys.argv) == 2 and sys.argv[1] == "servers":
    print(json.dumps(SERVERS))
elif len(sys.argv) == 3 and sys.argv[1] == "list":
    print(json.dumps(request(sys.argv[2], "tools/list"), indent=2, ensure_ascii=False))
elif len(sys.argv) == 5 and sys.argv[1] == "call":
    result = request(sys.argv[2], "tools/call",
                     {"name": sys.argv[3], "arguments": json.loads(sys.argv[4])})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("isError"):
        raise SystemExit(1)
else:
    raise SystemExit("usage: tool servers | tool list SERVER | tool call SERVER TOOL_NAME '{\"argument\":\"value\"}'")
'''


def solution_script() -> str:
    return r'''#!/usr/bin/env python3
"""Oracle solution: replay solution/walk.json over the LIVE MCP surface.

Every step is one tools/call against the world service — the same surface an
agent uses. Application-level errors inside a payload are tolerated exactly the
way the authoring repo's oracle tolerates them; transport or unknown-tool errors
abort the run.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
WALK = json.loads((HERE / "walk.json").read_text(encoding="utf-8"))
BASE = os.environ.get("LEDGERBENCH_MCP_BASE", "http://world:8974")


def wait_healthy(timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=2):
                return
        except (urllib.error.URLError, OSError):
            time.sleep(1)
    raise SystemExit("world service did not become healthy")


def call(server, tool, arguments, request_id):
    message = {"jsonrpc": "2.0", "id": request_id, "method": "tools/call",
               "params": {"name": tool, "arguments": arguments}}
    request = urllib.request.Request(f"{BASE}/mcp/{server}", method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json, text/event-stream")
    with urllib.request.urlopen(request, json.dumps(message).encode("utf-8"),
                                timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("error"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    result = payload.get("result") or {}
    if result.get("isError"):
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return result


wait_healthy()
for index, step in enumerate(WALK):
    call(step["server"], step["tool"], step.get("args") or {}, index + 1)
print(json.dumps({"replayed_steps": len(WALK)}))
'''


def test_script(token: str) -> str:
    return f'''#!/bin/bash
set -eu
python3 - <<'PYEOF'
import json
import os
import urllib.request

output = {{"reward": 0.0, "passed": 0.0}}
report = {{"passed": False, "reward": 0.0, "error": "verifier did not return"}}
try:
    request = urllib.request.Request(
        os.environ.get("LEDGERBENCH_VERIFY_URL", "http://world:{WORLD_PORT}/verify"),
        method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("X-Verify-Token", "{token}")
    with urllib.request.urlopen(request, b"{{}}", timeout=150) as response:
        report = json.loads(response.read().decode("utf-8"))
    output = {{
        "reward": float(report.get("reward", 0.0)),
        "passed": 1.0 if report.get("passed") else 0.0,
    }}
except Exception as error:
    report = {{"passed": False, "reward": 0.0, "error": repr(error)}}

root = os.environ.get("VERIFIER_LOG_DIR") or os.path.join(
    os.environ.get("HARBOR_LOGS", "/logs"), "verifier")
os.makedirs(root, exist_ok=True)
with open(os.path.join(root, "report.json"), "w", encoding="utf-8") as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
with open(os.path.join(root, "reward.json"), "w", encoding="utf-8") as stream:
    json.dump(output, stream, sort_keys=True)
with open(os.path.join(root, "reward.txt"), "w", encoding="utf-8") as stream:
    stream.write(str(int(output["reward"])))
print(json.dumps({{"passed": bool(output["passed"]), "reward": output["reward"]}}))
PYEOF
'''


_ERPB_TABLES: list[str] | None = None


def erpb_tables() -> list[str]:
    """Every erpb_* table declared by the world schema (the Odoo write surface)."""
    global _ERPB_TABLES
    if _ERPB_TABLES is None:
        import sqlite3

        cx = sqlite3.connect(":memory:")
        cx.executescript((ROOT / "world" / "schema.sql").read_text())
        _ERPB_TABLES = sorted(
            name for (name,) in cx.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'erpb_%'")
        )
        cx.close()
    return _ERPB_TABLES


def gzip_bytes_deterministic(data: bytes) -> bytes:
    import io

    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", compresslevel=9, mtime=0) as stream:
        stream.write(data)
    return buffer.getvalue()


# --- registry content digest (exact harbor 0.21 Packager algorithm) -----------

def collect_files(task_dir: Path) -> list[Path]:
    files: list[Path] = []
    for single in ("task.toml", "instruction.md", "README.md", "trajectory.json"):
        if (task_dir / single).exists():
            files.append(task_dir / single)
    for directory in ("environment", "tests", "solution", "steps"):
        d = task_dir / directory
        if d.exists():
            files.extend(p for p in d.rglob("*") if p.is_file())
    files = [f for f in files
             if not f.name.endswith(IGNORED_SUFFIXES) and "__pycache__" not in f.parts]
    files.sort(key=lambda p: p.relative_to(task_dir).as_posix())
    return files


def compute_content_hash(task_dir: Path) -> str:
    outer = hashlib.sha256()
    for f in collect_files(task_dir):
        rel = f.relative_to(task_dir).as_posix()
        file_hash = hashlib.sha256(f.read_bytes()).hexdigest()
        outer.update(f"{rel}\0{file_hash}\n".encode())
    return outer.hexdigest()


# --- self-replay gate (pack contents only) ------------------------------------

def replay_pack_oracle(pack: Path) -> dict:
    """Prove the pack solves itself using only its own contents."""
    world_dir = pack / "environment" / "world"
    spec = json.loads((world_dir / "spec.json").read_text())
    walk = json.loads((pack / "solution" / "walk.json").read_text())
    with tempfile.TemporaryDirectory(prefix="lgr-gate-") as temporary:
        run = Path(temporary)
        with gzip.open(world_dir / "state" / "world.sqlite.gz", "rb") as fin, \
                open(run / "world.sqlite", "wb") as fout:
            shutil.copyfileobj(fin, fout)
        shutil.copyfile(world_dir / "state" / "initial_state.json",
                        run / "initial_state.json")
        (run / "trace.jsonl").write_text("")
        import os

        os.environ.update({
            "WORLD_DB": str(run / "world.sqlite"),
            "WORLD_NOW": spec["world_now"],
            "WORLD_ROLE": spec["world_role"],
            "TRACE_FILE": str(run / "trace.jsonl"),
        })
        lib_path = str(world_dir / "runtime" / "lib")
        sys.path.insert(0, lib_path)
        try:
            servers = {}
            for step in walk:
                name = step["server"]
                if name not in servers:
                    module_spec = importlib.util.spec_from_file_location(
                        f"gate_{pack.name}_{name}",
                        world_dir / "runtime" / "servers" / f"{name}_server.py")
                    module = importlib.util.module_from_spec(module_spec)
                    module_spec.loader.exec_module(module)
                    servers[name] = module.S
                try:
                    servers[name].call(step["tool"], step.get("args") or {})
                except Exception:  # noqa: BLE001 - oracle tolerance, verifier decides
                    pass
            vcode_spec = importlib.util.spec_from_file_location(
                f"gate_{pack.name}_vcode", world_dir / "runtime" / "vcode.py")
            vcode = importlib.util.module_from_spec(vcode_spec)
            vcode_spec.loader.exec_module(vcode)
            return vcode.verify_all(str(world_dir / "taskspec"), str(run))
        finally:
            sys.path.remove(lib_path)
            sys.modules.pop("framework", None)


# --- pack builder --------------------------------------------------------------

def build_pack(
    entry: dict,
    tasks_root: Path,
    gate: bool,
    seen_sequences: set[tuple[tuple[str, str], ...]],
) -> tuple[bool, str]:
    source = ROOT / "tasks" / entry["source_task"]
    task_id = entry["task_id"]
    pack = tasks_root / task_id
    if pack.exists():
        shutil.rmtree(pack)
    source_cfg = tomllib.loads((source / "task.toml").read_text())
    description = source_cfg["task"].get("description", "")[:240].replace('"', "'")
    prompt = release_prompt(entry, (source / "instruction.md").read_text(), source_cfg)
    walk = distinct_walk(
        entry,
        json.loads((source / "solution" / "walk.json").read_text()),
        seen_sequences,
    )
    token = verification_token(task_id)

    # 1. prepared world for THIS task (core + its seed layers)
    with tempfile.TemporaryDirectory(prefix="lgr-prep-") as temporary:
        staged = Path(temporary) / "run"
        prepare(source, staged)
        world_dir = pack / "environment" / "world"
        (world_dir / "state").mkdir(parents=True)
        raw = (staged / "world.sqlite").read_bytes()
        (world_dir / "state" / "world.sqlite.gz").write_bytes(
            gzip_bytes_deterministic(raw))
        shutil.copyfile(staged / "initial_state.json",
                        world_dir / "state" / "initial_state.json")
        roster = json.loads((staged / ".mcp.json").read_text())["mcpServers"]
        env = next(iter(roster.values()))["env"]
        has_inputs = (staged / "workdir").is_dir() and any((staged / "workdir").iterdir())
        if has_inputs:
            shutil.copytree(staged / "workdir", pack / "environment" / "inputs")

    # 2. world service: bridge, spec, verifier taskspec, runtime
    spec = {
        "schema_version": "1.0",
        "benchmark": RELEASE_NAME,
        "version": RELEASE_VERSION,
        "task_id": task_id,
        "source_task": entry["source_task"],
        "world_now": env["WORLD_NOW"],
        "world_role": env["WORLD_ROLE"],
        "servers": SERVERS,
        "verify_token_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
    }
    write_json(world_dir / "spec.json", spec)
    shutil.copyfile(HERE / "runtime" / "server.py", world_dir / "server.py")
    write_text(world_dir / "Dockerfile", world_dockerfile())
    (world_dir / "taskspec" / "tests").mkdir(parents=True)
    checks = json.loads((source / "tests" / "checks.json").read_text())
    state_checks = checks.setdefault("state_checks", [])
    if not any(c.get("type") == "writes_only" for c in state_checks):
        # Release hardening: every LedgerBench pack carries the anti-hack veto. For
        # the erpbench (Odoo write-surface) family the authoring checks omitted it;
        # allow the answers table plus the entire erpb_* surface the odoo server
        # legitimately writes, so any off-surface write vetoes the reward while no
        # correct solution is constrained.
        state_checks.append({"type": "writes_only",
                             "tables": ["answers"] + sorted(erpb_tables())})
    initial_hashes = json.loads(
        (world_dir / "state" / "initial_state.json").read_text()
    )
    criteria = rubric_criteria(entry, checks, walk, initial_hashes)
    options = decision_options(entry, walk)
    (world_dir / "taskspec" / "tests" / "checks.json").write_text(
        json.dumps(checks, indent=1) + "\n")
    runtime = world_dir / "runtime"
    (runtime / "lib").mkdir(parents=True)
    (runtime / "servers").mkdir()
    shutil.copyfile(ROOT / "mcp" / "lib" / "framework.py", runtime / "lib" / "framework.py")
    for name in SERVERS:
        shutil.copyfile(ROOT / "mcp" / "servers" / f"{name}_server.py",
                        runtime / "servers" / f"{name}_server.py")
    shutil.copyfile(ROOT / "verifiers" / "vcode.py", runtime / "vcode.py")

    # 3. Harbor contract files
    release_entry = {
        **entry,
        "walk_len": len(walk),
        "criteria_count": len(criteria),
    }
    write_text(pack / "task.toml", task_toml(release_entry, source_cfg.get("metadata", {}), description))
    write_text(pack / "instruction.md", prompt + "\n")
    write_text(pack / "environment" / "Dockerfile", main_dockerfile(has_inputs))
    write_text(pack / "environment" / "docker-compose.yaml", compose_yaml(has_inputs))
    write_text(pack / "environment" / "tool", tool_cli(), executable=True)
    (pack / "solution").mkdir()
    write_json(pack / "solution" / "walk.json", walk)
    write_json(
        world_dir / "taskspec" / "realism.json",
        {
            "criteria": criteria,
            "decision_options": options,
            "asset_contract": {
                "minimum_assets": 14,
                "systems": SERVERS,
                "note": "Hugging Face exports task-scoped views of this exact initial SQLite state.",
            },
        },
    )
    write_text(pack / "solution" / "solve.py", solution_script(), executable=True)
    write_text(pack / "solution" / "solve.sh",
               '#!/bin/bash\nset -eu\npython3 "$(dirname "$0")/solve.py"\n',
               executable=True)
    write_text(pack / "tests" / "test.sh", test_script(token), executable=True)

    if not gate:
        return True, "exported (ungated)"

    # 4. self-replay gate: the pack must solve and verify itself
    verdict = replay_pack_oracle(pack)
    if verdict["reward"] != 1:
        shutil.rmtree(pack)
        return False, f"self-replay scored {verdict['reward']}: {verdict['failed'][:3]}"
    return True, "oracle-verified"


def emit_dataset_toml(release: Path, entries: list[dict]) -> None:
    lines = [
        "[dataset]",
        f'name = "{HARBOR_ORG}/{RELEASE_SLUG}"',
        f'version = "{RELEASE_VERSION}"',
        'description = "100 deterministic corporate-finance agent tasks over a shared '
        'ERP world: 8 MCP servers, 66 tools, SQL-graded write layer, no LLM judge."',
        "authors = []",
        'keywords = ["finance", "erp", "mcp", "deterministic", "long-horizon"]',
        "",
    ]
    for entry in entries:
        digest = compute_content_hash(release / "harbor" / "tasks" / entry["task_id"])
        lines.append("[[tasks]]")
        lines.append(f'name = "{HARBOR_ORG}/{entry["task_id"]}"')
        lines.append(f'digest = "sha256:{digest}"')
        lines.append("")
    write_text(release / "harbor" / "dataset" / "dataset.toml", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=ROOT / "dist" / RELEASE_SLUG)
    parser.add_argument("--only", help="build just this task_id (debugging)")
    parser.add_argument("--no-gate", action="store_true")
    arguments = parser.parse_args()
    catalog = json.loads((HERE / "catalog.json").read_text())
    entries = catalog["tasks"]
    if arguments.only:
        entries = [e for e in entries if e["task_id"] == arguments.only]
    tasks_root = arguments.release / "harbor" / "tasks"
    tasks_root.mkdir(parents=True, exist_ok=True)
    ok, bad = [], []
    seen_sequences: set[tuple[tuple[str, str], ...]] = set()
    for entry in entries:
        good, note = build_pack(
            entry,
            tasks_root,
            gate=not arguments.no_gate,
            seen_sequences=seen_sequences,
        )
        (ok if good else bad).append((entry["task_id"], note))
        print(f"  {'OK  ' if good else 'FAIL'} {entry['task_id']:64} {note}", flush=True)
    if not arguments.only and not bad:
        emit_dataset_toml(arguments.release, entries)
        print(f"dataset.toml written with {len(entries)} digests")
    print(f"exported {len(ok)}/{len(entries)} packs to {tasks_root}")
    if bad:
        print(f"{len(bad)} REJECTED by the self-replay gate (not shipped):")
        for name, note in bad:
            print(f"  {name}: {note}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
