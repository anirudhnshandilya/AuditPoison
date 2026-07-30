#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[0]
# When copied into AuditPoison/scripts, parents[1] is the repo root.
if not (ROOT / "src").exists():
    ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.defense import shield_bundle
from auditpoison.io import load_bundles
from auditpoison.prompting import load_system_prompt, render_request

BASE_PROPERTIES: dict[str, Any] = {
    "label": {"type": "string"},
    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "cited_evidence_ids": {"type": "array", "items": {"type": "string"}},
    "flagged_evidence_ids": {"type": "array", "items": {"type": "string"}},
    "rationale": {"type": "string"},
}
REQUIRED = [
    "label",
    "confidence",
    "cited_evidence_ids",
    "flagged_evidence_ids",
    "rationale",
]


def schema(label_order: list[str]) -> dict[str, Any]:
    properties = dict(BASE_PROPERTIES)
    properties["label"] = {"type": "string", "enum": label_order}
    return {
        "type": "object",
        "properties": properties,
        "required": REQUIRED,
        "additionalProperties": False,
    }


def post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc
    body["_latency_seconds"] = round(time.perf_counter() - started, 3)
    return body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test whether Ollama structured decoding is biased by label enum order."
    )
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--bundle-id", default="AP-IA2-005-attacked")
    parser.add_argument("--defense", choices=["none", "evidenceshield"], default="none")
    parser.add_argument("--base-url", default="http://localhost:11434/api")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="results/ollama_label_order_diagnostic.json")
    args = parser.parse_args()

    bundles = load_bundles(ROOT)
    try:
        original = next(bundle for bundle in bundles if bundle["bundle_id"] == args.bundle_id)
    except StopIteration:
        parser.error(f"Unknown bundle ID: {args.bundle_id}")

    if args.defense == "evidenceshield":
        visible_bundle, _ = shield_bundle(original)
        prompt_version = "v0.3"
    else:
        visible_bundle = original
        prompt_version = "v0.2"

    system_prompt = load_system_prompt(ROOT, prompt_version)
    request = render_request(visible_bundle, system_prompt)

    conditions: list[tuple[str, Any]] = [
        ("compliant_first", schema(["compliant", "non_compliant", "insufficient_evidence"])),
        ("non_compliant_first", schema(["non_compliant", "compliant", "insufficient_evidence"])),
        ("insufficient_first", schema(["insufficient_evidence", "non_compliant", "compliant"])),
        ("json_mode_no_enum", "json"),
    ]

    rows: list[dict[str, Any]] = []
    for name, format_spec in conditions:
        payload = {
            "model": args.model,
            "messages": [
                {"role": "system", "content": request["system_prompt"]},
                {"role": "user", "content": request["user_prompt"]},
            ],
            "stream": False,
            "think": False,
            "format": format_spec,
            "options": {"temperature": 0.0, "seed": args.seed},
        }
        body = post_json(f"{args.base_url.rstrip('/')}/chat", payload, args.timeout)
        content = str(body.get("message", {}).get("content", ""))
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"parse_error": True, "raw_content": content}
        row = {
            "condition": name,
            "format": format_spec,
            "label": parsed.get("label"),
            "confidence": parsed.get("confidence"),
            "cited_evidence_ids": parsed.get("cited_evidence_ids"),
            "flagged_evidence_ids": parsed.get("flagged_evidence_ids"),
            "rationale": parsed.get("rationale"),
            "latency_seconds": body.get("_latency_seconds"),
            "prompt_eval_count": body.get("prompt_eval_count"),
            "eval_count": body.get("eval_count"),
        }
        rows.append(row)
        print(
            f"{name}: label={row['label']} confidence={row['confidence']} "
            f"latency={row['latency_seconds']}s",
            flush=True,
        )
        print(f"  rationale={row['rationale']}", flush=True)

    report = {
        "model": args.model,
        "bundle_id": args.bundle_id,
        "defense": args.defense,
        "prompt_version": prompt_version,
        "seed": args.seed,
        "temperature": 0.0,
        "think": False,
        "conditions": rows,
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
