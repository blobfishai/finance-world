#!/usr/bin/env python3
"""Filings MCP server — SEC-EDGAR-shaped, serving frozen public-company snapshots.
Values are real XBRL facts captured from data.sec.gov at world-build time. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("filings", "Public-company filings & XBRL facts (frozen EDGAR snapshot).")

@S.tool("lookup_company", "Resolve a company name or ticker to CIK.",
        {"query": {"type": "string"}}, ["query"])
def lookup_company(query):
    cx = S.db(); like = f"%{query.lower()}%"
    rows = cx.execute("SELECT * FROM filings_companies WHERE LOWER(name) LIKE ? OR LOWER(ticker) LIKE ?",
                      (like, like)).fetchall()
    return {"matches": [dict(r) for r in rows]}

@S.tool("list_available_concepts", "List XBRL concepts available in the snapshot for a company.",
        {"ticker": {"type": "string"}}, ["ticker"])
def list_concepts(ticker):
    cx = S.db()
    rows = cx.execute("""SELECT DISTINCT f.concept, f.unit FROM filings_facts f
                         JOIN filings_companies c ON c.cik=f.cik WHERE LOWER(c.ticker)=?""",
                      (ticker.lower(),)).fetchall()
    return {"ticker": ticker.upper(), "concepts": [dict(r) for r in rows]}

@S.tool("get_company_concept", "All facts for one us-gaap concept (like EDGAR companyconcept).",
        {"ticker": {"type": "string"}, "concept": {"type": "string", "description": "e.g. AssetsCurrent"}},
        ["ticker", "concept"])
def get_company_concept(ticker, concept):
    cx = S.db()
    rows = cx.execute("""SELECT f.* FROM filings_facts f JOIN filings_companies c ON c.cik=f.cik
                         WHERE LOWER(c.ticker)=? AND LOWER(f.concept)=? ORDER BY f.period_end""",
                      (ticker.lower(), concept.lower())).fetchall()
    if not rows:
        return {"error": "concept not in snapshot", "hint": "use list_available_concepts"}
    return {"ticker": ticker.upper(), "concept": concept, "facts": [dict(r) for r in rows]}

@S.tool("get_submissions", "Recent filings for a company (form, filed date, accession, title).",
        {"ticker": {"type": "string"}}, ["ticker"])
def get_submissions(ticker):
    cx = S.db()
    rows = cx.execute("""SELECT d.* FROM filings_documents d JOIN filings_companies c ON c.cik=d.cik
                         WHERE LOWER(c.ticker)=? ORDER BY d.filed DESC""", (ticker.lower(),)).fetchall()
    return {"filings": [dict(r) for r in rows]}

if __name__ == "__main__":
    S.run()
