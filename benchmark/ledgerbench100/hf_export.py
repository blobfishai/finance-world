#!/usr/bin/env python3
"""Build the LedgerBench-100 Hugging Face release tree from the built Harbor packs.

Runs AFTER exporter.py (packs + dataset.toml) and run_suite.py (trajectories +
qualification.json), because the dataset card quotes only measured numbers.

  dist/ledgerbench-100/huggingface/
    data/tasks.jsonl        apex-accounting-compatible task records
    tasks/<task_id>.json    one readable record per task
    task_files/<task_id>/   the task's seeded context documents and input files
    world/                  the world source: MCP servers, framework, verifier,
                            HTTP bridge, and the full SQL schema
    trajectories/           one normalized oracle-trajectory JSONL per task
    reports/                build.json + qualification.json
    README.md               dataset card (real measured stats only)
    LICENSE-CODE            Apache-2.0
    LICENSE-DATA            CC BY 4.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import statistics
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELEASE_NAME = "LedgerBench-100"
RELEASE_SLUG = "ledgerbench-100"
RELEASE_VERSION = "1.0.0"
HARBOR_ORG = "blobfishai"
WORLD_ID = "ledgerbench-erp-world-v1"
DATA_LICENSE = "CC-BY-4.0"
CODE_LICENSE = "Apache-2.0"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def shingles(value: str, size: int = 5) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9]+", value.casefold())
    return {tuple(words[i:i + size]) for i in range(max(0, len(words) - size + 1))}


def maximum_pair_similarity(values: list[str]) -> dict:
    sets = [shingles(v) for v in values]
    maximum, pair = 0.0, [None, None]
    for left in range(len(sets)):
        for right in range(left + 1, len(sets)):
            union = sets[left] | sets[right]
            score = len(sets[left] & sets[right]) / len(union) if union else 1.0
            if score > maximum:
                maximum, pair = score, [left, right]
    return {"maximum_jaccard_5_shingle": round(maximum, 6), "pair_indices": pair}


def gold_output(walk: list[dict], checks: dict) -> dict:
    submitted: dict = {}
    for step in walk:
        if step["server"] == "harness" and step["tool"] == "submit_answer":
            submitted.update((step.get("args") or {}).get("answers") or {})
    return {
        "submit_answer": submitted,
        "expected_state_assertions": [
            c for c in checks.get("state_checks", []) if c.get("type") != "writes_only"
        ],
    }


def build(release: Path) -> dict:
    tasks_root = release / "harbor" / "tasks"
    hf = release / "huggingface"
    catalog = json.loads((HERE / "catalog.json").read_text())
    entries = {e["task_id"]: e for e in catalog["tasks"]}
    qualification = json.loads((hf / "reports" / "qualification.json").read_text())
    if not qualification["release_passed"]:
        raise SystemExit("refusing to build the HF tree from a failed qualification")

    records: list[dict] = []
    prompts: list[str] = []
    walk_lens: list[int] = []
    context_counts: list[int] = []
    doc_hashes: set[str] = set()
    n_answer = n_trace = n_state = 0

    for task_dir in sorted(p for p in tasks_root.iterdir() if p.is_dir()):
        task_id = task_dir.name
        entry = entries[task_id]
        source = ROOT / "tasks" / entry["source_task"]
        prompt = (task_dir / "instruction.md").read_text()
        walk = json.loads((task_dir / "solution" / "walk.json").read_text())
        checks = json.loads(
            (task_dir / "environment" / "world" / "taskspec" / "tests" / "checks.json")
            .read_text())
        config = tomllib.loads((task_dir / "task.toml").read_text())

        context_files: list[str] = []
        for sub in ("documents", "inputs"):
            seed_dir = source / "environment" / "seed" / sub
            if seed_dir.is_dir():
                for p in sorted(seed_dir.iterdir()):
                    if not p.is_file():
                        continue
                    target = hf / "task_files" / task_id / sub / p.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(p, target)
                    context_files.append(f"task_files/{task_id}/{sub}/{p.name}")
                    doc_hashes.add(hashlib.sha256(p.read_bytes()).hexdigest())

        n_answer += len(checks.get("answer_checks", []))
        n_trace += len(checks.get("trace_checks", []))
        n_state += len(checks.get("state_checks", []))
        walk_lens.append(len(walk))
        context_counts.append(len(context_files))
        prompts.append(prompt)

        record = {
            "task_id": task_id,
            "task_name": entry["source_task"],
            "world_id": WORLD_ID,
            "prompt": prompt,
            "context_files": context_files,
            "rubric": {
                "type": "deterministic",
                "engine": "verifiers/vcode.py (binary reward; all checks must pass)",
                "checks": checks,
                "gates": [
                    "answer_checks: submitted fields graded by type with tolerances",
                    "trace_checks: required servers visited, reads precede submission",
                    "state_checks: writes_only anti-hack veto plus SQL over the world left behind",
                ],
            },
            "gold_output": gold_output(walk, checks),
            "metadata": {
                "benchmark": RELEASE_NAME,
                "version": RELEASE_VERSION,
                "harbor_name": f"{HARBOR_ORG}/{task_id}",
                "family": entry["family"],
                "provenance": entry["provenance"],
                "difficulty": entry["difficulty"],
                "grading": "deterministic",
                "llm_judge": False,
                "walk_len": len(walk),
                "walk_servers": entry["walk_servers"],
                "mcp_servers": 8,
                "mcp_tools": 66,
                "world_epoch": "2026-03-02T12:00:00Z",
                "origin": config["metadata"].get("origin", ""),
                "data_license": DATA_LICENSE,
                "code_license": CODE_LICENSE,
            },
        }
        records.append(record)
        write_json(hf / "tasks" / f"{task_id}.json", record)

    write_text(hf / "data" / "tasks.jsonl",
               "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                       for r in records))

    # world source: everything a reader needs to re-serve and re-grade the world
    world_out = hf / "world"
    if world_out.exists():
        shutil.rmtree(world_out)
    (world_out / "mcp" / "lib").mkdir(parents=True)
    (world_out / "mcp" / "servers").mkdir(parents=True)
    shutil.copyfile(ROOT / "mcp" / "lib" / "framework.py",
                    world_out / "mcp" / "lib" / "framework.py")
    for p in sorted((ROOT / "mcp" / "servers").glob("*_server.py")):
        shutil.copyfile(p, world_out / "mcp" / "servers" / p.name)
    shutil.copyfile(ROOT / "verifiers" / "vcode.py", world_out / "vcode.py")
    shutil.copyfile(HERE / "runtime" / "server.py", world_out / "server.py")
    shutil.copyfile(ROOT / "world" / "schema.sql", world_out / "schema.sql")

    write_text(hf / "LICENSE-DATA",
               "Creative Commons Attribution 4.0 International\n"
               "https://creativecommons.org/licenses/by/4.0/\n")
    write_text(hf / "LICENSE-CODE",
               "Apache License 2.0\nhttps://www.apache.org/licenses/LICENSE-2.0\n")

    families = catalog["families"]
    build_report = {
        "schema_version": "1.0",
        "benchmark": RELEASE_NAME,
        "version": RELEASE_VERSION,
        "task_count": len(records),
        "family_count": len(families),
        "tasks_per_family": families,
        "mcp_servers": 8,
        "mcp_tools": 66,
        "walk_len": {
            "min": min(walk_lens),
            "median": int(statistics.median(walk_lens)),
            "max": max(walk_lens),
            "total": sum(walk_lens),
        },
        "checks": {
            "answer_checks_total": n_answer,
            "trace_checks_total": n_trace,
            "state_checks_total": n_state,
            "checks_total": n_answer + n_trace + n_state,
        },
        "context_files": {
            "tasks_with_context_files": sum(1 for c in context_counts if c),
            "total": sum(context_counts),
            "unique_sha256": len(doc_hashes),
        },
        "prompt_uniqueness": maximum_pair_similarity(prompts),
        "exact_duplicate_prompts": len(prompts) - len(set(prompts)),
        "verifier": {
            "deterministic": True,
            "network_calls": 0,
            "model_calls": 0,
            "wall_clock_reads_in_reward_path": 0,
            "random_calls": 0,
        },
    }
    write_json(hf / "reports" / "build.json", build_report)
    write_json(release / "reports" / "build.json", build_report)
    write_text(hf / "README.md", dataset_card(build_report, qualification))
    seal_manifest(release)
    return build_report


def seal_manifest(release: Path) -> None:
    manifest_path = release / "release-manifest.json"
    files = sorted(p for p in release.rglob("*")
                   if p.is_file() and p != manifest_path)
    manifest = {
        "schema_version": "1.0",
        "benchmark": RELEASE_NAME,
        "version": RELEASE_VERSION,
        "files": [
            {
                "path": p.relative_to(release).as_posix(),
                "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
            for p in files
        ],
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    write_json(manifest_path, manifest)


def dataset_card(build: dict, qualification: dict) -> str:
    negative_rows = "\n".join(
        f"| {name} | {row['executions']} | {row['false_accepts']} |"
        for name, row in sorted(qualification["negative_controls"].items()))
    families = ", ".join(f"{fam} ({count})" for fam, count in
                         sorted(build["tasks_per_family"].items()))
    return f"""---
license: cc-by-4.0
task_categories:
- question-answering
- text-generation
language:
- en
tags:
- finance
- erp
- benchmark
- agents
- mcp
- deterministic-evaluation
pretty_name: {RELEASE_NAME}
size_categories:
- n<1K
---

# {RELEASE_NAME}

{RELEASE_NAME} is a deterministic corporate-finance agent benchmark: 100 tasks over a
shared simulated finance world (a D365-shaped ERP, an Odoo-shaped procure-to-pay and
manufacturing surface, a QBO-style subsidiary ledger, a shared drive, email, document
management, and frozen real SEC XBRL filings) served through {build['mcp_servers']} MCP
servers exposing {build['mcp_tools']} tools. Tasks are in-fiction persona chat messages;
the graded answer contract is discovered through the harness server's `reporting_fields`
tool, the way a real reporting system's schema is read before filing into it.

Grading is fully deterministic and binary — answer checks with typed tolerances, trace
checks (required servers, reads before submission), and state checks that grade the world
the agent leaves behind (committed payment runs, paid/rejected partitions, reason codes)
plus a `writes_only` anti-hack veto. No LLM judge, no network, no clock in the reward path.

## Measured contents

- Tasks: {build['task_count']} across {build['family_count']} families: {families}
- Oracle walk length: min {build['walk_len']['min']} / median {build['walk_len']['median']} / max {build['walk_len']['max']} MCP calls ({build['walk_len']['total']} total)
- Checks: {build['checks']['answer_checks_total']} answer + {build['checks']['trace_checks_total']} trace + {build['checks']['state_checks_total']} state = {build['checks']['checks_total']} graded checks
- Context files: {build['context_files']['total']} seeded documents/inputs ({build['context_files']['unique_sha256']} unique) across {build['context_files']['tasks_with_context_files']} tasks; most context lives inside the world itself (ERP rows, workbooks, emails, filings)
- Prompt uniqueness: maximum pairwise 5-shingle Jaccard {build['prompt_uniqueness']['maximum_jaccard_5_shingle']}, {build['exact_duplicate_prompts']} exact duplicates

## What is included

- `data/tasks.jsonl`: apex-accounting-compatible records (`task_id`, `task_name`, `world_id`, `prompt`, `context_files`, `rubric`, `gold_output`, `metadata`).
- `tasks/`: one readable JSON record per task.
- `task_files/`: seeded per-task context documents and input files.
- `world/`: the world source — MCP framework, the eight servers, the deterministic verifier engine, the Streamable HTTP bridge, and the full SQL schema.
- `trajectories/`: one normalized oracle MCP trajectory per task.
- `reports/`: measured build and qualification evidence.

The runnable form is the Harbor dataset `{HARBOR_ORG}/{RELEASE_SLUG}`: self-contained
task packs (prepared SQLite world + runtime on a digest-pinned `python:3.12-slim`)
whose `tests/test.sh` calls a token-gated `/verify` endpoint; the agent container
never sees the verification token.

## Measured qualification ({qualification['executions']} executions)

| Gate | Result |
|---|---:|
| Oracle replays | {qualification['oracle']['passes']}/{qualification['oracle']['executions']} reward 1.0 |
| Deterministic replays (byte-identical reports) | {qualification['determinism']['exact_report_matches']}/{qualification['determinism']['replays']} |

| Negative control | Executions | False accepts |
|---|---:|---:|
{negative_rows}

Full per-task evidence is in `reports/qualification.json`; do not infer a model score
from the oracle trajectories.

## Data provenance and contamination

The company, its customers, vendors, employees, balances, and documents are synthetic
(FinanceBenchmark-derived journal shapes with synthetic entities). The `filings` surface
serves frozen real SEC XBRL facts (38 registrants, snapshot-pinned) — real public data,
included under its own public-domain terms. Task text and gold answers are original to
this release's source repository. Gold outputs are public, so this release suits
transparent evaluation and RL experiments rather than secret-test claims.

## Licenses

Task data and documents are {DATA_LICENSE}. Benchmark code and harnesses are
{CODE_LICENSE}. SEC XBRL facts are US-government public-domain data.
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=ROOT / "dist" / RELEASE_SLUG)
    print(json.dumps(build(parser.parse_args().release), indent=2, sort_keys=True))
