#!/usr/bin/env python3
"""Entity sweep — many instances of each verified ERP question pattern.

The cloner emits one task per FinanceBenchmark question, so it is capped at the 100 questions
the benchmark ships. The *patterns* those questions exercise are not capped: "what is the
aged balance for X" is a pattern, and this world holds 708 named parties with real ledger
history. This generates additional instances of each pattern over other entities, with ground
truth recomputed in-world exactly as the cloner does.

Honesty about what this is (`docs/PARITY.md` states it too): these are **instances of an
existing pattern**, not new patterns. ERP-Bench does the same thing — 300 tasks from 29
patterns — and it is defensible so long as the count is reported as patterns x instances
rather than as if every task were a distinct kind of problem. Instances go to their own
family (`erp_qa_gen`) so they never inflate the FinanceBenchmark parity number, which counts
only real clones of real benchmark questions.

Phrasing is borrowed from the benchmark question that exercises the pattern, with the entity
substituted, so the wording stays natural rather than template-stamped.

    python3 world/etl/sweep_erp_qa.py --per-pattern 6
    python3 world/etl/sweep_erp_qa.py --per-pattern 12 --out tasks/erp_qa_gen
"""
import argparse, importlib.util, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"


def _load_cloner():
    spec = importlib.util.spec_from_file_location("cloner", ROOT / "world/etl/clone_fb_erp.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def eligible(cx, side, limit=400):
    """Parties with enough ledger history that a question about them has a real answer."""
    if side == "vend":
        sql = """SELECT v.account, v.name FROM erp_vendors v
                 JOIN erp_vend_trans t ON t.account = v.account AND t.txn_type='Invoice'
                 GROUP BY v.account HAVING COUNT(*) >= 2 AND SUM(t.amount - t.settled) > 0"""
    else:
        sql = """SELECT c.account, c.name FROM erp_customers c
                 JOIN erp_cust_trans t ON t.account = c.account AND t.txn_type='Invoice'
                 GROUP BY c.account HAVING COUNT(*) >= 2 AND SUM(t.amount - t.settled) > 0"""
    rows = cx.execute(sql).fetchall()
    # one account per name: a name shared by several accounts makes "the" answer ambiguous
    seen, out = set(), []
    for acct, name in rows:
        n = (name or "").strip()
        if not n or len(n) <= 4 or n.lower() in seen: continue
        seen.add(n.lower()); out.append((acct, n))
        if len(out) >= limit: break
    return out


def _all_null_checks(task_dir):
    """True when every answer check is satisfied without reading anything."""
    try:
        ac = json.loads((task_dir / "tests/checks.json").read_text()).get("answer_checks", [])
    except Exception:
        return False
    if not ac: return True
    def nul(c):
        k = c.get("type", "string")
        if k == "none_answer": return True
        if k == "number": return float(c.get("expect", 0) or 0) == 0
        if k == "yes_no": return str(c.get("expect", "")).lower() == "no"
        if k == "contains_all":
            e = [str(x).strip().lower() for x in (c.get("expect") or [])]
            return all(x in ("0", "none", "no", "n/a", "") for x in e)
        return str(c.get("expect", "")).strip().lower() in ("0", "none", "no", "")
    return all(nul(c) for c in ac)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-pattern", type=int, default=6)
    ap.add_argument("--out", default="tasks/erp_qa_gen")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    C = _load_cloner()
    import yaml
    data = yaml.safe_load(C.DATASET.read_text())
    erp = [t for t in data if t.get("plugin") == "erp_qa"]
    cx = sqlite3.connect(DB)
    out_dir = ROOT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)

    pool = {"cust": eligible(cx, "cust"), "vend": eligible(cx, "vend")}
    made, per_pattern, skipped, degenerate = 0, {}, 0, 0

    for t in erp:
        sc, seg, q = t.get("scenario"), t.get("segment"), t["query"]
        if next((1 for rx, _ in C.EXCLUDE if rx.search(q)), None): continue
        r = C.route(sc, q)
        if not r or not r.get("ent"): continue           # entity-free patterns have one answer
        accts, name, side, missing = C.resolve(cx, q, seg)
        if not accts or not name: continue               # need a resolvable exemplar to rephrase
        key = f"{sc}|{r['fn'].__name__}"
        if per_pattern.get(key, 0) >= a.per_pattern: continue

        want = r["ent"]
        for acct2, name2 in pool.get(want, []):
            if per_pattern.get(key, 0) >= a.per_pattern: break
            if name2.lower() == name.lower(): continue
            q2 = re.sub(re.escape(name), name2, q, flags=re.I)
            if q2 == q: continue                          # entity not literally in the wording
            q2 = re.sub(r"\((SYN(?:CUS|VEN)-\d{4}|US-\d{3})\)", f"({acct2})", q2)
            try:
                a2, n2, s2, miss2 = C.resolve(cx, q2, seg)
                if not a2: continue
                ctx = C.Ctx(cx, q2, seg, a2, n2, s2, miss2)
                ctx.side = want
                ctx.table = "erp_vendors" if want == "vend" else "erp_customers"
                res = r["fn"](cx, ctx)
            except Exception:
                skipped += 1; continue
            if not res: skipped += 1; continue
            fields, steps = res[0], res[1]
            sqls = res[2] if len(res) > 2 and isinstance(res[2], dict) else {}
            if not fields: skipped += 1; continue
            # Reject instances whose graded answer is entirely null. Eligibility is measured
            # on open invoices, but a pattern like "letters sent" or "open sales orders" asks
            # about a different table — pairing it with an entity that has no rows there
            # produces a task answerable with "0/none" and no reading at all. An empty table
            # does not make a task hard, it makes it free (docs/AUDIT.md A11).
            def _null(v, kind):
                if kind == "number": return float(v or 0) == 0
                s = str(v).strip().lower()
                return s in ("", "none", "no", "n/a", "0", "[]")
            if all(_null(v, k) for v, k in fields.values()):
                degenerate += 1; continue
            slug = f"{C.slug(sc)}-{C.slug(name2)[:26]}"
            if (out_dir / slug).exists(): continue
            if a.dry_run:
                made += 1; per_pattern[key] = per_pattern.get(key, 0) + 1; continue
            try:
                C.emit(out_dir, slug, q2, sc, seg, fields, steps, sqls, instance_of=key)
            except Exception:
                skipped += 1; continue
            # Judge the EMITTED checks, not the handler's field dict. The two disagreed on
            # list-valued answers, and the gate that matters is the one a model actually
            # faces: if every graded check is satisfied by "0 / none / no", the task is free.
            if _all_null_checks(out_dir / slug):
                import shutil as _sh; _sh.rmtree(out_dir / slug)
                degenerate += 1; continue
            made += 1; per_pattern[key] = per_pattern.get(key, 0) + 1

    print(f"generated {made} instances across {len(per_pattern)} patterns "
          f"({skipped} dropped: handler declined · {degenerate} dropped: answer would be "
          f"entirely null, i.e. free to a model that never reads)")
    for k, v in sorted(per_pattern.items()): print(f"   {v:3}  {k}")


if __name__ == "__main__":
    sys.exit(main())
