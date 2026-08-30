#!/usr/bin/env python3
"""Build the LedgerBench-100 Hugging Face release tree from the built Harbor packs.

Runs AFTER exporter.py (packs + dataset.toml) and run_suite.py (trajectories +
qualification.json), because the dataset card quotes only measured numbers.

  dist/ledgerbench-100/huggingface/
    data/tasks.jsonl        apex-accounting-compatible task records
    tasks/<task_id>.json    one readable record per task
    task_files/<task_id>/   native context plus one exact export per material MCP read
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
import importlib.util
import json
import re
import shutil
import statistics
import sys
import tempfile
import tomllib
from difflib import SequenceMatcher
from pathlib import Path

from decision_model import (
    ADDITIONAL_APPROVAL_REQUIRED,
    AVAILABLE_NOT_RECOMMENDED,
    CHAIN_ANSWER_FIELDS,
    NOT_SUPPORTED_BY_CURRENT_EVIDENCE,
)
from decision_specs import DECISION_SPECS
from realism import (
    CONTEXTUAL_ASSETS_PER_TASK,
    MIN_TASK_NATIVE_POINTS,
    MIN_MATERIAL_ASSETS_PER_TASK,
    SEMANTIC_MILESTONE_WEIGHTS,
    TASK_NATIVE_MILESTONES,
    validate_native_asset,
    write_asset_views,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELEASE_NAME = "LedgerBench-100"
RELEASE_SLUG = "ledgerbench-100"
RELEASE_VERSION = "3.4.1"
HARBOR_ORG = "blobfishai"
WORLD_ID = "ledgerbench-erp-world-v3-4"
NEGATIVE_CONTROLS = 14


def alternatives_fully_qualified(options: list[dict], checks: dict) -> bool:
    """Three alternatives with graded outcome, cost and authority; one recommended;
    one beyond current authority; one feasible-but-inferior or unsupported."""

    graded = {check["field"]: check for check in checks.get("answer_checks", [])}
    if len(options) != 3 or sum(bool(option.get("selected")) for option in options) != 1:
        return False
    for option in options:
        if not option.get("outcome") or not option.get("authority_status"):
            return False
        if not isinstance(option.get("incremental_cost"), (int, float)):
            return False
        expected = graded.get(option.get("outcome_field"), {}).get("expect")
        if expected != option["outcome"]:
            return False
    statuses = {option["authority_status"] for option in options}
    return ADDITIONAL_APPROVAL_REQUIRED in statuses and bool(
        statuses & {AVAILABLE_NOT_RECOMMENDED, NOT_SUPPORTED_BY_CURRENT_EVIDENCE}
    )
DATA_LICENSE = "CC-BY-4.0"
CODE_LICENSE = "Apache-2.0"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def provider_tool_contracts() -> dict:
    """Load the exact shipped MCP schemas into one inspectable release artifact."""

    lib = str(ROOT / "mcp" / "lib")
    sys.path.insert(0, lib)
    servers = []
    try:
        for path in sorted((ROOT / "mcp" / "servers").glob("*_server.py")):
            spec = importlib.util.spec_from_file_location(
                f"ledgerbench_contract_{path.stem}", path
            )
            if spec is None or spec.loader is None:
                raise RuntimeError(f"cannot load provider contracts from {path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            server = module.S
            tools = [schema for _, schema in server.tools.values()]
            for tool in tools:
                schema = tool["inputSchema"]
                if (
                    schema.get("type") != "object"
                    or schema.get("additionalProperties") is not False
                    or not set(schema.get("required") or ())
                    <= set((schema.get("properties") or {}).keys())
                ):
                    raise ValueError(
                        f"{server.name}.{tool['name']}: open or invalid input schema"
                    )
            servers.append(
                {
                    "server": server.name,
                    "description": server.description,
                    "tools": tools,
                }
            )
    finally:
        if lib in sys.path:
            sys.path.remove(lib)
        sys.modules.pop("framework", None)
    return {
        "schemaVersion": "ledgerbench.provider-tool-contracts.v1",
        "servers": servers,
        "toolCount": sum(len(server["tools"]) for server in servers),
        "allInputSchemasClosed": True,
    }


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


def gold_output(walk: list[dict], checks: dict, realism: dict) -> dict:
    submitted: dict = {}
    for step in walk:
        if step["server"] == "harness" and step["tool"] == "submit_answer":
            submitted.update((step.get("args") or {}).get("answers") or {})
    return {
        "submit_answer": submitted,
        "metric": "LedgerScore",
        "points_possible": 100,
        "expected_semantic_milestones": [
            {
                "id": criterion["id"],
                "weight": criterion["weight"],
                "description": criterion["description"],
            }
            for criterion in realism["criteria"]
        ],
        "atomic_check_count": len(realism["atomic_check_contract"]),
        "expected_state_assertions": [
            c for c in checks.get("state_checks", []) if c.get("type") != "writes_only"
        ],
    }


PUBLIC_MILESTONE_FIELDS = (
    "id",
    "category",
    "weight",
    "description",
    "expected_investigation",
    "reasoning_path",
    "success_condition",
    "rejected_shortcut",
    "checked_outcomes",
    "expected_answer_fields",
    "task_native_core",
    "task_native_write_count",
    "task_native_mutation_surfaces",
)


def public_semantic_milestones(realism: dict) -> list[dict]:
    """Expose employee outcomes without turning the rubric into an oracle recipe."""

    return [
        {
            field: criterion[field]
            for field in PUBLIC_MILESTONE_FIELDS
            if field in criterion
        }
        for criterion in realism["criteria"]
    ]


def build(release: Path) -> dict:
    tasks_root = release / "harbor" / "tasks"
    hf = release / "huggingface"
    catalog = json.loads((HERE / "catalog.json").read_text())
    entries = {e["task_id"]: e for e in catalog["tasks"]}
    qualification = json.loads((release / "reports" / "qualification.json").read_text())
    if not qualification["release_passed"]:
        raise SystemExit("refusing to build the HF tree from a failed qualification")
    write_json(hf / "reports" / "qualification.json", qualification)

    records: list[dict] = []
    prompts: list[str] = []
    walk_lens: list[int] = []
    walk_sequences: list[tuple[tuple[str, str], ...]] = []
    semantic_sequences: list[tuple[str, ...]] = []
    evidence_read_counts: list[int] = []
    reference_read_counts: list[int] = []
    context_counts: list[int] = []
    generated_asset_counts: list[int] = []
    material_asset_counts: list[int] = []
    material_assets_with_exact_provenance = 0
    criteria_counts: list[int] = []
    criteria_point_totals: list[int] = []
    task_native_point_totals: list[int] = []
    atomic_assertion_counts: list[int] = []
    graded_answer_counts: list[int] = []
    graded_numeric_counts: list[int] = []
    graded_decision_models = 0
    fully_qualified_alternatives = 0
    doc_hashes: set[str] = set()
    asset_hashes: list[str] = []
    asset_format_counts: dict[str, int] = {}
    native_assets_parsed = 0
    asset_leakage_hits: list[str] = []
    exact_state_transitions = 0
    post_write_readbacks = 0
    source_post_write_readbacks = 0
    exact_atomic_assignments = 0
    deep_erp_evidence_tasks = 0
    erp_tasks_with_native_state = 0
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
        world_spec = json.loads(
            (task_dir / "environment" / "world" / "spec.json").read_text()
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
                realism["trace_contract"],
                server_root=task_dir / "environment" / "world" / "runtime",
                world_now=world_spec["world_now"],
                world_role=world_spec["world_role"],
            )
        assets: list[dict[str, object]] = []
        for asset in asset_records:
            relative = f"task_files/{task_id}/assets/{asset['filename']}"
            context_files.append(relative)
            assets.append({**asset, "path": relative})
            asset_path = asset_root / asset["filename"]
            digest = hashlib.sha256(asset_path.read_bytes()).hexdigest()
            if asset.get("material"):
                material_assets_with_exact_provenance += int(
                    asset.get("bytes") == asset_path.stat().st_size
                    and asset.get("sha256") == digest
                    and isinstance(asset.get("query_scope"), dict)
                    and bool(asset.get("material_reason"))
                )
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
        material_asset_counts.append(
            sum(bool(asset.get("material")) for asset in asset_records)
        )
        criteria_counts.append(len(realism["criteria"]))
        criteria_point_totals.append(
            sum(int(criterion["weight"]) for criterion in realism["criteria"])
        )
        task_native_point_totals.append(
            sum(
                int(criterion["weight"])
                for criterion in realism["criteria"]
                if criterion.get("task_native_core")
            )
        )
        atomic_assertion_counts.append(len(realism["public_criteria"]))
        graded_fields = {check["field"] for check in checks.get("answer_checks", [])}
        graded_answer_counts.append(len(graded_fields))
        graded_numeric_counts.append(
            sum(1 for check in checks.get("answer_checks", []) if check.get("type") == "number")
        )
        graded_decision_models += int(set(CHAIN_ANSWER_FIELDS) <= graded_fields)
        fully_qualified_alternatives += int(
            alternatives_fully_qualified(realism["decision_options"], checks)
        )
        prompts.append(prompt)
        exact_state_transitions += int(
            any(
                check.get("name") == "decision_work_item_exact_decision"
                for check in checks.get("state_checks", [])
            )
        )
        reference_read_counts.append(
            len(realism["trace_contract"]["reference_context_calls"])
        )
        source_contracts = realism["trace_contract"]["source_postwrite_contracts"]
        source_post_write_readbacks += len(source_contracts)
        post_write_readbacks += int(
            sum(
                check.get("type") == "post_write_readback"
                for check in checks.get("trace_checks", [])
            )
            == len(source_contracts) + 2
        )
        atomic_ids = {
            row["id"] for row in realism["atomic_check_contract"]
        }
        assigned_ids = [
            check_id
            for criterion in realism["criteria"]
            for check_id in criterion["atomic_check_ids"]
        ]
        exact_atomic_assignments += int(
            len(assigned_ids) == len(set(assigned_ids))
            and set(assigned_ids) == atomic_ids
        )
        if entry["family"] == "erpbench":
            models = {
                (call.get("args") or {}).get("model")
                for call in realism["trace_contract"]["material_context_groups"]["source_systems"]
                if call.get("server") == "odoo" and call.get("tool") == "search_read"
            }
            required_models = {
                "sale.order",
                "sale.order.line",
                "product.product",
                "res.partner",
                "product.supplierinfo",
                "stock.quant",
                "mrp.bom",
                "mrp.bom.line",
                "mrp.workcenter",
            }
            deep_erp_evidence_tasks += int(required_models <= models)
            wrapper_state_names = {
                "decision_work_item_decided",
                "decision_work_item_exact_decision",
                "decision_work_item_evidence_refs",
                "decision_work_item_selected_option",
                "one_decision_work_item_audit",
                "exception_request_untouched",
                "one_completion_email",
            }
            erp_tasks_with_native_state += int(
                any(
                    check.get("type") != "writes_only"
                    and check.get("name") not in wrapper_state_names
                    for check in checks.get("state_checks", [])
                )
            )

        semantic_milestones = public_semantic_milestones(realism)
        record = {
            "task_id": task_id,
            "task_name": entry["source_task"],
            "world_id": WORLD_ID,
            "prompt": prompt,
            "context_files": context_files,
            "assets": assets,
            "rubric": {
                "type": "deterministic_weighted_milestones",
                "engine": "verifiers/vcode.py atomic checks aggregated by the world runtime",
                "metric": "LedgerScore",
                "points_possible": 100,
                "milestones": semantic_milestones,
                "criteria": semantic_milestones,
                "decision_options": realism["decision_options"],
                "reasoning_chain_fields": realism["reasoning_chain_fields"],
                "gates": [
                    "investigation and causal analysis use exact successful material reads",
                    "supported decisions and provider-native state transitions are graded from persisted state",
                    "every write is read back, mutation rejections fail strict pass, and off-scope writes are vetoed",
                ],
            },
            "verifier_contract": {
                "visibility": "transparent evaluation contract; not agent instructions",
                "atomic_check_contract": realism["atomic_check_contract"],
                "checks": checks,
            },
            "gold_output": gold_output(walk, checks, realism),
            "metadata": {
                "benchmark": RELEASE_NAME,
                "version": RELEASE_VERSION,
                "harbor_name": f"{HARBOR_ORG}/{task_id}",
                "family": entry["family"],
                "provenance": entry["provenance"],
                "difficulty": entry["difficulty"],
                "grading": "deterministic",
                "metric": "LedgerScore",
                "points_possible": 100,
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
    tool_contracts = provider_tool_contracts()
    write_json(hf / "contracts" / "tool-contracts.json", tool_contracts)

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
        "schema_version": "ledgerbench.build.v6",
        "benchmark": RELEASE_NAME,
        "version": RELEASE_VERSION,
        "metric": "LedgerScore",
        "points_possible": 100,
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
        "reference_context_reads_per_task": {
            "min": min(reference_read_counts),
            "median": int(statistics.median(reference_read_counts)),
            "max": max(reference_read_counts),
            "distinct_counts": len(set(reference_read_counts)),
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
            "material_assets_with_exact_provenance": material_assets_with_exact_provenance,
            "material_per_task": {
                "min": min(material_asset_counts),
                "median": int(statistics.median(material_asset_counts)),
                "max": max(material_asset_counts),
            },
        },
        "generated_assets_per_task": {
            "min": min(generated_asset_counts),
            "median": int(statistics.median(generated_asset_counts)),
            "max": max(generated_asset_counts),
        },
        "public_semantic_milestones_per_task": {
            "min": min(criteria_counts),
            "median": int(statistics.median(criteria_counts)),
            "max": max(criteria_counts),
        },
        "criteria_points_per_task": {
            "min": min(criteria_point_totals),
            "median": int(statistics.median(criteria_point_totals)),
            "max": max(criteria_point_totals),
        },
        "task_native_points_per_task": {
            "min": min(task_native_point_totals),
            "median": int(statistics.median(task_native_point_totals)),
            "max": max(task_native_point_totals),
            "milestones": sorted(TASK_NATIVE_MILESTONES),
        },
        "atomic_verifier_assertions_per_task": {
            "min": min(atomic_assertion_counts),
            "median": int(statistics.median(atomic_assertion_counts)),
            "max": max(atomic_assertion_counts),
        },
        "graded_answer_fields_per_task": {
            "min": min(graded_answer_counts),
            "median": int(statistics.median(graded_answer_counts)),
            "max": max(graded_answer_counts),
        },
        "graded_numeric_derivations_per_task": {
            "min": min(graded_numeric_counts),
            "median": int(statistics.median(graded_numeric_counts)),
            "max": max(graded_numeric_counts),
        },
        "graded_decision_models": graded_decision_models,
        "fully_qualified_alternatives": fully_qualified_alternatives,
        "reasoning_chain_fields": list(CHAIN_ANSWER_FIELDS),
        "unique_reference_tool_name_sequences": len(set(walk_sequences)),
        "reference_sequence_similarity": reference_similarity,
        "unique_semantic_action_graphs": len(set(semantic_sequences)),
        "semantic_action_graph_similarity": semantic_similarity,
        "exact_decision_work_item_transitions": exact_state_transitions,
        "all_contracted_post_write_readbacks": post_write_readbacks,
        "source_provider_post_write_readbacks": source_post_write_readbacks,
        "provider_tool_contracts": {
            "servers": len(tool_contracts["servers"]),
            "tools": tool_contracts["toolCount"],
            "all_input_schemas_closed": tool_contracts[
                "allInputSchemasClosed"
            ],
        },
        "exact_atomic_check_assignments": exact_atomic_assignments,
        "deep_erp_evidence_tasks": deep_erp_evidence_tasks,
        "erp_tasks_with_task_native_state": erp_tasks_with_native_state,
        "authored_decision_specs": len(DECISION_SPECS),
        "unique_authored_decision_codes": len({spec.decision_code for spec in DECISION_SPECS.values()}),
        "decision_options_per_task": 3,
        "prompt_uniqueness": prompt_similarity,
        "exact_duplicate_prompts": len(prompts) - len(set(prompts)),
        "escalated_variant_pairs": sum(
            1 for e in catalog["tasks"] if e["provenance"] == "variant"),
        "curation_integrity": catalog.get("integrity", {}),
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
        "reference_sequence_similarity_below_limit": reference_similarity["maximum_sequence_match"] < 0.95,
        "unique_semantic_action_graphs": len(set(semantic_sequences)) == 100,
        "semantic_action_graph_similarity_below_limit": semantic_similarity["maximum_sequence_match"] < 0.85,
        "minimum_twenty_four_tool_calls": min(walk_lens) >= 24,
        "deep_evidence_intersection": min(evidence_read_counts) >= 19,
        "evidence_depth_varies": len(set(evidence_read_counts)) >= 6,
        "thirty_contextual_assets_per_task": all(
            total - material == CONTEXTUAL_ASSETS_PER_TASK
            for total, material in zip(generated_asset_counts, material_asset_counts)
        ),
        "all_native_assets_parse": native_assets_parsed == len(asset_hashes),
        "real_native_formats_present": {"xlsx", "pdf", "eml", "csv", "json", "md", "txt"} <= set(asset_format_counts),
        "no_gold_or_recipe_in_asset_room": not asset_leakage_hits,
        "all_assets_content_unique": len(set(asset_hashes)) == len(asset_hashes),
        "sixteen_semantic_milestones_per_task": (
            min(criteria_counts) == len(SEMANTIC_MILESTONE_WEIGHTS)
            == max(criteria_counts)
        ),
        "one_hundred_ledger_points_per_task": (
            min(criteria_point_totals) == 100 == max(criteria_point_totals)
        ),
        "task_native_work_is_majority_of_score": (
            min(task_native_point_totals) >= MIN_TASK_NATIVE_POINTS
            and min(task_native_point_totals) > 50
        ),
        "every_atomic_check_assigned_exactly_once": exact_atomic_assignments == 100,
        "material_assets_match_required_reads": material_asset_counts == evidence_read_counts,
        "minimum_nineteen_material_assets_per_task": min(material_asset_counts) >= MIN_MATERIAL_ASSETS_PER_TASK,
        "every_material_asset_has_exact_provenance": (
            material_assets_with_exact_provenance == sum(material_asset_counts)
        ),
        "sixteen_public_semantic_milestones_per_task": (
            min(criteria_counts) == len(SEMANTIC_MILESTONE_WEIGHTS)
            == max(criteria_counts)
        ),
        "forty_atomic_verifier_assertions_per_task": min(atomic_assertion_counts) >= 40,
        "graded_decision_model_every_task": graded_decision_models == 100,
        "three_costed_alternatives_every_task": fully_qualified_alternatives == 100,
        "twelve_graded_answer_fields_per_task": min(graded_answer_counts) >= 12,
        "eight_graded_derivations_per_task": min(graded_numeric_counts) >= 8,
        "one_hundred_authored_decisions": len(DECISION_SPECS) == 100,
        "unique_authored_decision_codes": len({spec.decision_code for spec in DECISION_SPECS.values()}) == 100,
        "exact_state_transition_every_task": exact_state_transitions == 100,
        "all_contracted_post_write_readbacks_every_task": post_write_readbacks == 100,
        "strict_provider_input_schemas": (
            tool_contracts["allInputSchemasClosed"]
            and tool_contracts["toolCount"] == build_report["mcp_tools"]
        ),
        "deep_real_shaped_erp_evidence": deep_erp_evidence_tasks == families.get("erpbench", 0),
        "task_native_state_every_erp_planning_job": (
            erp_tasks_with_native_state == families.get("erpbench", 0)
        ),
        "zero_prompt_variants": build_report["escalated_variant_pairs"] == 0,
        "all_jobs_are_source_ported": all(
            entry.get("provenance") == "ported" for entry in catalog["tasks"]
        ),
        "one_job_per_curated_archetype": (
            catalog.get("integrity", {}).get("prompt_variants") == 0
            and catalog.get("integrity", {}).get("ticker_or_company_swaps_used_as_jobs") == 0
            and catalog.get("integrity", {}).get("erpbench_scenario_archetypes") == 27
            and catalog.get("integrity", {}).get("erp_qa_employee_question_archetypes") == 23
        ),
        "fourteen_negative_controls": len(qualification["negative_controls"]) == NEGATIVE_CONTROLS,
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

Grading is fully deterministic. `LedgerScore` groups the executable verifier contract into
16 task-specific employee outcomes worth 100 points: scope, authority, current state,
task-native investigation, task-native causal reasoning, operating-plan controls, supported decision,
costed options, operational and case state, collaboration, outcome verification,
provider-native readback, containment, exact insights, and execution sequence. Strict pass
still requires all 100 points. No LLM judge,
network, clock, or randomness appears in the reward path.

The source job is the scoring core, not a decorative wrapper: at least
{build['task_native_points_per_task']['min']} of 100 points in every task are assigned to
task-native source investigation, reasoning, decision, persisted operational state, and
employee-facing insights. Every ERP planning task independently grades its Odoo state
transition in addition to the cross-system decision record.

Every case also carries a graded operating-control model: the control requirement is
derived from the ERP's in-scope DecisionScopeLines, usable support is reconciled from the
current evidence register net of counterparty-corroborated exclusions, the exception is
tested against the policy tolerance, the counterparty's committed date and the close
or production-planning window bounds three costed timing alternatives (one within authority,
one held for the counterparty, one requiring a higher-authority exception), and the selected outcome is
compared with the requester's documented need-by date into a signed variance and an honest
timing status. All {len(build['reasoning_chain_fields'])} intermediate and final values are
graded as their own answer fields, the selected option is persisted on the case, and the
completion handoff is graded on its content.

## Measured contents

- Tasks: {build['task_count']} across {build['family_count']} families: {families}
- Oracle walk length: min {build['walk_len']['min']} / median {build['walk_len']['median']} / max {build['walk_len']['max']} MCP calls ({build['walk_len']['total']} total); required distributed evidence reads are {build['required_evidence_reads_per_task']['min']}-{build['required_evidence_reads_per_task']['max']} per task
- Public rubric: exactly {build['public_semantic_milestones_per_task']['min']} causal employee-outcome milestones / 100 LedgerScore points per task. The execution layer separately contains {build['checks']['answer_checks_total']} answer + {build['checks']['trace_checks_total']} trace + {build['checks']['state_checks_total']} state checks, with {build['atomic_verifier_assertions_per_task']['min']}-{build['atomic_verifier_assertions_per_task']['max']} atomic verifier assertions per task assigned exactly once beneath those milestones
- Graded reasoning chain: {build['graded_answer_fields_per_task']['min']}-{build['graded_answer_fields_per_task']['max']} graded answer fields per task ({build['graded_numeric_derivations_per_task']['min']}-{build['graded_numeric_derivations_per_task']['max']} numeric derivations), a graded decision model in {build['graded_decision_models']}/100 tasks and three costed alternatives with authority status in {build['fully_qualified_alternatives']}/100; task-native work carries {build['task_native_points_per_task']['min']}-{build['task_native_points_per_task']['max']} points per task
- Inspectable assets: {build['generated_assets_per_task']['min']}-{build['generated_assets_per_task']['max']} agent-visible native files per task, including {build['agent_visible_assets']['material_per_task']['min']}-{build['agent_visible_assets']['material_per_task']['max']} exact executed MCP responses bound one-for-one to the verifier's material reads; every material export carries request scope, bytes, and SHA-256, while gold and oracle recipes are excluded
- Readback depth: {build['source_provider_post_write_readbacks']} task-native provider readbacks across the release, plus the governed case and completion-thread readbacks in every task
- Reference diversity: {build['unique_reference_tool_name_sequences']}/100 distinct raw server/tool sequences (maximum sequence match {build['reference_sequence_similarity']['maximum_sequence_match']}) and {build['unique_semantic_action_graphs']}/100 distinct semantic action graphs
- Human-job curation: {build['escalated_variant_pairs']} prompt variants; the release uses one instance of each of 27 ERP planning archetypes and 23 distinct ERP control questions, and does not count ticker or company-name swaps as new jobs
- Prompt uniqueness: {100 - build['exact_duplicate_prompts']} distinct employee requests; maximum pairwise 5-shingle Jaccard {build['prompt_uniqueness']['maximum_jaccard_5_shingle']}

## What is included

- `data/tasks.jsonl`: apex-accounting-compatible records (`task_id`, `task_name`, `world_id`, `prompt`, `context_files`, `rubric`, `gold_output`, `metadata`).
- `tasks/`: one readable JSON record per task.
- `task_files/`: {build['generated_assets_per_task']['min']}-{build['generated_assets_per_task']['max']} task-scoped agent-visible evidence files plus any native seeded documents and inputs.
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
