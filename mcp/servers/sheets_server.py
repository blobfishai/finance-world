#!/usr/bin/env python3
"""Shadow-spreadsheet MCP server — the team's Excel trackers on the shared drive. Read-only."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("sheets", "Finance team shared-drive spreadsheets (shadow trackers). SIMULATION ONLY.")

@S.tool("list_spreadsheets", "List spreadsheet files on the finance shared drive.")
def list_spreadsheets():
    cx = S.db()
    return {"files": [dict(r) for r in cx.execute("SELECT * FROM sheet_files ORDER BY name")]}

@S.tool("read_sheet", "Read rows of a spreadsheet (first row is usually the header).",
        {"name": {"type": "string"}, "max_rows": {"type": "integer"}}, ["name"])
def read_sheet(name, max_rows=50):
    cx = S.db()
    rows = cx.execute("SELECT row_no, cells FROM sheet_rows WHERE file=? ORDER BY row_no LIMIT ?",
                      (name, min(int(max_rows or 50), 200))).fetchall()
    if not rows:
        files = [r["name"] for r in cx.execute("SELECT name FROM sheet_files")]
        return {"error": f"no sheet named {name!r}", "available": files}
    return {"file": name, "rows": [{"row": r["row_no"], "cells": json.loads(r["cells"])} for r in rows]}

if __name__ == "__main__":
    S.run()
