#!/usr/bin/env python3
"""Adapter: TheAgentCompany finance tasks -> TaskSpec.

Every item is `judgement_port`: the judgement transfers, the plumbing (Docker + ownCloud +
RocketChat, graded over written .xlsx artefacts) does not.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ir import TaskSpec, GroundTruth

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "research/external/repos/TheAgentCompany/workspaces/tasks"
REPO, LICENCE = "TheAgentCompany", "MIT"

def specs():
    out = []
    for d in sorted(TASKS.glob("finance-*")):
        md = (d / "task.md")
        if not md.exists(): continue
        out.append(TaskSpec(
            source_repo=REPO, source_path=str(d.relative_to(ROOT)), source_id=d.name,
            licence=LICENCE, portability="judgement_port",
            question=md.read_text().strip()[:600], family="ported",
            capabilities=["sheets", "docs", "erp"],
            ground_truth=[GroundTruth("ported_fields", "contains_all")],
            dropped=["ownCloud/RocketChat/Docker estate and .xlsx artefact grading; the "
                     "judgement is re-authored onto sheets/docs/submit_answer"],
        ))
    return out

if __name__ == "__main__":
    print(f"{REPO}: {len(specs())} finance items")
