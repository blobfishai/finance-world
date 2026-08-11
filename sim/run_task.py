#!/usr/bin/env python3
"""Run one trial of one task with an agent (oracle | claude -p <model>), verify, store trace.

Traces land in traces/<label>/<family>/<slug>/trial-N.<pass|fail>.json — including failures,
which are first-class data for failure reports."""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim")); sys.path.insert(0, str(ROOT / "verifiers"))
from prepare import prepare
from vcode import verify_all as verify, steps_of

ALLOWED = "mcp__erp,mcp__books,mcp__sheets,mcp__email,mcp__filings,mcp__docs,mcp__harness"
DISALLOWED = "Bash,Edit,Write,Read,Glob,Grep,WebSearch,WebFetch,NotebookEdit,Task"
INFRA_MARKERS = ("session limit", "rate limit", "overloaded", "credit balance",
                 "login", "authentication", "api error")

def is_infra(agent_error, n_calls, final_text):
    """A run that died before any tool call for account/limit reasons is a harness
    failure, never a model verdict (audit-before-blame)."""
    return bool(agent_error) and n_calls == 0 and any(m in final_text.lower() for m in INFRA_MARKERS)

def run_trial(task_dir, agent="oracle", model=None, trial=1, _attempt=1):
    task_dir = Path(task_dir)
    family, slug = task_dir.parent.name, task_dir.name
    label = model if agent == "claude" else "oracle"
    run_dir = ROOT / ".runs" / label / family / slug / f"trial-{trial}"
    prepare(task_dir, run_dir)

    walk_len = len(json.loads((task_dir / "solution/walk.json").read_text()))
    for _sd in steps_of(task_dir):
        if (_sd / "walk.json").exists():
            walk_len += len(json.loads((_sd / "walk.json").read_text()))
    budget = max(24, walk_len * 3 + 6)   # reference-relative turn budget, never a capability cap
    t0, final_text, num_turns, cost = time.time(), "", None, None

    if agent == "oracle":
        p = subprocess.run([sys.executable, str(ROOT / "sim/oracle.py"), str(task_dir), str(run_dir)],
                           capture_output=True, text=True, timeout=300)
        final_text = (p.stdout + p.stderr)[-2000:]
        agent_error = p.returncode != 0
    else:
        instruction = (task_dir / "instruction.md").read_text()
        cmd = ["claude", "-p", instruction,
               "--mcp-config", str(run_dir / ".mcp.json"), "--strict-mcp-config",
               "--model", model, "--max-turns", str(budget), "--output-format", "json",
               "--allowedTools", ALLOWED, "--disallowedTools", DISALLOWED]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=900,
                               cwd=run_dir / "workdir")
            agent_error = False
            try:
                out = json.loads(p.stdout.strip().splitlines()[-1])
                final_text = str(out.get("result", ""))[:2000]
                num_turns, cost = out.get("num_turns"), out.get("total_cost_usd")
                agent_error = bool(out.get("is_error"))
            except Exception:
                final_text = (p.stdout + p.stderr)[-2000:]; agent_error = p.returncode != 0
        except subprocess.TimeoutExpired:
            final_text, agent_error = "AGENT_TIMEOUT(900s)", True
        # multi-turn: later steps resume the SAME session against the SAME world state
        sid = None
        try: sid = json.loads(p.stdout.strip().splitlines()[-1]).get("session_id")
        except Exception: pass
        for sd in steps_of(task_dir):
            si = sd / "instruction.md"
            if not si.exists() or not sid: break
            follow = ["claude", "-p", "--resume", sid, si.read_text(),
                      "--mcp-config", str(run_dir / ".mcp.json"), "--strict-mcp-config",
                      "--model", model, "--max-turns", str(budget), "--output-format", "json",
                      "--allowedTools", ALLOWED, "--disallowedTools", DISALLOWED]
            try:
                pf = subprocess.run(follow, capture_output=True, text=True, timeout=900,
                                    cwd=run_dir / "workdir")
                out = json.loads(pf.stdout.strip().splitlines()[-1])
                final_text += "\n\n[step " + sd.name + "] " + str(out.get("result", ""))[:800]
                sid = out.get("session_id", sid)
            except Exception as e:
                final_text += f"\n\n[step {sd.name}] follow-up failed: {e!r}"; break

    v = verify(task_dir, run_dir)
    trace = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines() if l.strip()]
    for r in trace:
        r["args"] = json.dumps(r.get("args", {}), default=str)[:300]

    if agent == "claude" and is_infra(agent_error, v["n_tool_calls"], final_text):
        if _attempt == 1:
            print(f"[{label}] {family}/{slug} trial-{trial}: INFRA ({final_text[:60]!r}) — one retry")
            time.sleep(20)
            return run_trial(task_dir, agent, model, trial, _attempt=2)
        # retry also infra: record it labeled, excluded from triage by run_batch
    rec = {"task": f"{family}/{slug}", "family": family, "agent": agent, "model": model,
           "infra_error": agent == "claude" and is_infra(agent_error, v["n_tool_calls"], final_text),
           "trial": trial, "reward": v["reward"], "failed": v["failed"],
           "servers_used": v["servers_used"], "n_tool_calls": v["n_tool_calls"],
           "walk_len": walk_len, "budget_turns": budget, "num_turns": num_turns,
           "agent_error": agent_error, "duration_s": round(time.time() - t0, 1),
           "cost_usd": cost, "final_text": final_text, "trace": trace}
    out_dir = ROOT / "traces" / label / family / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "infra" if rec["infra_error"] else ("pass" if v["reward"] else "fail")
    out = out_dir / f"trial-{trial}.{suffix}.json"
    for stale in out_dir.glob(f"trial-{trial}.*.json"): stale.unlink()
    out.write_text(json.dumps(rec, indent=1))
    print(f"[{label}] {family}/{slug} trial-{trial}: reward={v['reward']}{' (INFRA)' if rec['infra_error'] else ''} "
          f"calls={v['n_tool_calls']} {('FAILED: ' + ';'.join(v['failed'])) if v['failed'] and not rec['infra_error'] else ''}")
    return rec

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True); ap.add_argument("--agent", default="oracle")
    ap.add_argument("--model"); ap.add_argument("--trial", type=int, default=1)
    a = ap.parse_args()
    rec = run_trial(a.task, a.agent, a.model, a.trial)
    sys.exit(0 if rec["reward"] == 1 else 1)
