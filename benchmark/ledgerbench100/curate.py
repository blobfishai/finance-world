#!/usr/bin/env python3
"""Curate the LedgerBench-100 release subset from the measured candidate scan.

Input: a scan JSON produced by replaying EVERY non-generated task's oracle walk at
HEAD (prepare -> in-process MCP replay -> vcode verify). Selection is deterministic:

  1. Pool = 478 ported + 30 variant tasks. erp_qa_gen template instances are
     excluded wholesale (the repo's own PARITY discipline).
  2. Hard gates: oracle reward == 1 at HEAD, single-step, walk ends in
     harness.submit_answer, checks carry the writes_only anti-hack veto.
  3. Every operational family is taken in full (they are small and hand-authored).
  4. The four large corpus-port families (erpbench, erp_qa_fb, business_brief_fb,
     finance_qa_fb) contribute a fixed-size slice, preferring write-layer grading
     (state_checks sql), harder difficulty, then longer walks.

Output: catalog.json with ids, family, provenance, and per-task rationale tags.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

RELEASE_VERSION = "3.3.0"
TARGET = 100
# Families taken in full (every eligible task ships).
FULL_FAMILIES = [
    "anomaly_triage", "bank_rec", "business_brief", "cash_app", "cash_forecast",
    "close_mgmt", "collections_ops", "cross_system", "erp_qa", "expense_audit",
    "finance_qa", "fpna", "journal_entry", "payment_proposal", "payment_run",
    "pbc", "threeway_match", "vendor_master",
]
# Hand-picked slice sizes from the large corpus-port families.
SLICE_FAMILIES = {"erpbench": 10, "erp_qa_fb": 5, "business_brief_fb": 3, "finance_qa_fb": 2}

DIFFICULTY_RANK = {"hard": 2, "medium": 1, "easy": 0}


def eligible(rec: dict) -> tuple[bool, str]:
    if rec["oracle_reward"] != 1:
        return False, f"oracle not green at HEAD: {rec['oracle_failed'][:2]}"
    if rec["multi_step"]:
        return False, "multi-step task; release packages a uniform single-step contract"
    if not rec["has_submit_answer"]:
        return False, "walk has no harness.submit_answer step"
    if not rec["has_writes_only"] and rec["family"] != "erpbench":
        # erpbench authoring checks carry no writes_only veto; the exporter adds one
        # (answers + the erpb_* surface) so the off-task-write control is sound there.
        return False, "checks carry no writes_only anti-hack veto"
    return True, ""


def slice_sort_key(rec: dict):
    return (
        -int(rec["has_state_sql"]),
        -DIFFICULTY_RANK.get(rec["difficulty"], 0),
        -rec["walk_len"],
        rec["task"],
    )


def rationale(rec: dict, picked_from: str) -> list[str]:
    tags = [picked_from]
    if not rec["has_writes_only"]:
        tags.append("export-adds-writes_only-veto(answers+erpb_*)")
    if rec["has_state_sql"]:
        tags.append("write-layer:state_checks.sql grades the world left behind")
    if rec["difficulty"] == "hard":
        tags.append("difficulty:hard")
    if rec["walk_len"] >= 10:
        tags.append(f"long-walk:{rec['walk_len']}-step oracle")
    if rec["doc_mode"] == "buried":
        tags.append("doc_mode:buried (governing policy must be found among decoys)")
    if rec["provenance"] == "variant":
        tags.append(f"escalated-variant-of:{rec['variant_of']}")
    if len(rec["walk_servers"]) >= 3:
        tags.append("cross-server:" + "+".join(rec["walk_servers"]))
    return tags


def main() -> int:
    scan_path = Path(sys.argv[1])
    scan = json.loads(scan_path.read_text())
    by_family: dict[str, list[dict]] = {}
    dropped: list[dict] = []
    for rec in scan:
        ok, why = eligible(rec)
        if ok:
            by_family.setdefault(rec["family"], []).append(rec)
        else:
            dropped.append({"task": rec["task"], "family": rec["family"], "reason": why})

    selected: list[tuple[dict, str]] = []
    for fam in FULL_FAMILIES:
        for rec in sorted(by_family.get(fam, []), key=lambda r: r["task"]):
            selected.append((rec, "full-family-coverage"))
    n_full = len(selected)
    for fam, quota in sorted(SLICE_FAMILIES.items()):
        pool = sorted(by_family.get(fam, []), key=slice_sort_key)
        for rec in pool[:quota]:
            selected.append((rec, f"hand-picked-slice({fam}:{quota}/{len(pool)})"))

    if len(selected) != TARGET:
        # Deterministic backfill from the largest slice pools if a full family lost
        # members to the gates.
        need = TARGET - len(selected)
        chosen = {r["task"] for r, _ in selected}
        backfill_pool = sorted(
            (r for fam in SLICE_FAMILIES for r in by_family.get(fam, [])
             if r["task"] not in chosen),
            key=slice_sort_key)
        for rec in backfill_pool[:need]:
            selected.append((rec, "backfill"))

    assert len(selected) == TARGET, f"selected {len(selected)} != {TARGET}"

    # Stable ids: alphabetical by family then slug, numbered 001..100.
    selected.sort(key=lambda pair: pair[0]["task"])
    entries = []
    for index, (rec, picked_from) in enumerate(selected, start=1):
        family, slug = rec["task"].split("/", 1)
        entries.append({
            "task_id": f"lgr100-{index:03d}-{slug}",
            "source_task": rec["task"],
            "family": family,
            "provenance": rec["provenance"],
            "difficulty": rec["difficulty"],
            "walk_len": rec["walk_len"],
            "walk_servers": rec["walk_servers"],
            "n_answer_checks": rec["n_answer_checks"],
            "n_state_checks": rec["n_state_checks"],
            "n_trace_checks": rec["n_trace_checks"],
            "has_state_sql": rec["has_state_sql"],
            "oracle_reward_at_head": rec["oracle_reward"],
            "rationale": rationale(rec, picked_from),
        })

    catalog = {
        "benchmark": "LedgerBench-100",
        "version": RELEASE_VERSION,
        "task_count": len(entries),
        "selection_pool": {
            "candidates_scanned": len(scan),
            "oracle_green": sum(1 for r in scan if r["oracle_reward"] == 1),
            "eligible": sum(len(v) for v in by_family.values()),
        },
        "families": {
            fam: sum(1 for e in entries if e["family"] == fam)
            for fam in sorted({e["family"] for e in entries})
        },
        "excluded": [d for d in dropped if d["family"] in FULL_FAMILIES],
        "tasks": entries,
    }
    out = HERE / "catalog.json"
    out.write_text(json.dumps(catalog, indent=1) + "\n")
    print(json.dumps({"selected": len(entries), "families": catalog["families"],
                      "excluded_from_full_families": catalog["excluded"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
