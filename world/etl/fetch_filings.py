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
import argparse, datetime as dt, json, sys, time
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
    # Banks do not report "revenue" as a product sale: Goldman and Wells Fargo tag
    # RevenuesNetOfInterestExpense and nothing else, so before this line Goldman held NO annual
    # revenue at all and Wells Fargo's most recent was FY2019. A financial-sector brief was
    # therefore either impossible or six years stale.
    "Revenues": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                 "RevenueFromContractWithCustomerIncludingAssessedTax",
                 "RevenuesNetOfInterestExpense",
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
    # Added after the finance_qa bind probe: FB asks for operating cash flow and capex by name
    # and neither was fetched, so four items rejected as `fact_absent` against a world that
    # simply had not been asked to hold them.
    "NetCashProvidedByUsedInOperatingActivities": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "PaymentsToAcquirePropertyPlantAndEquipment": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets"],
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
    """Annual (10-K/FY) and quarterly (10-Q/Q1-Q3) facts.

    Two corrections found by the finance_qa bind probe:

    1. Tag selection preferred PRESENCE over COVERAGE. `next(c for c in candidates if c in gaap)`
       picked `Revenues` for Microsoft, who tag it for FY2010 only and report everything since
       under the ASC-606 contract-with-customer tag — so Microsoft held 12 revenue facts, all
       from 2010, and every modern revenue question rejected as `fact_absent`. Candidates are
       now merged across the whole history and resolved PER PERIOD in priority order, which is
       what the 2018 ASC-606 transition actually requires: legacy tag before, new tag after.

    2. Quarterly facts were dropped entirely (`form != "10-K"` skipped every 10-Q), so a
       question asking for Q3 silently matched the FULL-YEAR row. That is a wrong ground truth
       that looks bound, the A10.3 failure mode. Quarterly rows are now stored with their real
       `fp`, and duration-filtered so a Q3 row is one quarter, never a nine-month cumulative.
    """
    cf = _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json") or {}
    gaap = (cf.get("facts") or {}).get("us-gaap") or {}
    facts, used = [], {}

    def _duration_ok(r, fp):
        """Income-statement rows carry start+end; keep annual ~365d and quarterly ~90d.
        Without this, a 10-Q's year-to-date column is stored as if it were the quarter."""
        s, e = r.get("start"), r.get("end")
        if not s or not e: return True                     # balance-sheet instant
        try:
            d = (dt.date.fromisoformat(e) - dt.date.fromisoformat(s)).days
        except Exception:
            return True
        return 300 <= d <= 400 if fp == "FY" else 60 <= d <= 115

    for item, candidates in LINE_ITEMS.items():
        present = [c for c in candidates if c in gaap]
        if not present: continue
        used[item] = present[0] if len(present) == 1 else f"{present[0]} (+{len(present)-1} fallback)"
        # priority order = candidate order; later candidates only fill periods earlier ones miss
        for prio, tag in enumerate(present):
            for unit, rows in (gaap[tag].get("units") or {}).items():
                if unit not in ("USD", "USD/shares"): continue
                for r in rows:
                    form, fp = r.get("form"), r.get("fp")
                    if form == "10-K" and fp == "FY": pass
                    elif form == "10-Q" and fp in ("Q1", "Q2", "Q3"): pass
                    else: continue
                    if not _duration_ok(r, fp): continue
                    facts.append({"concept": item, "xbrl_tag": tag, "unit": unit,
                                  "fy": str(r.get("fy")), "fp": fp, "_prio": prio,
                                  "period_end": r.get("end"), "value": r.get("val"),
                                  "form": form, "filed": r.get("filed"),
                                  "accession": r.get("accn")})
    # one row per (concept, period_end, fp): prefer the higher-priority tag, then the most
    # recently filed restatement. fp is part of the key because a period_end can carry both a
    # quarterly and an annual figure.
    best = {}
    for f in facts:
        k = (f["concept"], f["period_end"], f["fp"])
        cur = best.get(k)
        # lower _prio wins outright; within the same tag, the latest filing (restatement) wins
        if cur is None or f["_prio"] < cur["_prio"] or (
                f["_prio"] == cur["_prio"] and (f["filed"] or "") > (cur["filed"] or "")):
            best[k] = f
    for f in best.values(): f.pop("_prio", None)
    facts = sorted(best.values(), key=lambda f: (f["concept"], f["period_end"], f["fp"]))
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
    # The snapshots ARE the source of truth for this surface, so seeding replaces rather than
    # appends. filings_facts carries no unique constraint, so `INSERT OR REPLACE` does not
    # replace anything — re-running this against a populated table silently doubled every fact,
    # and a duplicated fact reads downstream as "two period_ends equidistant from the date you
    # asked for", i.e. a legitimate question becomes unanswerable. Same shape as A6: an ETL step
    # that is only correct on an empty database.
    cx.execute("DELETE FROM filings_facts")
    cx.execute("DELETE FROM filings_companies")
    cx.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_filings_facts "
               "ON filings_facts(cik, concept, period_end, fp)")
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
