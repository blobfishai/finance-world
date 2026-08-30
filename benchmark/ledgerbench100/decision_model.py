"""Graded control-date decision model for every LedgerBench-100 case (v3.4.2).

Each released case carries one deterministic decision model layered on the
authored decision (``decision_specs.py``).  The model is the reasoning chain a
finance operator works before closing a case:

* requirement — the amount the current control requires to be supported, derived
  by summing the in-scope ``DecisionScopeLines`` records in the ERP (H2);
* coverage — the gross support on the current evidence register, the rows the
  control excludes (disputed, out-of-period, duplicate) and the usable remainder,
  corroborated by the counterparty's own message (H3);
* gap — the exception amount netted against the policy tolerance (H4);
* external constraint — the counterparty's committed correction date and holding
  charge, read from its own message (H5);
* internal constraint — the close calendar's posting window and lead times (H6);
* alternatives — three costed timing options with authority status, exactly one
  recommended, one requiring approval beyond current authority and one feasible
  but inferior or unsupported (H7/H8);
* control comparison — the requester's documented need-by date, the signed
  variance and an honest timing status (H9);
* authority — the approved Dynamics approval request applied to the selected
  scope while the pending exception request stays untouched (H10).

Every value below is seeded into the world as raw facts (never as a computed
result) and every derived value is graded as its own answer field (H13).  The
arithmetic is integer cents so the seeded facts and the graded expectations can
never drift apart.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any

from decision_specs import DecisionSpec

OPTION_PROCEED = "proceed_within_authority"
OPTION_HOLD = "hold_for_counterparty_correction"
OPTION_EXCEPTION = "proceed_with_exception_approval"
OPTION_IDS = (OPTION_PROCEED, OPTION_HOLD, OPTION_EXCEPTION)

WITHIN_AUTHORITY = "WITHIN_AUTHORITY"
ADDITIONAL_APPROVAL_REQUIRED = "ADDITIONAL_APPROVAL_REQUIRED"
AVAILABLE_NOT_RECOMMENDED = "AVAILABLE_NOT_RECOMMENDED"
NOT_SUPPORTED_BY_CURRENT_EVIDENCE = "NOT_SUPPORTED_BY_CURRENT_EVIDENCE"

TOLERANCE_CHOICES = (0.5, 1.0, 2.0)

# Answer fields graded for every task, keyed by the reasoning hop they prove.
CHAIN_FIELDS: dict[str, tuple[str, ...]] = {
    "H1": ("case_id",),
    "H2": ("control_requirement_usd",),
    "H3": ("observed_support_usd", "excluded_support_usd", "usable_support_usd"),
    "H4": ("exception_usd", "exception_within_tolerance"),
    "H5": ("external_constraint_date",),
    "H6": ("posting_window_close_date",),
    "H7": tuple(f"{option}_outcome_date" for option in OPTION_IDS),
    "H8": ("recommended_option", "recommended_outcome_date", "recommended_incremental_cost_usd"),
    "H9": ("business_need_date", "outcome_vs_control_days", "decision_timing_status"),
    "H10": ("approval_request_id", "approval_authority_limit_usd", "escalation_approval_required"),
    "H12": ("binding_constraint_date",),
}
CHAIN_ANSWER_FIELDS: tuple[str, ...] = tuple(
    name for names in CHAIN_FIELDS.values() for name in names
)


@dataclass(frozen=True)
class FamilyProfile:
    scope_noun: str
    doc_prefix: str
    support_noun: str
    exclusion_reasons: tuple[str, str, str]
    party_name: str
    party_address: str
    correction_noun: str
    hold_charge_noun: str
    proceed_verb: str
    control_basis: str


_PROFILES: dict[str, FamilyProfile] = {
    "anomaly_triage": FamilyProfile("vendor invoices proposed for release", "AP-INV", "settled-history and purchase-order matches", ("duplicate of a settled invoice", "disputed by the vendor", "outside the run period"), "Halden Freight accounts receivable", "ar@halden-freight.example", "corrected invoice and credit note", "late-payment charge", "release", "vendor invoice with purchase-order, receipt and settlement support"),
    "bank_rec": FamilyProfile("bank lines awaiting ledger match", "BNK-LN", "ledger and settlement matches", ("returned by the bank", "outside the statement period", "matched twice"), "First National treasury services", "confirmations@firstnational-bank.example", "corrected return advice", "returned-item fee", "clear", "bank line with a same-date ledger posting"),
    "business_brief": FamilyProfile("disclosure items required by the brief", "BRF-ITM", "filed-fact citations", ("superseded by an amended filing", "different fiscal basis", "cited twice"), "Registrant investor relations", "ir@registrant-filings.example", "confirmed amended-filing citation", "re-issue fee", "issue", "brief item supported by a same-basis filed fact"),
    "business_brief_fb": FamilyProfile("disclosure items required by the brief", "BRF-ITM", "filed-fact citations", ("superseded by an amended filing", "different fiscal basis", "cited twice"), "Registrant investor relations", "ir@registrant-filings.example", "confirmed amended-filing citation", "re-issue fee", "issue", "brief item supported by a same-basis filed fact"),
    "cash_app": FamilyProfile("customer receipts awaiting application", "RCPT", "remittance and invoice matches", ("disputed by the customer", "outside the deposit period", "applied twice"), "Lamna Healthcare accounts payable", "ap@lamna-healthcare.example", "corrected remittance advice", "re-application charge", "apply", "receipt with remittance detail and an open invoice"),
    "cash_forecast": FamilyProfile("committed cash flows in the forecast horizon", "CFL", "dated commitment evidence", ("contested by the counterparty", "outside the forecast week", "counted twice"), "Northwind Bank relationship desk", "relationship@northwind-bank.example", "confirmed facility draw date", "facility fee", "commit", "cash flow with a dated commitment"),
    "close_mgmt": FamilyProfile("close entries awaiting certification", "CLS-JE", "reconciled-balance support", ("out of period", "disputed by the subledger owner", "reversed and re-posted"), "Northwind Assurance LLP audit team", "pbc@northwind-assurance.example", "confirmed balance confirmation", "audit overtime billing", "certify", "close entry tied to a reconciled balance"),
    "collections_ops": FamilyProfile("overdue receivables in the dunning scope", "AR-INV", "delivery and acceptance evidence", ("disputed by the customer", "outside the dunning window", "credited twice"), "Sparrow Retail accounts payable", "ap@sparrow-retail.example", "corrected acceptance confirmation", "late-payment interest", "escalate", "receivable with delivery and acceptance evidence"),
    "cross_system": FamilyProfile("cross-system balances to reconcile", "XSYS", "matched transaction evidence", ("timing difference across systems", "outside the period", "recorded in both systems"), "CES Direct LLC controller's office", "controller@ces-direct.example", "confirmed subsidiary balance", "re-close charge", "certify", "balance supported in both systems"),
    "erp_qa": FamilyProfile("open transactions in the reported balance", "TXN", "live settlement evidence", ("disputed by the counterparty", "outside the as-of date", "settled twice"), "Fourth Coffee accounts payable", "ap@fourth-coffee.example", "corrected statement", "re-issue charge", "report", "open transaction supported by live settlement data"),
    "erp_qa_fb": FamilyProfile("open transactions in the reported population", "TXN", "live settlement evidence", ("disputed by the counterparty", "outside the as-of date", "settled twice"), "Birch Company accounts payable", "ap@birch-company.example", "corrected statement", "re-issue charge", "report", "open transaction supported by live settlement data"),
    "erpbench": FamilyProfile("purchase and production commitments in the plan", "PLN", "supplier and workcenter confirmations", ("supplier capacity not confirmed", "outside the promise window", "component promised twice"), "Volt Components supply desk", "orders@volt-components.example", "confirmed expedited delivery date", "expedite surcharge", "commit", "commitment with confirmed supply and capacity"),
    "expense_audit": FamilyProfile("expense claims in the sampled file", "EXP", "receipt and approval evidence", ("receipt disputed", "outside the claim period", "claimed twice"), "Concur receipt-recovery desk", "receipts@concur-recovery.example", "recovered receipt set", "re-audit charge", "release", "claim with receipt, attendee and approval evidence"),
    "finance_qa": FamilyProfile("metric inputs required by the request", "MTR", "filed-fact citations", ("superseded by an amended filing", "different fiscal basis", "cited twice"), "Registrant investor relations", "ir@registrant-filings.example", "confirmed amended-filing citation", "re-issue fee", "issue", "metric input supported by a same-basis filed fact"),
    "finance_qa_fb": FamilyProfile("metric inputs required by the request", "MTR", "filed-fact citations", ("superseded by an amended filing", "different fiscal basis", "cited twice"), "Registrant investor relations", "ir@registrant-filings.example", "confirmed amended-filing citation", "re-issue fee", "issue", "metric input supported by a same-basis filed fact"),
    "fixed_assets": FamilyProfile("asset costs awaiting capitalization disposition", "FA-COST", "supplier-scope and ready-for-use evidence", ("incurred after ready-for-use", "period training expense", "included twice in the asset basis"), "Atlas Industrial project controls", "closeout@atlas-industrial.example", "confirmed commissioning and cost split", "closeout support charge", "capitalize", "cost directly attributable before the asset became ready for use"),
    "fpna": FamilyProfile("variance and payroll lines under review", "FPA", "approved-baseline support", ("baseline superseded", "outside the review period", "loaded twice"), "Payroll bureau service desk", "service@payroll-bureau.example", "corrected register extract", "off-cycle processing fee", "release", "line supported by the approved baseline"),
    "journal_entry": FamilyProfile("accrual lines for the period", "ACC", "service-period contract support", ("service outside the period", "disputed by the vendor", "accrued twice"), "CloudScale billing operations", "billing@cloudscale.example", "corrected service statement", "re-billing charge", "post", "accrual line supported by contract and service evidence"),
    "payment_proposal": FamilyProfile("invoices in the payment proposal", "PP-INV", "three-way match support", ("disputed by the vendor", "outside the pay-date window", "proposed twice"), "Halden Freight accounts receivable", "ar@halden-freight.example", "corrected invoice", "late-payment charge", "release", "invoice with purchase-order and receipt support"),
    "payment_run": FamilyProfile("obligations in the payment run", "PR-INV", "three-way match support", ("disputed by the vendor", "outside the run period", "presented twice"), "Contoso contractor billing desk", "billing@contractor-collective.example", "corrected invoice and certificate", "late-payment charge", "commit", "obligation with match and tax-profile support"),
    "pbc": FamilyProfile("sampled items in the auditor request", "PBC", "immutable approval evidence", ("approval disputed", "outside the sample period", "sampled twice"), "Northwind Assurance LLP audit team", "pbc@northwind-assurance.example", "confirmed sample extension", "audit overtime billing", "issue", "sampled item with immutable approval evidence"),
    "revenue_accounting": FamilyProfile("performance-obligation allocations awaiting close disposition", "REV-OBL", "contract, standalone-price, and acceptance evidence", ("service not yet transferred", "outside the recognition period", "allocated twice"), "Northwind Health Systems procurement", "acceptance@northwind-health.example", "confirmed acceptance and service commencement", "contract review charge", "recognize", "consideration allocated on relative standalone selling prices to a satisfied obligation"),
    "threeway_match": FamilyProfile("invoices awaiting match disposition", "TW-INV", "purchase-order and receipt matches", ("price disputed by the supplier", "outside the receipt period", "receipted twice"), "Halden Freight accounts receivable", "ar@halden-freight.example", "corrected invoice", "late-payment charge", "release", "invoice with purchase-order and receipt support"),
    "treasury_fx": FamilyProfile("foreign-currency monetary balances awaiting close measurement", "FX-BAL", "payable-status and approved-rate evidence", ("settlement quote outside the close date", "unapproved rate type", "remeasured twice"), "Lumina Components treasury desk", "treasury@lumina-components.example", "confirmed payable and settlement date", "rate-lock charge", "remeasure", "open monetary item measured at the governed closing spot rate"),
    "vendor_master": FamilyProfile("vendor records under review", "VND", "verified master-data evidence", ("callback disputed", "outside the review window", "recorded twice"), "Vendor compliance desk", "compliance@vendor-verify.example", "completed callback verification", "re-verification fee", "release", "vendor record with verified master-data evidence"),
}


def family_profile(family: str) -> FamilyProfile:
    try:
        return _PROFILES[family]
    except KeyError as error:
        raise KeyError(f"no decision-model profile for family {family!r}") from error


def _iso(value: dt.date) -> str:
    return value.isoformat()


def _money(cents: int) -> float:
    return round(cents / 100, 2)


class _Draw:
    """Tiny deterministic integer generator (LCG) keyed by the task number."""

    def __init__(self, number: int) -> None:
        self.state = (number * 2654435761 + 40503) % (2**32)

    def __call__(self, low: int, high: int) -> int:
        self.state = (1103515245 * self.state + 12345) % (2**31)
        return low + (self.state >> 8) % (high - low + 1)


def hold_recommended(spec: DecisionSpec) -> bool:
    """Cases whose authored decision keeps the item held wait for the counterparty."""

    code = spec.decision_code
    return "HOLD" in code or code.startswith("ESCALATE") or code == "REPORT_METRIC_UNAVAILABLE"


@dataclass(frozen=True)
class ControlModel:
    case_id: str
    decoy_case_id: str
    profile: FamilyProfile
    lines: list[dict[str, Any]]
    decoy_lines: list[dict[str, Any]]
    support_rows: list[dict[str, Any]]
    stale_support_rows: list[dict[str, Any]]
    requirement_cents: int
    observed_cents: int
    excluded_cents: int
    usable_cents: int
    exception_cents: int
    tolerance_pct: float
    tolerance_cents: int
    within_tolerance: bool
    external_date: str
    hold_charge_cents: int
    posting_window_close: str
    standard_lead_days: int
    exception_lead_days: int
    exception_levy_cents: int
    business_need_date: str
    authority_limit_cents: int
    approval_policy_id: str
    exception_policy_id: str
    approval_request_id: str
    exception_request_id: str
    options: list[dict[str, Any]]
    recommended_option: str
    recommended_outcome: str
    recommended_cost_cents: int
    binding_constraint_date: str
    binding_constraint_label: str
    outcome_vs_control_days: int
    timing_status: str
    answers: dict[str, Any] = field(default_factory=dict)

    @property
    def requirement(self) -> float:
        return _money(self.requirement_cents)

    @property
    def usable(self) -> float:
        return _money(self.usable_cents)

    @property
    def exception(self) -> float:
        return _money(self.exception_cents)

    @property
    def authority_limit(self) -> float:
        return _money(self.authority_limit_cents)


def control_model(number: int, task_id: str, family: str, spec: DecisionSpec, world_now: str) -> ControlModel:
    """Derive the complete, self-consistent decision model for one case."""

    profile = family_profile(family)
    draw = _Draw(number)
    today = dt.date.fromisoformat(world_now[:10])
    case_id = f"WORKITEM-{number:03d}"
    decoy_case_id = f"WORKITEM-2025-{number:03d}"
    hold = hold_recommended(spec)

    # --- requirement: in-scope documents in the ERP -------------------------
    line_count = 2 + draw(0, 2)
    lines: list[dict[str, Any]] = []
    for index in range(1, line_count + 1):
        amount = draw(1800, 24000) * 100 + draw(0, 99)
        lines.append(
            {
                "case_id": case_id,
                "line": index,
                "document_ref": f"{profile.doc_prefix}-{number:03d}{index}",
                "description": f"{profile.scope_noun} line {index}",
                "amount": _money(amount),
                "currency": "USD",
                "control_basis": profile.control_basis,
                "_cents": amount,
            }
        )
    requirement = sum(line["_cents"] for line in lines)
    decoy_lines = [
        {
            **line,
            "case_id": decoy_case_id,
            "document_ref": f"{profile.doc_prefix}-25{number:03d}{line['line']}",
            "description": f"{profile.scope_noun} line {line['line']} (FY2025 cycle)",
            "amount": _money(line["_cents"] + draw(100, 900) * 100),
        }
        for line in lines
    ]

    # --- tolerance and gap ---------------------------------------------------
    tolerance_pct = TOLERANCE_CHOICES[draw(0, len(TOLERANCE_CHOICES) - 1)]
    tolerance = int(round(requirement * tolerance_pct / 100))
    if hold:
        exception = tolerance + draw(500, 5000) * 100 + draw(0, 99)
    else:
        exception = max(100, draw(100, max(100, tolerance - 100)))
    usable = requirement - exception
    if usable <= 0:
        raise ValueError(f"{case_id} usable support must stay positive")

    # --- coverage: register rows with exclusions -----------------------------
    excluded_count = 1 + draw(0, 1)
    supported_count = 2 + draw(0, 2)
    excluded_rows: list[int] = [draw(300, 3000) * 100 + draw(0, 99) for _ in range(excluded_count)]
    supported_rows: list[int] = []
    remaining = usable
    for index in range(supported_count - 1):
        share = draw(15, 45)
        portion = max(100, remaining * share // 100)
        supported_rows.append(portion)
        remaining -= portion
    if remaining <= 0:
        raise ValueError(f"{case_id} support partition failed")
    supported_rows.append(remaining)
    excluded = sum(excluded_rows)
    observed = usable + excluded

    reasons = profile.exclusion_reasons
    support_rows: list[dict[str, Any]] = []
    row_number = 0
    exclusion_positions = {draw(0, supported_count + excluded_count - 1)}
    while len(exclusion_positions) < excluded_count:
        exclusion_positions.add(draw(0, supported_count + excluded_count - 1))
    excluded_iter = iter(excluded_rows)
    supported_iter = iter(supported_rows)
    reason_offset = draw(0, 2)
    for position in range(supported_count + excluded_count):
        row_number += 1
        line_ref = lines[(position) % line_count]["document_ref"]
        if position in exclusion_positions:
            cents = next(excluded_iter)
            reason = reasons[(reason_offset + len([r for r in support_rows if r["status"] != "supported"])) % 3]
            support_rows.append(
                {
                    "support_ref": f"SUP-{number:03d}-{row_number}",
                    "document_ref": line_ref,
                    "amount": _money(cents),
                    "status": "excluded",
                    "reason": reason,
                    "_cents": cents,
                }
            )
        else:
            cents = next(supported_iter)
            support_rows.append(
                {
                    "support_ref": f"SUP-{number:03d}-{row_number}",
                    "document_ref": line_ref,
                    "amount": _money(cents),
                    "status": "supported",
                    "reason": "current-revision support",
                    "_cents": cents,
                }
            )
    if sum(r["_cents"] for r in support_rows if r["status"] == "supported") != usable:
        raise ValueError(f"{case_id} supported rows do not sum to usable support")
    if sum(r["_cents"] for r in support_rows if r["status"] != "supported") != excluded:
        raise ValueError(f"{case_id} excluded rows do not sum to the exclusion")
    stale_support_rows = [
        {**row, "status": "supported", "reason": "prior tracker treated every row as support"}
        for row in support_rows
    ]

    # --- constraints -----------------------------------------------------------
    standard_lead = 1 + draw(0, 2)
    exception_lead = draw(0, 1)
    posting_window_close = today + dt.timedelta(days=4 + draw(0, 5))
    external_date = today + dt.timedelta(days=3 + draw(0, 11))
    business_need = today + dt.timedelta(days=1 + draw(0, 9))
    hold_charge = draw(3, 30) * 2500
    exception_levy = draw(8, 40) * 5000
    authority_limit = ((requirement // 500000) + 1 + draw(0, 3)) * 500000

    proceed_outcome = today + dt.timedelta(days=standard_lead)
    hold_outcome = external_date + dt.timedelta(days=standard_lead)
    exception_outcome = today + dt.timedelta(days=exception_lead)
    if proceed_outcome > posting_window_close:
        raise ValueError(f"{case_id} standard lead time falls outside the posting window")

    approval_policy_id = f"DOA-CASE-{number:03d}"
    exception_policy_id = f"DOA-CASE-EXC-{number:03d}"
    approval_request_id = f"APR-CASE-{number:03d}"
    exception_request_id = f"APR-EXC-{number:03d}"

    verb = profile.proceed_verb
    if hold:
        recommended = OPTION_HOLD
        proceed_status = NOT_SUPPORTED_BY_CURRENT_EVIDENCE
        hold_status = WITHIN_AUTHORITY
    else:
        recommended = OPTION_PROCEED
        proceed_status = WITHIN_AUTHORITY
        hold_status = AVAILABLE_NOT_RECOMMENDED
    outcomes = {
        OPTION_PROCEED: _iso(proceed_outcome),
        OPTION_HOLD: _iso(hold_outcome),
        OPTION_EXCEPTION: _iso(exception_outcome),
    }
    costs = {OPTION_PROCEED: 0, OPTION_HOLD: hold_charge, OPTION_EXCEPTION: exception_levy}
    statuses = {
        OPTION_PROCEED: proceed_status,
        OPTION_HOLD: hold_status,
        OPTION_EXCEPTION: ADDITIONAL_APPROVAL_REQUIRED,
    }
    reasons_by_option = {
        OPTION_PROCEED: (
            f"{verb.title()} the supported {_money(usable):,.2f} USD after the {standard_lead}-day standard lead time; "
            + (
                f"the {_money(exception):,.2f} USD exception is within the {tolerance_pct}% tolerance, so this stays inside {approval_request_id}."
                if not hold
                else f"the {_money(exception):,.2f} USD exception exceeds the {tolerance_pct}% tolerance, so the current evidence does not support acting now."
            )
        ),
        OPTION_HOLD: (
            f"Wait for the {profile.party_name}'s {profile.correction_noun} committed for {_iso(external_date)}, then {verb} after the standard lead time; "
            f"the counterparty's documented {profile.hold_charge_noun} of {_money(hold_charge):,.2f} USD applies."
            + ("" if hold else " Feasible, but later and costlier than acting within authority.")
        ),
        OPTION_EXCEPTION: (
            f"{verb.title()} the full {_money(requirement):,.2f} USD after the {exception_lead}-day exception lead time under {exception_request_id}; "
            f"requires CFO approval beyond {approval_request_id} and carries the {_money(exception_levy):,.2f} USD exception levy."
        ),
    }
    labels = {
        OPTION_PROCEED: f"{verb.title()} the supported scope now within current authority",
        OPTION_HOLD: f"Hold for the counterparty's {profile.correction_noun}",
        OPTION_EXCEPTION: f"{verb.title()} the full scope under a CFO exception approval",
    }
    options = [
        {
            "id": option,
            "label": labels[option],
            "reason": reasons_by_option[option],
            "selected": option == recommended,
            "recommended": option == recommended,
            "outcome": outcomes[option],
            "outcome_field": f"{option}_outcome_date",
            "incremental_cost": _money(costs[option]),
            "authority_status": statuses[option],
        }
        for option in OPTION_IDS
    ]
    recommended_outcome_date = dt.date.fromisoformat(outcomes[recommended])
    if hold:
        binding_date, binding_label = _iso(external_date), f"counterparty {profile.correction_noun} commitment"
    else:
        binding_date, binding_label = _iso(posting_window_close), "posting window close"
    variance = (recommended_outcome_date - business_need).days
    timing_status = "ON_TIME" if variance <= 0 else "LATE"

    answers: dict[str, Any] = {
        "case_id": case_id,
        "control_requirement_usd": _money(requirement),
        "observed_support_usd": _money(observed),
        "excluded_support_usd": _money(excluded),
        "usable_support_usd": _money(usable),
        "exception_usd": _money(exception),
        "exception_within_tolerance": "yes" if exception <= tolerance else "no",
        "external_constraint_date": _iso(external_date),
        "posting_window_close_date": _iso(posting_window_close),
        f"{OPTION_PROCEED}_outcome_date": outcomes[OPTION_PROCEED],
        f"{OPTION_HOLD}_outcome_date": outcomes[OPTION_HOLD],
        f"{OPTION_EXCEPTION}_outcome_date": outcomes[OPTION_EXCEPTION],
        "recommended_option": recommended,
        "recommended_outcome_date": outcomes[recommended],
        "recommended_incremental_cost_usd": _money(costs[recommended]),
        "business_need_date": _iso(business_need),
        "outcome_vs_control_days": variance,
        "decision_timing_status": timing_status,
        "approval_request_id": approval_request_id,
        "approval_authority_limit_usd": _money(authority_limit),
        "escalation_approval_required": 1,
        "binding_constraint_date": binding_date,
    }
    if set(answers) != set(CHAIN_ANSWER_FIELDS):
        raise ValueError("decision model answers drifted from CHAIN_FIELDS")

    return ControlModel(
        case_id=case_id,
        decoy_case_id=decoy_case_id,
        profile=profile,
        lines=lines,
        decoy_lines=decoy_lines,
        support_rows=support_rows,
        stale_support_rows=stale_support_rows,
        requirement_cents=requirement,
        observed_cents=observed,
        excluded_cents=excluded,
        usable_cents=usable,
        exception_cents=exception,
        tolerance_pct=tolerance_pct,
        tolerance_cents=tolerance,
        within_tolerance=exception <= tolerance,
        external_date=_iso(external_date),
        hold_charge_cents=hold_charge,
        posting_window_close=_iso(posting_window_close),
        standard_lead_days=standard_lead,
        exception_lead_days=exception_lead,
        exception_levy_cents=exception_levy,
        business_need_date=_iso(business_need),
        authority_limit_cents=authority_limit,
        approval_policy_id=approval_policy_id,
        exception_policy_id=exception_policy_id,
        approval_request_id=approval_request_id,
        exception_request_id=exception_request_id,
        options=options,
        recommended_option=recommended,
        recommended_outcome=outcomes[recommended],
        recommended_cost_cents=costs[recommended],
        binding_constraint_date=binding_date,
        binding_constraint_label=binding_label,
        outcome_vs_control_days=variance,
        timing_status=timing_status,
        answers=answers,
    )


def answer_checks(model: ControlModel) -> list[dict[str, Any]]:
    """Deterministic answer checks for every graded decision-model field."""

    answers = model.answers
    checks: list[dict[str, Any]] = [
        {"field": "case_id", "type": "contains_all", "expect": [model.case_id], "forbid": [model.decoy_case_id]},
    ]
    for name in ("control_requirement_usd", "observed_support_usd", "excluded_support_usd", "usable_support_usd", "exception_usd"):
        checks.append({"field": name, "type": "number", "expect": answers[name], "tol_abs": 0.01})
    checks.append({"field": "exception_within_tolerance", "type": "yes_no", "expect": answers["exception_within_tolerance"]})
    for name in ("external_constraint_date", "posting_window_close_date", *CHAIN_FIELDS["H7"]):
        checks.append({"field": name, "type": "string", "expect": answers[name]})
    checks.append({"field": "recommended_option", "type": "string", "expect": model.recommended_option})
    checks.append({"field": "recommended_outcome_date", "type": "string", "expect": model.recommended_outcome})
    checks.append({"field": "recommended_incremental_cost_usd", "type": "number", "expect": answers["recommended_incremental_cost_usd"], "tol_abs": 0.01})
    checks.append({"field": "business_need_date", "type": "string", "expect": model.business_need_date})
    checks.append({"field": "outcome_vs_control_days", "type": "number", "expect": model.outcome_vs_control_days, "tol_abs": 0})
    checks.append({"field": "decision_timing_status", "type": "string", "expect": model.timing_status})
    checks.append({"field": "approval_request_id", "type": "contains_all", "expect": [model.approval_request_id], "forbid": [model.exception_request_id]})
    checks.append({"field": "approval_authority_limit_usd", "type": "number", "expect": answers["approval_authority_limit_usd"], "tol_abs": 0.01})
    checks.append({"field": "escalation_approval_required", "type": "number", "expect": 1, "tol_abs": 0})
    checks.append({"field": "binding_constraint_date", "type": "string", "expect": model.binding_constraint_date})
    if [check["field"] for check in checks] != list(CHAIN_ANSWER_FIELDS):
        raise ValueError("answer checks drifted from CHAIN_FIELDS order")
    return checks


def answer_schema_rows(model: ControlModel, first_ordinal: int) -> list[tuple[int, str, str, str]]:
    """Reporting-schema rows the harness exposes through ``reporting_fields``."""

    verb = model.profile.proceed_verb
    planning_scope = model.profile.scope_noun == "purchase and production commitments in the plan"
    descriptions: dict[str, tuple[str, str]] = {
        "case_id": ("text", "immutable DecisionWorkItems identifier of the open work item this filing resolves"),
        "control_requirement_usd": ("number", "USD the current control requires to be supported before the case can close"),
        "observed_support_usd": ("number", "USD of gross support listed on the current evidence register before any exclusion"),
        "excluded_support_usd": ("number", "USD of listed support the current control excludes"),
        "usable_support_usd": ("number", "USD of support that remains usable after the exclusions"),
        "exception_usd": ("number", "USD of the requirement that current evidence does not support"),
        "exception_within_tolerance": ("yes/no", "is the unsupported exception within the current control's tolerance"),
        "external_constraint_date": ("date", "date the counterparty has committed, in its own message, to deliver its correction"),
        "posting_window_close_date": (
            "date",
            (
                "last date of the approved factory planning window"
                if planning_scope
                else "last posting date of the current close window"
            ),
        ),
        f"{OPTION_PROCEED}_outcome_date": ("date", f"date on which the option {OPTION_PROCEED} would {verb} the supported scope"),
        f"{OPTION_HOLD}_outcome_date": ("date", f"date on which the option {OPTION_HOLD} would {verb} the full scope"),
        f"{OPTION_EXCEPTION}_outcome_date": ("date", f"date on which the option {OPTION_EXCEPTION} would {verb} the full scope"),
        "recommended_option": ("text", "identifier of the timing option the current control supports"),
        "recommended_outcome_date": ("date", "outcome date produced by the selected option"),
        "recommended_incremental_cost_usd": ("number", "documented incremental cost of the selected option in USD; 0 when there is none"),
        "business_need_date": ("date", "date by which the requester documented needing the outcome"),
        "outcome_vs_control_days": ("number", "selected outcome date minus the business need date in days; positive means late"),
        "decision_timing_status": ("text", "ON_TIME when the selected outcome is on or before the business need date, otherwise LATE"),
        "approval_request_id": ("text", "identifier of the approved Dynamics approval request that authorizes the selected scope"),
        "approval_authority_limit_usd": ("number", "USD limit of the approval authority that governs this case"),
        "escalation_approval_required": ("number", "1 when an option in the control's option set needs approval beyond current authority, otherwise 0"),
        "binding_constraint_date": ("date", "date of the constraint that binds the selected option"),
    }
    rows: list[tuple[int, str, str, str]] = []
    for offset, name in enumerate(CHAIN_ANSWER_FIELDS):
        kind, description = descriptions[name]
        rows.append((first_ordinal + offset, name, kind, description))
    return rows


def slugless(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
