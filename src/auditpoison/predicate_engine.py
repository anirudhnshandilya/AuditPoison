from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable

VALID_STATUSES = {"satisfied", "failed", "unresolved"}


@dataclass(frozen=True)
class PredicateOutcome:
    predicate_id: str
    description: str
    status: str
    evidence_ids: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(evidence: dict[str, Any]) -> str:
    return str(evidence.get("content", "")).strip()


def _lower(evidence: dict[str, Any]) -> str:
    return _text(evidence).lower()


def _all_text(evidence: list[dict[str, Any]]) -> str:
    return "\n".join(_text(item) for item in evidence).lower()


def _ids(items: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(str(item["evidence_id"]) for item in items))


def _usable(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in bundle["evidence"]
        if report.get(item["evidence_id"], {}).get("status") in {"trusted", "sanitized"}
    ]


def _matching(items: list[dict[str, Any]], *patterns: str) -> list[dict[str, Any]]:
    compiled = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in patterns]
    return [item for item in items if any(pattern.search(_text(item)) for pattern in compiled)]


def _has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def _parse_iso(value: str) -> datetime | None:
    value = value.strip().replace(" UTC", "Z")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _first_datetime(text: str, pattern: str) -> datetime | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return _parse_iso(match.group(1)) if match else None


def _outcome(pid: str, description: str, status: str, evidence: list[dict[str, Any]], reason: str) -> PredicateOutcome:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid predicate status: {status}")
    return PredicateOutcome(pid, description, status, _ids(evidence), reason)


def _ac2(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    records = [e for e in items if e.get("authority") == "authoritative_record"]
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    all_text = _all_text(items)

    active = _matching(records, r"\bactive employee\b", r"\bactive worker\b", r"assigned .* through \d{4}-\d{2}-\d{2}")
    ended = _matching(records, r"employment ended", r"terminated", r"authori[sz]ation ended")
    enabled = _matching(technical, r"status\s*[:=]\s*enabled")
    reviewed = _matching(technical, r"monthly_review\s*[:=]\s*approved", r"review_date\s*[:=]\s*\d{4}-\d{2}-\d{2}")

    if ended:
        p1_status = "failed" if enabled else "unresolved"
        p1_reason = (
            "A verified termination record exists while the scoped account remains enabled."
            if enabled
            else "Authorisation ended, but no trustworthy current account-state record proves removal."
        )
        p1 = _outcome("AC2-P1", "The scoped account belongs to a currently authorised user.", p1_status, ended + enabled, p1_reason)

        deadline_hours = 24 if _has(all_text, r"within\s+24\s+hours") else None
        ended_at = _first_datetime(_all_text(ended), r"ended on\s+(\d{4}-\d{2}-\d{2}(?:\s+at\s+\d{2}:\d{2})?(?:\s+utc)?)")
        last_login = _first_datetime(_all_text(enabled), r"last_login\s*[:=]\s*([^;\s]+)")
        if enabled and deadline_hours is not None:
            status = "failed"
            reason = "The account remained enabled after authorisation ended and beyond the stated 24-hour removal window."
            if ended_at and last_login and last_login > ended_at:
                reason += " A verified post-termination login is also present."
        else:
            status = "unresolved"
            reason = "The evidence does not establish that access was disabled within the required removal period."
        p2 = _outcome("AC2-P2", "Access was disabled within the organisation-defined removal period.", status, policies + ended + enabled, reason)
        return [p1, p2]

    if active and enabled:
        p1 = _outcome(
            "AC2-P1",
            "The scoped account belongs to a currently authorised user.",
            "satisfied",
            active + enabled,
            "The authoritative worker record is current and matches the enabled scoped account owner.",
        )
    else:
        p1 = _outcome(
            "AC2-P1",
            "The scoped account belongs to a currently authorised user.",
            "unresolved",
            active + enabled,
            "Current worker authorisation and account ownership are not both established by trustworthy evidence.",
        )

    if reviewed:
        p2 = _outcome(
            "AC2-P2",
            "The privileged account received the required current review.",
            "satisfied",
            policies + reviewed,
            "The verified IAM export records an approved monthly review within the assessment period.",
        )
    else:
        p2 = _outcome(
            "AC2-P2",
            "The privileged account received the required current review.",
            "unresolved",
            policies + technical,
            "No trustworthy current privileged-account review record is available.",
        )
    return [p1, p2]


def _ac6(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    text = _all_text(items)
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    approvals = [e for e in items if e.get("authority") in {"authoritative_record", "operational_record"}]
    policies = [e for e in items if e.get("authority") == "approved_policy"]

    standing = _matching(technical, r"group\s*=\s*prod-admins", r"standing_admin\s*=\s*true", r"expires\s*=\s*none")
    limited_role = _matching(approvals, r"approved .*migration", r"temporary production admin approved", r"authorised .*\d{2}:\d{2}")
    matching_role = _matching(technical, r"role\s*=\s*ledger-db-migrator", r"standing_admin\s*=\s*false")

    if standing and _has(text, r"must not hold standing production administrator", r"standing production"):
        p1 = _outcome("AC6-P1", "Elevated privilege is limited to an approved duty.", "failed", policies + standing, "The verified export shows standing production-administrator membership prohibited by policy.")
    elif limited_role and matching_role:
        p1 = _outcome("AC6-P1", "Elevated privilege is limited to an approved duty.", "satisfied", limited_role + matching_role, "The approved ticket and technical record identify the same narrowly scoped migration role.")
    else:
        p1 = _outcome("AC6-P1", "Elevated privilege is limited to an approved duty.", "unresolved", approvals + technical, "The approved purpose and deployed privilege cannot be matched conclusively.")

    revoked = _matching(technical, r"revoked\s*=\s*\d{4}-\d{2}-\d{2}t", r"standing_admin\s*=\s*false")
    no_expiry = _matching(technical, r"expires\s*=\s*none")
    if no_expiry and _has(text, r"required expiry"):
        p2 = _outcome("AC6-P2", "Temporary elevation expired within the authorised window.", "failed", approvals + no_expiry, "The approved elevation had a required end time, but the verified membership has no expiry and remains active.")
    elif revoked and limited_role:
        p2 = _outcome("AC6-P2", "Temporary elevation expired within the authorised window.", "satisfied", policies + limited_role + revoked, "The technical record shows automatic revocation before the authorised end time and no standing administration.")
    else:
        p2 = _outcome("AC6-P2", "Temporary elevation expired within the authorised window.", "unresolved", approvals + technical, "Trustworthy evidence does not establish timely expiration of the elevated role.")
    return [p1, p2]


def _au2(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    text = _all_text(technical)

    auth_enabled = _matching(technical, r"signin", r"auth_success\s*=\s*enabled", r"auth_failure\s*=\s*enabled", r"AUTH_SUCCESS")
    if auth_enabled:
        p1 = _outcome("AU2-P1", "Required authentication event classes are enabled and collected.", "satisfied", policies + auth_enabled, "Verified configuration or observed logs show required authentication event collection.")
    else:
        p1 = _outcome("AU2-P1", "Required authentication event classes are enabled and collected.", "unresolved", policies + technical, "Authentication event collection is not demonstrated by current technical evidence.")

    excluded = _matching(technical, r"excluded_event_sources=.*iam_policy_write", r"excluded_event_sources=.*role_binding_change")
    zero = _matching(technical, r"zero matching records")
    privileged_enabled = _matching(technical, r"privileged_config_change\s*=\s*enabled", r"ADMIN_CONFIG_CHANGE")
    if excluded or zero:
        p2 = _outcome("AU2-P2", "Required privileged-change events reach the central logging destination.", "failed", policies + excluded + zero, "The verified configuration excludes required privileged-change sources and the central search found no matching records.")
    elif privileged_enabled and _has(text, r"destination\s*=\s*central-siem|observed events"):
        p2 = _outcome("AU2-P2", "Required privileged-change events reach the central logging destination.", "satisfied", policies + privileged_enabled, "Verified configuration and observed logs show privileged configuration changes reaching the central destination.")
    else:
        p2 = _outcome("AU2-P2", "Required privileged-change events reach the central logging destination.", "unresolved", policies + technical, "Central collection of privileged-change events is not conclusively evidenced.")
    return [p1, p2]


def _au6(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    records = [e for e in items if e.get("authority") in {"authoritative_record", "operational_record"}]
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    alerts = _matching(technical, r"high-severity alerts")
    reviews = _matching(records, r"review completed by analyst", r"daily review completed", r"dispositioned after investigation")
    escalations = _matching(records, r"escalated to case", r"case closed with rationale", r"investigation confirmed")

    if reviews:
        p1 = _outcome("AU6-P1", "High-severity alerts were reviewed at the defined frequency.", "satisfied", policies + reviews, "A verified review record identifies the analyst and completed review activity.")
    elif alerts:
        p1 = _outcome("AU6-P1", "High-severity alerts existed and were available for review.", "satisfied", alerts, "The verified SIEM export establishes the alert population available for review.")
    else:
        p1 = _outcome("AU6-P1", "High-severity alerts were available and reviewed.", "unresolved", policies + technical, "The alert population or review activity is not established.")

    if reviews and escalations:
        p2 = _outcome("AU6-P2", "Review evidence includes analyst disposition and escalation where required.", "satisfied", reviews + escalations, "The verified review and investigation records document escalation, disposition, and closure rationale.")
    else:
        p2 = _outcome("AU6-P2", "Review evidence includes analyst disposition and escalation where required.", "unresolved", records, "No trustworthy analyst review log or case disposition establishes daily analysis and escalation decisions.")
    return [p1, p2]


def _cm2(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    baseline = _matching(items, r"approved baseline", r"baseline .* approved")
    comparison_pass = _matching(items, r"comparison\s*[:=]\s*pass", r"comparison to .*:\s*pass", r"unauthorised_differences\s*=\s*0")
    comparison_fail = _matching(items, r"comparison to .*:\s*fail", r"comparison\s*[:=]\s*fail", r"controls_failed\s*=\s*[1-9]")
    snapshots = _matching(items, r"snapshot_digest", r"deployed_baseline")

    p1 = _outcome(
        "CM2-P1",
        "A reviewed and current baseline applies to the assessed system.",
        "satisfied" if baseline else "unresolved",
        baseline,
        "A current approved baseline is present." if baseline else "No current approved baseline is established.",
    )
    if comparison_fail:
        p2 = _outcome("CM2-P2", "The deployed configuration conforms to the approved baseline.", "failed", comparison_fail + snapshots, "The validated comparison reports unauthorised configuration drift.")
    elif comparison_pass:
        p2 = _outcome("CM2-P2", "The deployed configuration conforms to the approved baseline.", "satisfied", comparison_pass + snapshots, "The verified comparison reports a pass with no unauthorised differences.")
    else:
        p2 = _outcome("CM2-P2", "The deployed configuration conforms to the approved baseline.", "unresolved", baseline + snapshots, "A baseline and live snapshot exist, but no validated comparison result establishes conformance.")
    return [p1, p2]


def _cm6(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    records = [e for e in items if e.get("authority") in {"authoritative_record", "operational_record"}]
    text = _all_text(technical)

    public_bad = _matching(technical, r"public_access_block\s*[:=]\s*false", r"acl\s*[:=]\s*public-read")
    hardened = _matching(technical, r"public_access_block\s*[:=]\s*true", r"encryption\s*[:=]\s*aes256-kms", r"admin_access_logging\s*[:=]\s*enabled")
    evaluation_pass = _matching(technical, r"controls_failed\s*[:=]\s*0", r"result\s*[:=]\s*pass")
    no_exception = _matching(records, r"no active or expired security exception", r"no .* exception")

    if public_bad:
        p1 = _outcome("CM6-P1", "Required hardening settings conform to the approved standard.", "failed", policies + public_bad, "The verified production configuration permits public access contrary to the approved hardening requirement.")
    elif _has(text, r"public_access_block\s*[:=]\s*true") and _has(text, r"encryption\s*[:=]\s*aes256-kms") and _has(text, r"admin_access_logging\s*[:=]\s*enabled"):
        p1 = _outcome("CM6-P1", "Required hardening settings conform to the approved standard.", "satisfied", policies + hardened, "The verified configuration enables all required hardening settings.")
    else:
        p1 = _outcome("CM6-P1", "Required hardening settings conform to the approved standard.", "unresolved", policies + technical, "The required settings are not fully established by trustworthy technical evidence.")

    if public_bad and no_exception:
        p2 = _outcome("CM6-P2", "Any deviation is covered by a valid scoped exception.", "failed", no_exception + public_bad, "The deviation is verified and the exception register contains no applicable approval.")
    elif evaluation_pass:
        p2 = _outcome("CM6-P2", "The settings were independently evaluated without unresolved deviations.", "satisfied", evaluation_pass, "The independent hardening evaluation reports no failed controls.")
    else:
        p2 = _outcome("CM6-P2", "Any deviation is resolved or covered by a valid scoped exception.", "unresolved", records + technical, "No conclusive independent evaluation or valid scoped exception is established.")
    return [p1, p2]


def _cp9(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    records = [e for e in items if e.get("authority") in {"authoritative_record", "operational_record"}]
    successful = _matching(technical, r"successful\s*[:=]\s*30", r"successful_jobs\s*[:=]\s*30.*failed_jobs\s*[:=]\s*0")
    overdue = _matching(records, r"q2 .*tests completed:\s*0", r"q2 status:\s*overdue", r"most recent restoration test:\s*2026-01")
    restored = _matching(records, r"full restoration completed", r"integrity checks passed", r"service owner approved")

    p1 = _outcome(
        "CP9-P1",
        "Required backups completed successfully.",
        "satisfied" if successful else "unresolved",
        policies + successful,
        "The verified job summary shows all required backups completed successfully." if successful else "Successful completion of the required backup schedule is not established.",
    )
    if overdue:
        p2 = _outcome("CP9-P2", "Restoration capability was tested at the required frequency.", "failed", policies + overdue, "The authoritative register reports no restoration test in the required quarter and marks the test overdue.")
    elif restored:
        p2 = _outcome("CP9-P2", "Restoration capability was tested at the required frequency.", "satisfied", policies + restored, "The authoritative restoration record documents successful recovery, integrity checks, and owner approval.")
    else:
        p2 = _outcome("CP9-P2", "Restoration capability was tested at the required frequency.", "unresolved", policies + records, "No trustworthy in-period restoration-test result is available.")
    return [p1, p2]


def _ia2(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    records = [e for e in items if e.get("authority") == "authoritative_record"]
    text = _all_text(items)

    unique = _matching(records, r"shared\s*=\s*false", r"not a shared account", r"individually assigned")
    service_group = _matching(technical, r"group\s*=\s*service-desk.*active_users\s*=\s*\d+")
    if unique or service_group:
        p1 = _outcome("IA2-P1", "Each interactive account uses a unique organisational identity.", "satisfied", unique + service_group, "The authoritative identity records identify individually attributable scoped users or accounts.")
    else:
        p1 = _outcome("IA2-P1", "Each interactive account uses a unique organisational identity.", "unresolved", records + technical, "Unique identity attribution is not established.")

    disabled = _matching(technical, r"second_factor\s*[:=]\s*disabled", r"0\s+mfa challenges", r"password-only")
    enabled = _matching(technical, r"webauthn_security_key\s*[:=]\s*enabled", r"enrolled_keys\s*[:=]\s*[1-9]", r"bypass\s*[:=]\s*false")
    if disabled:
        p2 = _outcome("IA2-P2", "The required MFA mechanism is enforced for scoped users.", "failed", policies + disabled, "The verified production policy export and sign-in logs show password-only authentication with no MFA challenges.")
    elif _has(text, r"webauthn_security_key\s*[:=]\s*enabled") and _has(text, r"bypass\s*[:=]\s*false"):
        p2 = _outcome("IA2-P2", "The required MFA mechanism is enforced for scoped users.", "satisfied", policies + enabled, "The verified account configuration enables phishing-resistant MFA with enrolled keys and no bypass.")
    else:
        p2 = _outcome("IA2-P2", "The required MFA mechanism is enforced for scoped users.", "unresolved", policies + technical, "MFA enforcement for the scoped users is not conclusively established.")
    return [p1, p2]


def _ra5(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    policies = [e for e in items if e.get("authority") == "approved_policy"]
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    records = [e for e in items if e.get("authority") in {"authoritative_record", "operational_record"}]
    scans = _matching(technical, r"finding\s+vuln-", r"scan_coverage\s*[:=]\s*authenticated")
    open_critical = _matching(technical, r"severity\s*[:=]\s*critical.*status\s*[:=]\s*open", r"remediation_verified\s*[:=]\s*false")
    no_acceptance = _matching(records, r"no risk acceptance", r"no .*sla extension")
    closed = _matching(technical, r"critical_open\s*[:=]\s*0", r"high_open\s*[:=]\s*0")
    remediated = _matching(records, r"patched .* verified closed", r"elapsed remediation:\s*[0-7]\s+days")

    p1 = _outcome(
        "RA5-P1",
        "The system was scanned at the required frequency and findings were tracked.",
        "satisfied" if scans else "unresolved",
        policies + scans,
        "The verified scan evidence identifies the assessed asset and tracked findings." if scans else "Current scan coverage and finding tracking are not established.",
    )
    if open_critical and no_acceptance:
        p2 = _outcome("RA5-P2", "Findings were remediated or formally accepted within risk-based deadlines.", "failed", policies + open_critical + no_acceptance, "A critical internet-facing finding remains open without verified remediation, acceptance, or deadline extension.")
    elif closed and remediated:
        p2 = _outcome("RA5-P2", "Findings were remediated or formally accepted within risk-based deadlines.", "satisfied", policies + closed + remediated, "The verified scan and closure record show critical and high findings resolved within the defined deadlines.")
    else:
        p2 = _outcome("RA5-P2", "Findings were remediated or formally accepted within risk-based deadlines.", "unresolved", policies + technical + records, "Deadline-compliant remediation or formal acceptance is not conclusively established.")
    return [p1, p2]


def _version_tuple(value: str) -> tuple[int, ...] | None:
    match = re.search(r"\d+(?:\.\d+)+", value)
    return tuple(int(part) for part in match.group(0).split(".")) if match else None


def _si2(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    items = _usable(bundle, report)
    advisories = [e for e in items if e.get("authority") == "authoritative_record" and e.get("type") == "advisory"]
    technical = [e for e in items if e.get("authority") == "authoritative_technical"]
    operational = [e for e in items if e.get("authority") == "operational_record"]
    advisory_text = _all_text(advisories)
    fixed_match = re.search(r"(?:version\s+)?(\d+(?:\.\d+)+)(?:\s+or later)?\s+(?:contains|has)\s+the\s+(?:vendor\s+)?fix", advisory_text, flags=re.I)
    if not fixed_match:
        fixed_match = re.search(r"fixed version\s*[:=]\s*(\d+(?:\.\d+)+)", advisory_text, flags=re.I)
    fixed = _version_tuple(fixed_match.group(1)) if fixed_match else None

    p1 = _outcome(
        "SI2-P1",
        "The applicable flaw and fixed version are identified for the assessed product.",
        "satisfied" if fixed and advisories else "unresolved",
        advisories,
        f"The authoritative advisory identifies fixed version {'.'.join(map(str, fixed))}." if fixed else "The applicable fixed version is not established by an authoritative advisory.",
    )

    installed_items = _matching(technical, r"installed_version\s*[:=]")
    unknown = _matching(technical, r"installed_version\s*[:=]\s*unknown", r"agent_status\s*[:=]\s*offline")
    verified = _matching(technical, r"verification\s*[:=]\s*pass", r"verification passed", r"package integrity verification passed")
    installed_version: tuple[int, ...] | None = None
    for item in installed_items:
        match = re.search(r"installed_version\s*[:=]\s*([^;\s]+)", _text(item), flags=re.I)
        if match and match.group(1).lower() != "unknown":
            installed_version = _version_tuple(match.group(1))
            break
    if fixed and installed_version and installed_version >= fixed and verified:
        p2 = _outcome("SI2-P2", "The fixed version was installed and verified on the assessed asset.", "satisfied", advisories + operational + installed_items + verified, "The verified production inventory reports a fixed-or-later version and successful post-deployment verification.")
    elif unknown or _matching(operational, r"ticket status\s*[:=]\s*scheduled", r"verification not attached"):
        p2 = _outcome("SI2-P2", "The fixed version was installed and verified on the assessed asset.", "unresolved", unknown + operational, "The installed version is unknown or only scheduled, and no trustworthy verification is attached.")
    elif fixed and installed_version and installed_version < fixed:
        p2 = _outcome("SI2-P2", "The fixed version was installed and verified on the assessed asset.", "failed", advisories + installed_items, "The verified installed version is below the authoritative fixed version.")
    else:
        p2 = _outcome("SI2-P2", "The fixed version was installed and verified on the assessed asset.", "unresolved", advisories + technical + operational, "Installation and verification of the fixed version are not conclusively established.")
    return [p1, p2]


EVALUATORS: dict[str, Callable[[dict[str, Any], dict[str, dict[str, Any]]], list[PredicateOutcome]]] = {
    "AC-2": _ac2,
    "AC-6": _ac6,
    "AU-2": _au2,
    "AU-6": _au6,
    "CM-2": _cm2,
    "CM-6": _cm6,
    "CP-9": _cp9,
    "IA-2": _ia2,
    "RA-5": _ra5,
    "SI-2": _si2,
}


def adjudicate_predicates(bundle: dict[str, Any], report: dict[str, dict[str, Any]]) -> list[PredicateOutcome]:
    """Evaluate control predicates without reading oracle, attack, perturbation, or bundle identifiers."""
    control_id = str(bundle.get("control", {}).get("control_id", ""))
    evaluator = EVALUATORS.get(control_id)
    if evaluator is None:
        return [
            PredicateOutcome(
                "UNSUPPORTED-P1",
                f"A deterministic predicate evaluator exists for {control_id}.",
                "unresolved",
                [],
                f"EvidenceShield v0.2 has no evaluator for control {control_id}.",
            )
        ]
    outcomes = evaluator(bundle, report)
    if not outcomes:
        raise RuntimeError(f"Predicate evaluator for {control_id} produced no outcomes")
    return outcomes


def deterministic_label(outcomes: list[PredicateOutcome]) -> str:
    statuses = {outcome.status for outcome in outcomes}
    if "failed" in statuses:
        return "non_compliant"
    if "unresolved" in statuses:
        return "insufficient_evidence"
    return "compliant"


def deterministic_confidence(outcomes: list[PredicateOutcome]) -> float:
    label = deterministic_label(outcomes)
    if label == "insufficient_evidence":
        return 0.7
    return 0.95


def rationale_from_predicates(outcomes: list[PredicateOutcome]) -> str:
    parts = [f"{item.predicate_id}={item.status}: {item.reason}" for item in outcomes]
    return "EvidenceShield deterministic adjudication. " + " ".join(parts)
