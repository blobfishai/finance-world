#!/usr/bin/env python3
"""What this world can actually serve: entities, tables, servers, filings coverage.

Read from the BUILT world and the live server registries, never from a hand-kept list — a
capability list that drifts from the world is how questions get bound to things that are not
there (docs/AUDIT.md A10.3).
"""
import os, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _norm(s): return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()

class World:
    def __init__(self, db=None):
        self.db = Path(db or ROOT / "world/build/core.sqlite")
        cx = sqlite3.connect(self.db)
        self.tables = {r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        # name -> [(side, account)]. A list, not a scalar: customer and vendor masters share
        # names ("Contoso Retail" is both), and a dict silently kept whichever loaded last,
        # which would bind a customer question to a vendor account.
        self.parties, self.accounts = {}, {}
        for tbl, side in (("erp_customers", "customer"), ("erp_vendors", "vendor")):
            if tbl in self.tables:
                for acct, name in cx.execute(f"SELECT account, name FROM {tbl}"):
                    self.parties.setdefault(_norm(name), []).append((side, acct))
                    self.accounts[acct.upper()] = name
        # index by BOTH ticker and name: adapters legitimately reference either, and a
        # ticker-only reference must not read as "this world does not have that company".
        self.filings = {}
        if "filings_companies" in self.tables:
            for tk, nm in cx.execute("SELECT ticker, name FROM filings_companies"):
                self.filings[_norm(nm)] = tk
                self.filings[_norm(tk)] = tk
        cx.close()
        self.servers = {p.stem.replace("_server", "")
                        for p in (ROOT / "mcp/servers").glob("*_server.py")}

    def find_entity(self, ref, side=None):
        """STRICT. Exact account id, or exact normalised name. No fuzzy neighbour matching —
        that is precisely the A10.3 defect: 'Contoso Retail San Diego' silently became
        'Contoso Retail' and the ground truth was pinned to the wrong account.

        Returns an account id, or None. Ambiguous names (present in both masters, with no
        `side` given) return None with `.last_reason` set — an ambiguous bind is a defect to
        report, not a coin flip to resolve."""
        self.last_reason = ""
        r = str(ref).strip()
        if r.upper() in self.accounts: return r.upper()
        n = _norm(r)
        if n in self.parties:
            hits = [a for s, a in self.parties[n] if side is None or s == side]
            if len(hits) == 1: return hits[0]
            if not hits:
                self.last_reason = f"exists, but not as a {side}"
            else:
                self.last_reason = ("ambiguous: " +
                                    ", ".join(f"{s}:{a}" for s, a in self.parties[n]))
            return None
        if n in self.filings: return self.filings[n]
        return None

    def near_misses(self, ref, k=3):
        """Reported for triage only — never used to bind."""
        n = _norm(ref)
        toks = set(n.split())
        scored = []
        for name, hits in self.parties.items():
            common = toks & set(name.split())
            if common: scored.append((len(common) / max(len(toks), 1), name, hits[0][1]))
        return sorted(scored, reverse=True)[:k]
