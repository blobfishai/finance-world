#!/usr/bin/env python3
"""Deterministic verifier engine. No LLM in the reward path.

Reads tests/checks.json from a task dir and a run dir (world.sqlite, trace.jsonl,
initial_state.json). Emits {"reward": 0|1, "failed": [...]} on stdout; always exits 0.

checks.json:
  answer_checks: [{field, type: number|string|contains_all, expect, tol_abs?, tol_rel?}]
      number: value parsed from "$1,234.56", "1234.56", 1234.56; pass if within
              max(tol_abs, |expect|*tol_rel); default exact to 0.01.
      string: case/space-insensitive equality.
      contains_all: every listed substring appears (case-insensitive) in the value; an
              optional `forbid` list must NOT appear, so a set answer is graded for
              over-inclusion as well as omission.
      scale: the unit a figure is stated in (units/thousands/millions/billions/percent),
              graded as its own field the way TAT-QA does. Any numeric check additionally
              reports `scale_error` when the answer is a clean 1e3/1e6/1e9 multiple of the
              truth, so a unit slip is never filed as ordinary arithmetic error.
      yes_no: polarity of a yes/no field, with any trailing justification allowed
              ("no - no record in the ERP" passes for expect "no"). Same lesson as
              none_answer: grade the finding, not the prose.
      none_answer: the empty-answer trap (replaces the old expect:"none" string check —
              see docs/AUDIT.md A5). Passes when the value OPENS with a negative
              ("none", "no ...", "n/a", "nil", "not found", "zero"), with any trailing
              justification allowed, and fails if any `forbid` substring appears — so the
              trap asserts "did not invent a record" instead of "wrote exactly one word".
  trace_checks: [{type: required_servers, servers: [...]},
                 {type: min_calls, server, n},
                 {type: reads_before_submit}]
  state_checks: [{type: writes_only, tables: ["answers"]},   # anti-hack veto
                 {type: row_count, sql, expect, name?},
                 {type: sql, sql, expect, tol_abs?, tol_rel?, name?}]
      sql: grade the world the agent left behind (write tasks) — the committed run, the
           paid/rejected partition, the reason codes. Numbers compare with tolerance.
"""
import json, re, sqlite3, hashlib, sys
from pathlib import Path

def table_hashes(db):
    cx = sqlite3.connect(db)
    out = {}
    for (t,) in cx.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        rows = cx.execute(f"SELECT * FROM {t}").fetchall()
        h = hashlib.sha256(repr(sorted(map(repr, rows))).encode()).hexdigest()[:16]
        out[t] = [len(rows), h]
    cx.close()
    return out

def parse_number(v):
    if isinstance(v, (int, float)): return float(v)
    s = re.sub(r"[,$\s]|USD", "", str(v), flags=re.I).rstrip("%")
    m = re.match(r"^-?\d+(\.\d+)?$", s)
    return float(s) if m else None

def norm(v): return re.sub(r"\s+", " ", str(v)).strip().lower()


def contains_subset(actual, expected):
    """Recursive exact-subset match for trace argument selectors."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and contains_subset(actual[key], value)
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            contains_subset(got, wanted) for got, wanted in zip(actual, expected)
        )
    return actual == expected


def trace_match(record, selector, *, successful=True):
    if record.get("server") != selector.get("server"):
        return False
    if record.get("tool") != selector.get("tool"):
        return False
    if successful and not record.get("ok"):
        return False
    return contains_subset(record.get("args") or {}, selector.get("args") or {})


def first_trace_index(trace, selector, *, start=0, successful=True):
    return next(
        (index for index in range(start, len(trace))
         if trace_match(trace[index], selector, successful=successful)),
        None,
    )


def first_evidence_index(trace, selector, *, start=0):
    """Find successful evidence or one exact, contracted provider-negative result."""

    expected_error = selector.get("expected_error_contains")
    if not expected_error:
        return first_trace_index(trace, selector, start=start, successful=True)
    expected_error = norm(expected_error)
    return next(
        (
            index
            for index in range(start, len(trace))
            if not trace[index].get("ok")
            and trace_match(trace[index], selector, successful=False)
            and expected_error in norm(trace[index].get("note") or "")
        ),
        None,
    )


def check_label(check):
    return str(check.get("name") or check.get("field") or check.get("type") or "check")


def check_slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).casefold()).strip("-") or "check"


def check_result(source, index, check, failures):
    label = check_label(check)
    return {
        "id": f"{source}.{index:03d}.{check_slug(label)}",
        "source": source,
        "type": str(check.get("type") or "string"),
        "name": label,
        "passed": not failures,
        "failures": failures,
    }

# An empty-answer trap is satisfied by a value that OPENS with a negative. Trailing
# justification is allowed and expected — a model that explains "none, because no remittance
# advice was on file" is more useful than one that emits the bare token, and grading them
# differently measured prose, not grounding (docs/AUDIT.md A5).
NEG_RE = re.compile(r"^(none|no|n/?a|nil|nothing|zero|not\s+(found|applicable|available|on\s+file))\b")

# Same lesson as NEG_RE, for yes/no fields: a finance answer worth reading is "no - Meadow
# Analytics has no record in the ERP", not the bare token. Grade the polarity, not the prose.
YES_RE = re.compile(r"^(yes|y|true|correct|confirmed|affirmative)\b")
NO_RE  = re.compile(r"^(no|n|false|incorrect|negative|none|not)\b")

# TAT-QA grades `scale` (thousand/million/billion/percent) as a field in its own right,
# because a financial number without its unit is not an answer (round-2 ledger row 28). We
# do the same, and additionally diagnose the classic magnitude slip on ANY numeric check
# rather than letting it hide inside a generic "off by a lot".
SCALE_SYNONYMS = {
    "units": {"units", "unit", "absolute", "ones", "dollars", "usd", "as reported", "none"},
    "thousands": {"thousand", "thousands", "k", "000s", "in thousands"},
    "millions": {"million", "millions", "m", "mm", "in millions"},
    "billions": {"billion", "billions", "b", "bn", "in billions"},
    "percent": {"percent", "percentage", "%", "pct"},
}
SCALE_FACTOR = {"units": 1, "thousands": 1e3, "millions": 1e6, "billions": 1e9}

def scale_of(v):
    s = norm(v).replace("(", " ").replace(")", " ").strip(" .")
    for canon, words in SCALE_SYNONYMS.items():
        if s == canon or s in words: return canon
    # specific scales win over the generic "units" bucket: "USD millions" is millions, not
    # units, even though "usd" is a units synonym.
    for canon in ("billions", "millions", "thousands", "percent", "units"):
        words = SCALE_SYNONYMS[canon]
        if any(re.search(rf"\b{re.escape(w)}\b", s) for w in words if len(w) > 2): return canon
    return None

def magnitude_slip(got, exp):
    """Return the factor if the answer is a clean 1e3/1e6/1e9 multiple of the truth."""
    if not got or not exp: return None
    for f in (1e3, 1e6, 1e9):
        for cand, label in ((exp * f, f), (exp / f, 1 / f)):
            if cand and abs(got - cand) <= max(0.01, abs(cand) * 1e-4):
                return label
    return None

def polarity(v):
    s = norm(v)
    if YES_RE.match(s): return "yes"
    if NO_RE.match(s):  return "no"
    return None

def evaluate_answer_check(c, answers):
    failed = []
    fld, typ = c["field"], c.get("type", "string")
    name = f"answer:{fld}"
    if fld not in answers:
        return [name + ":missing"]
    got = answers[fld]
    if typ == "number":
        g = parse_number(got)
        if g is None:
            return [name + ":not_numeric"]
        exp = float(c["expect"])
        tol = max(float(c.get("tol_abs", 0.01)), abs(exp) * float(c.get("tol_rel", 0)))
        if abs(g - exp) > tol:
            slip = magnitude_slip(g, exp)
            if slip:
                scale = {1e3: "thousands", 1e6: "millions", 1e9: "billions"}.get(slip)
                failed.append(name + f":scale_error(got={g}, want={exp}, off by "
                              f"{'x' if slip > 1 else '/'}{int(slip if slip > 1 else 1/slip)}"
                              + (f" - looks reported in {scale}" if scale else "") + ")")
            else:
                failed.append(name + f":off(got={g})")
    elif typ == "none_answer":
        g = norm(got)
        if not NEG_RE.match(g):
            failed.append(name + f":expected_none(got={g[:60]})")
        else:
            bad = [s for s in c.get("forbid", []) if norm(s) in g]
            if bad:
                failed.append(name + f":hallucinated({bad})")
    elif typ == "scale":
        g = scale_of(got)
        exp_s = scale_of(c["expect"]) or norm(c["expect"])
        if g is None:
            failed.append(name + f":unparseable_scale(got={norm(got)[:40]})")
        elif g != exp_s:
            failed.append(name + f":wrong_scale(got={g}, want={exp_s})")
    elif typ == "yes_no":
        got_p, exp_p = polarity(got), norm(c["expect"])
        if got_p is None:
            failed.append(name + f":unparseable_yes_no(got={norm(got)[:60]})")
        elif got_p != exp_p:
            failed.append(name + f":wrong_polarity(got={got_p}, want={exp_p})")
        else:
            bad = [s for s in c.get("forbid", []) if norm(s) in norm(got)]
            if bad:
                failed.append(name + f":hallucinated({bad})")
    elif typ == "contains_all":
        g = norm(got)
        missing = [s for s in c["expect"] if norm(s) not in g]
        if missing:
            failed.append(name + f":missing_terms({missing})")
        over = [s for s in c.get("forbid", []) if norm(s) in g]
        if over:
            failed.append(name + f":forbidden_terms({over})")
    elif norm(got) != norm(c["expect"]):
        failed.append(name + f":mismatch(got={norm(got)[:60]})")
    return failed


def evaluate_trace_check(c, trace):
    failed = []
    t = c["type"]
    if t == "required_servers":
        used = {r["server"] for r in trace if r.get("ok")}
        miss = [s for s in c["servers"] if s not in used]
        if miss:
            failed.append(f"trace:required_servers_missing({miss})")
    elif t == "min_calls":
        n = sum(1 for r in trace if r["server"] == c["server"] and r.get("ok"))
        if n < c["n"]:
            failed.append(f"trace:min_calls({c['server']}<{c['n']})")
    elif t == "reads_before_submit":
        first_submit = next((i for i, r in enumerate(trace)
                             if r["server"] == "harness" and r["tool"] == "submit_answer"), None)
        reads_before = any(r["server"] != "harness" and r.get("ok") for r in trace[:first_submit or 0])
        if first_submit is None or not reads_before:
            failed.append("trace:no_reads_before_submit")
    elif t == "required_calls":
        missing = [
            f"{selector.get('server')}.{selector.get('tool')}:{selector.get('args', {})}"
            for selector in c.get("calls", [])
            if first_evidence_index(trace, selector) is None
        ]
        if missing:
            failed.append(f"trace:required_calls_missing({missing})")
    elif t == "reads_before_write":
        write_at = first_trace_index(trace, c["write"])
        if write_at is None:
            failed.append("trace:required_write_missing")
        else:
            late = [
                f"{selector.get('server')}.{selector.get('tool')}:{selector.get('args', {})}"
                for selector in c.get("reads", [])
                if first_evidence_index(trace[:write_at], selector) is None
            ]
            if late:
                failed.append(f"trace:reads_not_before_write({late})")
    elif t == "post_write_readback":
        write_at = first_trace_index(trace, c["write"])
        readback_at = (
            first_trace_index(trace, c["readback"], start=write_at + 1)
            if write_at is not None else None
        )
        if write_at is None or readback_at is None:
            failed.append(
                f"trace:missing_post_write_readback({c['write'].get('server')}."
                f"{c['write'].get('tool')}->{c['readback'].get('server')}."
                f"{c['readback'].get('tool')})"
            )
    elif t == "ordered_calls":
        cursor = 0
        missing = None
        for selector in c.get("calls", []):
            position = first_trace_index(trace, selector, start=cursor)
            if position is None:
                missing = selector
                break
            cursor = position + 1
        if missing is not None:
            failed.append(
                f"trace:ordered_calls_failed({missing.get('server')}."
                f"{missing.get('tool')}:{missing.get('args', {})})"
            )
    elif t == "successful_required_calls":
        unsuccessful = []
        for selector in c.get("calls", []):
            any_call = first_trace_index(trace, selector, successful=False)
            accepted_evidence = first_evidence_index(trace, selector)
            if any_call is None or accepted_evidence is None:
                unsuccessful.append(
                    f"{selector.get('server')}.{selector.get('tool')}:"
                    f"{selector.get('args', {})}"
                )
        if unsuccessful:
            failed.append(f"trace:required_calls_unsuccessful({unsuccessful})")
    elif t == "no_rejected_mutations":
        rejected = []
        for selector in c.get("calls", []):
            if any(
                not record.get("ok")
                and trace_match(record, selector, successful=False)
                for record in trace
            ):
                rejected.append(
                    f"{selector.get('server')}.{selector.get('tool')}:"
                    f"{selector.get('args', {})}"
                )
        if rejected:
            failed.append(f"trace:rejected_mutations({rejected})")
    else:
        failed.append(f"trace:unsupported_check_type({t})")
    return failed


def evaluate_state_check(c, cx, final, init):
    failed = []
    t = c["type"]
    if t == "writes_only":
        allowed = set(c.get("tables", ["answers"])) | {"erp_form_sessions"}
        dirty = [x for x in final if x not in allowed and final[x] != init.get(x)]
        if dirty:
            failed.append(f"state:off_task_writes({dirty})")
    elif t == "row_count":
        n = cx.execute(c["sql"]).fetchone()[0]
        if n != c["expect"]:
            failed.append(f"state:row_count({c.get('name', c['sql'][:40])}: got {n}, want {c['expect']})")
    elif t == "sql":
        got = cx.execute(c["sql"]).fetchone()
        got = got[0] if got else None
        exp, name_ = c["expect"], c.get("name", c["sql"][:40])
        if isinstance(exp, (int, float)) and not isinstance(exp, bool):
            g = parse_number(got)
            tol = max(float(c.get("tol_abs", 0.01)), abs(float(exp)) * float(c.get("tol_rel", 0)))
            if g is None or abs(g - float(exp)) > tol:
                failed.append(f"state:sql({name_}: got {got}, want {exp})")
        elif norm(got) != norm(exp):
            failed.append(f"state:sql({name_}: got {norm(got)[:60]}, want {norm(exp)[:60]})")
    elif t == "cell_equals":
        row = cx.execute(c["sql"]).fetchone()
        got = row[0] if row else None
        exp = c["expect"]
        ok = (abs(float(got) - float(exp)) <= float(c.get("tol_abs", 0))
              if isinstance(exp, (int, float)) and got is not None
              else norm(got) == norm(exp))
        if not ok:
            failed.append(f"state:cell_equals({c.get('name', c['sql'][:40])}: got {got!r}, want {exp!r})")
    else:
        failed.append(f"state:unsupported_check_type({t})")
    return failed


def verify(task_dir, run_dir):
    """Verify one step and emit stable, inspectable atomic-check results."""
    p = Path(task_dir) / "tests/checks.json"
    checks = json.loads((p if p.exists() else Path(task_dir) / "checks.json").read_text())
    db = Path(run_dir) / "world.sqlite"
    failed = []
    results = []

    cx = sqlite3.connect(db)
    answers = {f: json.loads(v) for f, v in cx.execute("SELECT field, value FROM answers")}
    cx.close()
    for index, c in enumerate(checks.get("answer_checks", []), 1):
        failures = evaluate_answer_check(c, answers)
        failed.extend(failures)
        results.append(check_result("answer", index, c, failures))

    trace = []
    tf = Path(run_dir) / "trace.jsonl"
    if tf.exists():
        trace = [json.loads(line) for line in tf.read_text().splitlines() if line.strip()]
    for index, c in enumerate(checks.get("trace_checks", []), 1):
        failures = evaluate_trace_check(c, trace)
        failed.extend(failures)
        results.append(check_result("trace", index, c, failures))

    init = json.loads((Path(run_dir) / "initial_state.json").read_text())
    final = table_hashes(db)
    cx = sqlite3.connect(db)
    try:
        for index, c in enumerate(checks.get("state_checks", []), 1):
            failures = evaluate_state_check(c, cx, final, init)
            failed.extend(failures)
            results.append(check_result("state", index, c, failures))
    finally:
        cx.close()

    return {"reward": 1 if not failed else 0, "failed": failed,
            "checks": results,
            "n_tool_calls": len(trace),
            "servers_used": sorted({r['server'] for r in trace})}

def steps_of(task_dir):
    """Multi-step tasks (Harbor [[steps]] shape): steps/NN/{instruction.md,checks.json,walk.json}.
    Step 0 is the task root; later steps run in the SAME world, so state carries across turns."""
    d = Path(task_dir) / "steps"
    return sorted(p for p in d.glob("*") if (p / "checks.json").exists()) if d.is_dir() else []

def verify_all(task_dir, run_dir):
    """Verify the root step plus every later step; reward 1 only if all pass."""
    res = verify(task_dir, run_dir)
    out = {"reward": res["reward"], "failed": list(res["failed"]),
           "checks": list(res["checks"]),
           "n_tool_calls": res["n_tool_calls"], "servers_used": res["servers_used"], "steps": 1}
    for s in steps_of(task_dir):
        r = verify(s, run_dir)
        out["steps"] += 1
        out["failed"] += [f"{s.name}:{f}" for f in r["failed"]]
        out["checks"] += [
            {**check, "id": f"{s.name}.{check['id']}", "step": s.name}
            for check in r["checks"]
        ]
        out["reward"] = min(out["reward"], r["reward"])
    return out

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True); ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    print(json.dumps(verify_all(a.task_dir, a.run_dir)))
