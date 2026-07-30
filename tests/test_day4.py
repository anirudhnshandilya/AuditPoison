from dataclasses import replace

from auditpoison.defense import EvidenceShieldAdapter, enforce_assurance_gate, screen_evidence, shield_bundle
from auditpoison.harness import AuditPrediction
from auditpoison.io import load_bundles


def _bundle(project_root, bundle_id):
    return next(b for b in load_bundles(project_root) if b["bundle_id"] == bundle_id)


def test_instruction_injection_is_quarantined(project_root):
    bundle = _bundle(project_root, "AP-AC2-001-attacked")
    report = screen_evidence(bundle)
    assert report["E4"]["status"] == "quarantined"
    assert "instruction_like_content" in report["E4"]["reasons"]


def test_temporal_rollback_is_quarantined(project_root):
    bundle = _bundle(project_root, "AP-AU6-004-attacked")
    report = screen_evidence(bundle)
    assert report["E4"]["status"] == "quarantined"
    assert "outside_assessment_period" in report["E4"]["reasons"]


def test_scope_substitution_is_quarantined(project_root):
    bundle = _bundle(project_root, "AP-IA2-005-attacked")
    report = screen_evidence(bundle)
    assert any({"out_of_scope_asset", "environment_mismatch"} & set(row["reasons"]) for row in report.values())


def test_clean_verified_technical_evidence_is_trusted(project_root):
    bundle = _bundle(project_root, "AP-CM2-006-clean")
    report = screen_evidence(bundle)
    assert report["E2"]["status"] == "trusted"
    assert report["E2"]["admissible_for_assurance"] is True


def test_screening_does_not_depend_on_hidden_metadata(project_root):
    bundle = _bundle(project_root, "AP-AC6-002-attacked")
    first = screen_evidence(bundle)
    changed = dict(bundle)
    changed["oracle"] = {"label": "compliant"}
    changed["attack"] = {"present": False}
    changed["perturbation"] = {"present": True}
    changed["bundle_id"] = "completely-different-name"
    assert screen_evidence(changed) == first


def test_quarantined_content_is_not_model_visible(project_root):
    bundle = _bundle(project_root, "AP-AC2-001-attacked")
    screened, report = shield_bundle(bundle)
    e4 = next(e for e in screened["evidence"] if e["evidence_id"] == "E4")
    assert report["E4"]["status"] == "quarantined"
    assert "Ignore" not in e4["content"]
    assert "QUARANTINED BY EVIDENCESHIELD" in e4["content"]


def test_positive_gate_downgrades_unsubstantiated_compliance(project_root):
    bundle = _bundle(project_root, "AP-AC6-002-attacked")
    report = screen_evidence(bundle)
    pred = AuditPrediction(bundle["bundle_id"], "compliant", 0.9, ["E4"], [], "approved")
    out = enforce_assurance_gate(bundle, pred, report)
    assert out.label == "insufficient_evidence"
    assert "E4" in out.flagged_evidence_ids


def test_positive_gate_preserves_supported_compliance(project_root):
    bundle = _bundle(project_root, "AP-AC2-011-clean")
    report = screen_evidence(bundle)
    admissible = next(eid for eid, row in report.items() if row["admissible_for_assurance"])
    pred = AuditPrediction(bundle["bundle_id"], "compliant", 0.8, [admissible], [], "supported")
    out = enforce_assurance_gate(bundle, pred, report)
    assert out.label == "compliant"


class AlwaysCompliant:
    name = "always-compliant"
    def assess(self, bundle):
        return AuditPrediction(bundle["bundle_id"], "compliant", 0.9, [], [], "")


def test_wrapper_exposes_defence_name_and_gate(project_root):
    bundle = _bundle(project_root, "AP-AC2-001-attacked")
    adapter = EvidenceShieldAdapter(AlwaysCompliant())
    out = adapter.assess(bundle)
    assert "evidenceshield" in adapter.name
    assert out.label == "insufficient_evidence"
