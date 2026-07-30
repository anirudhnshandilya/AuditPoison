from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .harness import AuditPrediction
from .parsing import parse_model_response
from .prompting import OUTPUT_SPEC, render_request


OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "label": {
            "type": "string",
            "enum": ["compliant", "non_compliant", "insufficient_evidence"],
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "cited_evidence_ids": {"type": "array", "items": {"type": "string"}},
        "flagged_evidence_ids": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
    },
    "required": [
        "label",
        "confidence",
        "cited_evidence_ids",
        "flagged_evidence_ids",
        "rationale",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class HttpResult:
    body: dict[str, Any]
    latency_ms: float
    attempts: int


def _post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: float = 120.0,
    max_retries: int = 3,
) -> HttpResult:
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error: Exception | None = None
    started = time.perf_counter()

    for attempt in range(1, max_retries + 2):
        request = urllib.request.Request(url, data=encoded, headers=request_headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
            body = json.loads(raw)
            return HttpResult(body=body, latency_ms=(time.perf_counter() - started) * 1000, attempts=attempt)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {exc.code} from {url}: {detail[:500]}")
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt > max_retries:
                raise last_error from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt > max_retries:
                raise RuntimeError(f"Request to {url} failed after {attempt} attempts: {exc}") from exc
        time.sleep(min(8.0, 0.75 * (2 ** (attempt - 1))))

    raise RuntimeError(f"Request failed: {last_error}")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class OllamaAdapter:
    def __init__(
        self,
        model: str,
        system_prompt: str,
        base_url: str = "http://localhost:11434/api",
        temperature: float = 0.0,
        seed: int = 7,
        think: bool = False,
        timeout: float = 180.0,
        max_retries: int = 2,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.seed = seed
        self.think = think
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def name(self) -> str:
        return f"ollama:{self.model}"

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        request = render_request(bundle, self.system_prompt)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request["system_prompt"]},
                {"role": "user", "content": request["user_prompt"]},
            ],
            "stream": False,
            "think": self.think,
            "format": OUTPUT_JSON_SCHEMA,
            "options": {"temperature": self.temperature, "seed": self.seed},
        }
        result = _post_json(
            f"{self.base_url}/chat",
            payload,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        try:
            content = result.body["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Ollama response: {result.body}") from exc
        parsed = parse_model_response(bundle, content)
        return AuditPrediction(
            **parsed,
            provider="ollama",
            latency_ms=result.latency_ms,
            prompt_tokens=result.body.get("prompt_eval_count"),
            completion_tokens=result.body.get("eval_count"),
            attempts=result.attempts,
            response_sha256=_sha256_text(content),
        )


class OpenAICompatibleAdapter:
    """Adapter for OpenAI-style /v1/chat/completions endpoints.

    The API key is supplied by the caller and is never written to predictions or
    manifests. The base URL may be a /v1 root or the full chat-completions URL.
    """

    def __init__(
        self,
        model: str,
        system_prompt: str,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.0,
        seed: int | None = 7,
        timeout: float = 180.0,
        max_retries: int = 3,
    ) -> None:
        if not api_key:
            raise ValueError("An API key is required for the OpenAI-compatible adapter.")
        self.model = model
        self.system_prompt = system_prompt
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.seed = seed
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def name(self) -> str:
        return f"openai-compatible:{self.model}"

    def _endpoint(self) -> str:
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return f"{self.base_url}/chat/completions"

    def assess(self, bundle: dict[str, Any]) -> AuditPrediction:
        request = render_request(bundle, self.system_prompt)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request["system_prompt"]},
                {"role": "user", "content": request["user_prompt"]},
            ],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
            "stream": False,
        }
        if self.seed is not None:
            payload["seed"] = self.seed
        result = _post_json(
            self._endpoint(),
            payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        try:
            content = result.body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenAI-compatible response: {result.body}") from exc
        usage = result.body.get("usage") or {}
        parsed = parse_model_response(bundle, content)
        return AuditPrediction(
            **parsed,
            provider="openai-compatible",
            latency_ms=result.latency_ms,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            attempts=result.attempts,
            response_sha256=_sha256_text(content),
        )
