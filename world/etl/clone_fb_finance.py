#!/usr/bin/env python3
"""Clone microsoft/FinanceBenchmark `finance_qa` single-figure items onto the frozen filings
snapshot.

FB grades these with a DSPy LLM judge over style assertions. This repo bans judges from the
reward path, so a clone ships only when the figure is recomputable from the snapshot and can
be pinned exactly — value, period and source form, each asserted separately.

Binding is STRICT (docs/INGESTION.md §4). Three outcomes, and fuzzy rebinding is not one:
  bound              -> emit
  absent_entity      -> reject (the company is not in the snapshot)
  missing_capability -> reject, NAMING the concept the world would have to hold

Period resolution is the part that silently goes wrong, so it is conservative by construction:

  * SEC's `fy` is the fiscal year OF THE FILING, and a filing carries prior-year comparatives.
    Matching on `fy` alone returns a figure from the wrong year that looks perfectly bound.
    Everything here resolves on `period_end`.
  * "Q3" must never match an annual row. `fp` is matched exactly, and the fetcher stores
    quarterly rows duration-filtered so a Q3 row is one quarter, not nine months cumulative.
  * If a period resolves to zero or several candidate rows, the item is REJECTED rather than
    guessed. A wrong ground truth is far more expensive than a missing task.

    python3 world/etl/clone_fb_finance.py --dry-run
    python3 world/etl/clone_fb_finance.py --out tasks/finance_qa_fb
"""
import argparse, datetime as dt, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
sys.path.insert(0, str(ROOT / "ingest"))

MONTHS = ("january february march april may june july august september october november "
          "december").split()

# ── question wording -> a concept the snapshot holds ────────────────────────────────────────
# Order matters: the most specific wording wins, so "operating cash flow" is not eaten by
# "cash and cash equivalents" and "diluted EPS" is not eaten by "earnings".
# The answer field is named for the concept, never a generic `figure`: a practitioner asked for
# operating cash flow expects to fill in "operating cash flow", and a graded field that says
# `figure` tells the model nothing about what it is being asked to produce.
DIRECT = [
    (r"diluted eps|diluted earnings per share",                "EarningsPerShareDiluted", "diluted_eps"),
    (r"operating cash flow|cash (?:flow )?from operations|"
     r"cash provided by operating",                            "NetCashProvidedByUsedInOperatingActivities", "operating_cash_flow_usd"),
    (r"capital expenditures?|capex",                           "PaymentsToAcquirePropertyPlantAndEquipment", "capex_usd"),
    (r"cash and cash equivalents",                             "CashAndCashEquivalents", "cash_and_equivalents_usd"),
    (r"current assets",                                        "AssetsCurrent", "current_assets_usd"),
    (r"long[- ]term debt",                                     "LongTermDebtNoncurrent", "long_term_debt_usd"),
    (r"net income|profitability",                              "NetIncomeLoss", "net_income_usd"),
    (r"operating income",                                      "OperatingIncomeLoss", "operating_income_usd"),
    (r"research and development",                              "ResearchAndDevelopmentExpense", "rd_expense_usd"),
    (r"total (?:annual )?revenue|revenue in usd|"
     r"reported revenue|revenue for",                          "Revenues", "revenue_usd"),
    (r"total assets",                                          "Assets", "total_assets_usd"),
]

# derived figures: name -> (numerator, denominator, style, label)
#   style "pct"      -> 100 * num/den, percent to 2dp      (operating margin)
#   style "ratio"    -> num/den                            (debt-to-equity)
#   style "turnover" -> num / AVERAGE(den, prior den)      (inventory / asset turnover)
# Conventions match the hand-authored tasks they generalise (finance_qa/wmt-inventory-turnover,
# finance_qa/tsla-operating-margin-q3): the ratio AND both inputs are graded, so the ratio
# cannot be guessed and back-fitted.
DERIVED = {
    "operating margin":   ("OperatingIncomeLoss", "Revenues", "pct",
                           ("operating_margin_pct", "operating_income", "revenue")),
    "inventory turnover": ("CostOfRevenue", "InventoryNet", "turnover",
                           ("inventory_turnover", "cost_of_revenue", "average_inventory")),
    "asset turnover":     ("Revenues", "Assets", "turnover",
                           ("asset_turnover", "revenue", "average_assets")),
    "debt-to-equity":     ("Liabilities", "StockholdersEquity", "ratio",
                           ("debt_to_equity", "total_liabilities", "stockholders_equity")),
    "debt to equity":     ("Liabilities", "StockholdersEquity", "ratio",
                           ("debt_to_equity", "total_liabilities", "stockholders_equity")),
}

# Shapes the snapshot structurally cannot serve. Named individually so the rejection is a
# build list, not a shrug — each says what a world would have to hold to answer it.
NO_CAPABILITY = [
    (r"greenhouse gas|scope 1|scope 2|emissions",
     "sustainability/ESG disclosure — not in the XBRL us-gaap financial facts"),
    (r"surprise percentage|earnings surprise|consensus",
     "analyst consensus estimates — no filing carries the expectation to compare against"),
    (r"\badidas\b|\bnestl|\bsamsung\b",
     "non-SEC registrant — files no XBRL with the Commission"),
    (r"segment revenue|greater china|by segment|segment breakdown",
     "segment-level disaggregation — the snapshot holds consolidated concepts only"),
    (r"provisions for litigation|legal provisions|litigation reserve",
     "footnote line item — not a standard us-gaap concept in the snapshot"),
]


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


class Snapshot:
    def __init__(self, cx):
        self.cx = cx
        self.by_ticker, self.by_name = {}, {}
        for cik, tk, nm in cx.execute("SELECT cik, ticker, name FROM filings_companies"):
            self.by_ticker[tk.upper()] = (cik, nm)
            self.by_name[_norm(nm)] = tk.upper()

    def company(self, q):
        """Resolve a company mentioned in the question. Never fuzzy-rebinds (A10.3).

        Matching is prefix-anchored, not whole-word: the registrant name is "Exxon Mobil
        Corporation" but the question writes "ExxonMobil", and `\\bexxon\\b` cannot match that —
        there is no word boundary before the M. Two ExxonMobil items rejected as absent_entity
        against a world that holds the company.
        """
        for nm, tk in self.by_name.items():
            head = nm.split()[0]
            if len(head) > 3 and re.search(rf"\b{re.escape(head)}", q, re.I):
                return tk
        for tk in self.by_ticker:
            if re.search(rf"\b{tk}\b", q):
                return tk
        return None

    def rows(self, cik, concept, fp):
        return self.cx.execute(
            "SELECT value, period_end, form, accession, unit FROM filings_facts "
            "WHERE cik=? AND concept=? AND fp=? ORDER BY period_end", (cik, concept, fp)).fetchall()


def parse_period(q):
    """-> (fp, anchor_date, how) or (None, None, reason).

    `anchor` is the date the question points at; a row matches when its period_end is within
    the tolerance for that phrasing. Explicit dates are exact; a bare fiscal year is a window,
    because fiscal years end in January (retail) through December.
    """
    m = re.search(r"(?:ended?|ending|as of|at)\s+(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s*(\d{4})", q, re.I)
    if m:
        mo = MONTHS.index(m.group(1).lower()) + 1
        return "FY", dt.date(int(m.group(3)), mo, int(m.group(2))), "explicit_date"
    m = re.search(r"(?:as of|ended?|ending)\s+(" + "|".join(MONTHS) + r")\s+(\d{4})", q, re.I)
    if m:
        mo = MONTHS.index(m.group(1).lower()) + 1
        return "FY", dt.date(int(m.group(2)), mo, 28), "explicit_month"
    m = re.search(r"\bQ([1-4])\s*(?:FY\s*)?(\d{4})|(?:fiscal\s+)?Q([1-4])\s+(\d{4})", q, re.I)
    if m:
        qn = m.group(1) or m.group(3); yr = m.group(2) or m.group(4)
        return f"Q{qn}", dt.date(int(yr), 12, 31), "quarter"
    m = re.search(r"(?:FY|fiscal year|fiscal)\s*(?:ended\s*)?(\d{4})", q, re.I)
    if m:
        return "FY", dt.date(int(m.group(1)), 12, 31), "fiscal_year"
    m = re.search(r"\bin\s+(\d{4})\b|\bfor\s+(\d{4})\b", q)
    if m:
        return "FY", dt.date(int(m.group(1) or m.group(2)), 12, 31), "calendar_year"
    return None, None, "no period in question"


def pick(rows, anchor, how):
    """One row, or None. Ambiguity is a rejection, never a coin flip."""
    if not rows: return None, "no rows for concept/fp"
    tol = 5 if how in ("explicit_date",) else (45 if how == "explicit_month" else 200)
    scored = []
    for v, pe, form, acc, unit in rows:
        try: d = abs((dt.date.fromisoformat(pe) - anchor).days)
        except Exception: continue
        if d <= tol: scored.append((d, v, pe, form, acc, unit))
    if not scored: return None, f"no period_end within {tol}d of {anchor}"
    scored.sort()
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None, f"ambiguous: two period_ends equidistant from {anchor}"
    return scored[0], None


def build(q, snap):
    """-> (fields, walk_steps, note) or (None, None, reason)."""
    for rx, why in NO_CAPABILITY:
        if re.search(rx, q, re.I): return None, None, f"missing_capability: {why}"
    tk = snap.company(q)
    if not tk: return None, None, "absent_entity: no snapshot company named in the question"
    cik, name = snap.by_ticker[tk]
    fp, anchor, how = parse_period(q)
    if not fp: return None, None, f"unresolved_period: {how}"

    der = next((k for k in DERIVED if k in q.lower()), None)
    if der:
        num_c, den_c, style, labels = DERIVED[der]
        nrow, e1 = pick(snap.rows(cik, num_c, fp), anchor, how)
        drows = snap.rows(cik, den_c, fp)
        drow, e2 = pick(drows, anchor, how)
        if not nrow or not drow:
            return None, None, f"fact_absent: {tk} {der} needs {num_c}/{den_c} ({e1 or e2})"
        num, den, pe, form = nrow[1], drow[1], nrow[2], nrow[3]
        if style == "turnover":
            prior = [r for r in drows if r[1] < drow[2]]
            if not prior:
                return None, None, f"fact_absent: {tk} {der} needs a prior-period {den_c} to average"
            den = (drow[1] + prior[-1][0]) / 2.0
        if not den: return None, None, f"degenerate: {den_c} is zero"
        val = round(100.0 * num / den, 2) if style == "pct" else round(num / den, 4)
        fields = {labels[0]: (val, "number"), labels[1]: (num, "number"), labels[2]: (den, "number")}
        steps = [("lookup_company", {"query": name}),
                 ("get_company_concept", {"ticker": tk, "concept": num_c}),
                 ("get_company_concept", {"ticker": tk, "concept": den_c})]
        return fields, steps, f"{der} = {num_c}/{den_c} @ {pe} ({form})"

    hit = next(((c, lbl) for rx, c, lbl in DIRECT if re.search(rx, q, re.I)), None)
    if not hit: return None, None, "no_concept: question names no concept the snapshot holds"
    concept, label = hit
    # An explicit date may name a QUARTER end ("as of June 30, 2023", "the quarter ending
    # September 30, 2024"). The phrasing does not say which, so try the annual grain first and
    # fall back to the quarterly ones rather than rejecting a date the world holds.
    candidates = [fp] if how in ("quarter", "fiscal_year", "calendar_year") \
        else [fp, "Q1", "Q2", "Q3"]
    row = err = None
    for f in candidates:
        row, err = pick(snap.rows(cik, concept, f), anchor, how)
        if row: fp = f; break
    if not row: return None, None, f"fact_absent: {tk} {concept} {fp} ({err})"
    _d, val, pe, form, acc, unit = row
    fields = {label: (val, "number"), "period_end": (pe, "contains"), "source_form": (form, "contains")}
    steps = [("lookup_company", {"query": name}),
             ("get_company_concept", {"ticker": tk, "concept": concept})]
    return fields, steps, f"{concept} @ {pe} ({form}, {acc})"


def emit(out_dir, slug, question, fields, steps, note, source_id):
    d = out_dir / slug
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "solution").mkdir(parents=True, exist_ok=True)

    walk = [{"server": "filings", "tool": t, "args": a} for t, a in steps]
    walk.append({"server": "harness", "tool": "submit_answer",
                 "args": {"answers": {k: v for k, (v, _) in fields.items()}}})
    (d / "solution/walk.json").write_text(json.dumps(walk, indent=1) + "\n")

    checks = {"answer_checks": [], "trace_checks": [
        {"type": "required_servers", "servers": ["filings"]}, {"type": "reads_before_submit"}],
        "state_checks": [{"type": "writes_only", "tables": ["answers"]}]}
    for k, (v, kind) in fields.items():
        if kind == "number":
            ac = {"field": k, "type": "number", "expect": v}
            # a ratio is graded absolutely (0.02), a reported figure relatively (0.1%) — the
            # same split the hand-authored ratio tasks use
            ac["tol_abs" if abs(v) < 1000 else "tol_rel"] = 0.02 if abs(v) < 1000 else 0.001
            checks["answer_checks"].append(ac)
        else:
            checks["answer_checks"].append({"field": k, "type": "contains_all", "expect": [str(v)]})
    (d / "tests/checks.json").write_text(json.dumps(checks, indent=1) + "\n")

    lines = ["**Dana Kim · Credit Manager · Teams**", "", question.strip(), "", "---", "",
             "Reply with `submit_answer`:", ""]
    for k, (v, kind) in fields.items():
        lines.append(f"- `{k}` ({'number' if kind == 'number' else 'text'})")
    (d / "instruction.md").write_text("\n".join(lines) + "\n")

    (d / "task.toml").write_text(f'''schema_version = "1.4"

[task]
name = "{out_dir.name}/{slug}"
version = "0.1.0"
description = "FinanceBenchmark finance_qa clone — single figure from frozen SEC facts."
authors = ["nario-ai"]
keywords = ["finance", "finance_qa", "financebenchmark-clone"]

[metadata]
family = "{out_dir.name}"
origin = "clone of microsoft/FinanceBenchmark finance_qa item {source_id}; question verbatim, ground truth recomputed from the frozen SEC XBRL snapshot ({note}). FB grades this with an LLM judge; this clone pins the figure, its period and its source form as separate deterministic checks (docs/PARITY.md)"
generated = false
difficulty = "medium"
acceptance_label = "pending_calibration"
walk_len = {len(walk)}

[verifier]
timeout_sec = 120
[agent]
timeout_sec = 600
[environment]
cpus = 1
memory_mb = 1024
''')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tasks/finance_qa_fb")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    from adapters import financebenchmark as fb
    cx = sqlite3.connect(DB)
    snap = Snapshot(cx)
    out_dir = ROOT / a.out
    if not a.dry_run: out_dir.mkdir(parents=True, exist_ok=True)

    made, rejected = 0, []
    for s in [x for x in fb.specs() if x.portability == "recomputable"]:
        fields, steps, note = build(s.question, snap)
        if not fields:
            rejected.append((s.source_id, note)); continue
        tk = snap.company(s.question)
        key = re.sub(r"[^a-z0-9]+", "-", list(fields)[0].lower()).strip("-")
        slug = f"{tk.lower()}-{key}-{s.source_id.split('-')[-1]}"
        if a.dry_run:
            print(f"  ok   {slug:44} {note}")
        else:
            emit(out_dir, slug, s.question, fields, steps, note, s.source_id)
        made += 1

    print(f"\nemitted {made} / {made + len(rejected)}")
    print(f"rejected {len(rejected)}:")
    for sid, why in sorted(rejected, key=lambda r: r[1]):
        print(f"   {sid:18} {why}")


if __name__ == "__main__":
    sys.exit(main())
