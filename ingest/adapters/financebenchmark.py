#!/usr/bin/env python3
"""Adapter: microsoft/FinanceBenchmark -> TaskSpec.

Three plugins, three different porting classes — which is the point of classifying per ITEM
rather than per repo:
  erp_qa (100)          verbatim_gt   question + checkable GT against the ERP
  finance_qa (126)      split         single-figure items are `recomputable`; open analytical
                                      prompts are `not_agentic` for us (their rubric is 2,394
                                      style assertions scored by an LLM judge, and this repo
                                      bans LLM judges from the reward path)
  business_brief (25)   judgement_port structured profile; graded per required field
"""
import re, sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ir import TaskSpec, GroundTruth

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "research/external/financebenchmark-extracts/data/dataset.yaml"
REPO = "microsoft/FinanceBenchmark"
LICENCE = "MIT"

# A finance_qa item is deterministically checkable only if it asks for a FIGURE. These are the
# shapes that do; everything else is an analytical prompt whose only grader is a judge.
FIGURE = re.compile(r"\b(what (is|was|are|were)|how much|how many|reported|total|provide the "
                    r"(figure|amount|value)|state the)\b", re.I)
ANALYTIC = re.compile(r"\b(assess|evaluate|analy[sz]e|comprehensive|outlook|positioning|"
                      r"strategy|compare .* and .* across|discuss|summari[sz]e|brief|overview|"
                      r"recommend|implications)\b", re.I)

TICKERS = {
    "walmart": "WMT", "coca-cola": "KO", "coca cola": "KO", "chevron": "CVX",
    "caterpillar": "CAT", "intel": "INTC", "exxonmobil": "XOM", "exxon mobil": "XOM",
    "amazon": "AMZN", "microsoft": "MSFT", "pfizer": "PFE", "apple": "AAPL",
    "ford motor company": "F", "tesla": "TSLA", "boeing": "BA", "nvidia": "NVDA",
}

def _companies(q):
    ql = q.lower()
    return sorted({t for name, t in TICKERS.items() if name in ql})

def load():
    d = yaml.safe_load(DATASET.read_text())
    return d if isinstance(d, list) else d["tasks"]

def specs():
    out = []
    for i, t in enumerate(load()):
        q = (t.get("query") or "").strip()
        plugin = t.get("plugin")
        base = dict(source_repo=REPO, source_path="data/dataset.yaml",
                    source_id=f"{plugin}-{i:03d}", licence=LICENCE, question=q)

        if plugin == "erp_qa":
            # entity references are resolved by the existing cloner's handlers; the adapter
            # records the scenario so binding can be checked per question
            out.append(TaskSpec(**base, portability="verbatim_gt", family="erp_qa_fb",
                                capabilities=["erp", "erp_customers", "erp_vendors", "erp_cust_trans"],
                                notes=f"scenario={t.get('scenario')}",
                                ground_truth=[GroundTruth("answer", "number")]))

        elif plugin == "finance_qa":
            comps = _companies(q)
            analytic = bool(ANALYTIC.search(q)) or len(comps) > 1
            checkable = bool(FIGURE.search(q)) and not analytic
            if checkable:
                out.append(TaskSpec(**base, portability="recomputable", family="finance_qa",
                                    entities=comps,
                                    capabilities=["filings", "filings_facts", "filings_companies"],
                                    ground_truth=[GroundTruth("figure", "number", tol_rel=0.001)],
                                    notes="single-figure; GT computable from a frozen filings snapshot"))
            else:
                out.append(TaskSpec(**base, portability="not_agentic", family="finance_qa",
                                    entities=comps, capabilities=["filings"],
                                    dropped=["open analytical prompt: FB grades it with a DSPy "
                                             "LLM judge over style assertions (clarity, "
                                             "groundedness, citations); this repo bans LLM "
                                             "judges from the reward path"],
                                    notes="analytical" + (f"; multi-company {comps}" if len(comps) > 1 else "")))

        elif plugin == "business_brief":
            out.append(TaskSpec(**base, portability="judgement_port", family="business_brief",
                                entities=_companies(q),
                                capabilities=["filings", "erp"],
                                ground_truth=[GroundTruth("sections", "contains_all")],
                                dropped=["free-text prose scoring; we grade required fields "
                                         "and per-field figures instead"],
                                notes="structured profile fusing public filings with internal AR/AP"))
    return out

if __name__ == "__main__":
    import collections
    s = specs()
    print(f"{REPO}: {len(s)} items")
    print(collections.Counter(x.portability for x in s))
