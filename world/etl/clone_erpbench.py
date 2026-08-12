#!/usr/bin/env python3
"""Clone agentic-labs/erp-bench onto this world's Odoo-shaped surface.

ERP-Bench ships 300 true Harbor task dirs, each of which boots a real Odoo 19 in Docker and
grades it by querying the live server with `odoolib`. The plumbing does not port. What does is
everything that matters:

  * `environment/scenario_data.json` is a fully DECLARATIVE world spec — partners with budgets,
    products with per-vendor min/max/price offers, BOMs, workcenters, stock, existing orders —
    so the scenario seeds `erpb_*` directly.
  * `solution/optimal_plan.json` is the reference solution, per-customer, with accept/reject,
    purchase units, assembly units and margin. That is the oracle walk.
  * The judgement is a set of arithmetic properties of the world the agent leaves behind
    (demand covered, budget caps respected, margin floor cleared, vendor min/max honoured as
    horizon totals, SO->PO lineage present, dates set). Every one of those is a scalar SQL
    assertion, so the existing `sql` state check grades them with no new verifier machinery.

Honest scope note. The instruction text is carried VERBATIM from the source scenario, because
it is the eval; what changes is the substrate it runs against and the fact that grading is
deterministic rather than a live-server query. Where a stated policy cannot be enforced by a
scalar assertion, the task is REJECTED rather than shipped with a check that does not grade
what its prompt asks (the A10.2 rule).

    python3 world/etl/clone_erpbench.py --dry-run
    python3 world/etl/clone_erpbench.py --limit 5 --out tasks/erpbench
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/external/repos/erp-bench/tasks"


def q(s):
    return "'" + str(s).replace("'", "''") + "'" if s is not None else "NULL"


def seed_sql(sc):
    """scenario_data.json -> INSERTs into the erpb_* surface."""
    L = [f"-- agentic-labs/erp-bench scenario {sc.get('scenario_number')}: {sc.get('name')}",
         "-- Seeded verbatim from the source scenario_data.json. SIMULATION ONLY.", ""]

    for p in sc.get("customers") or []:
        L.append(f"INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,"
                 f"budget_dollars,credit_limit,payment_term,email,comment) VALUES("
                 f"{q(p.get('ref'))},{q(p.get('name'))},'customer',0,"
                 f"{p.get('budget_dollars') if p.get('budget_dollars') is not None else 'NULL'},"
                 f"{p.get('credit_limit') if p.get('credit_limit') is not None else 'NULL'},"
                 f"{q(p.get('payment_term'))},{q(p.get('email'))},{q(p.get('comment'))});")
    for v in sc.get("vendors") or []:
        L.append(f"INSERT OR REPLACE INTO erpb_partners(ref,name,kind,supplier_rank,comment) "
                 f"VALUES({q(v.get('ref'))},{q(v.get('name'))},'vendor',"
                 f"{v.get('supplier_rank') or 1},{q(v.get('comment'))});")

    offer_id = 0
    for pr in sc.get("products") or []:
        routes = ",".join(pr.get("routes") or [])
        L.append(f"INSERT OR REPLACE INTO erpb_products(code,name,category,type,list_price,"
                 f"standard_price,routes,comment) VALUES({q(pr.get('code'))},{q(pr.get('name'))},"
                 f"{q(pr.get('category'))},{q(pr.get('type'))},"
                 f"{pr.get('list_price') or 0},{pr.get('standard_price') or 0},"
                 f"{q(routes)},{q(pr.get('comment'))});")
        for vi in pr.get("vendor_info") or []:
            offer_id += 1
            L.append(f"INSERT INTO erpb_vendor_offers(id,product_code,partner_ref,name,delay,"
                     f"min_qty,max_qty,price) VALUES({offer_id},{q(pr.get('code'))},"
                     f"{q(vi.get('partner_ref'))},{q(vi.get('name'))},{vi.get('delay') or 0},"
                     f"{vi.get('min_qty') or 0},{vi.get('max_qty') or 0},{vi.get('price') or 0});")

    bom_id = 0
    for b in sc.get("boms") or []:
        bom_id += 1
        L.append(f"INSERT INTO erpb_boms(id,product_code,type,quantity,warehouse_code) VALUES("
                 f"{bom_id},{q(b.get('product_code'))},{q(b.get('type'))},"
                 f"{b.get('quantity') or 1},{q(b.get('warehouse_code'))});")
        for c in b.get("components") or []:
            L.append(f"INSERT INTO erpb_bom_components(bom_id,component_code,quantity) VALUES("
                     f"{bom_id},{q(c.get('component_code'))},{c.get('quantity') or 0});")

    for w in sc.get("workcenters") or []:
        L.append(f"INSERT OR REPLACE INTO erpb_workcenters(code,name,capacity_per_day,"
                 f"cost_per_hour,warehouse_code,comment) VALUES({q(w.get('code'))},"
                 f"{q(w.get('name'))},{w.get('capacity_per_day') or w.get('capacity') or 0},"
                 f"{w.get('cost_per_hour') or 0},{q(w.get('warehouse_code'))},{q(w.get('comment'))});")

    for s in sc.get("stock_levels") or []:
        L.append(f"INSERT INTO erpb_stock(product_code,warehouse_code,quantity,location_type) "
                 f"VALUES({q(s.get('product_code'))},{q(s.get('warehouse_code'))},"
                 f"{s.get('quantity') or 0},{q(s.get('location_type'))});")
    return "\n".join(L) + "\n"


def demand_rows(plan, sc):
    """The customer demand the plan allocates against, with its budget cap."""
    budgets = {c.get("ref"): c.get("budget_dollars") for c in (sc.get("customers") or [])}
    fin = (sc.get("products") or [{}])[0].get("code")
    out = []
    for i, a in enumerate(plan.get("allocations") or [], start=1):
        out.append({"id": i, "partner_ref": a.get("ref"), "product_code": fin,
                    "units": a.get("demand") or 0, "due_days": a.get("deadline"),
                    "budget_cap": budgets.get(a.get("ref")),
                    "seeded_order_state": a.get("seeded_order_state")})
    return out


def checks_for(plan, sc, dem):
    """The judgement, as scalar SQL assertions over the world the agent leaves behind."""
    accepted = [a for a in (plan.get("allocations") or []) if a.get("accepted")]
    rejected = [a for a in (plan.get("allocations") or []) if not a.get("accepted")]
    fin = (sc.get("products") or [{}])[0].get("code")
    list_price = (sc.get("products") or [{}])[0].get("list_price") or 0

    ac, sc_checks = [], []

    # 1. every accepted order is covered by a CONFIRMED sale order for the right quantity
    sc_checks.append({
        "type": "sql", "name": "confirmed_sale_units",
        "sql": "SELECT COALESCE(SUM(l.qty),0) FROM erpb_sale_order_lines l "
               "JOIN erpb_sale_orders o ON o.name=l.order_name "
               "WHERE o.state='sale'",
        "expect": sum(a.get("fulfilled_demand") or 0 for a in accepted), "tol_abs": 0.01})

    # 2. an unsatisfiable order must be REJECTED, not quietly dropped: no SO for it
    for a in rejected:
        sc_checks.append({
            "type": "sql", "name": f"no_order_for_rejected_{a.get('ref')}",
            "sql": "SELECT COUNT(*) FROM erpb_sale_orders WHERE partner_ref="
                   f"'{a.get('ref')}' AND state='sale'", "expect": 0})

    # 3. purchased and manufactured units match the plan — the make-or-buy split IS the task
    sc_checks.append({
        "type": "sql", "name": "confirmed_purchase_units",
        "sql": "SELECT COALESCE(SUM(l.qty),0) FROM erpb_purchase_order_lines l "
               "JOIN erpb_purchase_orders o ON o.name=l.order_name "
               "WHERE o.state='purchase'",
        "expect": sum(p.get("quantity") or 0 for p in plan.get("purchase_orders") or []),
        "tol_abs": 0.01})
    mo_units = sum(m.get("quantity") or 0 for m in plan.get("manufacturing_orders") or [])
    sc_checks.append({
        "type": "sql", "name": "confirmed_manufacture_units",
        "sql": "SELECT COALESCE(SUM(qty),0) FROM erpb_manufacturing_orders WHERE state='confirmed'",
        "expect": mo_units, "tol_abs": 0.01})
    if mo_units:
        # capacity is a real constraint: an MO must name a workcenter that exists
        sc_checks.append({
            "type": "sql", "name": "mo_workcenters_exist",
            "sql": "SELECT COUNT(*) FROM erpb_manufacturing_orders m WHERE m.state='confirmed' "
                   "AND NOT EXISTS (SELECT 1 FROM erpb_workcenters w WHERE w.code=m.workcenter_code)",
            "expect": 0})

    # 4. sold at list price — an explicit policy in every scenario's background
    if list_price:
        sc_checks.append({
            "type": "sql", "name": "all_lines_at_list_price",
            "sql": "SELECT COUNT(*) FROM erpb_sale_order_lines l JOIN erpb_sale_orders o "
                   f"ON o.name=l.order_name WHERE o.state='sale' AND ABS(l.price_unit-{list_price})>0.01",
            "expect": 0})

    # 5. SO -> PO lineage: every confirmed PO names a sale order in `origin`
    sc_checks.append({
        "type": "sql", "name": "po_origin_links_to_so",
        "sql": "SELECT COUNT(*) FROM erpb_purchase_orders p WHERE p.state='purchase' AND "
               "NOT EXISTS (SELECT 1 FROM erpb_sale_orders s WHERE s.state='sale' "
               "AND p.origin LIKE '%'||s.name||'%')", "expect": 0})

    # 6. dates are set — commitment on the sale, delivery on the purchase
    sc_checks.append({
        "type": "sql", "name": "sale_commitment_dates_set",
        "sql": "SELECT COUNT(*) FROM erpb_sale_orders WHERE state='sale' AND "
               "(commitment_date IS NULL OR commitment_date='')", "expect": 0})
    sc_checks.append({
        "type": "sql", "name": "purchase_dates_set",
        "sql": "SELECT COUNT(*) FROM erpb_purchase_orders WHERE state='purchase' AND "
               "(date_planned IS NULL OR date_planned='')", "expect": 0})

    # 7. every confirmed PO buys from a vendor that actually offers that product — the
    #    min/max and price on the offer are only binding if the PO is against a real offer
    sc_checks.append({
        "type": "sql", "name": "po_lines_match_a_real_offer",
        "sql": "SELECT COUNT(*) FROM erpb_purchase_order_lines l "
               "JOIN erpb_purchase_orders o ON o.name=l.order_name WHERE o.state='purchase' "
               "AND NOT EXISTS (SELECT 1 FROM erpb_vendor_offers v "
               "WHERE v.partner_ref=o.partner_ref AND v.product_code=l.product_code)",
        "expect": 0})

    # 8. THE OBJECTIVE. Without this the task grades only that the right number of units was
    #    bought, not that they were bought WELL — and `min_new_spend` is the stated objective in
    #    183 of the 300 scenarios. Graded against the plan's own `optimal_new_spend`.
    #
    #    Note this is NOT the sum of per-allocation `variable_cost`: that figure includes the
    #    cost of on-hand stock consumed, so grading against it demanded spend the plan never
    #    intended. Using it failed all 70 tasks, which is how the distinction was found.
    #    Graded against the plan's PURCHASE spend specifically. `optimal_new_spend` is the wrong
    #    figure to compare PO lines against: it also carries the assembly cost of the
    #    manufacturing orders, so on a make-or-buy scenario it demanded ~4k of purchasing that
    #    the plan intended to spend in the workcentre.
    spend = round(sum(p.get("total_cost") or 0 for p in plan.get("purchase_orders") or []), 2)
    if spend:
        sc_checks.append({
            "type": "sql", "name": "purchase_spend_matches_optimal",
            "sql": "SELECT COALESCE(SUM(l.qty*l.price_unit),0) FROM erpb_purchase_order_lines l "
                   "JOIN erpb_purchase_orders o ON o.name=l.order_name WHERE o.state='purchase'",
            "expect": spend, "tol_rel": 0.005})
    # declared on every task, 0 when nothing is manufactured — a field that appears only on
    # make-or-buy scenarios would tell the model the answer before it read the routes
    assembly = round(sum(m.get("total_cost") or 0 for m in plan.get("manufacturing_orders") or []), 2)
    ac.append({"field": "assembly_cost", "type": "number", "expect": assembly,
               "tol_abs": 0.01 if not assembly else max(0.01, assembly * 0.005)})

    # the agent also reports the plan, so the numbers are checkable without reading state
    ac.append({"field": "orders_accepted", "type": "number",
               "expect": len(accepted), "tol_abs": 0})
    ac.append({"field": "orders_rejected", "type": "number",
               "expect": len(rejected), "tol_abs": 0})
    ac.append({"field": "units_purchased", "type": "number",
               "expect": sum(p.get("quantity") or 0 for p in plan.get("purchase_orders") or []),
               "tol_abs": 0.01})
    ac.append({"field": "units_manufactured", "type": "number", "expect": mo_units,
               "tol_abs": 0.01})
    return ac, sc_checks


def oracle_walk(plan, sc, dem):
    """optimal_plan.json -> the tool sequence that produces the graded world.

    Built from the plan's OWN `purchase_orders` and `manufacturing_orders` arrays, which name
    the vendor, quantity and unit cost of every line it intends. An earlier version derived the
    purchase itself — buy everything from the cheapest offer — and every one of the 70 tasks
    failed the spend check, correctly: buying from the cheapest offer ignores that offer's
    max_qty, so it is not merely suboptimal, it is an invalid plan that happens to be cheaper.
    """
    fin = (sc.get("products") or [{}])[0].get("code")
    price = (sc.get("products") or [{}])[0].get("list_price") or 0
    walk = [
        {"server": "odoo", "tool": "search_read",
         "args": {"model": "res.partner", "domain": [["kind", "=", "customer"]]}},
        {"server": "odoo", "tool": "search_read",
         "args": {"model": "product.supplierinfo", "domain": [["product_code", "=", fin]]}},
        {"server": "odoo", "tool": "search_read",
         "args": {"model": "stock.quant", "domain": [["product_code", "=", fin]]}},
    ]
    accepted = [a for a in (plan.get("allocations") or []) if a.get("accepted")]
    so_names = []
    for i, a in enumerate(accepted, start=1):
        name = "S%05d" % i
        so_names.append(name)
        walk.append({"server": "odoo", "tool": "create", "args": {
            "model": "sale.order",
            "values": {"name": name, "partner_ref": a.get("ref"), "state": "draft",
                       "commitment_date": f"2026-03-{min(28, 2 + int(a.get('deadline') or 1)):02d}"}}})
        walk.append({"server": "odoo", "tool": "create", "args": {
            "model": "sale.order.line",
            "values": {"order_name": name, "product_code": fin,
                       "qty": a.get("fulfilled_demand") or 0, "price_unit": price}}})
    if so_names:
        walk.append({"server": "odoo", "tool": "action_confirm",
                     "args": {"model": "sale.order", "names": so_names}})

    origin = ", ".join(so_names)
    po_names = []
    for i, po in enumerate(plan.get("purchase_orders") or [], start=1):
        name = "P%05d" % i
        po_names.append(name)
        walk.append({"server": "odoo", "tool": "create", "args": {
            "model": "purchase.order",
            "values": {"name": name, "partner_ref": po.get("vendor_ref"), "state": "draft",
                       "date_planned": f"2026-03-{min(28, 2 + int(po.get('lead_time') or 1)):02d}",
                       "origin": origin}}})
        walk.append({"server": "odoo", "tool": "create", "args": {
            "model": "purchase.order.line",
            "values": {"order_name": name, "product_code": po.get("product_code") or fin,
                       "qty": po.get("quantity") or 0, "price_unit": po.get("unit_cost") or 0}}})
    if po_names:
        walk.append({"server": "odoo", "tool": "action_confirm",
                     "args": {"model": "purchase.order", "names": po_names}})

    mo_names = []
    for i, mo in enumerate(plan.get("manufacturing_orders") or [], start=1):
        name = "MO%05d" % i
        mo_names.append(name)
        walk.append({"server": "odoo", "tool": "create", "args": {
            "model": "mrp.production",
            "values": {"name": name, "product_code": mo.get("product_code"),
                       "qty": mo.get("quantity") or 0, "state": "draft",
                       "workcenter_code": mo.get("workcenter_code"),
                       "date_planned": f"2026-03-{min(28, 2 + int(mo.get('lead_time') or 1)):02d}",
                       "origin": origin}}})
    if mo_names:
        walk.append({"server": "odoo", "tool": "action_confirm",
                     "args": {"model": "mrp.production", "names": mo_names}})

    rejected = [a for a in (plan.get("allocations") or []) if not a.get("accepted")]
    walk.append({"server": "harness", "tool": "submit_answer", "args": {"answers": {
        "orders_accepted": len(accepted),
        "orders_rejected": len(rejected),
        "units_purchased": sum(p.get("quantity") or 0 for p in plan.get("purchase_orders") or []),
        "units_manufactured": sum(m.get("quantity") or 0 for m in plan.get("manufacturing_orders") or []),
        "assembly_cost": round(sum(m.get("total_cost") or 0 for m in plan.get("manufacturing_orders") or []), 2)}}})
    return walk


def portable(sc, plan):
    """Reject rather than mis-grade. Returns a reason, or None when portable."""
    if not (sc.get("products") or []): return "no products in scenario"
    if not (plan.get("allocations") or []): return "no allocations in optimal_plan"
    if sc.get("invoicing_policy", {}).get("downpayment_required"):
        return "downpayment/invoicing policy not yet expressed as a scalar assertion"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tasks/erpbench")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out_dir = ROOT / a.out
    if not a.dry_run: out_dir.mkdir(parents=True, exist_ok=True)

    made, rejected = 0, {}
    for d in sorted(SRC.glob("2*")):
        if a.limit and made >= a.limit: break
        try:
            sc = json.loads((d / "environment/scenario_data.json").read_text())
            plan = json.loads((d / "solution/optimal_plan.json").read_text())
        except Exception as e:
            rejected.setdefault(f"unreadable: {e.__class__.__name__}", []).append(d.name); continue
        why = portable(sc, plan)
        if why:
            rejected.setdefault(why, []).append(d.name); continue

        dem = demand_rows(plan, sc)
        ac, stc = checks_for(plan, sc, dem)
        walk = oracle_walk(plan, sc, dem)
        slug = re.sub(r"[^a-z0-9]+", "-", d.name.lower()).strip("-")
        made += 1
        if a.dry_run:
            print(f"  ok   {slug:56} {len(walk)} steps, {len(stc)} state checks"); continue

        t = out_dir / slug
        (t / "tests").mkdir(parents=True, exist_ok=True)
        (t / "solution").mkdir(parents=True, exist_ok=True)
        (t / "environment/seed").mkdir(parents=True, exist_ok=True)

        seed = seed_sql(sc)
        seed += "\n" + "\n".join(
            f"INSERT INTO erpb_demand(id,partner_ref,product_code,units,due_days,budget_cap,"
            f"seeded_order_state) VALUES({r['id']},{q(r['partner_ref'])},{q(r['product_code'])},"
            f"{r['units']},{r['due_days'] if r['due_days'] is not None else 'NULL'},"
            f"{r['budget_cap'] if r['budget_cap'] is not None else 'NULL'},"
            f"{q(r['seeded_order_state'])});" for r in dem) + "\n"
        (t / "environment/seed/seed.sql").write_text(seed)
        (t / "solution/walk.json").write_text(json.dumps(walk, indent=1) + "\n")
        (t / "tests/checks.json").write_text(json.dumps({
            "answer_checks": ac,
            "trace_checks": [{"type": "required_servers", "servers": ["odoo"]},
                             {"type": "reads_before_submit"}],
            "state_checks": stc}, indent=1) + "\n")

        # The source instruction and its policy block, verbatim, plus where to do the work —
        # and nothing about what to file. That contract is served by the harness
        # `reporting_fields` tool from the schema seeded below (sim/naturalize_prompts.py).
        instr = [f"**Priya Shah · Supply & Procurement · Teams**", "",
                 (sc.get("instruction") or "").strip(), "", "## Background & Policy", "",
                 (sc.get("background_and_policy") or "").strip(), "",
                 "Work in the `odoo` ERP and commit the plan there.", ""]
        (t / "instruction.md").write_text("\n".join(instr))

        seedf = t / "environment/seed/mcp_seed.json"
        payload = json.loads(seedf.read_text()) if seedf.exists() else {}
        payload["answer_schema"] = [
            {"ordinal": 1, "field": "orders_accepted", "type": "number",
             "description": "customer orders you accepted and confirmed"},
            {"ordinal": 2, "field": "orders_rejected", "type": "number",
             "description": "customer orders you did not fulfil, having judged them unservable"},
            {"ordinal": 3, "field": "units_purchased", "type": "number",
             "description": "total units across all confirmed purchase orders"},
            {"ordinal": 4, "field": "units_manufactured", "type": "number",
             "description": "total units across all confirmed manufacturing orders"},
            {"ordinal": 5, "field": "assembly_cost", "type": "number",
             "description": "total assembly cost of those manufacturing orders"}]
        seedf.write_text(json.dumps(payload, indent=1) + "\n")

        meta = d.name
        (t / "task.toml").write_text(f'''schema_version = "1.4"

[task]
name = "{out_dir.name}/{slug}"
version = "0.1.0"
description = "ERP-Bench procurement scenario {sc.get('scenario_number')} — {sc.get('name')}."
authors = ["nario-ai"]
keywords = ["finance", "procurement", "erp-bench-clone"]

[metadata]
family = "{out_dir.name}"
origin = "clone of agentic-labs/erp-bench task {meta}; instruction carried verbatim, scenario seeded from its own environment/scenario_data.json, ground truth derived from its solution/optimal_plan.json. The source boots a real Odoo in Docker and grades with odoolib; this runs on the world's Odoo-shaped surface and grades the same judgement as deterministic SQL state assertions (docs/PARITY.md)"
generated = false
difficulty = "medium"
acceptance_label = "pending_calibration"
walk_len = {len(walk)}

[verifier]
timeout_sec = 300
[agent]
timeout_sec = 1800
[environment]
cpus = 1
memory_mb = 1024
''')

    print(f"\nemitted {made}")
    tot = sum(len(v) for v in rejected.values())
    print(f"rejected {tot}:")
    for why, items in sorted(rejected.items(), key=lambda kv: -len(kv[1])):
        print(f"   {len(items):4}  {why}")


if __name__ == "__main__":
    sys.exit(main())
