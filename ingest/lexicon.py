#!/usr/bin/env python3
"""Company-name -> ticker lexicon, built from SEC's own registrant list.

Entity extraction by hardcoded map was the wrong shape: 30 of 61 addressable FinanceBenchmark
finance items extracted NO entity, so they bound as "bound" while naming companies the world
does not hold. A binder that cannot see an entity cannot report it missing, and the ledger
inherits that as false confidence.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research/external/edgar-snapshots/_company_tickers.json"

SUFFIX = re.compile(r"\b(inc|corp|corporation|co|company|holdings|holding|group|plc|ltd|"
                    r"limited|lp|llc|sa|nv|ag|the|class|common|stock)\b\.?", re.I)
# words that are real company names but also ordinary English; require a longer or
# suffixed match before believing them
AMBIGUOUS = {"target", "discover", "visa", "block", "match", "gap", "cost", "peak", "shell"}

def _norm(s):
    s = SUFFIX.sub(" ", str(s).lower())
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()

class Lexicon:
    def __init__(self):
        # Several registrants normalise to the same key once legal suffixes are stripped:
        # "TARGET CORP" and "Target Group Inc." both become "target", and first-wins picked
        # the wrong one. Keep every candidate and resolve by (fewest words in the real title,
        # then SEC's own rank order) — the canonical registrant is the plainly-named one.
        self.by_ticker, cands = {}, {}
        if not SRC.exists():
            self.by_name, self._names = {}, []
            return
        for i, v in enumerate(json.loads(SRC.read_text()).values()):
            tk, title = v["ticker"], v["title"]
            self.by_ticker[tk.upper()] = title
            n = _norm(title)
            if not n or len(n) < 3: continue
            keys = {n}
            # SEC titles carry registrant cruft the question never uses:
            # "COSTCO WHOLESALE CORP /NEW" -> the question says "Costco Wholesale".
            # Index the leading significant tokens as aliases too.
            toks = n.split()
            if len(toks) >= 2: keys.add(" ".join(toks[:2]))
            if len(toks) >= 3: keys.add(" ".join(toks[:3]))
            for k in keys:
                if len(k) >= 4:
                    cands.setdefault(k, []).append((len(title.split()), i, tk))
        self.by_name = {n: sorted(c)[0][2] for n, c in cands.items()}
        # longest names first so "jpmorgan chase" wins over "jpmorgan"
        self._names = sorted(self.by_name, key=len, reverse=True)

    @staticmethod
    def _proper_in(name, text):
        toks = [re.escape(w) for w in name.split()]
        pat = r"\b" + r"[^A-Za-z0-9]{0,3}".join(r"[A-Z][A-Za-z&.\-]*" for _ in toks) + r"\b"
        for m in re.finditer(pat, text):
            if " ".join(re.findall(r"[a-z0-9]+", m.group(0).lower())).startswith(
                    " ".join(re.findall(r"[a-z0-9]+", name))[:len(name)][:40]):
                return True
        # single-token names: accept an exact capitalised occurrence
        if len(toks) == 1:
            return re.search(rf"\b{name.capitalize()}\b", text) is not None or \
                   re.search(rf"\b{name.upper()}\b", text) is not None
        return False

    def find(self, text):
        """Tickers for companies actually named in the text."""
        t = " " + _norm(text) + " "
        hits, consumed = [], []
        for name in self._names:
            if len(name) < 4: continue
            if name in AMBIGUOUS and f" {name} " not in t: continue
            if f" {name} " in t and not any(name in c for c in consumed):
                # Require proper-noun evidence in the ORIGINAL text. Plenty of registrants are
                # named after ordinary words — "The Joint Corp" (JYNT) matched the word
                # "joint" in "joint venture" — and a lowercase occurrence is not a company
                # reference. Each token of the name must appear capitalised.
                if not self._proper_in(name, text): continue
                hits.append(self.by_name[name]); consumed.append(name)
        # Explicit tickers ONLY where the text marks them as such. Bare uppercase matching
        # invented companies out of finance acronyms — GTM (go-to-market), FCF (free cash
        # flow), MA (M&A) are all real tickers — which inflated the "missing companies"
        # backlog with things nobody asked about.
        for m in re.findall(r"\((?:NYSE:|NASDAQ:)?\s*([A-Z]{1,5})\s*\)|\bticker\s+([A-Z]{1,5})\b", text):
            tk = (m[0] or m[1]).strip()
            if tk in self.by_ticker and tk not in hits: hits.append(tk)
        return sorted(set(hits))
