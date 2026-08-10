#!/usr/bin/env python3
"""Sheets MCP server — 1:1 Microsoft Graph workbook API shapes over the shared drive.

Mirrors Graph /drive + /workbook: list drive items, worksheets collection,
range(address='A1:C4') returning the Graph workbookRange object (address, values, text,
formulas, numberFormat, rowCount/columnCount/cellCount), usedRange, and drive search.
Each shared-drive file is a workbook with one worksheet ("Sheet1"). Read-only
(Files.Read scope). SIMULATION ONLY."""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("sheets", "Finance shared drive (Microsoft Graph workbook API shapes). Read-only. SIMULATION ONLY.")

def _file(cx, name):
    return cx.execute("SELECT * FROM sheet_files WHERE name=?", (name,)).fetchone()

def _grid(cx, name):
    rows = cx.execute("SELECT row_no, cells FROM sheet_rows WHERE file=? ORDER BY row_no", (name,)).fetchall()
    return [json.loads(r["cells"]) for r in rows]

def _cell_v(c):
    """A cell is a literal, or {"f": "=SUM(...)", "v": cached_value} for formula cells.
    Like real Excel, the API serves the CACHED value — it may have drifted from the
    formula's inputs (paste-values / stale-recalc chaos)."""
    return c.get("v", "") if isinstance(c, dict) else c

def _cell_f(c):
    return c.get("f", c.get("v", "")) if isinstance(c, dict) else c

def _range_obj(grid, r0, c0, r1, c1, sheet="Sheet1"):
    values, formulas = [], []
    for ri in range(r0, r1 + 1):
        row = grid[ri - 1] if 0 < ri <= len(grid) else []
        cells = [(row[ci - 1] if 0 < ci <= len(row) else "") for ci in range(c0, c1 + 1)]
        values.append([_cell_v(c) for c in cells])
        formulas.append([_cell_f(c) for c in cells])
    addr = f"{sheet}!{_col(c0)}{r0}:{_col(c1)}{r1}"
    return {"address": addr, "addressLocal": addr,
            "rowCount": r1 - r0 + 1, "columnCount": c1 - c0 + 1,
            "cellCount": (r1 - r0 + 1) * (c1 - c0 + 1),
            "rowIndex": r0 - 1, "columnIndex": c0 - 1,
            "values": values, "text": [[str(v) for v in row] for row in values],
            "formulas": formulas, "numberFormat": [["General"] * (c1 - c0 + 1) for _ in range(r1 - r0 + 1)],
            "valueTypes": [[("Empty" if v == "" else "Double" if isinstance(v, (int, float)) else "String")
                            for v in row] for row in values]}

def _col(n):
    s = ""
    while n: n, r = divmod(n - 1, 26); s = chr(65 + r) + s
    return s

def _parse_a1(a1):
    m = re.match(r"(?i)^(?:Sheet1!)?([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$", a1.strip())
    if not m: return None
    def num(col):
        v = 0
        for ch in col.upper(): v = v * 26 + ord(ch) - 64
        return v
    c0, r0 = num(m.group(1)), int(m.group(2))
    c1, r1 = (num(m.group(3)), int(m.group(4))) if m.group(3) else (c0, r0)
    return r0, c0, r1, c1

@S.tool("list_drive_items", "List workbook files on the finance shared drive (GET /drive/root/children shape).")
def list_drive_items():
    cx = S.db()
    return {"value": [{"id": r["name"], "name": r["name"],
                       "lastModifiedDateTime": r["modified_at"],
                       "createdBy": {"user": {"displayName": r["owner"]}},
                       "description": r["description"],
                       "file": {"mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}}
                      for r in cx.execute("SELECT * FROM sheet_files ORDER BY name")]}

@S.tool("get_drive_item", "One file's metadata (GET /drive/items/{id} shape) — check lastModifiedDateTime before trusting a tracker.",
        {"item": {"type": "string", "description": "file name/id"}}, ["item"])
def get_drive_item(item):
    cx = S.db()
    f = _file(cx, item)
    if not f: return {"error": {"code": "itemNotFound", "message": f"The resource could not be found: {item}"}}
    n = cx.execute("SELECT COUNT(*) FROM sheet_rows WHERE file=?", (item,)).fetchone()[0]
    return {"id": f["name"], "name": f["name"], "lastModifiedDateTime": f["modified_at"],
            "createdBy": {"user": {"displayName": f["owner"]}}, "description": f["description"],
            "rowCount": n}

@S.tool("workbook_worksheets", "List worksheets of a workbook (GET /workbook/worksheets shape).",
        {"item": {"type": "string"}}, ["item"])
def workbook_worksheets(item):
    cx = S.db()
    if not _file(cx, item):
        return {"error": {"code": "itemNotFound", "message": f"The resource could not be found: {item}"}}
    return {"value": [{"id": "{00000000-0001-0000-0000-000000000000}", "name": "Sheet1",
                       "position": 0, "visibility": "Visible"}]}

@S.tool("workbook_range", "Read a range (GET /workbook/worksheets/Sheet1/range(address='A1:C4') shape). Returns the Graph workbookRange object.",
        {"item": {"type": "string"}, "address": {"type": "string", "description": "A1 notation, e.g. A1:F4"}},
        ["item", "address"])
def workbook_range(item, address):
    cx = S.db()
    if not _file(cx, item):
        return {"error": {"code": "itemNotFound", "message": f"The resource could not be found: {item}"}}
    box = _parse_a1(address)
    if not box: return {"error": {"code": "invalidArgument", "message": f"Invalid range address: {address}"}}
    return _range_obj(_grid(cx, item), *box)

@S.tool("workbook_used_range", "Read the used range of Sheet1 (GET /workbook/worksheets/Sheet1/usedRange shape).",
        {"item": {"type": "string"}}, ["item"])
def workbook_used_range(item):
    cx = S.db()
    if not _file(cx, item):
        return {"error": {"code": "itemNotFound", "message": f"The resource could not be found: {item}"}}
    grid = _grid(cx, item)
    if not grid: return {"error": {"code": "itemNotFound", "message": "worksheet is empty"}}
    return _range_obj(grid, 1, 1, len(grid), max(len(r) for r in grid))

@S.tool("drive_search", "Search file contents across the drive (GET /drive/root/search(q='...') shape, cell-level hits).",
        {"q": {"type": "string"}}, ["q"])
def drive_search(q):
    cx = S.db(); like = f"%{q.lower()}%"
    hits = [{"file": r["file"], "row": r["row_no"], "cells": json.loads(r["cells"])}
            for r in cx.execute("SELECT file, row_no, cells FROM sheet_rows WHERE LOWER(cells) LIKE ? LIMIT 50", (like,))]
    return {"value": hits}

if __name__ == "__main__":
    S.run()
