# traces/

Real agent traces, one JSON per trial: `traces/<model|oracle>/<family>/<slug>/trial-N.<pass|fail>.json`.

Failures are first-class — kept forever, named `.fail.json` so they're scannable. Each record:
task, model, trial, reward, failed check names, servers used, full tool-call trace (args
truncated at 300 chars), reference walk length vs actual calls, turn budget vs turns used,
duration, cost, and the agent's final message excerpt.

Produced by `sim/run_task.py` / `sim/run_batch.py`. Consumed by `sim/build_reports.py`
(per-model failure reports) and by escalation decisions (diff passing vs failing call paths
of flaky tasks to name the failure mode).
