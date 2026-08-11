#!/usr/bin/env python3
"""Freeze real SEC XBRL facts into a snapshot the `filings` server can serve.

Why fetch at all: the parity ledger (`ingest/run.py`) reports 31 FinanceBenchmark items that
bind to nothing because they name public companies the shared world does not hold. Those
questions are `recomputable` — factual, with a checkable figure — but only if we hold the
facts. This builds that capability once, from the authoritative source, and freezes it.

Frozen on purpose: the world runs on a fixed clock (2026-03-02), so a live API would make
ground truth move underneath the tasks. The snapshot is committed and stamped with the
fetch date and the accession each value came from, so any figure can be traced back.

    python3 world/etl/fetch_filings.py                 # all default tickers
    python3 world/etl/fetch_filings.py --tickers KO,WMT
    python3 world/etl/fetch_filings.py --load          # seed the built world from snapshots

SEC's fair-access rules: a descriptive User-Agent is mandatory and the limit is 10 req/s.
We stay well under it deliberately — this is someone else's public infrastructure.
"""
import argparse, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/external/edgar-snapshots"
UA = {"User-Agent": "finance-world eval simulation build (sam@blobfish.ai)"}

# The roster is derived, not guessed: these are the companies FinanceBenchmark's questions
# actually name, per `python3 ingest/run.py --detail`. Adding a ticker here and re-running
# closes the corresponding absent_entity rows in the parity ledger.
DEFAULT_TICKERS = ["WMT", "KO", "XOM", "CAT", "CVX", "MSFT", "AAPL", "AMZN",
                   "PFE", "BA", "TSLA", "INTC", "NVDA", "F"]

# A ticker does not always point at the entity that holds the filing history. SEC's
# company_tickers.json maps XOM to CIK 0002115436 ("ExxonMobil Holdings Corp"), a successor
# registrant with no 10-K history; the operating history is under 0000034088. Resolving
# blindly would have shipped an XOM with zero facts — and XOM is named by 14 of the questions
# this snapshot exists to unblock. Overrides are explicit and carry their reason.
CIK_OVERRIDES = {
    "XOM": ("0000034088", "Exxon Mobil Corporation",
            "ticker resolves to successor 'ExxonMobil Holdings Corp' (0002115436) with no "
            "10-K history; operating history is under 0000034088"),
}

# Companies do not tag the same line item the same way: Caterpillar reports revenue as
# `Revenues`, Coca-Cola does not use that tag at all (it 404s) and reports under a
# contract-with-customer tag. Asking for a fixed concept list per company therefore returns
# almost nothing for half the roster — KO came back with 16 facts and no revenue at all.
# So: fetch `companyfacts` ONCE per company and select locally, preferring the first tag the
# company actually uses. One request instead of sixteen, and it adapts to the filer.
LINE_ITEMS = {
    "Revenues": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                 "RevenueFromContractWithCustomerIncludingAssessedTax",
                 "SalesRevenueNet", "SalesRevenueGoodsNet"],
    "CostOfRevenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    "GrossProfit": ["GrossProfit"],
    "OperatingIncomeLoss": ["OperatingIncomeLoss"],
    "NetIncomeLoss": ["NetIncomeLoss", "ProfitLoss"],
    "Assets": ["Assets"],
    "AssetsCurrent": ["AssetsCurrent"],
    "Liabilities": ["Liabilities"],
    "LiabilitiesCurrent": ["LiabilitiesCurrent"],
    "StockholdersEquity": ["StockholdersEquity",
                           "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "CashAndCashEquivalents": ["CashAndCashEquivalentsAtCarryingValue"],
    "InventoryNet": ["InventoryNet"],
    "LongTermDebtNoncurrent": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "ResearchAndDevelopmentExpense": ["ResearchAndDevelopmentExpense"],
    "EarningsPerShareDiluted": ["EarningsPerShareDiluted"],
}

def _get(url):
    import requests
    r = requests.get(url, headers=UA, timeout=30)
    if r.status_code == 404: return None
    r.raise_for_status()
    time.sleep(0.15)          # ~7 req/s, under SEC's 10/s
    return r.json()


def resolve(tickers):
    d = _get("https://www.sec.gov/files/company_tickers.json")
    want = set(tickers)
    out = {}
    for v in d.values():
        if v["ticker"] in want:
            out[v["ticker"]] = (str(v["cik_str"]).zfill(10), v["title"])
    return out


def snapshot(ticker, cik, name):
    """Annual (FY, 10-K) facts only — the grain finance_qa questions ask at."""
    cf = _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json") or {}
    gaap = (cf.get("facts") or {}).get("us-gaap") or {}
    facts, used = [], {}
    for item, candidates in LINE_ITEMS.items():
        tag = next((c for c in candidates if c in gaap), None)
        if not tag: continue
        used[item] = tag
        for unit, rows in (gaap[tag].get("units") or {}).items():
            if unit not in ("USD", "USD/shares"): continue
            for r in rows:
                if r.get("form") != "10-K" or r.get("fp") != "FY": continue
                facts.append({"concept": item, "xbrl_tag": tag, "unit": unit,
                              "fy": str(r.get("fy")), "fp": r.get("fp"),
                              "period_end": r.get("end"), "value": r.get("val"),
                              "form": r.get("form"), "filed": r.get("filed"),
                              "accession": r.get("accn")})
    # one row per (concept, period_end): keep the most recently filed restatement
    best = {}
    for f in facts:
        k = (f["concept"], f["period_end"])
        if k not in best or (f["filed"] or "") > (best[k]["filed"] or ""):
            best[k] = f
    facts = sorted(best.values(), key=lambda f: (f["concept"], f["period_end"]))
    return {"ticker": ticker, "cik": cik, "name": name,
            "fetched_at": time.strftime("%Y-%m-%d"),
            "source": "https://data.sec.gov/api/xbrl/companyfacts",
            "tags_used": used,
            "note": "SIMULATION FIXTURE — real reported values, frozen; the world clock is 2026-03-02",
            "facts": facts}


def load_into_world(db=None):
    """Seed filings_companies/filings_facts in the built world from the snapshots."""
    import sqlite3
    db = Path(db or ROOT / "world/build/core.sqlite")
    cx = sqlite3.connect(db)
    n_c = n_f = 0
    for p in sorted(OUT.glob("*.json")):
        if p.name.startswith("_"): continue   # _company_tickers.json is the lexicon cache, not a snapshot
        s = json.loads(p.read_text())
        cx.execute("INSERT OR REPLACE INTO filings_companies VALUES(?,?,?)",
                   (s["cik"], s["ticker"], s["name"]))
        n_c += 1
        for f in s["facts"]:
            cx.execute("INSERT OR REPLACE INTO filings_facts"
                       "(cik,concept,unit,fy,fp,period_end,value,form,filed,accession)"
                       " VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (s["cik"], f["concept"], f["unit"], f["fy"], f["fp"],
                        f["period_end"], f["value"], f["form"], f["filed"], f["accession"]))
            n_f += 1
    cx.commit(); cx.close()
    print(f"loaded {n_c} companies / {n_f} facts into {db}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", default=",".join(DEFAULT_TICKERS))
    ap.add_argument("--load", action="store_true", help="seed the built world from existing snapshots")
    a = ap.parse_args()
    if a.load:
        return load_into_world()
    OUT.mkdir(parents=True, exist_ok=True)
    tickers = [t.strip().upper() for t in a.tickers.split(",") if t.strip()]
    resolved = resolve(tickers)
    for tk, (cik, name, why) in CIK_OVERRIDES.items():
        if tk in tickers:
            resolved[tk] = (cik, name)
            print(f"  [override] {tk} -> CIK {cik}: {why}")
    missing = sorted(set(tickers) - set(resolved))
    if missing: print("unresolved tickers:", missing)
    for t, (cik, name) in sorted(resolved.items()):
        s = snapshot(t, cik, name)
        (OUT / f"{t}.json").write_text(json.dumps(s, indent=1) + "\n")
        yrs = sorted({f["period_end"][:4] for f in s["facts"]})
        print(f"  {t:5} CIK {cik}  {len(s['facts']):4} facts  FY {yrs[0] if yrs else '-'}-{yrs[-1] if yrs else '-'}  {name}")


if __name__ == "__main__":
    sys.exit(main())
