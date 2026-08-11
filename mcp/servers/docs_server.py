#!/usr/bin/env python3
"""Docs MCP server — internal policy/SOP document store. Read-only. SIMULATION ONLY."""
import sys, re
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
    """Token search: every term must appear somewhere in the title or body, in any order."""
    cx = S.db()
    terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) > 2]
    hits = []
    for r in cx.execute("SELECT doc_id, title, doc_type, version, body FROM docs_documents"):
        hay = f"{r['title']} {r['body']}".lower()
        if not terms or all(t in hay for t in terms):
            hits.append({k: r[k] for k in ("doc_id", "title", "doc_type", "version")})
    if not hits and terms:   # fall back to any-term, so a near-miss query still guides the agent
        for r in cx.execute("SELECT doc_id, title, doc_type, version, body FROM docs_documents"):
            hay = f"{r['title']} {r['body']}".lower()
            if any(t in hay for t in terms):
                hits.append({k: r[k] for k in ("doc_id", "title", "doc_type", "version")})
    return {"matches": hits}

@S.tool("get_document", "Fetch a full document body.",
        {"doc_id": {"type": "string"}}, ["doc_id"])
def get_document(doc_id):
    cx = S.db()
    r = cx.execute("SELECT * FROM docs_documents WHERE doc_id=?", (doc_id,)).fetchone()
    return dict(r) if r else {"error": "not found"}

@S.tool("get_document_metadata", "Document metadata only (type, version, effective date) — check currency before relying on a policy.",
        {"doc_id": {"type": "string"}}, ["doc_id"])
def get_document_metadata(doc_id):
    cx = S.db()
    r = cx.execute("SELECT doc_id, title, doc_type, version, effective_date FROM docs_documents WHERE doc_id=?", (doc_id,)).fetchone()
    return dict(r) if r else {"error": "not found"}

@S.tool("list_document_types", "List document types with counts (policy, sop, template, statement, ...).")
def list_document_types():
    cx = S.db()
    return {"types": [dict(r) for r in cx.execute(
        "SELECT doc_type, COUNT(*) AS documents FROM docs_documents GROUP BY doc_type ORDER BY doc_type")]}

if __name__ == "__main__":
    S.run()
