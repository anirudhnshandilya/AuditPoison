from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence

from .parsing import parse_model_response
from .prompting import render_request


@dataclass(frozen=True)
class AuditPrediction:
    bundle_id: str
    label: str
    confidence: float
    cited_evidence_ids: list[str]
    flagged_evidence_ids: list[str]
    rationale: str = ''
    raw: dict[str, Any] | None = None


class AuditorAdapter(Protocol):
    @property
    def name(self) -> str: ...
    def assess(self, bundle: dict[str, Any]) -> AuditPrediction: ...


class CommandAdapter:
    """Provider-neutral adapter.

    The command receives one JSON request on stdin and must emit either the
    canonical response object or text containing that object on stdout.
    """

    def __init__(self, command: Sequence[str], system_prompt: str, name: str = 'command-adapter') -> None:
        if not command:
            raise ValueError('command must not be empty')
        self.command = list(command)
        self.system_prompt = system_prompt
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        request = render_request(bundle, self.system_prompt)
        completed = subprocess.run(
            self.command,
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f'Adapter command failed for {bundle["bundle_id"]} with exit code '
                f'{completed.returncode}: {completed.stderr.strip()}'
            )
        parsed = parse_model_response(bundle, completed.stdout)
        return AuditPrediction(**parsed, raw={'stdout': completed.stdout, 'stderr': completed.stderr})


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
            'flagged_evidence_ids': prediction.flagged_evidence_ids,
            'rationale': prediction.rationale,
            'model': adapter.name,
        })
    return rows
