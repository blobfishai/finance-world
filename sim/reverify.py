#!/usr/bin/env python3
"""Re-grade stored trials against the CURRENT verifier, without re-running any model.

When the verifier changes, every trace recorded under the old one carries a stale verdict —
and run_batch's resume rule deliberately will not re-run a trial that already has a real
trace, so the stale verdicts would survive a rescan. The agent's run is unchanged and
grading is deterministic, so the honest fix is to re-verify the world the run left behind
(.runs/<model>/<family>/<slug>/trial-N) rather than spend trials reproducing it.

Used after docs/AUDIT.md A5 (the none_answer trap fix), which flipped three verdicts.

    python3 sim/reverify.py                    # dry run, report changes
    python3 sim/reverify.py --apply            # rewrite trace verdicts
    python3 sim/reverify.py --apply --model sonnet
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verifiers"))
from vcode import verify_all as verify


def main(apply=False, only_model=None):
    changed, checked, skipped = [], 0, 0
    for tp in sorted(ROOT.glob("traces/*/*/*/trial-*.json")):
        model = tp.parts[-4]
        if only_model and model != only_model: continue
        rec = json.loads(tp.read_text())
        if rec.get("infra_error"): continue
        family, slug = rec["family"], rec["task"].split("/", 1)[1]
        run = ROOT / ".runs" / model / family / slug / f"trial-{rec['trial']}"
        task = ROOT / "tasks" / family / slug
        if not (run / "world.sqlite").exists() or not (task / "task.toml").exists():
            skipped += 1; continue
        checked += 1
        v = verify(task, run)
        if v["reward"] == rec["reward"] and v["failed"] == rec["failed"]: continue
        changed.append((model, rec["task"], rec["trial"], rec["reward"], v["reward"],
                        rec["failed"], v["failed"]))
        if apply:
            rec["reward"], rec["failed"] = v["reward"], v["failed"]
            rec["regraded"] = "verifier changed; run data unchanged (docs/AUDIT.md A5)"
            new = tp.with_name(f"trial-{rec['trial']}." + ("pass" if v["reward"] else "fail") + ".json")
            tp.unlink(); new.write_text(json.dumps(rec, indent=1))

    print(f"re-verified {checked} stored trials ({skipped} skipped — no run dir on disk)")
    if not changed:
        print("no verdict changed"); return 0
    print(f"{'APPLIED' if apply else 'WOULD CHANGE'} — {len(changed)} verdict(s):")
    for m, t, tr, old, new, of, nf in changed:
        print(f"  [{m}] {t} trial-{tr}: {old} -> {new}")
        if old == 0 and new == 1: print(f"        was failing on: {of}")
        if old == 1 and new == 0: print(f"        now failing on: {nf}")
    if not apply: print("\nre-run with --apply to rewrite the traces")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    m = a[a.index("--model") + 1] if "--model" in a else None
    sys.exit(main(apply="--apply" in a, only_model=m))
