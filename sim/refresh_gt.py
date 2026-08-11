#!/usr/bin/env python3
"""Re-derive every gt_sql-backed ground truth from the built world, and (with --apply)
write it back into tests/checks.json and solution/walk.json.

sim/validate.py's S11 check *detects* ground-truth drift when the ledger is regenerated;
this is the other half — it repairs it, from the world, deterministically. The world is the
truth (docs/AUDIT.md A3: no ground truth is ever copied from benchmark prose), so a check
that disagrees with a reproducible build is stale by definition.

Only checks that carry `gt_sql` are touched: those are the ones whose truth is declared
re-derivable. Everything else is authored truth and is left alone.

    python3 sim/refresh_gt.py            # dry run — report drift
    python3 sim/refresh_gt.py --apply    # rewrite the stale expectations
"""
import json, shutil, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim")); sys.path.insert(0, str(ROOT / "verifiers"))
from prepare import prepare
from vcode import steps_of


def walk_update(task_dir, field, old, new):
    """Update the oracle's submitted answer so the gold walk still replays green."""
    hits = 0
    for wp in [task_dir / "solution/walk.json"] + [d / "walk.json" for d in steps_of(task_dir)]:
        if not wp.exists(): continue
        walk = json.loads(wp.read_text())
        for step in walk:
            args = step.get("args") or {}
            for key, val in list(args.items()):
                # submit_answer carries the fields directly; some tasks nest them one level.
                if key == field and isinstance(val, (int, float)):
                    args[key] = new; hits += 1
                elif isinstance(val, dict) and field in val and isinstance(val[field], (int, float)):
                    val[field] = new; hits += 1
        if hits:
            wp.write_text(json.dumps(walk, indent=1) + "\n")
    return hits


def main(apply=False):
    drift, unresolved = [], []
    for task in sorted(ROOT.glob("tasks/*/*")):
        if not (task / "task.toml").exists(): continue
        run = ROOT / ".runs/gtrefresh" / task.parent.name / task.name
        prepare(task, run)
        cx = sqlite3.connect(run / "world.sqlite")
        for d in [task] + list(steps_of(task)):
            cp = (d / "tests/checks.json") if (d / "tests/checks.json").exists() else (d / "checks.json")
            if not cp.exists(): continue
            checks = json.loads(cp.read_text())
            dirty = False
            for c in checks.get("answer_checks", []):
                if "gt_sql" not in c: continue
                row = cx.execute(c["gt_sql"]).fetchone()
                live = row[0] if row else None
                if live is None:
                    # The query returns nothing against the world as the agent FINDS it.
                    # For a write task that is expected — `total_paid` only exists once the
                    # run has been committed — so the pre-state cannot re-derive it, and
                    # coercing NULL to 0 rewrote a correct 34,450.00 to 0.00 (docs/AUDIT.md
                    # A13). Skip; the post-episode value is graded by a state_check instead.
                    unresolved.append((f"{task.parent.name}/{task.name}", c["field"]))
                    continue
                exp = float(c["expect"])
                tol = max(float(c.get("tol_abs", 0.01)), abs(exp) * float(c.get("tol_rel", 0)))
                if abs(float(live) - exp) <= tol: continue
                live = round(float(live), 2)
                drift.append((f"{task.parent.name}/{task.name}", c["field"], exp, live))
                if apply:
                    c["expect"] = live
                    walk_update(task, c["field"], exp, live)
                    dirty = True
            if dirty:
                cp.write_text(json.dumps(checks, indent=1) + "\n")
        cx.close()
        # prepare() copies the whole world per task (~3 MB). At 1,200+ tasks that is several
        # GB of transient disk, which is how this filled a 42 GB disk mid-run. The copy is
        # scratch the moment its gt_sql has been read.
        shutil.rmtree(run, ignore_errors=True)

    if unresolved:
        print(f"{len(unresolved)} gt_sql checks do not resolve against the pre-episode world "
              f"(write-task outputs; graded by state_checks) — left untouched:")
        for t_, f_ in unresolved[:8]: print(f"    {t_:46} {f_}")
    if not drift:
        print("no ground-truth drift — every gt_sql check matches the world")
        return 0
    print(f"{'APPLIED' if apply else 'DRIFT (dry run)'} — {len(drift)} stale ground truth(s):")
    for t, f, exp, live in drift:
        print(f"  {t:46} {f:24} {exp} -> {live}")
    if not apply:
        print("\nre-run with --apply to rewrite them, then run sim/validate.py")
    return 0 if apply else 1


if __name__ == "__main__":
    sys.exit(main(apply="--apply" in sys.argv))
