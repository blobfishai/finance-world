from __future__ import annotations

import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import SimpleNamespace


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from decision_specs import DECISION_SPECS  # noqa: E402
from exporter import remove_generated_bytecode  # noqa: E402
from run_suite import incomplete_read_steps  # noqa: E402
from realism import (  # noqa: E402
    _pdf,
    _xlsx,
    augment_checks,
    case_contract,
    decision_options,
    reference_walk,
    release_prompt,
    rubric_criteria,
    validate_native_asset,
)


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
            self.assertEqual(2, sum("readback_call" in key for key in contract))
        self.assertEqual(100, len(raw_sequences))
        self.assertEqual(100, len(semantic_graphs))

    def test_every_decision_has_one_supported_and_two_rejected_options(self) -> None:
        for entry in self.catalog["tasks"]:
            options = decision_options(entry)
            self.assertEqual(3, len(options))
            self.assertEqual(1, sum(bool(option["selected"]) for option in options))

    def test_public_rubric_exposes_each_causal_evidence_gate(self) -> None:
        required_categories = {
            "evidence",
            "authority",
            "correlation",
            "communications",
            "approval",
            "operations",
            "reconciliation",
        }
        for entry in self.catalog["tasks"]:
            source = ROOT / "tasks" / entry["source_task"]
            source_walk = json.loads((source / "solution" / "walk.json").read_text())
            contract = case_contract(entry)
            _, trace_contract = reference_walk(entry, source_walk, contract)
            checks = json.loads((source / "tests" / "checks.json").read_text())
            checks = augment_checks(entry, checks, contract, trace_contract)
            criteria = rubric_criteria(entry, checks, trace_contract, contract)

            self.assertGreaterEqual(len(criteria), 40)
            self.assertTrue(required_categories <= {row["category"] for row in criteria})
            exact_call_criteria = [
                row for row in criteria
                if row["enforced_by"].startswith("required_calls exact ")
            ]
            self.assertEqual(18, len(exact_call_criteria))
            self.assertEqual(18, len({row["id"] for row in exact_call_criteria}))

    def test_native_pdf_and_workbook_are_parseable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdf = root / "evidence.pdf"
            pdf.write_bytes(_pdf("Case FINCASE-TEST\nCurrent control evidence"))
            workbook = root / "evidence.xlsx"
            workbook.write_bytes(_xlsx([["case", "status"], ["FINCASE-TEST", "open"]]))
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
