#!/usr/bin/env python3
"""Flake-scan batch: models x tasks x trials. Triage per house rule:
pass all -> too_easy (escalate) | mixed -> flaky = the frontier | fail all -> too_hard (audit first)."""
import argparse, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim"))
from run_task import run_trial

def classify(rewards):
    if not rewards: return "infra_only"
    if all(r == 1 for r in rewards): return "solidPass"
    if all(r == 0 for r in rewards): return "solidFail"
    return "flaky"

def existing_real(model, task_path, trial):
    """Resume rule: a trial reruns only if it has no trace, or one the harness disowns
    (infra-tainted, or cut off by the turn budget before it could answer)."""
    d = ROOT / "traces" / model / task_path.parent.name / task_path.name
    hits = list(d.glob(f"trial-{trial}.*.json"))
    return bool(hits) and not hits[0].name.endswith((".infra.json", ".starved.json"))

def rebuild_summary(models):
    summary = {}
    for m in models:
        for p in sorted((ROOT / "traces" / m).glob("*/*/trial-*.json")):
            r = json.loads(p.read_text())
            s = summary.setdefault(m, {}).setdefault(r["task"], {"rewards": [], "failed": [],
                                                                   "infra_trials": 0, "starved_trials": 0})
            if r.get("infra_error"): s["infra_trials"] += 1
            elif r.get("budget_exhausted"): s["starved_trials"] = s.get("starved_trials", 0) + 1
            else:
                s["rewards"].append(r["reward"]); s["failed"].append(r["failed"])
    for m in summary:
        for t in summary[m]:
            summary[m][t]["class"] = classify(summary[m][t]["rewards"])
    return summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True, help="comma-separated claude model names")
    ap.add_argument("--trials", type=int, default=2)
    ap.add_argument("--tasks", default="tasks/*/*")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--fresh", action="store_true", help="rerun everything, ignore existing traces")
    a = ap.parse_args()
    models = a.models.split(",")
    tasks = sorted(p for p in ROOT.glob(a.tasks) if (p / "task.toml").exists())
    jobs = [(t, m, n) for m in models for t in tasks for n in range(1, a.trials + 1)
            if a.fresh or not existing_real(m, t, n)]
    print(f"{len(tasks)} tasks x {len(models)} models x {a.trials} trials -> {len(jobs)} runs (resume skips real traces)")

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_trial, t, "claude", m, n) for t, m, n in jobs]
        for f in futs:
            try: f.result()
            except Exception as e: print("RUN ERROR:", e)

    summary = rebuild_summary(models)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/summary.json").write_text(json.dumps(summary, indent=1))
    for m, tasks_ in summary.items():
        counts = {}
        for t, s in tasks_.items(): counts[s["class"]] = counts.get(s["class"], 0) + 1
        print(m, counts)

if __name__ == "__main__":
    main()
