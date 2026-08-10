#!/usr/bin/env python3
"""Filings MCP server — 1:1 SEC EDGAR data-API response shapes over frozen snapshots.

Endpoint mapping (values are real XBRL facts captured from data.sec.gov, frozen):
  lookup_company        ≈ company_tickers.json          (cik_str / ticker / title)
  get_company_concept   ≈ api/xbrl/companyconcept       (units.USD[].{end,val,accn,fy,fp,form,filed})
  get_company_facts     ≈ api/xbrl/companyfacts         (facts["us-gaap"][tag].units)
  get_xbrl_frames       ≈ api/xbrl/frames               (ccp "CY2024Q4I", data[].{cik,entityName,end,val})
  get_submissions       ≈ data.sec.gov/submissions      (filings.recent columnar arrays)
  full_text_search      ≈ efts.sec.gov/LATEST/search-index (hits.hits[]._source)
  list_available_concepts — snapshot index helper (no EDGAR equivalent; discovery aid).
Read-only. Rate-limit/User-Agent friction not reproduced (documented escalation lever)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("filings", "Public-company filings & XBRL facts (frozen EDGAR snapshot, real API shapes).")

def _fact(r):
    return {"end": r["period_end"], "val": r["value"], "accn": r["accession"],
            "fy": int(r["fy"]), "fp": r["fp"], "form": r["form"], "filed": r["filed"]}

@S.tool("lookup_company", "Resolve a company name or ticker to CIK (company_tickers.json shape).",
        {"query": {"type": "string"}}, ["query"])
def lookup_company(query):
    cx = S.db(); like = f"%{query.lower()}%"
    rows = cx.execute("SELECT * FROM filings_companies WHERE LOWER(name) LIKE ? OR LOWER(ticker) LIKE ?",
                      (like, like)).fetchall()
    return {"matches": [{"cik_str": int(r["cik"]), "ticker": r["ticker"], "title": r["name"]} for r in rows]}

@S.tool("list_available_concepts", "Snapshot index helper: XBRL concepts available for a company (no EDGAR equivalent).",
        {"ticker": {"type": "string"}}, ["ticker"])
def list_available_concepts(ticker):
    cx = S.db()
    rows = cx.execute("""SELECT DISTINCT f.concept, f.unit FROM filings_facts f
                         JOIN filings_companies c ON c.cik=f.cik WHERE LOWER(c.ticker)=?""",
                      (ticker.lower(),)).fetchall()
    return {"ticker": ticker.upper(), "concepts": [dict(r) for r in rows]}

@S.tool("get_company_concept", "All facts for one us-gaap concept (api/xbrl/companyconcept shape).",
        {"ticker": {"type": "string"}, "concept": {"type": "string", "description": "e.g. AssetsCurrent"}},
        ["ticker", "concept"])
def get_company_concept(ticker, concept):
    cx = S.db()
    c = cx.execute("SELECT * FROM filings_companies WHERE LOWER(ticker)=?", (ticker.lower(),)).fetchone()
    if not c: return {"error": "unknown ticker in snapshot", "hint": "use lookup_company"}
    rows = cx.execute("SELECT * FROM filings_facts WHERE cik=? AND LOWER(concept)=? ORDER BY period_end",
                      (c["cik"], concept.lower())).fetchall()
    if not rows:
        return {"error": "concept not in snapshot for this company", "hint": "use list_available_concepts"}
    units = {}
    for r in rows: units.setdefault(r["unit"], []).append(_fact(r))
    return {"cik": int(c["cik"]), "taxonomy": "us-gaap", "tag": rows[0]["concept"],
            "label": rows[0]["concept"], "description": "", "entityName": c["name"], "units": units}

@S.tool("get_company_facts", "ALL facts for a company across concepts (api/xbrl/companyfacts shape; large payload like the real endpoint).",
        {"ticker": {"type": "string"}}, ["ticker"])
def get_company_facts(ticker):
    cx = S.db()
    c = cx.execute("SELECT * FROM filings_companies WHERE LOWER(ticker)=?", (ticker.lower(),)).fetchone()
    if not c: return {"error": "unknown ticker in snapshot", "hint": "use lookup_company"}
    gaap = {}
    for r in cx.execute("SELECT * FROM filings_facts WHERE cik=? ORDER BY concept, period_end", (c["cik"],)):
        tag = gaap.setdefault(r["concept"], {"label": r["concept"], "description": "", "units": {}})
        tag["units"].setdefault(r["unit"], []).append(_fact(r))
    return {"cik": int(c["cik"]), "entityName": c["name"], "facts": {"us-gaap": gaap}}

@S.tool("get_xbrl_frames", "One concept, one annual period, across all companies in the snapshot (api/xbrl/frames shape).",
        {"concept": {"type": "string"}, "unit": {"type": "string"}, "fy": {"type": "string", "description": "e.g. 2024"}},
        ["concept", "fy"])
def get_xbrl_frames(concept, fy, unit="USD"):
    cx = S.db()
    rows = cx.execute("""SELECT c.ticker, c.name, f.* FROM filings_facts f
                         JOIN filings_companies c ON c.cik=f.cik
                         WHERE LOWER(f.concept)=? AND f.unit=? AND f.fy=? ORDER BY c.ticker""",
                      (concept.lower(), unit, str(fy))).fetchall()
    if not rows: return {"error": "no facts for that concept/period in snapshot",
                         "hint": "list_available_concepts per ticker"}
    return {"taxonomy": "us-gaap", "tag": rows[0]["concept"], "ccp": f"CY{fy}Q4I", "uom": unit,
            "pts": len(rows),
            "data": [{"accn": r["accession"], "cik": int(r["cik"]), "entityName": r["name"],
                      "end": r["period_end"], "val": r["value"]} for r in rows]}

@S.tool("get_submissions", "Company filing history (data.sec.gov/submissions shape: filings.recent columnar arrays).",
        {"ticker": {"type": "string"}}, ["ticker"])
def get_submissions(ticker):
    cx = S.db()
    c = cx.execute("SELECT * FROM filings_companies WHERE LOWER(ticker)=?", (ticker.lower(),)).fetchone()
    if not c: return {"error": "unknown ticker in snapshot", "hint": "use lookup_company"}
    rows = cx.execute("SELECT * FROM filings_documents WHERE cik=? ORDER BY filed DESC", (c["cik"],)).fetchall()
    return {"cik": c["cik"], "name": c["name"], "tickers": [c["ticker"]],
            "filings": {"recent": {
                "accessionNumber": [r["accession"] for r in rows],
                "filingDate": [r["filed"] for r in rows],
                "form": [r["form"] for r in rows],
                "primaryDocDescription": [r["title"] for r in rows]}}}

@S.tool("full_text_search", "Full-text search across filing documents (efts.sec.gov search shape).",
        {"q": {"type": "string"}}, ["q"])
def full_text_search(q):
    cx = S.db(); like = f"%{q.lower()}%"
    rows = cx.execute("""SELECT c.ticker, c.cik, c.name, d.form, d.filed, d.accession, d.title, d.excerpt
                         FROM filings_documents d JOIN filings_companies c ON c.cik=d.cik
                         WHERE LOWER(d.title) LIKE ? OR LOWER(d.excerpt) LIKE ?""", (like, like)).fetchall()
    return {"hits": {"total": {"value": len(rows)},
                     "hits": [{"_id": f"{r['accession']}", "_source": {
                         "ciks": [r["cik"]], "display_names": [f"{r['name']} ({r['ticker']})"],
                         "file_type": r["form"], "file_date": r["filed"],
                         "file_description": r["title"], "excerpt": r["excerpt"]}} for r in rows]}}

if __name__ == "__main__":
    S.run()
