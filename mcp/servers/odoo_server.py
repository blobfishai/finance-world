#!/usr/bin/env python3
"""Odoo MCP server — procure-to-pay and make-or-buy, shaped after Odoo 19's ORM RPC.

This is the surface agentic-labs/erp-bench drives. Its 300 tasks each boot a real Odoo in
Docker and grade it with `odoolib` against the live server; that plumbing does not port, but
the surface does, because the tasks only ever touch a handful of models through the standard
`execute_kw` verbs.

Shaped from the checkout, not from docs (`research/external/repos/odoo`, wave 4):
  * `odoo/service/model.py` — the real `execute_kw` dispatcher, so the verb set here is
    search_read / create / write / fields_get rather than something invented.
  * `odoo/osv/expression.py` — the domain grammar: a list of `[field, operator, value]` leaves
    with implicit AND, and the operator vocabulary below is its documented set.

Deliberate fidelity choices, each of which a task depends on:
  * `min_qty`/`max_qty` on a vendor offer are HORIZON-WIDE totals, not per-line minimums —
    consolidating an offer into one PO is a rule several patterns test.
  * `comment` ("Internal Notes" in the UI) is a real field and is sometimes the ONLY place a
    binding constraint lives, so it is returned like any other field and never summarised away.
  * A draft order is not a commitment: `state` starts `draft` and only `action_confirm` moves
    it to `sale`/`purchase`. Tasks grade confirmed orders.

All state is SQLite (WORLD_DB). SIMULATION ONLY.
"""
import sys, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from framework import Server, PAGE

S = Server("odoo", "Odoo 19 ERP — procurement, sales and manufacturing. SIMULATION ONLY.")

# model -> (table, primary key, writable?)
MODELS = {
    "res.partner":          ("erpb_partners", "ref", False),
    "product.product":      ("erpb_products", "code", False),
    "product.supplierinfo": ("erpb_vendor_offers", "id", False),
    "mrp.bom":              ("erpb_boms", "id", False),
    "mrp.bom.line":         ("erpb_bom_components", "bom_id", False),
    "mrp.workcenter":       ("erpb_workcenters", "code", False),
    "stock.quant":          ("erpb_stock", "product_code", False),
    "sale.order":           ("erpb_sale_orders", "name", True),
    "sale.order.line":      ("erpb_sale_order_lines", "id", True),
    "purchase.order":       ("erpb_purchase_orders", "name", True),
    "purchase.order.line":  ("erpb_purchase_order_lines", "id", True),
    "mrp.production":       ("erpb_manufacturing_orders", "name", True),
}
SEQ = {"sale.order": ("S%05d", "erpb_sale_orders"),
       "purchase.order": ("P%05d", "erpb_purchase_orders"),
       "mrp.production": ("MO%05d", "erpb_manufacturing_orders")}

OPS = {"=": "=", "!=": "!=", ">": ">", ">=": ">=", "<": "<", "<=": "<=",
       "like": "LIKE", "ilike": "LIKE", "in": "IN", "not in": "NOT IN"}


def _cols(cx, table):
    return [r[1] for r in cx.execute(f"PRAGMA table_info({table})")]


def _where(domain, cols):
    """Odoo domain -> SQL. Implicit AND between leaves (expression.py's default)."""
    if not domain: return "", []
    sql, args = [], []
    for leaf in domain:
        if not isinstance(leaf, (list, tuple)) or len(leaf) != 3:
            raise ValueError(f"malformed domain leaf {leaf!r}; expected [field, operator, value]")
        f, op, v = leaf
        if f not in cols:
            raise ValueError(f"unknown field {f!r}; known: {', '.join(sorted(cols))}")
        if op not in OPS:
            raise ValueError(f"unsupported operator {op!r}; supported: {', '.join(sorted(OPS))}")
        if op in ("in", "not in"):
            vals = list(v) if isinstance(v, (list, tuple)) else [v]
            sql.append(f"{f} {OPS[op]} ({','.join('?' * len(vals))})"); args += vals
        elif op in ("like", "ilike"):
            sql.append(f"{f} LIKE ?"); args.append(f"%{v}%")
        else:
            sql.append(f"{f} {OPS[op]} ?"); args.append(v)
    return " WHERE " + " AND ".join(sql), args


def _model(model):
    if model not in MODELS:
        raise ValueError(f"unknown model {model!r}; served: {', '.join(sorted(MODELS))}")
    return MODELS[model]


@S.tool("fields_get", "List the fields of a model, with type. Discovery step before search_read.",
        {"model": {"type": "string"}}, ["model"])
def fields_get(model):
    table, pk, writable = _model(model)
    with S.db() as cx:
        info = [{"name": r[1], "type": r[2] or "text"} for r in cx.execute(f"PRAGMA table_info({table})")]
    return {"model": model, "primary_key": pk, "writable": writable, "fields": info}


@S.tool("search_read",
        "Search and read records. `domain` is a list of [field, operator, value] leaves "
        "combined with AND, e.g. [[\"product_code\",\"=\",\"P123\"],[\"price\",\"<\",100]].",
        {"model": {"type": "string"},
         "domain": {"type": "array", "description": "list of [field, operator, value]"},
         "fields": {"type": "array", "description": "field names; omit for all"},
         "page": {"type": "integer"}},
        ["model"])
def search_read(model, domain=None, fields=None, page=1):
    table, pk, _w = _model(model)
    with S.db() as cx:
        cols = _cols(cx, table)
        sel = "*"
        if fields:
            bad = [f for f in fields if f not in cols]
            if bad: raise ValueError(f"unknown field(s) {bad}; known: {', '.join(sorted(cols))}")
            sel = ", ".join(fields)
        w, args = _where(domain, cols)
        return S.rows(cx, f"SELECT {sel} FROM {table}{w}", args, page)


@S.tool("create", "Create a record. Returns its name/id. Orders are created in state 'draft' — "
                  "confirm them with action_confirm.",
        {"model": {"type": "string"}, "values": {"type": "object"}},
        ["model", "values"])
def create(model, values):
    table, pk, writable = _model(model)
    if not writable:
        raise ValueError(f"{model} is master data in this world and is read-only; "
                         f"writable models: {', '.join(m for m, v in MODELS.items() if v[2])}")
    vals = dict(values or {})
    with S.db() as cx:
        cols = _cols(cx, table)
        bad = [k for k in vals if k not in cols]
        if bad: raise ValueError(f"unknown field(s) {bad} on {model}; known: {', '.join(sorted(cols))}")
        if model in SEQ and not vals.get("name"):
            fmt, tbl = SEQ[model]
            n = cx.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0] + 1
            vals["name"] = fmt % n
        if "state" in cols and not vals.get("state"):
            vals["state"] = "draft"
        keys = list(vals)
        cx.execute(f"INSERT INTO {table} ({','.join(keys)}) VALUES ({','.join('?' * len(keys))})",
                   [vals[k] for k in keys])
        cx.commit()
        return {"model": model, "created": vals.get("name") or cx.execute(
            f"SELECT last_insert_rowid()").fetchone()[0], "values": vals}


@S.tool("write", "Update records matching a domain.",
        {"model": {"type": "string"}, "domain": {"type": "array"}, "values": {"type": "object"}},
        ["model", "domain", "values"])
def write(model, domain, values):
    table, pk, writable = _model(model)
    if not writable:
        raise ValueError(f"{model} is master data in this world and is read-only")
    vals = dict(values or {})
    with S.db() as cx:
        cols = _cols(cx, table)
        bad = [k for k in vals if k not in cols]
        if bad: raise ValueError(f"unknown field(s) {bad} on {model}")
        w, args = _where(domain, cols)
        if not w: raise ValueError("refusing to write with an empty domain")
        sets = ", ".join(f"{k}=?" for k in vals)
        cur = cx.execute(f"UPDATE {table} SET {sets}{w}", list(vals.values()) + args)
        cx.commit()
        return {"model": model, "updated": cur.rowcount}


@S.tool("action_confirm", "Confirm draft orders by name — sale.order -> 'sale', "
                          "purchase.order -> 'purchase', mrp.production -> 'confirmed'. "
                          "A draft order is not a commitment and is not graded as one.",
        {"model": {"type": "string"}, "names": {"type": "array"}},
        ["model", "names"])
def action_confirm(model, names):
    table, pk, writable = _model(model)
    if not writable or model not in SEQ:
        raise ValueError(f"{model} has no confirm action")
    target = {"sale.order": "sale", "purchase.order": "purchase",
              "mrp.production": "confirmed"}[model]
    names = list(names or [])
    if not names: raise ValueError("names is required")
    with S.db() as cx:
        rows = cx.execute(f"SELECT name, state FROM {table} WHERE name IN "
                          f"({','.join('?' * len(names))})", names).fetchall()
        found = {r["name"] for r in rows}
        missing = [n for n in names if n not in found]
        if missing: raise ValueError(f"no such {model}: {missing}")
        cx.execute(f"UPDATE {table} SET state=? WHERE name IN "
                   f"({','.join('?' * len(names))})", [target] + names)
        cx.commit()
    return {"model": model, "confirmed": names, "state": target}


if __name__ == "__main__":
    S.run()
