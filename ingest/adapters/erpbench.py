#!/usr/bin/env python3
"""Adapter: agentic-labs/erp-bench -> TaskSpec.

Every item is `needs_surface`. The tasks are already true Harbor directories — the blocker is
not format, it is that they drive Odoo 19 procurement/manufacturing over a JSON-2 API this
world does not mock. Recorded explicitly so 300 tasks are a build decision, not silence.
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ir import TaskSpec

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "research/external/repos/erp-bench/tasks"
REPO, LICENCE = "agentic-labs/erp-bench", "see repo LICENSE"

def specs():
    out = []
    for d in sorted(TASKS.glob("2*")):
        if not (d / "task.toml").exists(): continue
        m = re.match(r"(\d+)_(easy|medium|hard)_(.*)", d.name)
        out.append(TaskSpec(
            source_repo=REPO, source_path=f"tasks/{d.name}", source_id=d.name, licence=LICENCE,
            portability="needs_surface", family="procurement",
            question=(d / "instruction.md").read_text()[:300] if (d / "instruction.md").exists() else d.name,
            capabilities=["odoo"],            # deliberately unbindable: names the missing surface
            notes=f"difficulty={m.group(2) if m else '?'} pattern={m.group(3) if m else '?'}",
            dropped=["Odoo 19 procurement/manufacturing surface (sale.order, purchase.order, "
                     "mrp.production) is not mocked here; porting needs that build, not a "
                     "transcription"],
        ))
    return out

if __name__ == "__main__":
    print(f"{REPO}: {len(specs())} items")
