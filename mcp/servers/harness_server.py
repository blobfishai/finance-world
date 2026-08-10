#!/usr/bin/env python3
"""Harness MCP server — answer submission only. The answers table IS the graded state.
Verification/reset live in the runner, deliberately off the agent's surface."""
import sys, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server

S = Server("harness", "Submit your final answer fields here. Submitted state is what gets graded.")

@S.tool("submit_answer",
        "Submit final answer fields as an object, e.g. {\"outstanding_balance\": 12345.67, \"currency\": \"USD\"}. "
        "Submit every field the task asks for; resubmitting a field overwrites it. "
        "Use the literal string \"none\" where the task asks about something that does not exist.",
        {"answers": {"type": "object", "description": "field -> value map"}}, ["answers"])
def submit_answer(answers):
    if not isinstance(answers, dict) or not answers:
        raise ValueError("answers must be a non-empty object")
    cx = S.db()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    for field, value in answers.items():
        cx.execute("INSERT INTO answers(field, value, submitted_at) VALUES(?,?,?) "
                   "ON CONFLICT(field) DO UPDATE SET value=excluded.value, submitted_at=excluded.submitted_at",
                   (str(field), json.dumps(value, default=str), now))
    cx.commit()
    return {"recorded_fields": sorted(answers.keys())}

@S.tool("list_submitted", "See what you have submitted so far.")
def list_submitted():
    cx = S.db()
    return {"submitted": {r["field"]: json.loads(r["value"]) for r in cx.execute("SELECT * FROM answers")}}

if __name__ == "__main__":
    S.run()
