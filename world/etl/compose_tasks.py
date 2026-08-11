#!/usr/bin/env python3
"""Composite tasks — depth, not breadth.

The entity sweep multiplies instances of single-lookup patterns, so its tasks inherit a 2-4
hop walk. This composes them: a **selector** narrows a population, a **detail** query runs per
selected entity, and an **aggregate** turns the set into one defensible answer. That is the
shape of the questions analysts actually get ("of the customers on hold, which owes us most
past-due?"), and it produces a walk that grows with the population rather than a fixed stub.

Every composite carries objective non-collapse (validator gate S12) by construction: the
naive answer ignores the selector and reports the population-wide extreme, which is a
different entity and a different number. The generator asserts that before emitting — a
composite whose naive answer happens to equal the graded one is dropped, not shipped.

Ground truth is one SQL statement over the built world, carried as `gt_sql`, so the freshness
gate re-derives it on every validation run.

    python3 world/etl/compose_tasks.py --per-template 8
    python3 world/etl/compose_tasks.py --per-template 8 --out tasks/composite --dry-run
"""
import argparse, json, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
EPOCH = "2026-03-02"

OPEN_AR = "t.txn_type='Invoice' AND t.closed=0"


def _slug(s):
    import re
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(s).lower())).strip("-")[:44]


# Each template: a population the agent must first identify, a per-entity figure, and an
# aggregate. `naive_sql` is the same aggregate WITHOUT the selector — the shortcut a hurried
# analyst runs — and must differ from `gt_sql`.
TEMPLATES = [
    dict(
        key="hold-largest-pastdue",
        persona="Dana Kim · Credit Manager",
        ask=("We're reviewing everyone we've got blocked. Of the customers currently on credit "
             "hold in {group}, which one is sitting on the largest past-due balance, and how much is it?"),
        fields=["customer_account", "customer_name", "past_due_usd"],
        select_sql="""SELECT c.account, c.name FROM erp_customers c
                      WHERE c.on_hold='Yes' AND c.customer_group=:g ORDER BY c.account""",
        gt_sql="""SELECT c.account, c.name, ROUND(SUM(t.amount-t.settled),2) AS v
                  FROM erp_customers c JOIN erp_cust_trans t ON t.account=c.account
                  WHERE c.on_hold='Yes' AND c.customer_group=:g AND {open_ar}
                    AND t.due_date < '{epoch}'
                  GROUP BY c.account ORDER BY v DESC LIMIT 1""",
        naive_sql="""SELECT c.account, c.name, ROUND(SUM(t.amount-t.settled),2) AS v
                     FROM erp_customers c JOIN erp_cust_trans t ON t.account=c.account
                     WHERE c.customer_group=:g AND {open_ar} AND t.due_date < '{epoch}'
                     GROUP BY c.account ORDER BY v DESC LIMIT 1""",
        naive_note="reports the biggest past-due balance in the group, ignoring the hold filter",
    ),
    dict(
        key="letterlevel-oldest-invoice",
        persona="Casey Morgan · AR & Collections",
        ask=("For the dunning review: among customers in {group} who have already had a collection "
             "letter, who is carrying the oldest unpaid invoice, and what is the invoice date?"),
        fields=["customer_account", "customer_name", "oldest_invoice_date"],
        select_sql="""SELECT DISTINCT c.account, c.name FROM erp_customers c
                      JOIN erp_collection_letters l ON l.account=c.account
                      WHERE c.customer_group=:g ORDER BY c.account""",
        gt_sql="""SELECT c.account, c.name, MIN(t.trans_date) AS v
                  FROM erp_customers c JOIN erp_cust_trans t ON t.account=c.account
                  WHERE c.customer_group=:g AND {open_ar}
                    AND c.account IN (SELECT account FROM erp_collection_letters)
                  GROUP BY c.account ORDER BY v ASC LIMIT 1""",
        naive_sql="""SELECT c.account, c.name, MIN(t.trans_date) AS v
                     FROM erp_customers c JOIN erp_cust_trans t ON t.account=c.account
                     WHERE c.customer_group=:g AND {open_ar}
                     GROUP BY c.account ORDER BY v ASC LIMIT 1""",
        naive_note="reports the oldest unpaid invoice in the group, ignoring who has been dunned",
    ),
    dict(
        key="overlimit-exposure",
        persona="Dana Kim · Credit Manager",
        ask=("Risk pack question: within {group}, which customer is furthest over its credit limit "
             "right now, and by how much?"),
        fields=["customer_account", "customer_name", "over_limit_usd"],
        select_sql="""SELECT c.account, c.name FROM erp_customers c
                      WHERE c.customer_group=:g AND c.credit_max > 0 ORDER BY c.account""",
        gt_sql="""SELECT c.account, c.name, ROUND(SUM(t.amount-t.settled) - c.credit_max, 2) AS v
                  FROM erp_customers c JOIN erp_cust_trans t ON t.account=c.account
                  WHERE c.customer_group=:g AND c.credit_max > 0 AND {open_ar}
                  GROUP BY c.account HAVING v > 0 ORDER BY v DESC LIMIT 1""",
        naive_sql="""SELECT c.account, c.name, ROUND(SUM(t.amount-t.settled),2) AS v
                     FROM erp_customers c JOIN erp_cust_trans t ON t.account=c.account
                     WHERE c.customer_group=:g AND c.credit_max > 0 AND {open_ar}
                     GROUP BY c.account ORDER BY v DESC LIMIT 1""",
        naive_note="reports the largest exposure rather than the largest breach of a limit",
    ),
]


def _fill(sql, group):
    return sql.replace("{open_ar}", OPEN_AR).replace("{epoch}", EPOCH).replace(":g", f"'{group}'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-template", type=int, default=8)
    ap.add_argument("--out", default="tasks/composite")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cx = sqlite3.connect(DB)
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)

    groups = [g for (g,) in cx.execute(
        "SELECT customer_group FROM erp_customers WHERE customer_group IS NOT NULL "
        "GROUP BY customer_group HAVING COUNT(*) >= 8 ORDER BY COUNT(*) DESC")]
    made, dropped = 0, {"no_population": 0, "collapses": 0, "no_answer": 0}

    for tpl in TEMPLATES:
        n = 0
        for g in groups:
            if n >= a.per_template: break
            pop = cx.execute(_fill(tpl["select_sql"], g)).fetchall()
            if len(pop) < 3:                      # a population of one is not a selection
                dropped["no_population"] += 1; continue
            gt = cx.execute(_fill(tpl["gt_sql"], g)).fetchone()
            nv = cx.execute(_fill(tpl["naive_sql"], g)).fetchone()
            if not gt or gt[2] is None:
                dropped["no_answer"] += 1; continue
            if nv and str(nv[0]) == str(gt[0]):   # S12: the shortcut lands on the same entity
                dropped["collapses"] += 1; continue

            slug = f"{tpl['key']}-{_slug(g)}"
            d = out / slug
            (d / "tests").mkdir(parents=True, exist_ok=True)
            (d / "solution").mkdir(parents=True, exist_ok=True)
            n += 1; made += 1
            if a.dry_run: continue

            # the walk: discover the population, then query each member, then answer
            steps = [{"server": "erp", "tool": "data_find_entity_type", "args": {"query": "customers"}},
                     {"server": "erp", "tool": "data_find_entities_sql",
                      "args": {"sql": _fill(tpl["select_sql"], g).strip()}}]
            for acct, _nm in pop[:10]:
                steps.append({"server": "erp", "tool": "data_find_entities_sql",
                              "args": {"sql": f"SELECT invoice, trans_date, due_date, "
                                              f"ROUND(amount-settled,2) AS open_amount "
                                              f"FROM erp_cust_trans WHERE account='{acct}' "
                                              f"AND txn_type='Invoice' AND closed=0"}})
            answers = {tpl["fields"][0]: gt[0], tpl["fields"][1]: gt[1], tpl["fields"][2]: gt[2]}
            steps.append({"server": "harness", "tool": "submit_answer", "args": {"answers": answers}})
            (d / "solution/walk.json").write_text(json.dumps(steps, indent=1) + "\n")

            num = isinstance(gt[2], (int, float))
            checks = {"answer_checks": [
                {"field": tpl["fields"][0], "type": "contains_all", "expect": [gt[0]],
                 "forbid": [nv[0]] if nv and nv[0] != gt[0] else []},
                {"field": tpl["fields"][1], "type": "contains_all", "expect": [str(gt[1])[:24]]},
                ({"field": tpl["fields"][2], "type": "number", "expect": gt[2], "tol_abs": 0.02,
                  "gt_sql": " ".join(_fill(tpl["gt_sql"], g).split()).replace(
                      "SELECT c.account, c.name,", "SELECT").replace("SELECT c.account, c.name, ", "SELECT ")}
                 if num else
                 {"field": tpl["fields"][2], "type": "contains_all", "expect": [str(gt[2])]})],
                "trace_checks": [{"type": "required_servers", "servers": ["erp"]},
                                 {"type": "min_calls", "server": "erp", "n": 3},
                                 {"type": "reads_before_submit"}],
                "state_checks": [{"type": "writes_only", "tables": ["answers"]}]}
            (d / "tests/checks.json").write_text(json.dumps(checks, indent=1) + "\n")

            (d / "instruction.md").write_text(
                f"**{tpl['persona']} · Teams**\n\n{tpl['ask'].format(group=f'customer group {g}')}\n\n"
                f"---\n\nReply with `submit_answer`:\n\n"
                + "\n".join(f"- `{f}`" for f in tpl["fields"]) + "\n")

            (d / "task.toml").write_text(f'''schema_version = "1.4"

[task]
name = "composite/{slug}"
version = "0.1.0"
description = "Composite: identify a population, query each member, and aggregate to one defensible answer."
authors = ["nario-ai"]
keywords = ["finance", "composite", "multi-hop"]

[metadata]
family = "composite"
origin = "generated by world/etl/compose_tasks.py — selector + per-entity detail + aggregate. Depth comes from the population size, not from padding: the walk visits every selected member."
difficulty = "hard"
acceptance_label = "pending_calibration"
walk_len = {len(steps)}

# Objective non-collapse (S12), asserted by the generator before emitting: the shortcut is the
# same aggregate without the selector — {tpl["naive_note"]} — and it lands on a different
# entity, so it cannot score.
naive_answer = "{nv[0] if nv else ''}"
graded_answer = "{gt[0]}"

[verifier]
timeout_sec = 120
[agent]
timeout_sec = 900
[environment]
cpus = 1
memory_mb = 1024
''')

    print(f"composed {made} tasks across {len(TEMPLATES)} templates; dropped {dropped}")


if __name__ == "__main__":
    sys.exit(main())
