#!/usr/bin/env python3
"""TaskSpec — the normalised representation every source corpus maps into.

Adapters are the only per-corpus code; bind/emit/gate are shared. See docs/INGESTION.md.
"""
from dataclasses import dataclass, field, asdict
from typing import Any

# The five porting classes. A corpus is never silently skipped; it is classified.
CLASSES = ("verbatim_gt", "recomputable", "judgement_port", "needs_surface", "not_agentic")

@dataclass
class GroundTruth:
    field_name: str
    kind: str                    # number | contains_all | yes_no | none_answer | scale | sql
    expect: Any = None
    gt_sql: str | None = None    # re-derivable truth; required where the world can compute it
    tol_abs: float | None = None
    tol_rel: float | None = None
    forbid: list[str] = field(default_factory=list)
    stated_type: str | None = None   # what the instruction promises the field is (A10.2 gate)

@dataclass
class TaskSpec:
    # provenance — not optional
    source_repo: str
    source_path: str
    source_id: str
    licence: str

    portability: str             # one of CLASSES
    question: str                # verbatim where the corpus is the eval
    family: str = "unclassified"
    persona: str | None = None

    entities: list[str] = field(default_factory=list)       # must bind strictly
    capabilities: list[str] = field(default_factory=list)   # servers/tables required
    ground_truth: list[GroundTruth] = field(default_factory=list)
    naive_baseline: dict | None = None                      # {strategy, answer}
    graded_answer: str | None = None
    dropped: list[str] = field(default_factory=list)        # what the port does not carry, and why
    notes: str = ""

    # filled by bind()
    bind_status: str | None = None      # bound | absent_entity | missing_capability
    bind_detail: str = ""

    def as_dict(self): return asdict(self)

    def validate(self):
        errs = []
        if self.portability not in CLASSES: errs.append(f"unknown class {self.portability}")
        if not self.question.strip(): errs.append("empty question")
        if not self.source_id: errs.append("no source id")
        if self.portability in ("verbatim_gt", "recomputable") and not self.ground_truth:
            errs.append("checkable class with no ground truth")
        if self.naive_baseline and self.graded_answer:
            if str(self.naive_baseline.get("answer")).strip() == str(self.graded_answer).strip():
                errs.append("naive == graded (would collapse; S12)")
        for g in self.ground_truth:
            if g.stated_type and g.kind == "yes_no" and g.stated_type not in ("yes/no", "yes_no"):
                errs.append(f"{g.field_name}: instruction promises '{g.stated_type}' but check grades polarity (A10.2)")
        return errs
