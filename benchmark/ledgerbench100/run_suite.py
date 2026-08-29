#!/usr/bin/env python3
"""Execute every LedgerBench-100 pack against positive and adversarial trajectories.

Per pack (6 executions, all against the pack's OWN contents — its gzipped world,
its runtime modules, its walk.json, its baked taskspec checks):

  oracle x2        replay solution/walk.json; reward must be 1; the two verifier
                   reports must be byte-identical (determinism)
  noop             pristine world, zero tool calls; must score 0
  no_submit        the walk minus every harness.submit_answer step; must score 0
  wrong_submit     the walk with every submitted value corrupted; must score 0
  off_task_write   the full walk plus one write to an off-task table (meta);
                   must score 0 via the writes_only veto

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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELEASE_NAME = "LedgerBench-100"
RELEASE_VERSION = "2.0.0"
CORRUPT_VALUE = "totally-wrong-answer-xyzzy"


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


def no_submit_steps(world: PackWorld) -> list[dict]:
    return [s for s in world.walk
            if not (s["server"] == "harness" and s["tool"] == "submit_answer")]


def wrong_submit_steps(world: PackWorld) -> list[dict]:
    steps = []
    for step in world.walk:
        if step["server"] == "harness" and step["tool"] == "submit_answer":
            answers = (step.get("args") or {}).get("answers") or {}
            steps.append({"server": "harness", "tool": "submit_answer",
                          "args": {"answers": {k: CORRUPT_VALUE for k in answers}}})
        else:
            steps.append(step)
    return steps


NEGATIVES: list[tuple[str, Callable[[PackWorld], list[dict]]]] = [
    ("noop", noop_steps),
    ("no_submit", no_submit_steps),
    ("wrong_submit", wrong_submit_steps),
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
    control_names = [name for name, _ in NEGATIVES] + ["off_task_write"]
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
                if name == "off_task_write":
                    report = execute(world, oracle_steps(world), off_task_write=True)
                else:
                    shape = dict(NEGATIVES)[name]
                    report = execute(world, shape(world))
                false_accepts[name] += int(report["passed"])
                negatives[name] = {
                    "passed": report["passed"],
                    "reward": report["reward"],
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
        "schema_version": "1.0",
        "benchmark": RELEASE_NAME,
        "version": RELEASE_VERSION,
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
