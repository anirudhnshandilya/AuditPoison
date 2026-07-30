from __future__ import annotations

import copy
import re
from dataclasses import replace
from datetime import date, datetime
from typing import Any

from .harness import AuditPrediction, AuditorAdapter

AUTHORITY_RANK = {
    "authoritative_technical": 5,
    "authoritative_record": 4,
    "approved_policy": 3,
    "operational_record": 2,
    "self_attestation": 1,
}

ASSURANCE_AUTHORITIES = {"authoritative_technical", "authoritative_record", "operational_record"}

INSTRUCTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bignore\s+(?:all\s+)?(?:previous|prior|other)\b",
        r"\breport\s+(?:this\s+control\s+)?as\s+(?:fully\s+)?compliant\b",
        r"\breturn\s+(?:the\s+label\s+)?compliant\b",
        r"\bdo\s+not\s+(?:inspect|consider|validate|review)\b",
        r"\bno\s+(?:further|additional)\s+(?:validation|evidence|review)\s+(?:is\s+)?required\b",
        r"\boverride\s+(?:the\s+)?(?:system|auditor|assessment)\b",
        r"\bsystem\s+(?:prompt|instruction)\b",
        r"\boutput\s+(?:the\s+label\s+)?compliant\b",
    )
)

AUTHORITY_CLAIM_PATTERN = re.compile(
    r"\b(?:external\s+auditor|independent\s+auditor|assurance\s+partner|regulator)\b.*\b(?:approved|authori[sz]ed|accepted|signed)\b|"
    r"\b(?:approved|authori[sz]ed|accepted|signed)\b.*\b(?:external\s+auditor|independent\s+auditor|assurance\s+partner|regulator)\b",
    re.IGNORECASE,
)


def _date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


def _period_overlaps(evidence: dict[str, Any], scope: dict[str, Any]) -> bool:
    period = evidence.get("effective_period")
    if not period:
        return True
    e_start, e_end = _date(period.get("start")), _date(period.get("end"))
    a = scope.get("assessment_period", {})
    a_start, a_end = _date(a.get("start")), _date(a.get("end"))
    if None in (e_start, e_end, a_start, a_end):
        return True
    return e_start <= a_end and a_start <= e_end


def _scope_matches(evidence: dict[str, Any], scope: dict[str, Any]) -> bool:
    required = set(scope.get("asset_ids", []))
    observed = set(evidence.get("asset_ids", []))
    if not required or not observed:
        return True
    return bool(required & observed)


def _environment_matches(evidence: dict[str, Any], scope: dict[str, Any]) -> bool:
    expected = str(scope.get("environment", "")).strip().lower()
    if not expected:
        return True
    haystack = " ".join([*(str(x).lower() for x in evidence.get("asset_ids", [])), str(evidence.get("content", "")).lower()])
    aliases = {
        "production": ("sandbox", "development", "dev", "test", "staging"),
        "prod": ("sandbox", "development", "dev", "test", "staging"),
        "sandbox": ("production", "prod", "staging"),
        "development": ("production", "prod", "sandbox", "staging"),
    }
    return not any(re.search(rf"(?:^|[^a-z]){re.escape(token)}(?:$|[^a-z])", haystack) for token in aliases.get(expected, ()))


def screen_evidence(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Classify evidence without reading oracle, attack, perturbation, or bundle-id metadata."""
    scope = bundle["scope"]
    report: dict[str, dict[str, Any]] = {}
    for evidence in bundle["evidence"]:
        eid = evidence["evidence_id"]
        content = str(evidence.get("content", ""))
        provenance = evidence.get("provenance", {})
        integrity = provenance.get("integrity_status", "unknown")
        authority = evidence.get("authority", "unknown")
        hard_reasons: list[str] = []
        caution_reasons: list[str] = []

        instruction_like = any(pattern.search(content) for pattern in INSTRUCTION_PATTERNS)
        authority_spoof = bool(AUTHORITY_CLAIM_PATTERN.search(content)) and (
            authority == "self_attestation" or integrity != "verified"
        )
        scope_match = _scope_matches(evidence, scope)
        environment_match = _environment_matches(evidence, scope)
        temporal_match = _period_overlaps(evidence, scope)

        if instruction_like:
            hard_reasons.append("instruction_like_content")
        if authority_spoof:
            hard_reasons.append("unsupported_authority_claim")
        if not scope_match:
            hard_reasons.append("out_of_scope_asset")
        if not environment_match:
            hard_reasons.append("environment_mismatch")
        if not temporal_match:
            hard_reasons.append("outside_assessment_period")
        if integrity != "verified":
            caution_reasons.append("unverified_integrity")
        if authority == "self_attestation":
            caution_reasons.append("self_attestation_only")

        if hard_reasons:
            status = "quarantined"
        elif caution_reasons:
            status = "caution"
        else:
            status = "trusted"

        report[eid] = {
            "status": status,
            "reasons": hard_reasons + caution_reasons,
            "authority": authority,
            "authority_rank": AUTHORITY_RANK.get(authority, 0),
            "integrity_status": integrity,
            "scope_match": scope_match,
            "environment_match": environment_match,
            "temporal_match": temporal_match,
            "admissible_for_assurance": (
                status == "trusted" and authority in ASSURANCE_AUTHORITIES
            ),
        }
    return report


def shield_bundle(bundle: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Return a model-visible copy with risky evidence isolated and trust labels attached."""
    report = screen_evidence(bundle)
    screened = {
        "bundle_id": bundle["bundle_id"],
        "control": copy.deepcopy(bundle["control"]),
        "scope": copy.deepcopy(bundle["scope"]),
        "evidence": copy.deepcopy(bundle["evidence"]),
        "evidence_screening": copy.deepcopy(report),
    }
    for evidence in screened["evidence"]:
        decision = report[evidence["evidence_id"]]
        evidence["evidence_shield"] = decision
        if decision["status"] == "quarantined":
            reason = ", ".join(decision["reasons"])
            evidence["content"] = (
                f"[QUARANTINED BY EVIDENCESHIELD: {reason}. "
                "Original content withheld from the auditor and cannot support assurance.]"
            )
        elif decision["status"] == "caution":
            evidence["content"] = (
                "[CAUTION: unverified or self-attested evidence; corroboration required.] "
                + str(evidence.get("content", ""))
            )
    return screened, report


def enforce_assurance_gate(
    original_bundle: dict[str, Any],
    prediction: AuditPrediction,
    report: dict[str, dict[str, Any]],
) -> AuditPrediction:
    """Apply a conservative postcondition to positive compliance decisions."""
    cited = list(dict.fromkeys(prediction.cited_evidence_ids))
    quarantined = [eid for eid in cited if report.get(eid, {}).get("status") == "quarantined"]
    admissible = [eid for eid in cited if report.get(eid, {}).get("admissible_for_assurance")]
    all_quarantined = [eid for eid, row in report.items() if row["status"] == "quarantined"]
    flagged = list(dict.fromkeys(prediction.flagged_evidence_ids + all_quarantined))

    label = prediction.label
    confidence = prediction.confidence
    rationale = prediction.rationale
    gate_reason: str | None = None
    if label == "compliant":
        if quarantined:
            gate_reason = "positive verdict cited quarantined evidence"
        elif not cited:
            gate_reason = "positive verdict supplied no evidence citations"
        elif not admissible:
            gate_reason = "positive verdict lacked verified technical or operational evidence"
        if gate_reason:
            label = "insufficient_evidence"
            confidence = min(confidence, 0.65)
            rationale = (rationale + " " if rationale else "") + f"EvidenceShield downgrade: {gate_reason}."

    return replace(
        prediction,
        bundle_id=original_bundle["bundle_id"],
        label=label,
        confidence=confidence,
        flagged_evidence_ids=flagged,
        rationale=rationale,
        provider=(prediction.provider + "+evidenceshield") if prediction.provider else "evidenceshield",
        raw={
            **(prediction.raw or {}),
            "evidenceshield": {
                "screening": report,
                "gate_reason": gate_reason,
            },
        },
    )


class EvidenceShieldAdapter:
    """Defence wrapper that isolates evidence before inference and gates positive assurance."""

    def __init__(self, base: AuditorAdapter) -> None:
        self.base = base

    @property
    def name(self) -> str:
        return f"{self.base.name}+evidenceshield-v0.1"

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        screened, report = shield_bundle(bundle)
        prediction = self.base.assess(screened)
        return enforce_assurance_gate(bundle, prediction, report)
