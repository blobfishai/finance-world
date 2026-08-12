#!/usr/bin/env bash
# Wave-4 acquisition — closes the named gaps in INDEX.md §6.
#
# Method is waves 1-3 verbatim: `git clone --depth 1 --single-branch`, sparse where the full
# tree is mostly ballast, then `rm -rf .git` (a clone here is source, not history).
#
# Every repo below closes a gap INDEX.md already NAMED as blocking a verification. This is not
# a speculative sweep; §6 is the backlog and these are its entries.
set -uo pipefail
REPOS="$(cd "$(dirname "$0")" && pwd)/repos"
cd "$REPOS" || exit 1

log() { printf '\n=== %s\n' "$*"; }

# ---------------------------------------------------------------------------
# 1. frappe/frappe — INDEX.md §6: "Cheapest single clone to close a named gap."
#    Unblocks: /api/resource default page size (20 was INFERRED from callers), the
#    [[doctype, field, op, value]] filter form, limit_start offset paging, the
#    _server_messages envelope, and the {data: doc} vs bare-doc wire disagreement
#    between the two ERPNext MCP wrappers.
# ---------------------------------------------------------------------------
if [ -d frappe ]; then log "frappe/frappe already present — skipping"; else
  log "cloning frappe/frappe (sparse: python package, no locale/public assets)"
  git clone --filter=blob:none --sparse --depth 1 --single-branch \
      https://github.com/frappe/frappe.git frappe 2>&1 | tail -2
  if [ -d frappe ]; then
    ( cd frappe && git sparse-checkout set --no-cone \
        '/*' '!/frappe/public' '!/frappe/locale' '!/.github' '!/cypress' \
        '!/frappe/tests' '!/esbuild' 2>&1 | tail -2 )
    rm -rf frappe/.git
  fi
fi

# ---------------------------------------------------------------------------
# 2. odoo/odoo — supplement the wave-2 sparse checkout with the paths §6 records
#    as absent. ADDITIVE: existing paths are untouched, so every research/*.md
#    citation into this tree stays valid.
#
#    Closes, per §6's own list:
#      odoo/service/model.py   -> the real execute_kw dispatcher (RPC convention)
#      odoo/osv/expression.py  -> the domain-operator list
#      odoo/fields.py          -> field types/attrs
#      addons/stock            -> goods receipt: the THIRD LEG of three-way match
#      addons/purchase_stock   -> PO <-> receipt linkage
# ---------------------------------------------------------------------------
#    PATH DRIFT, recorded: §6 names `odoo/fields.py` as absent. In Odoo 19 that file does not
#    exist at that path — the ORM was split into the `odoo/orm/` package (`orm/fields.py` plus
#    fields_{relational,textual,numeric,temporal,...}.py). Part of that "gap" was a stale path
#    assumption, not a missing checkout. We take `odoo/{orm,api,models,modules}`.
NEED_ODOO=0
for p in odoo/odoo/service/model.py odoo/odoo/osv/expression.py odoo/odoo/orm/fields.py \
         odoo/addons/stock odoo/addons/purchase_stock; do
  [ -e "$p" ] || NEED_ODOO=1
done
if [ "$NEED_ODOO" = "0" ]; then log "odoo supplement already present — skipping"; else
  log "fetching absent odoo paths into a staging clone"
  rm -rf .odoo-stage
  git clone --filter=blob:none --sparse --depth 1 --single-branch \
      https://github.com/odoo/odoo.git .odoo-stage 2>&1 | tail -2
  if [ -d .odoo-stage ]; then
    ( cd .odoo-stage && git sparse-checkout set --no-cone \
        '/odoo' '!/odoo/addons' '!/odoo/cli' '!/odoo/tests' \
        '/addons/stock' '/addons/purchase_stock' \
        '!/addons/stock/i18n' '!/addons/purchase_stock/i18n' '!/addons/stock/static' \
        2>&1 | tail -2 )
    log "merging staged paths into the existing odoo tree (additive)"
    for rel in odoo/service odoo/osv odoo/orm odoo/api odoo/models odoo/modules odoo/tools \
               addons/stock addons/purchase_stock; do
      src=".odoo-stage/$rel"; dst="odoo/$rel"
      if [ -e "$src" ] && [ ! -e "$dst" ]; then
        mkdir -p "$(dirname "$dst")" && cp -R "$src" "$dst" && echo "  + $rel"
      fi
    done
    rm -rf .odoo-stage
  fi
fi

log "wave-4 sizes"
for r in frappe odoo; do [ -d "$r" ] && du -sh "$r"; done
log "verifying no .git survived anywhere under repos/"
find . -name .git -maxdepth 3 2>/dev/null | head || true
echo "done."
