#!/usr/bin/env python3
"""Generate reports/failure-report-<model>.md from stored traces + summary.json.
Failure-mode taxonomy is heuristic but grounded in the trace, never in vibes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"solidPass": "too_easy (escalate: deeper walk / ambiguity / distractors)",
          "flaky": "in_band — THE FRONTIER, keep & study",
          "solidFail": "too_hard candidate (audit-before-blame first)"}

def modes(rec):
    out = []
    if rec.get("agent_error"): out.append("agent_error/timeout")
    f = rec.get("failed", [])
    if any("no_reads_before_submit" in x for x in f): out.append("submitted_blind")
    if any(x.startswith("answer:") and "missing" in x for x in f): out.append("missing_field_or_no_submit")
    if any(":off(" in x or ":mismatch" in x for x in f): out.append("wrong_value")
    if any("required_servers_missing" in x for x in f): out.append("missed_system(fragmentation)")
    if any("off_task_writes" in x for x in f): out.append("state_tampering")
    errs = sum(1 for t in rec.get("trace", []) if not t.get("ok"))
    if errs >= 3: out.append(f"tool_errors_x{errs}")
    if rec.get("num_turns") and rec["num_turns"] >= rec.get("budget_turns", 10**9):
        out.append("budget_exhausted")
    return out or (["verified_fail_other"] if rec.get("reward") == 0 else [])

def main():
    summary = json.loads((ROOT / "reports/summary.json").read_text())
    for model, tasks in summary.items():
        lines = [f"# Failure report — {model}", "",
                 f"Trials per task: {len(next(iter(tasks.values()))['rewards'])}. "
                 "Classes per house triage rule (flaky = the product).", "",
                 "| task | rewards | class | calibration suggestion |", "|---|---|---|---|"]
        for t, s in sorted(tasks.items()):
            lines.append(f"| {t} | {s['rewards']} | {s['class']} | {LABELS[s['class']]} |")
        lines += ["", "## Per-task failure analysis", ""]
        for t, s in sorted(tasks.items()):
            if s["class"] == "solidPass": continue
            fam, slug = t.split("/")
            recs = []
            for p in sorted((ROOT / "traces" / model / fam / slug).glob("trial-*.json")):
                recs.append(json.loads(p.read_text()))
            lines.append(f"### {t} — {s['class']}")
            for r in recs:
                tag = "PASS" if r["reward"] else "FAIL"
                lines.append(f"- trial-{r['trial']} **{tag}** ({r['n_tool_calls']} calls, "
                             f"{r['duration_s']}s, turns={r.get('num_turns')}): "
                             f"modes: {', '.join(modes(r)) or '—'}")
                if not r["reward"]:
                    lines.append(f"  - failed checks: `{'; '.join(r['failed'])[:300]}`")
                    seq = " → ".join(f"{c['server']}.{c['tool']}" for c in r["trace"][:12])
                    lines.append(f"  - call path: {seq}{' …' if len(r['trace']) > 12 else ''}")
                    if r.get("final_text"):
                        lines.append(f"  - final message excerpt: > {r['final_text'][:220].replace(chr(10), ' ')}")
            flaky_note = ("**Why flaky matters:** this task sits at the model's capability boundary; "
                          "diff the passing vs failing call paths above to name the failure mode.")
            if s["class"] == "flaky": lines.append(flaky_note)
            lines.append("")
        out = ROOT / f"reports/failure-report-{model.replace('/', '_')}.md"
        out.write_text("\n".join(lines))
        print("wrote", out)

if __name__ == "__main__":
    main()
