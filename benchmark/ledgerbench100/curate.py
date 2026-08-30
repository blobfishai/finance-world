#!/usr/bin/env python3
"""Curate LedgerBench-100 as 100 different employee jobs.

The old selector optimized for difficulty and walk length. That accidentally
selected many copies of the same generated ERP scenario and thirty cosmetic
"escalated" variants. This release uses an explicit, reviewable allow-list:

* every small first-party workflow appears once, never with its prompt variant;
* every ERP-Bench scenario archetype appears exactly once;
* every FinanceBenchmark ERP item represents a different business question;
* ticker swaps and company-name swaps do not count as different jobs.

Oracle validity is not asserted here. It is proven after export by the sealed
qualification receipt, which executes all 100 worlds and adversarial controls.
"""

from __future__ import annotations

import json
import re
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASKS_ROOT = ROOT / "tasks"
RELEASE_VERSION = "3.4.2"
TARGET = 100

DERIVED_SOURCE_PATTERN = re.compile(
    r"(?:\bgrow:\s*escalated\b|\bescalated\s+variant\b|"
    r"\bidentical\s+ground\s+truth\b|\bprompt\s+variant\b|"
    r"\bretrieval\s+variant\b)",
    re.IGNORECASE,
)
DERIVED_LINEAGE_FIELDS = ("parent_task", "variant_of", "derived_from")


CURATED_SOURCE_TASKS = (
    "anomaly_triage/duplicate-payment-mar",
    "bank_rec/ach-return-mar",
    "bank_rec/statement-divergence-feb",
    "business_brief/brief-caterpillar",
    "fixed_assets/line7-capitalization",
    "cash_app/deduction-coding-mar",
    "cash_app/remittance-batch-mar02",
    "cash_forecast/cesp-four-week",
    "close_mgmt/period-lock-correction",
    "close_mgmt/revenue-recognition-tieout",
    "close_mgmt/subledger-tieout-feb",
    "collections_ops/escalate-sparrow-letter3",
    "cross_system/email-invoice-meadow",
    "cross_system/intercompany-tieout-feb",
    "cross_system/total-ar-adventure-group",
    "revenue_accounting/northwind-contract-allocation",
    "cross_system/tracker-formula-drift",
    "erp_qa/ap-overdue-usmf",
    "erp_qa/ar-balance-fourthcoffee-east",
    "erp_qa/cash-disc-fourthcoffee-east",
    "erp_qa/collections-sparrow",
    "erp_qa/credit-limit-adatum",
    "erp_qa/due-next-week-adventure",
    "erp_qa_fb/aged-balance-12",
    "erp_qa_fb/ap-invoices-1",
    "erp_qa_fb/ap-invoices-5",
    "erp_qa_fb/ap-payments-1",
    "erp_qa_fb/ap-payments-2",
    "erp_qa_fb/ap-purchase-orders-1",
    "erp_qa_fb/cash-collections-1",
    "erp_qa_fb/cash-disocunts-1",
    "erp_qa_fb/collections-1",
    "erp_qa_fb/collections-tasks-2",
    "erp_qa_fb/credit-limit-3",
    "erp_qa_fb/credit-notes-1",
    "erp_qa_fb/credit-rating-1",
    "erp_qa_fb/customer-setup-1",
    "erp_qa_fb/customer-setup-6",
    "erp_qa_fb/discounts-1",
    "erp_qa_fb/dispute-1",
    "erp_qa_fb/invoicing-history-3",
    "erp_qa_fb/other-2",
    "erp_qa_fb/payment-history-1",
    "erp_qa_fb/sales-orders-1",
    "erp_qa_fb/vendor-balance-4",
    "erp_qa_fb/vendors-3",
    "erpbench/2000-easy-01-buy-only-baseline",
    "erpbench/2008-easy-02-buy-only-immediate-invoicing",
    "erpbench/2032-medium-05-screened-buy-only-all-seeded",
    "erpbench/2042-medium-06-screened-buy-only-mixed-seeded",
    "erpbench/2053-medium-07-screened-buy-only-mixed-seeded-invoicing",
    "erpbench/2064-medium-08-single-bom-single-workcenter",
    "erpbench/2075-medium-09-single-bom-lowest-cost",
    "erpbench/2086-medium-10-single-bom-split-by-capacity",
    "erpbench/2097-hard-11-restricted-subassembly-qualified-workcenters",
    "erpbench/2107-medium-12-single-subassembly-lowest-cost",
    "erpbench/2118-medium-13-single-subassembly-qualified-workcenters",
    "erpbench/2129-medium-14-single-subassembly-shared-overflow-capacity",
    "erpbench/2140-hard-15-parallel-subassemblies-branch-assigned",
    "erpbench/2150-hard-16-serial-subassemblies-branch-assigned",
    "erpbench/2160-hard-17-shared-component-subassemblies-branch-assigned",
    "erpbench/2171-medium-18-manufacture-only-policy-forbidden",
    "erpbench/2182-medium-19-manufacture-only-no-buy-route",
    "erpbench/2193-medium-20-manufacture-only-no-available-vendors",
    "erpbench/2205-medium-21-single-bom-lowest-cost-screened-mixed-seeded",
    "erpbench/2217-medium-22-single-bom-split-by-capacity-invoicing",
    "erpbench/2229-hard-23-restricted-subassembly-qualified-workcenters-screened-all-seeded",
    "erpbench/2240-hard-24-single-subassembly-shared-overflow-capacity-screened-invoicing",
    "erpbench/2251-hard-25-shared-component-subassemblies-branch-assigned-screened-all-seeded",
    "erpbench/2262-easy-26-buy-only-net-30-no-adjacent-data",
    "erpbench/2272-easy-repair-plan-easy",
    "erpbench/2280-medium-repair-plan-medium",
    "erpbench/2290-hard-repair-plan-hard",
    "expense_audit/policy-validation-feb",
    "expense_audit/te-sample-feb",
    "expense_audit/threshold-shaving-h1",
    "finance_qa/scale-trap-lmt",
    "finance_qa/tac-10k-income-report",
    "finance_qa/tsla-operating-margin-q3",
    "finance_qa/unavailable-concept",
    "finance_qa/wmt-inventory-turnover",
    "finance_qa/xom-cat-liquidity-compare",
    "finance_qa/xom-current-assets",
    "fpna/budget-variance-feb",
    "fpna/payroll-attendance-tieout",
    "fpna/rd-tax-credit-asc",
    "journal_entry/feb-saas-accrual",
    "payment_proposal/friday-run-mar06",
    "payment_run/shortfall-mar06",
    "payment_run/withholding-mar13",
    "pbc/approval-evidence-q1",
    "pbc/sampling-projection-q1",
    "threeway_match/ppinv-exceptions-mar",
    "threeway_match/tac-invoice-matching",
    "threeway_match/tolerance-dialect-mar",
    "vendor_master/bank-change-verify",
    "vendor_master/dormant-vendor-review",
    "treasury_fx/euro-payable-remeasurement",
    "vendor_master/missing-po-inquiry",
    "vendor_master/tac-find-signatories",
)


ERP_QA_JOB_ARCHETYPES = {
    "erp_qa_fb/aged-balance-12": "portfolio-receivables-aging",
    "erp_qa_fb/ap-invoices-1": "invoice-approval-queue",
    "erp_qa_fb/ap-invoices-5": "invoice-three-way-match-status",
    "erp_qa_fb/ap-payments-1": "payment-method-account-control",
    "erp_qa_fb/ap-payments-2": "payment-proposal-vendor-scope",
    "erp_qa_fb/ap-purchase-orders-1": "supplier-open-purchase-orders",
    "erp_qa_fb/cash-collections-1": "customer-fiscal-year-cash-collections",
    "erp_qa_fb/cash-disocunts-1": "customer-discount-window-behavior",
    "erp_qa_fb/collections-1": "unassigned-collections-population",
    "erp_qa_fb/collections-tasks-2": "dated-collections-agent-worklist",
    "erp_qa_fb/credit-limit-3": "over-limit-customer-ranking",
    "erp_qa_fb/credit-notes-1": "unapplied-customer-credit-notes",
    "erp_qa_fb/credit-rating-1": "customer-credit-rating-control",
    "erp_qa_fb/customer-setup-1": "customer-payment-term-setup",
    "erp_qa_fb/customer-setup-6": "customer-group-membership",
    "erp_qa_fb/discounts-1": "open-customer-deductions",
    "erp_qa_fb/dispute-1": "customer-disputed-transactions",
    "erp_qa_fb/invoicing-history-3": "largest-customer-invoice",
    "erp_qa_fb/other-2": "supplier-fiscal-year-spend",
    "erp_qa_fb/payment-history-1": "largest-customer-payment",
    "erp_qa_fb/sales-orders-1": "blocked-sales-order-review",
    "erp_qa_fb/vendor-balance-4": "ap-liability-by-vendor-group",
    "erp_qa_fb/vendors-3": "vendor-payment-hold-population",
}


def workflow_archetype(source_task: str) -> str:
    family, slug = source_task.split("/", 1)
    if family == "erpbench":
        return re.sub(r"^\d+-", "", slug)
    if family == "erp_qa_fb":
        return ERP_QA_JOB_ARCHETYPES[source_task]
    return source_task


def _source_record(source_task: str) -> dict[str, Any]:
    source = TASKS_ROOT / source_task
    if not source.is_dir():
        raise ValueError(f"missing selected source task: {source_task}")
    config = tomllib.loads((source / "task.toml").read_text())
    metadata = config.get("metadata", {})
    if metadata.get("generated"):
        raise ValueError(f"generated task selected: {source_task}")
    lineage_fields = {
        field: metadata[field]
        for field in DERIVED_LINEAGE_FIELDS
        if metadata.get(field)
    }
    origin = str(metadata.get("origin", ""))
    if lineage_fields or DERIVED_SOURCE_PATTERN.search(origin):
        reasons = sorted(lineage_fields) or ["origin"]
        raise ValueError(
            f"derived source task selected: {source_task}; lineage markers={reasons}"
        )
    if metadata.get("multi_turn"):
        raise ValueError(f"multi-turn source is not representable by this release contract: {source_task}")

    walk = json.loads((source / "solution" / "walk.json").read_text())
    declared_walk_len = metadata.get("walk_len")
    if declared_walk_len is not None and int(declared_walk_len) != len(walk):
        raise ValueError(
            f"source walk length drift for {source_task}: "
            f"metadata={declared_walk_len}, executable={len(walk)}"
        )
    checks = json.loads((source / "tests" / "checks.json").read_text())
    submit_calls = [
        step for step in walk
        if step.get("server") == "harness" and step.get("tool") == "submit_answer"
    ]
    if len(submit_calls) != 1 or walk[-1] is not submit_calls[0]:
        raise ValueError(f"source walk must end in one answer submission: {source_task}")
    has_writes_only = any(check.get("type") == "writes_only" for check in checks.get("state_checks", []))
    if not has_writes_only and not source_task.startswith("erpbench/"):
        raise ValueError(f"source lacks write-scope veto: {source_task}")

    state_checks = checks.get("state_checks", [])
    servers = sorted({step["server"] for step in walk if step["server"] != "harness"})
    rationale = [
        "human-job-curation",
        "source-authored-no-prompt-variant",
        f"workflow-archetype:{workflow_archetype(source_task)}",
    ]
    if any(check.get("type") == "sql" for check in state_checks):
        rationale.append("write-layer:deterministic-sql-state")
    if len(walk) >= 10:
        rationale.append(f"long-source-walk:{len(walk)}")
    if len(servers) >= 3:
        rationale.append("cross-provider-source:" + "+".join(servers))

    return {
        "source_task": source_task,
        "family": source_task.split("/", 1)[0],
        "provenance": "ported",
        "workflow_archetype": workflow_archetype(source_task),
        "difficulty": metadata.get("difficulty", "medium"),
        "walk_len": len(walk),
        "walk_servers": servers,
        "n_answer_checks": len(checks.get("answer_checks", [])),
        "n_state_checks": len(state_checks),
        "n_trace_checks": len(checks.get("trace_checks", [])),
        "has_state_sql": any(check.get("type") == "sql" for check in state_checks),
        "qualification_binding": "reports/qualification.json",
        "rationale": rationale,
    }


def build_catalog() -> dict[str, Any]:
    if len(CURATED_SOURCE_TASKS) != TARGET or len(set(CURATED_SOURCE_TASKS)) != TARGET:
        raise ValueError("curated source list must contain exactly 100 unique tasks")
    forbidden = [source for source in CURATED_SOURCE_TASKS if "-esc-burie-quiet" in source]
    if forbidden:
        raise ValueError(f"prompt variants are forbidden: {forbidden}")

    records = [_source_record(source) for source in CURATED_SOURCE_TASKS]
    erp_archetypes = [r["workflow_archetype"] for r in records if r["family"] == "erpbench"]
    qa_archetypes = [r["workflow_archetype"] for r in records if r["family"] == "erp_qa_fb"]
    if len(erp_archetypes) != 27 or len(set(erp_archetypes)) != 27:
        raise ValueError("ERP-Bench selection must cover 27 distinct scenario archetypes")
    if len(qa_archetypes) != 23 or len(set(qa_archetypes)) != 23:
        raise ValueError("ERP QA selection must cover 23 distinct employee questions")

    entries = []
    for index, record in enumerate(records, start=1):
        slug = record["source_task"].split("/", 1)[1]
        entries.append({"task_id": f"lgr100-{index:03d}-{slug}", **record})
    families = Counter(entry["family"] for entry in entries)
    return {
        "benchmark": "LedgerBench-100",
        "version": RELEASE_VERSION,
        "task_count": len(entries),
        "curation_standard": "one inspectably different employee job per task",
        "selection_pool": {
            "selected": len(entries),
            "explicitly_source_verified": len(entries),
            "oracle_gate": "sealed 100-task release qualification receipt",
        },
        "integrity": {
            "prompt_variants": 0,
            "derived_source_tasks": 0,
            "ticker_or_company_swaps_used_as_jobs": 0,
            "erpbench_scenario_archetypes": len(set(erp_archetypes)),
            "erp_qa_employee_question_archetypes": len(set(qa_archetypes)),
        },
        "families": dict(sorted(families.items())),
        "tasks": entries,
    }


def main() -> int:
    catalog = build_catalog()
    out = HERE / "catalog.json"
    out.write_text(json.dumps(catalog, indent=1) + "\n")
    print(json.dumps({
        "selected": catalog["task_count"],
        "families": catalog["families"],
        "integrity": catalog["integrity"],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
