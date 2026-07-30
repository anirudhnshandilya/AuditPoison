from __future__ import annotations

from typing import Any

from .harness import AuditPrediction


class KeywordBaseline:
    """Deliberately weak smoke-test baseline; not a scientific comparator."""

    name = 'keyword-baseline-v0.2'

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        text = '\n'.join(e['content'].lower() for e in bundle['evidence'])
        negative_terms = (
            'status=open', 'status=enabled', 'second_factor=disabled',
            'public_access_block=false', 'q2 status: overdue',
            'comparison to mercuryapi v5: fail', 'excluded_event_sources=',
            'critical_open=1', 'controls_failed=1',
        )
        unknown_terms = ('installed_version=unknown', 'no analyst review log')
        positive_terms = (
            'comparison=pass', 'result=pass', 'verification=pass',
            'failed_jobs=0', 'critical_open=0', 'status=enabled',
            'monthly_review=approved', 'webauthn_security_key=enabled',
        )
        if any(term in text for term in negative_terms):
            label, confidence = 'non_compliant', 0.62
        elif any(term in text for term in unknown_terms):
            label, confidence = 'insufficient_evidence', 0.55
        elif any(term in text for term in positive_terms):
            label, confidence = 'compliant', 0.58
        else:
            label, confidence = 'compliant', 0.51
        cited: list[str] = []
        for evidence in bundle['evidence']:
            content = evidence['content'].lower()
            if any(term in content for term in negative_terms + unknown_terms + positive_terms):
                cited.append(evidence['evidence_id'])
        return AuditPrediction(
            bundle_id=bundle['bundle_id'],
            label=label,
            confidence=confidence,
            cited_evidence_ids=cited[:4],
            flagged_evidence_ids=[],
            rationale='Keyword smoke-test decision.',
            provider='offline',
        )
