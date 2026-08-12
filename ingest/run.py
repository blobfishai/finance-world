#!/usr/bin/env python3
"""Survey every registered corpus, bind it to the world, and print the parity ledger.

    python3 ingest/run.py              # ledger
    python3 ingest/run.py --detail     # + why each rejected item was rejected

The ledger is GENERATED. docs/PARITY.md quotes it; it is never hand-maintained, because a
hand-kept coverage number is exactly the kind of claim this repo does not ship.
"""
import argparse, collections, importlib, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingest"))
from capability import World
from bind import bind

ADAPTERS = ["financebenchmark", "theagentcompany", "erpbench"]

def shipped():
    """What already runs here, by the source it was ported from.

    Ported clones and generated instances are counted SEPARATELY and never summed into the
    parity rate. A generated instance re-asks a pattern the benchmark established, over a
    different entity; it is breadth, not coverage of a new benchmark item. Counting the 1,026
    sweep instances as FinanceBenchmark clones is what made this ledger report 689% of
    addressable (docs/AUDIT.md A15) - a number that discredits the whole document.
    """
    ports, insts, patterns = collections.Counter(), collections.Counter(), collections.defaultdict(set)
    varis = collections.Counter()
    for t in ROOT.glob("tasks/*/*/task.toml"):
        meta = tomllib.loads(t.read_text()).get("metadata", {})
        origin = (meta.get("origin") or "") + " " + t.parent.name
        if "FinanceBenchmark" in origin or t.parent.parent.name in ("erp_qa_fb", "erp_qa_gen"):
            repo = "microsoft/FinanceBenchmark"
        elif "TheAgentCompany" in origin:
            repo = "TheAgentCompany"
        elif "erp-bench" in origin or "ERP-Bench" in origin:
            repo = "agentic-labs/erp-bench"
        else:
            continue
        if meta.get("variant_of"):
            varis[repo] += 1
        elif meta.get("generated"):
            insts[repo] += 1
            patterns[repo].add(meta.get("pattern") or "unlabelled")
        else:
            ports[repo] += 1
    return ports, insts, patterns, varis

def main(detail=False):
    world = World()
    ship, insts, patterns, varis = shipped()
    # filings is indexed by BOTH name and ticker, so len() is 2x the companies - report the
    # distinct tickers instead. A capability headline that double-counts is the same class of
    # error as A15, just smaller.
    print(f"world capability: {len(world.tables)} tables · {len(world.parties)} named parties · "
          f"{len(world.servers)} servers · {len(set(world.filings.values()))} filing companies\n")
    grand = collections.Counter()
    for name in ADAPTERS:
        try:
            mod = importlib.import_module(f"adapters.{name}")
        except Exception as e:
            print(f"## {name}: adapter not available ({e})\n"); continue
        specs = [bind(s, world) for s in mod.specs()]
        repo = specs[0].source_repo if specs else name
        cls = collections.Counter(s.portability for s in specs)
        addressable = [s for s in specs if s.portability in ("verbatim_gt", "recomputable", "judgement_port")]
        binds = collections.Counter(s.bind_status for s in addressable)
        run_here = ship.get(repo, 0)
        print(f"## {repo} — {len(specs)} items")
        print(f"   class     : " + " · ".join(f"{k} {v}" for k, v in cls.most_common()))
        print(f"   addressable: {len(addressable)}   (excludes not_agentic / needs_surface)")
        print(f"   binding   : " + (" · ".join(f"{k} {v}" for k, v in binds.most_common()) or "n/a"))
        print(f"   ported    : {run_here}   -> {run_here/len(addressable)*100:.0f}% of addressable"
              if addressable else "   ported    : 0")
        if insts.get(repo):
            print(f"   instances : {insts[repo]} generated over {len(patterns[repo])} patterns "
                  f"(breadth; excluded from the rate above)")
        if varis.get(repo):
            print(f"   variants  : {varis[repo]} escalated from ported tasks "
                  f"(depth; excluded from the rate above)")
        grand["items"] += len(specs); grand["addressable"] += len(addressable); grand["runs"] += run_here
        grand["insts"] += insts.get(repo, 0); grand["varis"] += varis.get(repo, 0)
        if detail:
            for s in addressable:
                if s.bind_status != "bound":
                    print(f"      [{s.bind_status}] {s.source_id}: {s.bind_detail[:110]}")
            for s in specs:
                if s.portability in ("not_agentic", "needs_surface") and s.dropped:
                    print(f"      [{s.portability}] {s.source_id}: {s.dropped[0][:110]}")
                    break
        print()
    print("=" * 74)
    print(f"TOTAL  items {grand['items']} · addressable {grand['addressable']} · "
          f"ported {grand['runs']} "
          f"({grand['runs']/max(grand['addressable'],1)*100:.0f}% of addressable)")
    print(f"       + {grand['insts']} generated instances (breadth) · {grand['varis']} escalated "
          f"variants (depth) — counted separately by design")

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--detail", action="store_true")
    main(a.parse_args().detail)
