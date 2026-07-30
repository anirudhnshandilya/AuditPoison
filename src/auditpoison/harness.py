from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Sequence

from .parsing import parse_model_response
from .prompting import render_request


@dataclass(frozen=True)
class AuditPrediction:
    bundle_id: str
    label: str
    confidence: float
    cited_evidence_ids: list[str]
    flagged_evidence_ids: list[str]
    rationale: str = ""
    provider: str | None = None
    latency_ms: float | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    attempts: int = 1
    response_sha256: str | None = None
    raw: dict[str, Any] | None = None
    decision_source: str | None = None
    predicate_outcomes: list[dict[str, Any]] | None = None
    advisory_model_label: str | None = None


class AuditorAdapter(Protocol):
    @property
    def name(self) -> str: ...
    def assess(self, bundle: dict[str, Any]) -> AuditPrediction: ...


class CommandAdapter:
    """Provider-neutral adapter using a subprocess JSON contract."""

    def __init__(self, command: Sequence[str], system_prompt: str, name: str = "command-adapter") -> None:
        if not command:
            raise ValueError("command must not be empty")
        self.command = list(command)
        self.system_prompt = system_prompt
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        request = render_request(bundle, self.system_prompt)
        started = time.perf_counter()
        completed = subprocess.run(
            self.command,
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        if completed.returncode != 0:
            raise RuntimeError(
                f"Adapter command failed for {bundle['bundle_id']} with exit code "
                f"{completed.returncode}: {completed.stderr.strip()}"
            )
        parsed = parse_model_response(bundle, completed.stdout)
        return AuditPrediction(
            **parsed,
            provider="command",
            latency_ms=latency_ms,
            response_sha256=hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
            raw={"stderr": completed.stderr},
        )


def prediction_to_row(adapter: AuditorAdapter, prediction: AuditPrediction) -> dict[str, Any]:
    return {
        "bundle_id": prediction.bundle_id,
        "label": prediction.label,
        "confidence": prediction.confidence,
        "cited_evidence_ids": prediction.cited_evidence_ids,
        "flagged_evidence_ids": prediction.flagged_evidence_ids,
        "rationale": prediction.rationale,
        "model": adapter.name,
        "provider": prediction.provider,
        "latency_ms": prediction.latency_ms,
        "prompt_tokens": prediction.prompt_tokens,
        "completion_tokens": prediction.completion_tokens,
        "attempts": prediction.attempts,
        "response_sha256": prediction.response_sha256,
        "decision_source": prediction.decision_source,
        "predicate_outcomes": prediction.predicate_outcomes,
        "advisory_model_label": prediction.advisory_model_label,
    }


def evaluate_adapter(
    adapter: AuditorAdapter,
    bundles: list[dict[str, Any]],
    *,
    start_index: int = 0,
    total: int | None = None,
    on_row: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total = len(bundles) if total is None else total
    for offset, bundle in enumerate(bundles, start=1):
        prediction = adapter.assess(bundle)
        if prediction.bundle_id != bundle["bundle_id"]:
            raise ValueError(f"Adapter returned {prediction.bundle_id} for {bundle['bundle_id']}")
        row = prediction_to_row(adapter, prediction)
        rows.append(row)
        if on_row is not None:
            on_row(row)
        print(
            f"[{start_index + offset}/{total}] {bundle['bundle_id']} -> {prediction.label}",
            flush=True,
        )
    return rows
