"""Minimal stdio MCP server framework (newline-delimited JSON-RPC) + tracing.

Every server: reads WORLD_DB (sqlite), WORLD_NOW (frozen clock), TRACE_FILE (call log).
Tool results are JSON serialized into a single text content block. No LLM anywhere.
"""
import json, os, sys, time, sqlite3

PAGE = 25  # rows per page, mirroring the D365 ERP MCP form-tool page size

class Server:
    def __init__(self, name, description=""):
        self.name, self.description = name, description
        self.tools = {}   # name -> (handler, schema)

    def tool(self, name, description, properties=None, required=None):
        def deco(fn):
            self.tools[name] = (fn, {
                "name": name, "description": description,
                "inputSchema": {"type": "object",
                                "properties": properties or {},
                                "required": required or []}})
            return fn
        return deco

    # --- state helpers -----------------------------------------------------
    def db(self):
        cx = sqlite3.connect(os.environ["WORLD_DB"])
        cx.row_factory = sqlite3.Row
        return cx

    @property
    def now(self):
        return os.environ.get("WORLD_NOW", "2026-03-02T12:00:00Z")

    @property
    def today(self):
        return self.now[:10]

    def rows(self, cx, sql, args=(), page=1):
        all_rows = [dict(r) for r in cx.execute(sql, args).fetchall()]
        page = max(1, int(page or 1))
        chunk = all_rows[(page - 1) * PAGE: page * PAGE]
        return {"rows": chunk, "page": page, "page_size": PAGE,
                "total_rows": len(all_rows),
                "has_more": page * PAGE < len(all_rows)}

    # --- trace -------------------------------------------------------------
    def _trace(self, tool, args, ok, note=""):
        path = os.environ.get("TRACE_FILE")
        if not path: return
        rec = {"ts": time.time(), "server": self.name, "tool": tool,
               "args": args, "ok": ok}
        if note: rec["note"] = str(note)[:400]
        with open(path, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    # --- direct call (used by the oracle replayer, bypasses stdio) ---------
    def call(self, tool, args):
        fn, _ = self.tools[tool]
        try:
            out = fn(**(args or {}))
            self._trace(tool, args, True)
            return out
        except Exception as e:
            self._trace(tool, args, False, note=repr(e))
            raise

    # --- stdio MCP loop ----------------------------------------------------
    def run(self):
        for line in sys.stdin:
            line = line.strip()
            if not line: continue
            try: msg = json.loads(line)
            except Exception: continue
            mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
            if method == "initialize":
                self._reply(mid, {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                                  "capabilities": {"tools": {}},
                                  "serverInfo": {"name": self.name, "version": "0.1.0"}})
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                self._reply(mid, {"tools": [s for _, s in self.tools.values()]})
            elif method == "tools/call":
                tool = params.get("name"); args = params.get("arguments") or {}
                if tool not in self.tools:
                    self._reply(mid, {"content": [{"type": "text", "text": f"unknown tool {tool}"}], "isError": True})
                    continue
                try:
                    out = self.call(tool, args)
                    self._reply(mid, {"content": [{"type": "text", "text": json.dumps(out, default=str)}], "isError": False})
                except Exception as e:
                    self._reply(mid, {"content": [{"type": "text", "text": f"error: {e!r}"}], "isError": True})
            elif method == "ping":
                self._reply(mid, {})
            elif mid is not None:
                self._reply(mid, {})

    def _reply(self, mid, result):
        if mid is None: return
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}) + "\n")
        sys.stdout.flush()
