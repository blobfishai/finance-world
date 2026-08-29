#!/usr/bin/env python3
"""LedgerBench-100 world service: Streamable HTTP MCP bridge + token-gated verifier.

One process serves the task's eight finance MCP servers (imported in-process from the
pack's own runtime/) over per-server Streamable HTTP endpoints:

    POST /mcp/<server>   JSON-RPC: initialize | ping | tools/list | tools/call
    GET  /health         readiness for the compose healthcheck
    POST /verify         token-gated deterministic verification (X-Verify-Token)

The agent container never sees the verification token: the pack bakes only its
SHA-256 digest into spec.json. tests/test.sh (copied into the container only at
verification time) holds the actual token.

Everything is offline and deterministic: SQLite world state, frozen WORLD_NOW
clock, stdlib-only, no LLM anywhere.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "spec.json").read_text(encoding="utf-8"))
RUNTIME = HERE / "runtime"
RUN_DIR = Path(os.environ.get("LEDGERBENCH_RUN_DIR", "/opt/world/run"))
PROTOCOL_VERSION = "2025-06-18"

_SERVERS: dict[str, Any] = {}


def load_servers() -> dict[str, Any]:
    """Import the pack's MCP server modules in-process (same handlers, same trace)."""
    if _SERVERS:
        return _SERVERS
    sys.path.insert(0, str(RUNTIME / "lib"))
    for name in SPEC["servers"]:
        spec = importlib.util.spec_from_file_location(
            f"lgr_{name}_server", RUNTIME / "servers" / f"{name}_server.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _SERVERS[name] = module.S
    return _SERVERS


def reset_run_dir() -> None:
    """Materialize a pristine run: fresh world DB, empty trace, initial hashes."""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    state = HERE / "state"
    db_gz = state / "world.sqlite.gz"
    db = state / "world.sqlite"
    target = RUN_DIR / "world.sqlite"
    if db.exists():
        shutil.copyfile(db, target)
    else:
        with gzip.open(db_gz, "rb") as fin, open(target, "wb") as fout:
            shutil.copyfileobj(fin, fout)
    shutil.copyfile(state / "initial_state.json", RUN_DIR / "initial_state.json")
    (RUN_DIR / "trace.jsonl").write_text("")
    os.environ["WORLD_DB"] = str(target)
    os.environ["WORLD_NOW"] = SPEC["world_now"]
    os.environ["WORLD_ROLE"] = SPEC["world_role"]
    os.environ["TRACE_FILE"] = str(RUN_DIR / "trace.jsonl")


def build_report(task_dir: Path, run_dir: Path, task_id: str) -> dict[str, Any]:
    """Deterministic verification report (no clock, no randomness, no network)."""
    sys.path.insert(0, str(RUNTIME))
    from vcode import verify_all  # the pack's own deterministic verifier engine

    verdict = verify_all(str(task_dir), str(run_dir))
    report = {
        "benchmark": SPEC["benchmark"],
        "version": SPEC["version"],
        "task_id": task_id,
        "passed": verdict["reward"] == 1,
        "reward": float(verdict["reward"]),
        "failed_checks": sorted(verdict["failed"]),
        "n_tool_calls": verdict["n_tool_calls"],
        "servers_used": verdict["servers_used"],
        "steps_graded": verdict.get("steps", 1),
    }
    report["report_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return report


def rpc_response(server_name: str, request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")
    if request_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None
    if request.get("jsonrpc") != "2.0" or not isinstance(method, str):
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32600, "message": "Invalid Request"}}
    servers = load_servers()
    if server_name not in servers:
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32601, "message": f"unknown server {server_name!r}"}}
    srv = servers[server_name]
    if method == "initialize":
        params = request.get("params") or {}
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            "protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": srv.name, "version": "1.0.0"},
            "instructions": srv.description,
        }}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id,
                "result": {"tools": [schema for _, schema in srv.tools.values()]}}
    if method == "tools/call":
        params = request.get("params") or {}
        tool = params.get("name")
        arguments = params.get("arguments") or {}
        if tool not in srv.tools:
            return {"jsonrpc": "2.0", "id": request_id, "result": {
                "content": [{"type": "text", "text": f"unknown tool {tool}"}],
                "isError": True}}
        try:
            out = srv.call(tool, arguments)
            return {"jsonrpc": "2.0", "id": request_id, "result": {
                "content": [{"type": "text", "text": json.dumps(out, default=str)}],
                "isError": False}}
        except Exception as error:  # noqa: BLE001 - surface tool failure to the agent
            return {"jsonrpc": "2.0", "id": request_id, "result": {
                "content": [{"type": "text", "text": f"error: {error!r}"}],
                "isError": True}}
    return {"jsonrpc": "2.0", "id": request_id,
            "error": {"code": -32601, "message": "Method not found"}}


class Handler(BaseHTTPRequestHandler):
    server_version = "LedgerBenchWorld/3.1"

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        return

    def _json(self, status: int, value: Any) -> None:
        payload = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("MCP-Protocol-Version", PROTOCOL_VERSION)
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(HTTPStatus.OK, {"status": "ok", "task_id": SPEC["task_id"]})
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        if self.path == "/verify":
            token = self.headers.get("X-Verify-Token") or ""
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            if digest != SPEC["verify_token_sha256"]:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            self._json(HTTPStatus.OK,
                       build_report(HERE / "taskspec", RUN_DIR, SPEC["task_id"]))
            return
        if not self.path.startswith("/mcp/"):
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        server_name = self.path[len("/mcp/"):].strip("/")
        try:
            request = json.loads(body.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._json(HTTPStatus.BAD_REQUEST,
                       {"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": "Parse error"}})
            return
        if isinstance(request, list):
            responses = [r for item in request
                         if (r := rpc_response(server_name, item)) is not None]
            self._json(HTTPStatus.OK, responses)
            return
        response = rpc_response(server_name, request)
        if response is None:
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._json(HTTPStatus.OK, response)


def main() -> None:
    reset_run_dir()
    load_servers()
    host = os.environ.get("LEDGERBENCH_HOST", "0.0.0.0")
    port = int(os.environ.get("LEDGERBENCH_PORT", "8974"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
