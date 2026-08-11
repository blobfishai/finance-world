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
    """What already runs here, by the source it was ported from."""
    out = collections.Counter()
    for t in ROOT.glob("tasks/*/*/task.toml"):
        meta = tomllib.loads(t.read_text()).get("metadata", {})
        origin = (meta.get("origin") or "") + " " + t.parent.name
        if "FinanceBenchmark" in origin or t.parent.parent.name == "erp_qa_fb":
            out["microsoft/FinanceBenchmark"] += 1
        elif "TheAgentCompany" in origin:
            out["TheAgentCompany"] += 1
        elif "erp-bench" in origin or "ERP-Bench" in origin:
            out["agentic-labs/erp-bench"] += 1
    return out

def main(detail=False):
    world = World()
    ship = shipped()
    print(f"world capability: {len(world.tables)} tables · {len(world.parties)} named parties · "
          f"{len(world.servers)} servers · {len(world.filings)} filing companies\n")
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
        print(f"   runs here : {run_here}   -> {run_here/len(addressable)*100:.0f}% of addressable"
              if addressable else "   runs here : 0")
        grand["items"] += len(specs); grand["addressable"] += len(addressable); grand["runs"] += run_here
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
          f"running here {grand['runs']} "
          f"({grand['runs']/max(grand['addressable'],1)*100:.0f}% of addressable)")

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--detail", action="store_true")
    main(a.parse_args().detail)
