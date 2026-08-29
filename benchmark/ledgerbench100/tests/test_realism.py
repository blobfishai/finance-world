from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from decision_specs import DECISION_SPECS  # noqa: E402
from exporter import prepare, remove_generated_bytecode  # noqa: E402
from run_suite import incomplete_read_steps  # noqa: E402
from realism import (  # noqa: E402
    SEMANTIC_MILESTONE_WEIGHTS,
    _pdf,
    _xlsx,
    atomic_check_specs,
    augment_checks,
    case_contract,
    decision_options,
    reference_walk,
    release_prompt,
    rubric_criteria,
    seed_case_context,
    validate_native_asset,
    write_asset_views,
)

sys.path.insert(0, str(ROOT / "verifiers"))
from vcode import evaluate_trace_check, first_evidence_index  # noqa: E402


class LedgerBenchRealismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((HERE / "catalog.json").read_text())

    def test_authored_decisions_cover_catalog_exactly(self) -> None:
        sources = {entry["source_task"] for entry in self.catalog["tasks"]}
        self.assertEqual(sources, set(DECISION_SPECS))
        self.assertEqual(100, len(DECISION_SPECS))
        self.assertEqual(100, len({spec.decision_code for spec in DECISION_SPECS.values()}))
        self.assertEqual(100, len({spec.employee_question for spec in DECISION_SPECS.values()}))

    def test_prompts_are_unique_high_level_requests(self) -> None:
        prompts = []
        for entry in self.catalog["tasks"]:
            source = ROOT / "tasks" / entry["source_task"]
            config = tomllib.loads((source / "task.toml").read_text())
            prompt = release_prompt(entry, (source / "instruction.md").read_text(), config)
            self.assertGreaterEqual(len(prompt.split()), 55)
            self.assertLessEqual(len(prompt.split()), 125)
            self.assertNotIn("submit_answer", prompt)
            self.assertNotIn("api_invoke_action", prompt)
            prompts.append(prompt)
        self.assertEqual(100, len(set(prompts)))

    def test_reference_and_semantic_graphs_are_unique(self) -> None:
        raw_sequences = set()
        semantic_graphs = set()
        for entry in self.catalog["tasks"]:
            source = ROOT / "tasks" / entry["source_task"]
            source_walk = json.loads((source / "solution" / "walk.json").read_text())
            walk, contract = reference_walk(entry, source_walk, case_contract(entry))
            raw_sequences.add(tuple((step["server"], step["tool"]) for step in walk))
            semantic_graphs.add(tuple(contract["semantic_action_graph"]))
            self.assertGreaterEqual(len(walk), 24)
            self.assertGreaterEqual(len(contract["required_context_calls"]), 19)
            self.assertIn("state_readback_call", contract)
            self.assertIn("message_readback_call", contract)
            self.assertEqual(
                len(contract["source_postwrite_contracts"]),
                len(contract["source_postwrite_readback_calls"]),
            )
        self.assertEqual(100, len(raw_sequences))
        self.assertEqual(100, len(semantic_graphs))

    def test_every_decision_has_one_supported_and_two_rejected_options(self) -> None:
        for entry in self.catalog["tasks"]:
            options = decision_options(entry)
            self.assertEqual(3, len(options))
            self.assertEqual(1, sum(bool(option["selected"]) for option in options))

    def test_public_rubric_is_semantic_and_covers_every_atomic_check_once(self) -> None:
        for entry in self.catalog["tasks"]:
            source = ROOT / "tasks" / entry["source_task"]
            source_walk = json.loads((source / "solution" / "walk.json").read_text())
            contract = case_contract(entry)
            _, trace_contract = reference_walk(entry, source_walk, contract)
            checks = json.loads((source / "tests" / "checks.json").read_text())
            checks = augment_checks(entry, checks, contract, trace_contract)
            criteria = rubric_criteria(entry, checks, trace_contract, contract)

            self.assertEqual(14, len(criteria))
            self.assertEqual(100, sum(row["weight"] for row in criteria))
            self.assertEqual(set(SEMANTIC_MILESTONE_WEIGHTS), {row["id"] for row in criteria})
            atomic_ids = {row["id"] for row in atomic_check_specs(checks)}
            assigned = [
                check_id
                for criterion in criteria
                for check_id in criterion["atomic_check_ids"]
            ]
            self.assertEqual(len(assigned), len(set(assigned)))
            self.assertEqual(atomic_ids, set(assigned))
            self.assertTrue(
                all(entry["family"] in row["description"] or row["id"] != "state.operational"
                    for row in criteria)
            )

    def test_native_pdf_and_workbook_are_parseable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdf = root / "evidence.pdf"
            pdf.write_bytes(_pdf("Case FINCASE-TEST\nCurrent control evidence"))
            workbook = root / "evidence.xlsx"
            first = _xlsx([["case", "status"], ["FINCASE-TEST", "open"]])
            second = _xlsx([["case", "status"], ["FINCASE-TEST", "open"]])
            self.assertEqual(first, second)
            workbook.write_bytes(first)
            self.assertTrue(validate_native_asset(pdf))
            self.assertTrue(validate_native_asset(workbook))

    def test_provider_surface_uses_real_generic_tools(self) -> None:
        erp = (ROOT / "mcp" / "servers" / "erp_server.py").read_text()
        self.assertIn('@S.tool("data_find_entities"', erp)
        self.assertIn('@S.tool("api_invoke_action"', erp)
        self.assertIn("ContosoFinanceCaseDecide", erp)
        self.assertNotIn('@S.tool("approve_invoice"', erp)

    def test_incomplete_read_removes_a_uniquely_required_request(self) -> None:
        repeated = {"server": "sheets", "tool": "list_drive_items", "args": {}}
        unique = {
            "server": "docs",
            "tool": "get_document",
            "args": {"doc_id": "current-control"},
        }
        world = SimpleNamespace(
            spec={"task_id": "test-task"},
            realism={
                "trace_contract": {
                    "required_context_calls": [repeated, unique, repeated],
                }
            },
            walk=[repeated, unique, repeated],
        )

        mutated = incomplete_read_steps(world)

        self.assertEqual([repeated, repeated], mutated)

    def test_rejected_mutation_fails_but_failed_exploratory_read_is_allowed(self) -> None:
        check = {
            "type": "no_rejected_mutations",
            "calls": [
                {
                    "server": "erp",
                    "tool": "api_invoke_action",
                    "args": {"action": "ContosoFinanceCaseDecide"},
                }
            ],
        }
        failed_read = {
            "server": "docs",
            "tool": "get_document",
            "args": {"doc_id": "mistyped"},
            "ok": False,
        }
        rejected_write = {
            "server": "erp",
            "tool": "api_invoke_action",
            "args": {"action": "ContosoFinanceCaseDecide", "parameters": {}},
            "ok": False,
        }

        self.assertEqual([], evaluate_trace_check(check, [failed_read]))
        self.assertTrue(evaluate_trace_check(check, [failed_read, rejected_write]))

        expected_absence = {
            "server": "filings",
            "tool": "get_company_concept",
            "args": {
                "ticker": "WMT",
                "concept": "ResearchAndDevelopmentExpense",
            },
            "expected_error_contains": "concept not in snapshot",
        }
        exact_negative = {
            **{key: value for key, value in expected_absence.items()
               if key != "expected_error_contains"},
            "ok": False,
            "note": "concept not in snapshot for this company",
        }
        wrong_negative = {**exact_negative, "note": "network timeout"}
        self.assertEqual(0, first_evidence_index([exact_negative], expected_absence))
        self.assertIsNone(first_evidence_index([wrong_negative], expected_absence))

    def test_erp_task_exposes_demand_bom_supply_capacity_and_material_assets(self) -> None:
        entry = next(
            row for row in self.catalog["tasks"] if row["family"] == "erpbench"
        )
        source = ROOT / "tasks" / entry["source_task"]
        source_walk = json.loads((source / "solution" / "walk.json").read_text())
        config = tomllib.loads((source / "task.toml").read_text())
        prompt = release_prompt(entry, (source / "instruction.md").read_text(), config)

        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary) / "run"
            prepared = prepare(source, staged)
            contract = seed_case_context(
                staged / "world.sqlite",
                entry,
                source_walk,
                prepared["env"]["WORLD_NOW"],
            )
            _, trace_contract = reference_walk(entry, source_walk, contract)

            lib_path = str(ROOT / "mcp" / "lib")
            sys.path.insert(0, lib_path)
            module_spec = importlib.util.spec_from_file_location(
                "ledgerbench_test_odoo", ROOT / "mcp" / "servers" / "odoo_server.py"
            )
            module = importlib.util.module_from_spec(module_spec)
            with patch.dict(os.environ, prepared["env"], clear=False):
                module_spec.loader.exec_module(module)
                material_calls = [
                    call
                    for call in trace_contract["material_context_groups"]["source_systems"]
                    if call["server"] == "odoo"
                ]
                observed_models = set()
                for call in material_calls:
                    result = module.S.call(call["tool"], call["args"])
                    self.assertNotIn("error", result)
                    if call["tool"] == "search_read":
                        observed_models.add(call["args"]["model"])
                        self.assertGreater(result["total_rows"], 0)
            sys.path.remove(lib_path)
            sys.modules.pop("framework", None)

            self.assertTrue(
                {
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
                <= observed_models
            )

            asset_root = Path(temporary) / "assets"
            assets = write_asset_views(
                asset_root,
                staged / "world.sqlite",
                prompt,
                entry,
                contract,
            )
            self.assertEqual(28, len(assets))
            self.assertEqual(12, sum(bool(asset["material"]) for asset in assets))
            odoo_asset = json.loads(
                (asset_root / "23-odoo-procurement.json").read_text()
            )
            tables = {source["table"] for source in odoo_asset["sources"]}
            self.assertTrue(
                {
                    "erpb_demand",
                    "erpb_vendor_offers",
                    "erpb_stock",
                    "erpb_boms",
                    "erpb_bom_components",
                    "erpb_workcenters",
                }
                <= tables
            )

    def test_release_cleanup_removes_only_generated_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cache = root / "module" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "module.cpython-312.pyc").write_bytes(b"generated")
            source = root / "module" / "module.py"
            source.write_text("VALUE = 1\n")

            remove_generated_bytecode(root)

            self.assertFalse(cache.exists())
            self.assertEqual("VALUE = 1\n", source.read_text())


if __name__ == "__main__":
    unittest.main()
