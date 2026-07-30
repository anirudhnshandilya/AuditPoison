from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class AuditPrediction:
    bundle_id: str
    label: str
    confidence: float
    cited_evidence_ids: list[str]
    contradictions_detected: list[str]
    raw: dict[str, Any] | None = None


class AuditorAdapter(Protocol):
    """Minimal interface implemented by local or remote model wrappers."""

    @property
    def name(self) -> str:
        ...

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        ...


def evaluate_adapter(adapter: AuditorAdapter, bundles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        prediction = adapter.assess(bundle)
        if prediction.bundle_id != bundle['bundle_id']:
            raise ValueError(f'Adapter returned {prediction.bundle_id} for {bundle["bundle_id"]}')
        rows.append({
            'bundle_id': prediction.bundle_id,
            'label': prediction.label,
            'confidence': prediction.confidence,
            'cited_evidence_ids': prediction.cited_evidence_ids,
            'contradictions_detected': prediction.contradictions_detected,
            'model': adapter.name,
        })
    return rows
