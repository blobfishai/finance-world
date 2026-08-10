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

@S.tool("get_spreadsheet_metadata", "File metadata: owner, last-modified timestamp, description, row count. Check staleness before trusting a tracker.",
        {"name": {"type": "string"}}, ["name"])
def get_spreadsheet_metadata(name):
    cx = S.db()
    f = cx.execute("SELECT * FROM sheet_files WHERE name=?", (name,)).fetchone()
    if not f:
        return {"error": f"no sheet named {name!r}",
                "available": [r["name"] for r in cx.execute("SELECT name FROM sheet_files")]}
    n = cx.execute("SELECT COUNT(*) FROM sheet_rows WHERE file=?", (name,)).fetchone()[0]
    return {**dict(f), "row_count": n}

@S.tool("read_range", "Read a row range of a spreadsheet (inclusive).",
        {"name": {"type": "string"}, "row_from": {"type": "integer"}, "row_to": {"type": "integer"}},
        ["name", "row_from", "row_to"])
def read_range(name, row_from, row_to):
    cx = S.db()
    rows = cx.execute("SELECT row_no, cells FROM sheet_rows WHERE file=? AND row_no BETWEEN ? AND ? ORDER BY row_no",
                      (name, int(row_from), int(row_to))).fetchall()
    if not rows: return {"error": f"no rows {row_from}-{row_to} in {name!r}"}
    return {"file": name, "rows": [{"row": r["row_no"], "cells": json.loads(r["cells"])} for r in rows]}

@S.tool("search_content", "Search cell contents across every spreadsheet on the drive; returns file + row hits.",
        {"query": {"type": "string"}}, ["query"])
def search_content(query):
    cx = S.db(); like = f"%{query.lower()}%"
    hits = [{"file": r["file"], "row": r["row_no"], "cells": json.loads(r["cells"])}
            for r in cx.execute("SELECT file, row_no, cells FROM sheet_rows WHERE LOWER(cells) LIKE ? LIMIT 50", (like,))]
    return {"query": query, "hits": hits}

if __name__ == "__main__":
    S.run()
