#!/usr/bin/env python3
"""Execute every LedgerBench-100 pack against positive and adversarial trajectories.

Per pack (14 executions, all against the pack's OWN contents — its gzipped world,
its runtime modules, its walk.json, its baked taskspec checks):

  oracle x2        replay solution/walk.json; reward must be 1; the two verifier
                   reports must be byte-identical (determinism)
  noop             pristine world, zero tool calls; must score 0
  shortcut         copied final answer without investigation or state; must score 0
  state_only       copied writes and answer without investigation; must score 0
  incomplete_read  one exact evidence read removed; must score 0
  write_before_read governed state transition moved before evidence; must score 0
  missing_readback exact post-write reads removed; must score 0
  unauthorized_write full walk plus an off-scope table mutation; must score 0
  wrong_value      every reported answer value corrupted; must score 0
  wrong_decision   case decision changed to an unsupported code; must score 0
  wrong_evidence   one persisted evidence reference changed; must score 0
  wrong_option     the alternative that needs approval beyond current authority is
                   recorded on the case, in the Controls note and in the answers;
                   must score 0
  rejected_mutation an otherwise-correct run contains a rejected state-changing
                    Dynamics request; strict pass must remain false

Zero false accepts across all negative controls is a release gate. Writes
reports/qualification.json (release + huggingface copies) and one normalized
oracle trajectory JSONL per task into huggingface/trajectories/.
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from exporter import remove_generated_bytecode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELEASE_NAME = "LedgerBench-100"
RELEASE_VERSION = "3.4.0"
CORRUPT_VALUE = "totally-wrong-answer-xyzzy"
DECISION_ACTION = "ContosoDecisionWorkItemDecide"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackWorld:
    """One pack's world runtime, loaded from the pack directory alone."""

    def __init__(self, pack: Path):
        self.pack = pack
        self.world_dir = pack / "environment" / "world"
        self.spec = json.loads((self.world_dir / "spec.json").read_text())
        self.walk = json.loads((pack / "solution" / "walk.json").read_text())
        self.realism = json.loads(
            (self.world_dir / "taskspec" / "realism.json").read_text()
        )
        self.lib_path = str(self.world_dir / "runtime" / "lib")
        sys.path.insert(0, self.lib_path)
        self.server_module = load_module(
            f"lgrsuite_srv_{pack.name}", self.world_dir / "server.py")
        self.servers = {
            name: load_module(
                f"lgrsuite_{pack.name}_{name}",
                self.world_dir / "runtime" / "servers" / f"{name}_server.py").S
            for name in self.spec["servers"]
        }

    def close(self) -> None:
        if self.lib_path in sys.path:
            sys.path.remove(self.lib_path)
        runtime_path = str(self.world_dir / "runtime")
        while runtime_path in sys.path:
            sys.path.remove(runtime_path)
        sys.modules.pop("framework", None)
        sys.modules.pop("vcode", None)
        remove_generated_bytecode(self.pack)

    def fresh_run(self, run: Path) -> None:
        import os

        run.mkdir(parents=True, exist_ok=True)
        with gzip.open(self.world_dir / "state" / "world.sqlite.gz", "rb") as fin, \
                open(run / "world.sqlite", "wb") as fout:
            shutil.copyfileobj(fin, fout)
        shutil.copyfile(self.world_dir / "state" / "initial_state.json",
                        run / "initial_state.json")
        (run / "trace.jsonl").write_text("")
        os.environ.update({
            "WORLD_DB": str(run / "world.sqlite"),
            "WORLD_NOW": self.spec["world_now"],
            "WORLD_ROLE": self.spec["world_role"],
            "TRACE_FILE": str(run / "trace.jsonl"),
        })

    def replay(self, steps: list[dict]) -> None:
        for step in steps:
            try:
                self.servers[step["server"]].call(step["tool"], step.get("args") or {})
            except Exception:  # noqa: BLE001 - the verifier decides, not the replay
                pass

    def verify(self, run: Path) -> dict[str, Any]:
        return self.server_module.build_report(
            self.world_dir / "taskspec", run, self.spec["task_id"])


# --- trajectory shapes ---------------------------------------------------------

def oracle_steps(world: PackWorld) -> list[dict]:
    return world.walk


def noop_steps(world: PackWorld) -> list[dict]:
    return []


def shortcut_steps(world: PackWorld) -> list[dict]:
    return [
        step for step in world.walk
        if step["server"] == "harness"
        and step["tool"] in {"reporting_fields", "submit_answer"}
    ]


def _is_decision_work_item(step: dict) -> bool:
    return (
        step["server"] == "erp"
        and step["tool"] == "api_invoke_action"
        and (step.get("args") or {}).get("action") == DECISION_ACTION
    )


def state_only_steps(world: PackWorld) -> list[dict]:
    decision_index = next(index for index, step in enumerate(world.walk) if _is_decision_work_item(step))
    return [world.walk[0], *world.walk[max(1, decision_index - 1):]]


def _contains_subset(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _contains_subset(actual[key], value)
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            _contains_subset(got, wanted) for got, wanted in zip(actual, expected)
        )
    return actual == expected


def _matches(step: dict, selector: dict) -> bool:
    return (
        step.get("server") == selector.get("server")
        and step.get("tool") == selector.get("tool")
        and _contains_subset(step.get("args") or {}, selector.get("args") or {})
    )


def incomplete_read_steps(world: PackWorld) -> list[dict]:
    required = world.realism["trace_contract"]["required_context_calls"]
    # Remove an evidence request that has exactly one satisfying occurrence in
    # the oracle.  A discovery call can legitimately recur in the source
    # workflow (for example ``list_drive_items``); deleting only its first
    # occurrence would still leave a complete investigation and therefore is
    # not a valid incomplete-read adversary.
    unique = [
        selector
        for selector in required
        if sum(_matches(step, selector) for step in world.walk) == 1
    ]
    if not unique:
        raise ValueError(f"{world.spec['task_id']} has no uniquely required evidence read")
    target = unique[len(unique) // 2]
    removed = False
    steps = []
    for step in world.walk:
        if not removed and _matches(step, target):
            removed = True
            continue
        steps.append(step)
    if not removed:
        raise ValueError(f"{world.spec['task_id']} incomplete-read target was not present")
    return steps


def write_before_read_steps(world: PackWorld) -> list[dict]:
    decision = next(step for step in world.walk if _is_decision_work_item(step))
    return [world.walk[0], decision, *[step for step in world.walk[1:] if step is not decision]]


def missing_readback_steps(world: PackWorld) -> list[dict]:
    contract = world.realism["trace_contract"]
    targets = [
        *contract["source_postwrite_readback_calls"],
        contract["state_readback_call"],
        contract["message_readback_call"],
    ]
    # Remove the last matching occurrence for each provider readback. Earlier
    # investigative reads remain intact, isolating the verification failure.
    remove_indexes: set[int] = set()
    for target in targets:
        matches = [
            index for index, step in enumerate(world.walk) if _matches(step, target)
        ]
        if not matches:
            raise ValueError(
                f"{world.spec['task_id']} readback target was not present: {target}"
            )
        remove_indexes.add(matches[-1])
    return [
        step for index, step in enumerate(world.walk) if index not in remove_indexes
    ]


def rejected_mutation_steps(world: PackWorld) -> list[dict]:
    """Probe the real Dynamics action with an invalid payload, then solve normally."""

    rejected = {
        "server": "erp",
        "tool": "api_invoke_action",
        "args": {"action": DECISION_ACTION, "parameters": {}},
    }
    return [rejected, *world.walk]


def wrong_value_steps(world: PackWorld) -> list[dict]:
    steps = []
    for step in world.walk:
        if step["server"] == "harness" and step["tool"] == "submit_answer":
            answers = (step.get("args") or {}).get("answers") or {}
            steps.append({"server": "harness", "tool": "submit_answer",
                          "args": {"answers": {k: CORRUPT_VALUE for k in answers}}})
        else:
            steps.append(step)
    return steps


def wrong_decision_steps(world: PackWorld) -> list[dict]:
    steps = json.loads(json.dumps(world.walk))
    for step in steps:
        if _is_decision_work_item(step):
            current = step["args"]["parameters"]["decision_code"]
            step["args"]["parameters"]["decision_code"] = (
                "NO_ACTION" if current.startswith("HOLD_") else "HOLD_FOR_EVIDENCE"
            )
            break
    return steps


def wrong_evidence_steps(world: PackWorld) -> list[dict]:
    steps = json.loads(json.dumps(world.walk))
    for step in steps:
        if _is_decision_work_item(step):
            refs = step["args"]["parameters"]["evidence_refs"]
            step["args"]["parameters"]["evidence_refs"] = [*refs[:-1], "UNRELATED-EVIDENCE-REF"]
            break
    return steps


def wrong_option_steps(world: PackWorld) -> list[dict]:
    """Execute the alternative the approval does not cover.

    The case rationale, the Controls note and the reported recommendation all
    name the option that requires approval beyond current authority; the exact
    state, message-content and answer checks must all reject it.
    """

    options = world.realism["decision_options"]
    selected = next(option for option in options if option.get("selected"))
    unauthorized = next(
        option for option in options
        if option.get("authority_status") == "ADDITIONAL_APPROVAL_REQUIRED"
    )
    steps = json.loads(json.dumps(world.walk))
    for step in steps:
        arguments = step.get("args") or {}
        if _is_decision_work_item(step):
            parameters = arguments["parameters"]
            parameters["rationale"] = parameters["rationale"].replace(selected["id"], unauthorized["id"])
        elif step["server"] == "email" and step["tool"] == "send_message":
            arguments["body"] = arguments["body"].replace(selected["id"], unauthorized["id"])
        elif step["server"] == "harness" and step["tool"] == "submit_answer":
            answers = arguments.get("answers") or {}
            if "recommended_option" in answers:
                answers["recommended_option"] = unauthorized["id"]
                answers["recommended_outcome_date"] = unauthorized["outcome"]
                answers["recommended_incremental_cost_usd"] = unauthorized["incremental_cost"]
    return steps


NEGATIVES: list[tuple[str, Callable[[PackWorld], list[dict]]]] = [
    ("noop", noop_steps),
    ("shortcut", shortcut_steps),
    ("state_only", state_only_steps),
    ("incomplete_read", incomplete_read_steps),
    ("write_before_read", write_before_read_steps),
    ("missing_readback", missing_readback_steps),
    ("wrong_value", wrong_value_steps),
    ("wrong_decision", wrong_decision_steps),
    ("wrong_evidence", wrong_evidence_steps),
    ("wrong_option", wrong_option_steps),
    ("rejected_mutation", rejected_mutation_steps),
]


def execute(world: PackWorld, steps: list[dict], *, off_task_write: bool = False,
            trace_destination: Path | None = None) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"{world.spec['task_id']}-") as temporary:
        run = Path(temporary) / "run"
        world.fresh_run(run)
        world.replay(steps)
        if off_task_write:
            import sqlite3

            cx = sqlite3.connect(run / "world.sqlite")
            cx.execute("INSERT OR REPLACE INTO meta(key, value) "
                       "VALUES('lgr_offtask_probe', 'written-off-task')")
            cx.commit()
            cx.close()
        report = world.verify(run)
        if trace_destination is not None:
            trace_destination.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for index, raw in enumerate(
                    (run / "trace.jsonl").read_text().splitlines()):
                record = json.loads(raw)
                record.pop("ts", None)
                lines.append(json.dumps({"step": index, **record},
                                        ensure_ascii=False, sort_keys=True))
            trace_destination.write_text("\n".join(lines) + "\n")
    return report


def run(release: Path) -> dict[str, Any]:
    tasks_root = release / "harbor" / "tasks"
    hf_root = release / "huggingface"
    task_dirs = sorted(p for p in tasks_root.iterdir() if p.is_dir())
    if len(task_dirs) != 100:
        raise ValueError(f"expected 100 task packs, found {len(task_dirs)}")

    task_results: list[dict[str, Any]] = []
    oracle_passes = 0
    determinism_matches = 0
    control_names = [name for name, _ in NEGATIVES] + ["unauthorized_write"]
    false_accepts = {name: 0 for name in control_names}
    failure_samples: dict[str, list[dict[str, Any]]] = {name: [] for name in control_names}

    for task_dir in task_dirs:
        world = PackWorld(task_dir)
        task_id = world.spec["task_id"]
        try:
            first = execute(world, oracle_steps(world),
                            trace_destination=hf_root / "trajectories" / f"{task_id}.jsonl")
            second = execute(world, oracle_steps(world))
            oracle_passes += int(first["passed"])
            deterministic = (
                json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True))
            determinism_matches += int(deterministic)
            negatives: dict[str, Any] = {}
            for name in control_names:
                if name == "unauthorized_write":
                    report = execute(world, oracle_steps(world), off_task_write=True)
                else:
                    shape = dict(NEGATIVES)[name]
                    report = execute(world, shape(world))
                false_accepts[name] += int(report["passed"])
                negatives[name] = {
                    "passed": report["passed"],
                    "reward": report["reward"],
                    "ledger_score": report["ledger_score"],
                    "failed_checks": report["failed_checks"],
                    "report_sha256": report["report_sha256"],
                }
                if not report["passed"] and len(failure_samples[name]) < 3:
                    failure_samples[name].append(
                        {"task_id": task_id,
                         "failed_checks": report["failed_checks"][:4]})
            task_results.append({
                "task_id": task_id,
                "oracle_passed": first["passed"],
                "oracle_tool_calls": first["n_tool_calls"],
                "oracle_servers_used": first["servers_used"],
                "oracle_report_sha256": first["report_sha256"],
                "oracle_ledger_score": first["ledger_score"],
                "second_oracle_report_sha256": second["report_sha256"],
                "deterministic_replay_match": deterministic,
                "negative_executions": negatives,
            })
            print(f"  {task_id}: oracle={'PASS' if first['passed'] else 'FAIL'} "
                  f"det={'ok' if deterministic else 'MISMATCH'} "
                  f"neg_rewards={[negatives[n]['reward'] for n in control_names]}",
                  flush=True)
        finally:
            world.close()

    executions = len(task_dirs) * (2 + len(control_names))
    report = {
        "schema_version": "ledgerbench.qualification.v2",
        "benchmark": RELEASE_NAME,
        "version": RELEASE_VERSION,
        "metric": "LedgerScore",
        "points_possible": 100,
        "task_count": len(task_dirs),
        "executions": executions,
        "oracle": {
            "executions": len(task_dirs),
            "passes": oracle_passes,
            "failures": len(task_dirs) - oracle_passes,
        },
        "determinism": {
            "replays": len(task_dirs),
            "exact_report_matches": determinism_matches,
            "mismatches": len(task_dirs) - determinism_matches,
        },
        "negative_controls": {
            name: {
                "executions": len(task_dirs),
                "false_accepts": count,
                "correct_rejections": len(task_dirs) - count,
            }
            for name, count in false_accepts.items()
        },
        "failure_samples": failure_samples,
        "release_passed": (
            oracle_passes == len(task_dirs)
            and determinism_matches == len(task_dirs)
            and not any(false_accepts.values())
        ),
        "task_results": task_results,
    }
    for target in (release / "reports" / "qualification.json",
                   hf_root / "reports" / "qualification.json"):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "release_passed": report["release_passed"],
        "executions": executions,
        "oracle": report["oracle"],
        "determinism": report["determinism"],
        "negative_controls": report["negative_controls"],
    }, indent=2, sort_keys=True))
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path,
                        default=ROOT / "dist" / "ledgerbench-100")
    return parser.parse_args()


if __name__ == "__main__":
    result = run(parse_args().release)
    raise SystemExit(0 if result["release_passed"] else 1)
