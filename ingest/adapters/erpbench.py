#!/usr/bin/env python3
"""Adapter: agentic-labs/erp-bench -> TaskSpec.

Every item used to be `needs_surface`: the tasks are already true Harbor directories, but they
drive Odoo 19 procurement and manufacturing over a JSON-2 API this world did not mock.

That is no longer the blocker. The surface exists — `erpb_*` in `world/schema.sql` and
`mcp/servers/odoo_server.py`, shaped from the wave-4 Odoo checkout — so these items are
reclassified `judgement_port` and the honest denominator now includes all 300.

**The rate goes DOWN when this lands, and that is correct.** Counting 300 items as
out-of-scope kept them out of the denominator; committing to build them puts them in. A
coverage number that only ever improves is a number being managed rather than measured.

What each item still needs to emit is recorded per item, not per repo, because the remaining
blockers differ:
  * assembly_units > 0 -> the oracle walk generator must explode the BOM and schedule
    workcenter capacity. The surface serves it; the walk builder does not yet.
  * downpayment/invoicing policy -> not yet expressed as a scalar SQL assertion, and shipping
    it graded by anything looser would break the A10.2 rule (the prompt states a policy the
    checks do not grade).
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ir import TaskSpec

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "research/external/repos/erp-bench/tasks"
REPO, LICENCE = "agentic-labs/erp-bench", "see repo LICENSE"


def _blocker(d):
    """Mirrors world/etl/clone_erpbench.portable(): what still stops this item emitting."""
    try:
        sc = json.loads((d / "environment/scenario_data.json").read_text())
        plan = json.loads((d / "solution/optimal_plan.json").read_text())
    except Exception:
        return "scenario or optimal_plan unreadable"
    if not (sc.get("products") or []): return "no products in scenario"
    if not (plan.get("allocations") or []): return "no allocations in optimal_plan"
    if any(a.get("assembly_units") for a in plan.get("allocations") or []):
        return "manufacturing walk generator (BOM explosion + workcenter capacity)"
    if (sc.get("invoicing_policy") or {}).get("downpayment_required"):
        return "downpayment/invoicing policy as a scalar assertion"
    return None


def specs():
    out = []
    for d in sorted(TASKS.glob("2*")):
        if not (d / "task.toml").exists(): continue
        m = re.match(r"(\d+)_(easy|medium|hard)_(.*)", d.name)
        blocker = _blocker(d)
        out.append(TaskSpec(
            source_repo=REPO, source_path=f"tasks/{d.name}", source_id=d.name, licence=LICENCE,
            portability="judgement_port", family="erpbench",
            question=(d / "instruction.md").read_text()[:300] if (d / "instruction.md").exists() else d.name,
            entities=[], capabilities=["odoo", "erpb_products", "erpb_vendor_offers"],
            notes=f"difficulty={m.group(2) if m else '?'} pattern={m.group(3) if m else '?'}"
                  + (f"; blocked: {blocker}" if blocker else "; portable"),
            dropped=([blocker] if blocker else
                     ["FB-style live-Odoo grading: the source queries a running server with "
                      "odoolib; here the same judgement is deterministic SQL state assertions"]),
        ))
    return out


if __name__ == "__main__":
    import collections
    s = specs()
    print(f"{REPO}: {len(s)} items")
    print(collections.Counter((x.dropped or ["?"])[0][:60] for x in s))
