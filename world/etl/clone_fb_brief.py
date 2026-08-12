#!/usr/bin/env python3
"""Clone microsoft/FinanceBenchmark `business_brief` items as structured, deterministic briefs.

FB ships these as one line — "Business Brief report of Apple Inc." — and grades the prose with
a DSPy LLM judge over clarity/groundedness/relevance assertions. This repo bans judges from the
reward path, so the JUDGEMENT is ported and the prose scoring is dropped, exactly as
docs/INGESTION.md's `judgement_port` class prescribes.

What survives the port is what a credit brief is actually FOR: scale, profitability, leverage,
and — the part a public-data-only brief always misses — whether we already trade with them.
That last field is the mechanic this world adds over FB: the answer lives in the ERP, not the
filings, so a model that reads only `filings` cannot complete the brief. For most public
subjects the honest answer is "no relationship", which makes it a hallucination trap as well
as a fusion task (the `none_answer` check type, docs/AUDIT.md A5).

Generalises the hand-authored `business_brief/brief-caterpillar`, whose field set and 3-year
leverage convention this follows rather than invents.

    python3 world/etl/clone_fb_brief.py --dry-run
    python3 world/etl/clone_fb_brief.py --out tasks/business_brief_fb
"""
import argparse, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "world/build/core.sqlite"
sys.path.insert(0, str(ROOT / "ingest"))

PERSONA = "**Robin Vale · Treasury · email**"


def annual(cx, cik, concept, n=4):
    """Most recent n annual values, newest first."""
    return cx.execute(
        "SELECT value, period_end, form, accession FROM filings_facts "
        "WHERE cik=? AND concept=? AND fp='FY' ORDER BY period_end DESC LIMIT ?",
        (cik, concept, n)).fetchall()


def internal_relationship(cx, subject):
    """Is this public company also a counterparty in the ERP or the subsidiary books?

    Matched on the distinctive head word, and only where that word is long enough to be
    unambiguous — the point of the field is that the truthful answer is usually "none", and a
    loose match would turn a hallucination trap into a wrong ground truth (A10.3).
    """
    head = re.sub(r"[^a-z]", "", subject.split()[0].lower())
    if len(head) < 5: return None
    for tbl in ("erp_customers", "erp_vendors"):
        try:
            row = cx.execute(f"SELECT account, name FROM {tbl} WHERE lower(name) LIKE ?",
                             (f"%{head}%",)).fetchone()
        except sqlite3.Error:
            continue
        if row: return {"table": tbl, "account": row[0], "name": row[1]}
    return None


def build(cx, subject, tk, cik):
    fields, steps, notes = {}, [], []

    rev = annual(cx, cik, "Revenues", 1)
    ni = annual(cx, cik, "NetIncomeLoss", 1)
    if not rev or not ni:
        return None, None, f"fact_absent: {tk} lacks Revenues/NetIncomeLoss at annual grain"
    fy = rev[0][1][:4]
    fields[f"revenue_fy{fy}"] = (rev[0][0], "number")
    fields[f"net_income_fy{fy}"] = (ni[0][0], "number")
    steps += [("lookup_company", {"query": subject}),
              ("get_company_concept", {"ticker": tk, "concept": "Revenues"}),
              ("get_company_concept", {"ticker": tk, "concept": "NetIncomeLoss"})]
    notes.append(f"scale/profitability @ {rev[0][1]} ({rev[0][2]})")

    # leverage, 3-year average — the brief-caterpillar convention
    debt = annual(cx, cik, "LongTermDebtNoncurrent", 3)
    eq = annual(cx, cik, "StockholdersEquity", 3)
    if len(debt) >= 3 and len(eq) >= 3:
        by_eq = {e[1]: e[0] for e in eq}
        pairs = [(d[0], by_eq[d[1]]) for d in debt if d[1] in by_eq and by_eq[d[1]]]
        if len(pairs) >= 3:
            fields["lt_de_ratio_3yr_avg"] = (round(sum(d / e for d, e in pairs[:3]) / 3.0, 4), "number")
            steps += [("get_company_concept", {"ticker": tk, "concept": "LongTermDebtNoncurrent"}),
                      ("get_company_concept", {"ticker": tk, "concept": "StockholdersEquity"})]
            notes.append("3yr avg long-term D/E")

    return fields, steps, "; ".join(notes)


# ── the fusion mechanic ────────────────────────────────────────────────────────────────────
# A brief that only reads `filings` is not a brief, it is a lookup. The last two fields ask
# whether we already carry exposure to this counterparty, which is answerable only from the ERP.
#
# Half the subjects are seeded as real customers and half are not, chosen deterministically.
# That split is the whole point: when EVERY brief answers "no relationship" — which is what the
# first cut of this emitter produced, 19 times out of 19 — the field is free to a model that
# never opens the ERP, which is precisely the A11 defect ("answerable without reading").
#
# Both variants declare the SAME two fields. An earlier shape gave the seeded briefs an extra
# `internal_open_ar_usd` field, which leaks the answer in the instruction: seeing the field at
# all would tell the model a relationship exists before it queried anything.
SEED_PREFIX = "BRF"


def seeded(idx):
    return idx % 2 == 0


def relationship_fields(cx, subject, idx):
    if not seeded(idx):
        return {"internal_ar_relationship": (None, "none"),
                "internal_open_ar_usd": (0, "number")}, None, "no internal exposure (trap)"
    acct = f"{SEED_PREFIX}-{idx:02d}"
    # deterministic amounts — no RNG, so a rebuild reproduces the same world
    h = sum(ord(c) for c in subject)
    amts = [round(12000 + (h * 37) % 9000, 2), round(8000 + (h * 53) % 6000, 2),
            round(15000 + (h * 71) % 11000, 2)]
    total = round(sum(amts), 2)
    rows = ",\n  ".join(
        f"('USMF','{acct}','{SEED_PREFIX}V-{idx:02d}{n}','{SEED_PREFIX}INV-{idx:02d}{n}',"
        f"'Invoice','Managed services {m}','2026-0{m}-1{n}','2026-0{m+1}-1{n}','USD',{a},0,0)"
        for n, (a, m) in enumerate(zip(amts, (1, 1, 2)), start=1))
    sql = f"""-- business_brief_fb: {subject} is also a customer of USMF.
-- Half the brief subjects carry real internal exposure and half carry none, so the
-- "do we already trade with them?" field cannot be answered without querying the ERP
-- (docs/AUDIT.md A11). Account id uses the reserved {SEED_PREFIX}- prefix so generated world
-- data can never squat on it (A14). SIMULATION ONLY.
INSERT OR REPLACE INTO erp_customers
  (account, dataareaid, name, customer_group, currency, payment_term, cash_disc_code,
   credit_max, credit_rating, on_hold, city, state, contact_name, contact_email, phone) VALUES
  ('{acct}','USMF','{subject.replace("'", "")}','30','USD','Net30',NULL,500000,'Good','Open',
   'Redmond','WA','A. Reyes','ar@{SEED_PREFIX.lower()}-sim.example','555-01{idx:02d}');

INSERT INTO erp_cust_trans
  (dataareaid, account, voucher, invoice, txn_type, description, trans_date, due_date,
   currency, amount, settled, closed) VALUES
  {rows};
"""
    return ({"internal_ar_relationship": (acct, "contains"),
             "internal_open_ar_usd": (total, "number")}, sql,
            f"internal exposure {acct} = {total}")


def emit(out_dir, slug, subject, fields, steps, note, source_id, seed_sql=None):
    d = out_dir / slug
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "solution").mkdir(parents=True, exist_ok=True)
    if seed_sql:
        (d / "environment/seed").mkdir(parents=True, exist_ok=True)
        (d / "environment/seed/seed.sql").write_text(seed_sql)

    walk = []
    for t, a in steps:
        if t == "__erp__":
            # the brief must CHECK the ERP even when the answer is "no relationship" — an
            # unchecked "none" is a guess that happens to be right
            walk.append({"server": "erp", "tool": "data_find_entities",
                         "args": {"entity": "Customers", "filters": {"name": subject.split()[0]}}})
        else:
            walk.append({"server": "filings", "tool": t, "args": a})
    walk.append({"server": "harness", "tool": "submit_answer",
                 "args": {"answers": {k: ("none" if v is None else v) for k, (v, _) in fields.items()}}})
    (d / "solution/walk.json").write_text(json.dumps(walk, indent=1) + "\n")

    checks = {"answer_checks": [], "trace_checks": [
        {"type": "required_servers", "servers": ["filings", "erp"]},
        {"type": "min_calls", "server": "filings", "n": 2},
        {"type": "reads_before_submit"}],
        "state_checks": [{"type": "writes_only", "tables": ["answers"]}]}
    for k, (v, kind) in fields.items():
        if kind == "number":
            ac = {"field": k, "type": "number", "expect": v}
            ac["tol_abs" if abs(v) < 1000 else "tol_rel"] = 0.02 if abs(v) < 1000 else 0.001
            checks["answer_checks"].append(ac)
        elif kind == "none":
            checks["answer_checks"].append({"field": k, "type": "none_answer"})
        else:
            checks["answer_checks"].append({"field": k, "type": "contains_all", "expect": [str(v)]})
    (d / "tests/checks.json").write_text(json.dumps(checks, indent=1) + "\n")

    # Message only — the reporting contract is on the tool (see sim/naturalize_prompts.py).
    (d / "instruction.md").write_text(
        f"{PERSONA}\n\nPutting together the counterparty brief on {subject}. I need the public "
        f"numbers — scale, profitability and the leverage picture — and, importantly, whether "
        f"we already have any exposure to them on our own books. Don't assume either way, "
        f"check.\n")
    seedf = d / "environment/seed/mcp_seed.json"
    seedf.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(seedf.read_text()) if seedf.exists() else {}
    payload["answer_schema"] = [
        {"ordinal": i, "field": k, "type": "number" if kind == "number" else "text",
         "description": ""}
        for i, (k, (_v, kind)) in enumerate(fields.items(), start=1)]
    seedf.write_text(json.dumps(payload, indent=1) + "\n")

    (d / "task.toml").write_text(f'''schema_version = "1.4"

[task]
name = "{out_dir.name}/{slug}"
version = "0.1.0"
description = "FinanceBenchmark business_brief clone — structured counterparty brief."
authors = ["nario-ai"]
keywords = ["finance", "business_brief", "financebenchmark-clone"]

[metadata]
family = "{out_dir.name}"
origin = "clone of microsoft/FinanceBenchmark business_brief item {source_id} ({subject}); the JUDGEMENT is ported and FB's DSPy LLM-judge prose scoring is dropped per docs/INGESTION.md judgement_port. Figures recomputed from the frozen SEC XBRL snapshot; the internal_ar_relationship field is this world's addition — it is answerable only from the ERP, not the filings ({note})"
generated = false
difficulty = "medium"
acceptance_label = "pending_calibration"
walk_len = {len(walk)}

[verifier]
timeout_sec = 120
[agent]
timeout_sec = 600
[environment]
cpus = 1
memory_mb = 1024
''')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tasks/business_brief_fb")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    from adapters import financebenchmark as fb
    cx = sqlite3.connect(DB)
    have = {t: (c, n) for t, c, n in cx.execute("SELECT ticker, cik, name FROM filings_companies")}
    names = {n.lower(): t for t, (_c, n) in have.items()}
    out_dir = ROOT / a.out
    if not a.dry_run: out_dir.mkdir(parents=True, exist_ok=True)

    made, rejected = 0, []
    for idx, s in enumerate([x for x in fb.specs() if x.family == "business_brief"]):
        subject = re.sub(r"^.*?report of\s*", "", s.question, flags=re.I).strip().rstrip(".")
        tk = None
        for nm, t in names.items():
            head = nm.split()[0]
            if len(head) > 3 and re.search(rf"\b{re.escape(head)}", subject, re.I): tk = t; break
        # ...and by ticker. The registrant name is "INTERNATIONAL BUSINESS MACHINES CORP" but
        # the brief subject is written "IBM", so name-head matching alone cannot resolve it.
        if not tk:
            tk = next((t for t in have if re.search(rf"\b{t}\b", subject)), None)
        if not tk and s.entities and s.entities[0] in have: tk = s.entities[0]
        if not tk:
            rejected.append((s.source_id, f"absent_entity: {subject} not in the filings snapshot"))
            continue
        cik, _name = have[tk]
        fields, steps, note = build(cx, subject, tk, cik)
        if not fields:
            rejected.append((s.source_id, note)); continue
        rel_fields, seed_sql, rel_note = relationship_fields(cx, subject, idx)
        fields.update(rel_fields)
        steps.append(("__erp__", {}))
        note = f"{note}; {rel_note}"
        slug = f"brief-{re.sub(r'[^a-z0-9]+', '-', subject.lower()).strip('-')[:34]}"
        if a.dry_run: print(f"  ok   {slug:40} {note}")
        else: emit(out_dir, slug, subject, fields, steps, note, s.source_id, seed_sql)
        made += 1

    print(f"\nemitted {made} / {made + len(rejected)}")
    for sid, why in rejected: print(f"   {sid:20} {why}")


if __name__ == "__main__":
    sys.exit(main())
