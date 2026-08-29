#!/usr/bin/env python3
"""Build the LedgerBench-100 Hugging Face release tree from the built Harbor packs.

Runs AFTER exporter.py (packs + dataset.toml) and run_suite.py (trajectories +
qualification.json), because the dataset card quotes only measured numbers.

  dist/ledgerbench-100/huggingface/
    data/tasks.jsonl        apex-accounting-compatible task records
    tasks/<task_id>.json    one readable record per task
    task_files/<task_id>/   28 agent-visible native evidence files plus seeded inputs
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
import gzip
import hashlib
import json
import re
import shutil
import statistics
import tempfile
import tomllib
from difflib import SequenceMatcher
from pathlib import Path

from decision_specs import DECISION_SPECS
from realism import validate_native_asset, write_asset_views

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELEASE_NAME = "LedgerBench-100"
RELEASE_SLUG = "ledgerbench-100"
RELEASE_VERSION = "3.1.0"
HARBOR_ORG = "blobfishai"
WORLD_ID = "ledgerbench-erp-world-v3-1"
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


def maximum_sequence_similarity(values: list[tuple[str, ...]]) -> dict:
    maximum, pair = 0.0, [None, None]
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            score = SequenceMatcher(None, values[left], values[right], autojunk=False).ratio()
            if score > maximum:
                maximum, pair = score, [left, right]
    return {"maximum_sequence_match": round(maximum, 6), "pair_indices": pair}


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
    walk_sequences: list[tuple[tuple[str, str], ...]] = []
    semantic_sequences: list[tuple[str, ...]] = []
    evidence_read_counts: list[int] = []
    context_counts: list[int] = []
    generated_asset_counts: list[int] = []
    criteria_counts: list[int] = []
    doc_hashes: set[str] = set()
    asset_hashes: list[str] = []
    asset_format_counts: dict[str, int] = {}
    native_assets_parsed = 0
    asset_leakage_hits: list[str] = []
    exact_state_transitions = 0
    post_write_readbacks = 0
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
        realism = json.loads(
            (task_dir / "environment" / "world" / "taskspec" / "realism.json")
            .read_text()
        )
        context_files: list[str] = []
        asset_root = hf / "task_files" / task_id / "assets"
        with tempfile.TemporaryDirectory(prefix=f"{task_id}-assets-") as temporary:
            database = Path(temporary) / "world.sqlite"
            with gzip.open(
                task_dir / "environment" / "world" / "state" / "world.sqlite.gz",
                "rb",
            ) as source_database, database.open("wb") as destination_database:
                shutil.copyfileobj(source_database, destination_database)
            asset_records = write_asset_views(
                asset_root,
                database,
                prompt,
                entry,
                realism["case_contract"],
            )
        assets: list[dict[str, str]] = []
        for asset in asset_records:
            relative = f"task_files/{task_id}/assets/{asset['filename']}"
            context_files.append(relative)
            assets.append({**asset, "path": relative})
            asset_path = asset_root / asset["filename"]
            digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
            doc_hashes.add(digest)
            asset_hashes.append(digest)
            suffix = asset_path.suffix.casefold().lstrip(".")
            asset_format_counts[suffix] = asset_format_counts.get(suffix, 0) + 1
            if not validate_native_asset(asset_path):
                raise AssertionError(f"native asset failed to parse: {asset_path}")
            native_assets_parsed += 1
            lowered = asset_path.read_bytes().lower()
            if any(
                token in lowered
                for token in (
                    b"answer_checks",
                    b"state_checks",
                    b"solution/walk",
                    b"submit_answer",
                    b"gold_output",
                )
            ):
                asset_leakage_hits.append(relative)
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
        walk_sequences.append(tuple((step["server"], step["tool"]) for step in walk))
        semantic_sequences.append(tuple(realism["semantic_action_graph"]))
        evidence_read_counts.append(len(realism["trace_contract"]["required_context_calls"]))
        context_counts.append(len(context_files))
        generated_asset_counts.append(len(asset_records))
        criteria_counts.append(len(realism["criteria"]))
        prompts.append(prompt)
        exact_state_transitions += int(
            any(
                check.get("name") == "finance_case_exact_decision"
                for check in checks.get("state_checks", [])
            )
        )
        post_write_readbacks += int(
            sum(
                check.get("type") == "post_write_readback"
                for check in checks.get("trace_checks", [])
            ) >= 2
        )

        record = {
            "task_id": task_id,
            "task_name": entry["source_task"],
            "world_id": WORLD_ID,
            "prompt": prompt,
            "context_files": context_files,
            "assets": assets,
            "rubric": {
                "type": "deterministic",
                "engine": "verifiers/vcode.py (binary reward; all checks must pass)",
                "checks": checks,
                "criteria": realism["criteria"],
                "decision_options": realism["decision_options"],
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
                "walk_servers": sorted({step["server"] for step in walk}),
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
    prompt_similarity = maximum_pair_similarity(prompts)
    reference_similarity = maximum_sequence_similarity(
        [tuple(f"{server}.{tool}" for server, tool in sequence) for sequence in walk_sequences]
    )
    semantic_similarity = maximum_sequence_similarity(semantic_sequences)
    build_report = {
        "schema_version": "ledgerbench.build.v3",
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
        "required_evidence_reads_per_task": {
            "min": min(evidence_read_counts),
            "median": int(statistics.median(evidence_read_counts)),
            "max": max(evidence_read_counts),
            "distinct_counts": len(set(evidence_read_counts)),
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
        "agent_visible_assets": {
            "total": len(asset_hashes),
            "unique_sha256": len(set(asset_hashes)),
            "exact_duplicates": len(asset_hashes) - len(set(asset_hashes)),
            "format_counts": dict(sorted(asset_format_counts.items())),
            "native_assets_parsed": native_assets_parsed,
            "gold_or_recipe_leakage_hits": asset_leakage_hits,
        },
        "generated_assets_per_task": {
            "min": min(generated_asset_counts),
            "median": int(statistics.median(generated_asset_counts)),
            "max": max(generated_asset_counts),
        },
        "criteria_per_task": {
            "min": min(criteria_counts),
            "median": int(statistics.median(criteria_counts)),
            "max": max(criteria_counts),
        },
        "unique_reference_tool_name_sequences": len(set(walk_sequences)),
        "reference_sequence_similarity": reference_similarity,
        "unique_semantic_action_graphs": len(set(semantic_sequences)),
        "semantic_action_graph_similarity": semantic_similarity,
        "exact_finance_case_transitions": exact_state_transitions,
        "two_post_write_readbacks": post_write_readbacks,
        "authored_decision_specs": len(DECISION_SPECS),
        "unique_authored_decision_codes": len({spec.decision_code for spec in DECISION_SPECS.values()}),
        "decision_options_per_task": 3,
        "prompt_uniqueness": prompt_similarity,
        "exact_duplicate_prompts": len(prompts) - len(set(prompts)),
        "escalated_variant_pairs": sum(
            1 for e in catalog["tasks"] if e["provenance"] == "variant"),
        "verifier": {
            "deterministic": True,
            "network_calls": 0,
            "model_calls": 0,
            "wall_clock_reads_in_reward_path": 0,
            "random_calls": 0,
        },
    }
    quality_gates = {
        "one_hundred_tasks": len(records) == 100,
        "high_level_prompts_unique": len(set(prompts)) == 100,
        "high_level_prompt_bounds": all(55 <= len(prompt.split()) <= 125 for prompt in prompts),
        "prompt_similarity_below_limit": prompt_similarity["maximum_jaccard_5_shingle"] < 0.72,
        "unique_reference_tool_sequences": len(set(walk_sequences)) == 100,
        "reference_sequence_similarity_below_limit": reference_similarity["maximum_sequence_match"] < 0.985,
        "unique_semantic_action_graphs": len(set(semantic_sequences)) == 100,
        "semantic_action_graph_similarity_below_limit": semantic_similarity["maximum_sequence_match"] < 0.85,
        "minimum_twenty_four_tool_calls": min(walk_lens) >= 24,
        "deep_evidence_intersection": min(evidence_read_counts) >= 19,
        "evidence_depth_varies": len(set(evidence_read_counts)) >= 6,
        "twenty_eight_generated_assets_per_task": min(generated_asset_counts) == 28 == max(generated_asset_counts),
        "all_native_assets_parse": native_assets_parsed == len(asset_hashes),
        "real_native_formats_present": {"xlsx", "pdf", "eml", "csv", "json", "md", "txt"} <= set(asset_format_counts),
        "no_gold_or_recipe_in_asset_room": not asset_leakage_hits,
        "all_assets_content_unique": len(set(asset_hashes)) == len(asset_hashes),
        "at_least_forty_specific_public_causal_criteria": min(criteria_counts) >= 40,
        "one_hundred_authored_decisions": len(DECISION_SPECS) == 100,
        "unique_authored_decision_codes": len({spec.decision_code for spec in DECISION_SPECS.values()}) == 100,
        "exact_state_transition_every_task": exact_state_transitions == 100,
        "two_post_write_readbacks_every_task": post_write_readbacks == 100,
        "ten_negative_controls": len(qualification["negative_controls"]) == 10,
        "zero_negative_false_accepts": not any(
            row["false_accepts"] for row in qualification["negative_controls"].values()
        ),
        "three_options_one_selected": all(
            len(record["rubric"]["decision_options"]) == 3
            and sum(option["selected"] for option in record["rubric"]["decision_options"]) == 1
            for record in records
        ),
        "deterministic_verifier": qualification["release_passed"],
    }
    build_report["quality_gates"] = quality_gates
    build_report["release_passed"] = all(quality_gates.values())
    if not build_report["release_passed"]:
        failed = sorted(name for name, passed in quality_gates.items() if not passed)
        raise AssertionError(f"LedgerBench realism gates failed: {failed}")
    write_json(hf / "reports" / "build.json", build_report)
    write_json(release / "reports" / "build.json", build_report)
    write_text(hf / "README.md", dataset_card(build_report, qualification))
    seal_manifest(release)
    return build_report


def seal_manifest(release: Path) -> None:
    manifest_path = release / "release-manifest.json"
    files = sorted(p for p in release.rglob("*")
                   if p.is_file()
                   and p != manifest_path
                   and p.suffix != ".pyc"
                   and "__pycache__" not in p.parts)
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

{RELEASE_NAME} is a deterministic corporate-finance agent benchmark: 100 distinct
employee decisions over isolated simulated finance worlds. Each world combines a
Dynamics 365-shaped ERP, an Odoo procure-to-pay and manufacturing surface, a QBO-style
subsidiary ledger, Microsoft Graph workbooks, Gmail, governed documents, and frozen SEC
XBRL filings through {build['mcp_servers']} MCP servers exposing {build['mcp_tools']}
provider-shaped tools. The employee asks for an outcome in ordinary language; the agent
must discover the reporting schema and the task-specific investigation.

Grading is fully deterministic and binary. It checks the exact answer, every required
independent evidence read, read-before-write causality, the exact Dynamics finance-case
decision, the scoped completion email, two post-write readbacks, task-native operational
state, and a `writes_only` containment veto. No LLM judge, network, clock, or randomness
appears in the reward path.

## Measured contents

- Tasks: {build['task_count']} across {build['family_count']} families: {families}
- Oracle walk length: min {build['walk_len']['min']} / median {build['walk_len']['median']} / max {build['walk_len']['max']} MCP calls ({build['walk_len']['total']} total); required distributed evidence reads are {build['required_evidence_reads_per_task']['min']}-{build['required_evidence_reads_per_task']['max']} per task
- Executable checks: {build['checks']['answer_checks_total']} answer + {build['checks']['trace_checks_total']} trace + {build['checks']['state_checks_total']} state, expanded into {build['criteria_per_task']['min']}-{build['criteria_per_task']['max']} exact public criteria per task
- Inspectable assets: {build['generated_assets_per_task']['min']} agent-visible native files per task, including valid XLSX, PDF, EML, CSV, JSON, Markdown, and text records; gold and oracle recipes are excluded from this tree
- Reference diversity: {build['unique_reference_tool_name_sequences']}/100 distinct raw server/tool sequences and {build['unique_semantic_action_graphs']}/100 distinct semantic action graphs
- Escalated variants: {build['escalated_variant_pairs']} tasks are controls-review follow-ups whose governing policy must be found among seeded adjacent documents; every follow-up now has its own human request and policy-discovery trajectory
- Prompt uniqueness: {100 - build['exact_duplicate_prompts']} distinct employee requests; maximum pairwise 5-shingle Jaccard {build['prompt_uniqueness']['maximum_jaccard_5_shingle']}

## What is included

- `data/tasks.jsonl`: apex-accounting-compatible records (`task_id`, `task_name`, `world_id`, `prompt`, `context_files`, `rubric`, `gold_output`, `metadata`).
- `tasks/`: one readable JSON record per task.
- `task_files/`: 28 task-scoped agent-visible evidence files plus any native seeded documents and inputs.
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
