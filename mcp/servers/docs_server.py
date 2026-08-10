#!/usr/bin/env python3
"""Docs MCP server — internal policy/SOP document store. Read-only. SIMULATION ONLY."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("docs", "Finance team policy & SOP library. SIMULATION ONLY.")

@S.tool("list_documents", "List documents, optionally by type (policy, sop, template, statement).",
        {"doc_type": {"type": "string"}})
def list_documents(doc_type=None):
    cx = S.db()
    if doc_type:
        rows = cx.execute("SELECT doc_id, title, doc_type, version, effective_date FROM docs_documents WHERE doc_type=?", (doc_type,))
    else:
        rows = cx.execute("SELECT doc_id, title, doc_type, version, effective_date FROM docs_documents")
    return {"documents": [dict(r) for r in rows]}

@S.tool("search_documents", "Keyword search over titles and bodies.",
        {"query": {"type": "string"}}, ["query"])
def search_documents(query):
    cx = S.db(); like = f"%{query.lower()}%"
    rows = cx.execute("""SELECT doc_id, title, doc_type, version FROM docs_documents
                         WHERE LOWER(title) LIKE ? OR LOWER(body) LIKE ?""", (like, like))
    return {"matches": [dict(r) for r in rows]}

@S.tool("get_document", "Fetch a full document body.",
        {"doc_id": {"type": "string"}}, ["doc_id"])
def get_document(doc_id):
    cx = S.db()
    r = cx.execute("SELECT * FROM docs_documents WHERE doc_id=?", (doc_id,)).fetchone()
    return dict(r) if r else {"error": "not found"}

if __name__ == "__main__":
    S.run()
