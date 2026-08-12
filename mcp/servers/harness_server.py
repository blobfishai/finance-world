#!/usr/bin/env python3
"""Harness MCP server — answer submission only. The answers table IS the graded state.
Verification/reset live in the runner, deliberately off the agent's surface."""
import sys, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("harness", "File your findings here. What you file is what gets graded. "
                      "Call reporting_fields first to see what this piece of work requires.")


def _schema():
    cx = S.db()
    try:
        rows = cx.execute("SELECT ordinal, field, type, description FROM answer_schema "
                          "ORDER BY ordinal, field").fetchall()
    except Exception:
        return []
    return [{"field": r["field"], "type": r["type"], "description": r["description"] or ""}
            for r in rows]


@S.tool("reporting_fields",
        "The fields this piece of work must be filed under, with their expected types. "
        "The request itself will not list them — read them here, the way you would read any "
        "reporting system's schema before filing into it.")
def reporting_fields():
    fields = _schema()
    if not fields:
        return {"fields": [], "note": "no schema registered; submit the figures the request asks for"}
    return {"fields": fields, "count": len(fields),
            "note": "file every field with submit_answer; use the literal string \"none\" "
                    "where the answer is that the thing does not exist"}


@S.tool("submit_answer",
        "File your findings as an object, e.g. {\"outstanding_balance\": 12345.67, "
        "\"currency\": \"USD\"}. Call reporting_fields to see which fields are required. "
        "Resubmitting a field overwrites it. Use the literal string \"none\" where the answer "
        "is that the thing does not exist.",
        {"answers": {"type": "object", "description": "field -> value map"}}, ["answers"])
def submit_answer(answers):
    if not isinstance(answers, dict) or not answers:
        raise ValueError("answers must be a non-empty object")
    # Tell the agent what it still owes, and what it filed that nothing asked for. This is
    # feedback on the CONTRACT, never on correctness — the value is not inspected here.
    want = {f["field"] for f in _schema()}
    unknown = sorted(set(answers) - want) if want else []
    cx = S.db()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for field, value in answers.items():
        cx.execute("INSERT INTO answers(field, value, submitted_at) VALUES(?,?,?) "
                   "ON CONFLICT(field) DO UPDATE SET value=excluded.value, submitted_at=excluded.submitted_at",
                   (str(field), json.dumps(value, default=str), now))
    cx.commit()
    filed = {r["field"] for r in cx.execute("SELECT field FROM answers")}
    out = {"recorded_fields": sorted(answers.keys())}
    if want:
        out["still_outstanding"] = sorted(want - filed)
        if unknown:
            out["not_requested"] = unknown
    return out

@S.tool("list_submitted", "See what you have submitted so far.")
def list_submitted():
    cx = S.db()
    return {"submitted": {r["field"]: json.loads(r["value"]) for r in cx.execute("SELECT * FROM answers")}}

if __name__ == "__main__":
    S.run()
