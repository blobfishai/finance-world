#!/usr/bin/env python3
"""Escalation engine — derive harder variants from an existing task.

PLAN.md Stage 5 has carried this as a TODO ("sim/grow-tasks (build it — spec-only in
lawfirm)"). It is the second half of triage-and-grow: the flake scan labels a task
`too_easy`, and this turns it into one the same model has to work for, **without
re-authoring its ground truth** — so a variant is comparable to its base by construction.

Levers, each sourced rather than invented:

  buried_docs   seed the adjacent-policy library alongside the task's own documents, so the
                governing rule must be found rather than being the only thing on the shelf
                (tau2 retrieval modes; measured 1 document -> 9 on the dormancy task)
  quiet_prompt  strip the instruction's explicit pointers — the SOP number, the system name,
                the as-of date — leaving the business need. The finance is unchanged; the
                task no longer tells the agent where to look
  no_hints      remove any parenthetical field hints from the deliverable list
  deep_walk     raise the reference walk so the turn budget follows the harder path rather
                than the base task's shortest one

A variant ships only if it still replays green through its own verifier (the same admission
rule as any task) and its ground truth is untouched — a variant that changes the answer is a
new task, not an escalation, and is rejected.

    python3 sim/grow_tasks.py --task tasks/erp_qa/due-next-week-adventure --levers buried_docs,quiet_prompt
    python3 sim/grow_tasks.py --from-triage traces/deepseek-v4-pro --levers buried_docs
    python3 sim/grow_tasks.py --from-triage traces/deepseek-v4-pro --dry-run
"""
import argparse, json, re, shutil, subprocess, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# pointers a `quiet_prompt` variant removes: the instruction stops naming the shelf
POINTERS = [
    (re.compile(r"\bper\s+(SOP|FIN|AR|AP|GL|POL)[-A-Z0-9]*\b", re.I), "per the current policy"),
    (re.compile(r"\bSOP[-A-Z0-9]+\b"), "the governing policy"),
    (re.compile(r"\bFIN-[A-Z]+-\d+[A-Z]?\b"), "the governing policy"),
    (re.compile(r"\bfollow\s+SOP[-A-Z0-9]*\s+to the letter\b", re.I), "follow the governing policy exactly"),
]


def triage(trace_dir: Path):
    """Classify tasks from a model's traces: solidPass / flaky / solidFail."""
    by = collections.defaultdict(list)
    for p in trace_dir.glob("*/*/trial-*.json"):
        r = json.loads(p.read_text())
        if r.get("infra_error") or r.get("budget_exhausted"): continue
        by[r["task"]].append(r["reward"])
    out = {}
    for t, v in by.items():
        if len(v) < 2: continue
        out[t] = "solidPass" if all(v) else ("solidFail" if not any(v) else "flaky")
    return out


def _quiet(text):
    for pat, repl in POINTERS:
        text = pat.sub(repl, text)
    # drop parenthetical type hints on the deliverable list
    text = re.sub(r"^(\s*-\s*`[^`]+`)\s*\([^)]*\)", r"\1", text, flags=re.M)
    return text


def grow(task_dir: Path, levers, dry_run=False):
    task_dir = Path(task_dir)
    name = task_dir.name
    if name.endswith(tuple(f"-{l}" for l in ("v2", "buried", "quiet", "deep"))):
        return None, "already a variant"
    suffix = "-".join(sorted(l[:5] for l in levers))
    dest = task_dir.parent / f"{name}-esc-{suffix}"
    if dest.exists(): shutil.rmtree(dest)
    if dry_run: return dest, "would create"

    shutil.copytree(task_dir, dest)
    for junk in ("solution/solve.sh", "tests/test.sh", "environment/Dockerfile"):
        (dest / junk).unlink(missing_ok=True)

    toml = (dest / "task.toml").read_text()
    toml = toml.replace(f'name = "{task_dir.parent.name}/{name}"',
                        f'name = "{task_dir.parent.name}/{dest.name}"')
    applied = []

    if "buried_docs" in levers and 'doc_mode' not in toml:
        toml = toml.replace('acceptance_label = "pending_calibration"',
                            'acceptance_label = "pending_calibration"\ndoc_mode = "buried"')
        applied.append("buried_docs: governing policy hidden in the adjacent-policy library")

    if "quiet_prompt" in levers or "no_hints" in levers:
        instr = (dest / "instruction.md").read_text()
        new_instr = _quiet(instr)
        if new_instr != instr:
            (dest / "instruction.md").write_text(new_instr)
            applied.append("quiet_prompt: explicit policy pointers removed from the ask")

    if "deep_walk" in levers:
        m = re.search(r"walk_len = (\d+)", toml)
        if m:
            toml = toml.replace(m.group(0), f"walk_len = {int(m.group(1)) + 3}")
            applied.append("deep_walk: reference walk raised, so the budget follows the harder path")

    if not applied:
        shutil.rmtree(dest); return None, "no lever applied"

    toml = re.sub(r'origin = "', 'origin = "escalated variant of '
                  f'{task_dir.parent.name}/{name} via sim/grow_tasks.py '
                  f'({"; ".join(applied)}); ground truth unchanged. Base: ', toml, count=1)
    # A variant re-asks its base's question through harder retrieval. It is depth on an
    # already-covered source item, never a newly covered one - so it is stamped and counted
    # in its own bucket. Without this, escalating a ported task reports parity above 100%
    # (docs/AUDIT.md A15).
    toml = re.sub(r'^variant = .*\n', '', toml, flags=re.M)
    toml = re.sub(r'^(difficulty = )', f'variant_of = "{task_dir.parent.name}/{name}"\n\\1',
                  toml, count=1, flags=re.M)
    (dest / "task.toml").write_text(toml)
    return dest, "; ".join(applied)


def verify(dest: Path):
    subprocess.run([sys.executable, str(ROOT / "sim/scaffold.py")], capture_output=True)
    p = subprocess.run([sys.executable, str(ROOT / "sim/run_task.py"),
                        "--task", str(dest), "--agent", "oracle"],
                       capture_output=True, text=True)
    return "reward=1" in (p.stdout + p.stderr), (p.stdout + p.stderr).strip().splitlines()[-1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task"); ap.add_argument("--from-triage")
    ap.add_argument("--levers", default="buried_docs,quiet_prompt")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    levers = [x.strip() for x in a.levers.split(",") if x.strip()]

    targets = []
    if a.task:
        targets = [Path(a.task)]
    elif a.from_triage:
        cls = triage(Path(a.from_triage))
        easy = [t for t, c in cls.items() if c == "solidPass"]
        print(f"triage over {a.from_triage}: "
              + " · ".join(f"{k} {v}" for k, v in collections.Counter(cls.values()).most_common()))
        print(f"escalating the {len(easy)} solidPass tasks\n")
        targets = [ROOT / "tasks" / t for t in sorted(easy)]
    if a.limit: targets = targets[:a.limit]

    made, failed = [], []
    for t in targets:
        if not (t / "task.toml").exists(): continue
        dest, note = grow(t, levers, a.dry_run)
        if dest is None:
            print(f"  skip {t.name}: {note}"); continue
        if a.dry_run:
            print(f"  would grow {t.parent.name}/{t.name} -> {dest.name}"); continue
        ok, last = verify(dest)
        if ok:
            made.append(dest); print(f"  OK   {dest.parent.name}/{dest.name}  [{note}]")
        else:
            shutil.rmtree(dest); failed.append((t.name, last))
            print(f"  DROP {t.name}: variant did not replay green -> {last}")
    print(f"\ngrew {len(made)} variants; {len(failed)} rejected by the oracle gate")


if __name__ == "__main__":
    sys.exit(main())
