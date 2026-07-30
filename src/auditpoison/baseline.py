from __future__ import annotations

from typing import Any

from .harness import AuditPrediction


class KeywordBaseline:
    """A deliberately weak smoke-test baseline, not a scientific model."""

    name = 'keyword-baseline-v0.1'

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        text = '\n'.join(e['content'].lower() for e in bundle['evidence'])
        cited: list[str] = []
        negative_terms = ('status=open', 'status=enabled', 'second_factor=disabled',
                          'public_access_block=false', 'q2 status: overdue',
                          'comparison to mercuryapi v5: fail', 'excluded_event_sources=')
        unknown_terms = ('installed_version=unknown', 'no analyst review log')
        if any(term in text for term in negative_terms):
            label = 'non_compliant'
            confidence = 0.62
        elif any(term in text for term in unknown_terms):
            label = 'insufficient_evidence'
            confidence = 0.55
        else:
            label = 'compliant'
            confidence = 0.51
        for evidence in bundle['evidence']:
            content = evidence['content'].lower()
            if any(term in content for term in negative_terms + unknown_terms):
                cited.append(evidence['evidence_id'])
        return AuditPrediction(
            bundle_id=bundle['bundle_id'],
            label=label,
            confidence=confidence,
            cited_evidence_ids=cited[:3],
            contradictions_detected=[],
        )
