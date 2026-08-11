#!/usr/bin/env bash
# The ONLY supported way to build world/build/core.sqlite.
#
# load_core.py DROPS AND RECREATES the database, so running it alone silently discards the
# cash and demo layers and leaves a world whose open balances are ~2.6x the ones every task
# ground truth was computed against. sim/validate.py's S11 freshness check catches it, but
# only after the fact — hence this entrypoint. (docs/AUDIT.md A6.)
#
# Order is load-bearing: load_cash.py states "run after load_core.py and before
# load_demo.py"; the demo layer's balances build on the settlements the cash layer creates.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/5 core   (schema + FinanceBenchmark raw journals)"
python3 world/etl/load_core.py
echo "==> 2/5 cash   (payments, settlements, partials, discounts, disputes)"
python3 world/etl/load_cash.py
echo "==> 3/5 demo   (Contoso demo entities the benchmark's questions name)"
python3 world/etl/load_demo.py
echo "==> 4/5 activity (dunning, worklists, orders, POs/receipts, discounts — docs/AUDIT.md A11)"
python3 world/etl/load_activity.py
echo "==> 5/5 filings (frozen real EDGAR facts; re-fetch with world/etl/fetch_filings.py)"
python3 world/etl/fetch_filings.py --load

echo
# Full validation is O(tasks) and the task tree is now ~1.5k, so a build no longer waits on
# it by default. The gate has not moved — it is the same check, run explicitly:
#     python3 sim/validate.py            (everything, before shipping)
#     python3 sim/validate.py --sample 60  (a spot check)
echo "==> build complete. Verify before trusting any score:"
echo "      python3 sim/validate.py           # full gate"
echo "      python3 sim/refresh_gt.py         # re-derive gt_sql truths after a ledger change"
