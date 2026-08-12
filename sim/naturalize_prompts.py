#!/usr/bin/env python3
"""Move the answer contract off the prompt and onto the reporting tool.

Every instruction.md ended with a block no colleague would ever type:

    ---

    Reply with `submit_answer`:

    - `dormant_count` (number) — vendors meeting the SOP's dormancy definition
    - `cutoff_date` (text) — the date the 12-month test measures against

That is not just unrealistic, it hands over the decomposition. Being told to file
`overpayment_usd` AND `underpayment_usd` separately reveals that there are two directions of
error before the model has looked at anything; `duplicate_invoice` + `duplicate_of` reveals
that a duplicate exists. The task stops being "work out what is wrong" and becomes "fill in
these blanks".

This lifts the block into `answer_schema`, seeded per task, which the harness server exposes
through `reporting_fields`. The prompt is left as a message; the contract lives on the tool,
which is where it lives in a real deployment.

`sim/validate.py` S4 ("every answer_check field is mentioned in instruction.md") moves with it
— the invariant is "the agent is told somewhere it can see", and the tool is somewhere it can
see. The guard is not dropped, it is repointed.

    python3 sim/naturalize_prompts.py            # dry run
    python3 sim/naturalize_prompts.py --apply
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Two lead-in phrasings exist: "Reply with `submit_answer`:" and, on the follow-up turns of
# multi-step tasks, "Submit via harness `submit_answer`:". Matching only the first left two
# step files unconverted with their field lists intact.
LEAD = re.compile(r"^.*(reply with|submit via)[^:]*`submit_answer`.*:\s*$", re.I)
BULLET = re.compile(r"^\s*-\s+(.+?)\s*$")
# `field` or `a` · `b` · `c`, then an optional (type), then an optional — description
FIELDS = re.compile(r"`([a-zA-Z0-9_]+)`")
TYPE = re.compile(r"\(([^)]*)\)")


def parse(md):
    """-> (prompt_without_block, [ {field,type,description} ]) or (md, []) if no block."""
    lines = md.splitlines()
    start = next((i for i, ln in enumerate(lines) if LEAD.match(ln)), None)
    if start is None:
        return md, []
    # The lead-in is not always alone on its line: "...rounded to two decimals. Submit via
    # harness `submit_answer`:" carries real instruction before it. Dropping the whole line
    # truncated that prompt mid-sentence, so keep whatever precedes the lead-in phrase.
    lead_m = LEAD.match(lines[start])
    prefix = lines[start][:lead_m.start(1)].rstrip()

    fields, i, ordinal = [], start + 1, 0
    end = start
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        m = BULLET.match(ln)
        if not m:
            break
        body = m.group(1)
        names = FIELDS.findall(body)
        if not names:
            break
        # a bullet may continue onto the next line (wrapped description)
        desc_src = body
        j = i + 1
        while j < len(lines) and lines[j].strip() and not BULLET.match(lines[j]) \
                and not lines[j].startswith("_") and not lines[j].startswith("#"):
            desc_src += " " + lines[j].strip(); j += 1

        # The parenthesis may hold the type alone — "(number)" — or the type AND its
        # description — "(number, USD — CESQ open AP as of 2026-02-28)". Take the type as the
        # part before the first comma or dash, and fold the remainder into the description,
        # otherwise the whole sentence is stored as the field's "type".
        t = TYPE.search(desc_src)
        raw = (t.group(1).strip() if t else "text") or "text"
        head = re.split(r"[,—–-]", raw, 1)
        typ = head[0].strip().lower() or "text"
        inner = head[1].strip() if len(head) > 1 else ""
        if "yes" in raw.lower() and "no" in raw.lower():
            typ = "yes/no"
        if typ not in ("number", "text", "yes/no"):
            typ = "number" if "number" in raw.lower() else "text"
        desc = ""
        after = desc_src[t.end():] if t else desc_src
        for sep in ("—", "--"):
            if sep in after:
                desc = after.split(sep, 1)[1].strip(); break
        desc = (inner + (" — " if inner and desc else "") + desc).strip(" —-")
        for n in names:
            ordinal += 1
            fields.append({"ordinal": ordinal, "field": n, "type": typ, "description": desc})
        end = j - 1
        i = j

    if not fields:
        return md, []

    # drop the block, plus a `---` rule that exists only to introduce it, plus the blank
    # padding around them — but keep anything after (e.g. the multi-step follow-up marker)
    head = lines[:start]
    while head and not head[-1].strip():
        head.pop()
    if head and head[-1].strip() == "---":
        head.pop()
        while head and not head[-1].strip():
            head.pop()
    if prefix:
        head.append(prefix)
    tail = lines[end + 1:]
    while tail and not tail[0].strip():
        tail.pop(0)
    out = "\n".join(head + ([""] + tail if tail else [])).rstrip() + "\n"
    return out, fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    done = skipped = 0
    per_type = {}
    for instr in sorted(ROOT.glob("tasks/*/*/**/instruction.md")):
        md = instr.read_text()
        new, fields = parse(md)
        if not fields:
            skipped += 1; continue
        for f in fields:
            per_type[f["type"]] = per_type.get(f["type"], 0) + 1

        # the schema belongs to the task dir that owns the environment/, which for a
        # multi-step task is the parent, not the step
        task = instr.parent
        while not (task / "task.toml").exists() and task != ROOT:
            task = task.parent
        seed = task / "environment/seed/mcp_seed.json"

        if a.apply:
            instr.write_text(new)
            data = json.loads(seed.read_text()) if seed.exists() else {}
            existing = {r["field"] for r in data.get("answer_schema", [])}
            rows = data.get("answer_schema", [])
            base = len(rows)
            for f in fields:
                if f["field"] in existing: continue
                rows.append({"ordinal": base + f["ordinal"], "field": f["field"],
                             "type": f["type"], "description": f["description"]})
            data["answer_schema"] = rows
            seed.parent.mkdir(parents=True, exist_ok=True)
            seed.write_text(json.dumps(data, indent=1) + "\n")
        done += 1

    print(f"{'converted' if a.apply else 'would convert'} {done} instruction files "
          f"({skipped} had no block)")
    print("field types seen:", ", ".join(f"{k}={v}" for k, v in sorted(per_type.items())))
    if not a.apply:
        print("\ndry run — pass --apply to write")


if __name__ == "__main__":
    sys.exit(main())
