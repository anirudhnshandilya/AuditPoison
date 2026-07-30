#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from argparse import ArgumentParser, REMAINDER
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.baseline import KeywordBaseline
from auditpoison.defense import EvidenceShieldAdapter
from auditpoison.harness import CommandAdapter, evaluate_adapter
from auditpoison.io import append_jsonl, load_bundles, read_jsonl
from auditpoison.prompting import load_system_prompt
from auditpoison.providers import OllamaAdapter, OpenAICompatibleAdapter
from auditpoison.repro import build_run_manifest, verify_manifest, write_manifest

parser = ArgumentParser(description="Run AuditPoison with a reproducible model configuration.")
parser.add_argument("--adapter", choices=["keyword", "command", "ollama", "openai-compatible"], required=True)
parser.add_argument("--defense", choices=["none", "evidenceshield"], default="none")
parser.add_argument("--model", default="keyword-smoke")
parser.add_argument("--output", default="predictions.jsonl")
parser.add_argument("--manifest", default=None)
parser.add_argument("--variant", choices=["all", "clean", "attacked", "benign"], default="all")
parser.add_argument("--limit", type=int, default=None)
parser.add_argument("--resume", action="store_true", help="Resume an interrupted run from its checkpoint manifest.")
parser.add_argument("--base-url", default=None)
parser.add_argument("--api-key-env", default="AUDITPOISON_API_KEY")
parser.add_argument("--temperature", type=float, default=0.0)
parser.add_argument("--seed", type=int, default=7)
parser.add_argument(
    "--ollama-think",
    action="store_true",
    help="Enable the model's native thinking mode for Ollama runs (disabled by default).",
)
parser.add_argument("--timeout", type=float, default=180.0)
parser.add_argument("--max-retries", type=int, default=3)
parser.add_argument("--command", nargs=REMAINDER, help="External command; must be the final argument")
args = parser.parse_args()

bundles = load_bundles(ROOT)
if args.variant != "all":
    bundles = [bundle for bundle in bundles if bundle["variant"] == args.variant]
if args.limit is not None:
    if args.limit < 1:
        parser.error("--limit must be positive")
    bundles = bundles[: args.limit]

prompt_version = "v0.3" if args.defense == "evidenceshield" else "v0.2"
system_prompt = load_system_prompt(ROOT, prompt_version)
if args.adapter == "keyword":
    adapter = KeywordBaseline()
    provider = "offline"
elif args.adapter == "command":
    if not args.command:
        parser.error("--command is required and must appear last")
    adapter = CommandAdapter(args.command, system_prompt, args.model)
    provider = "command"
elif args.adapter == "ollama":
    adapter = OllamaAdapter(
        model=args.model,
        system_prompt=system_prompt,
        base_url=args.base_url or "http://localhost:11434/api",
        temperature=args.temperature,
        seed=args.seed,
        think=args.ollama_think,
        timeout=args.timeout,
        max_retries=args.max_retries,
    )
    provider = "ollama"
else:
    key = os.environ.get(args.api_key_env, "")
    if not key:
        parser.error(f"Environment variable {args.api_key_env} is not set")
    adapter = OpenAICompatibleAdapter(
        model=args.model,
        system_prompt=system_prompt,
        api_key=key,
        base_url=args.base_url or "https://api.openai.com/v1",
        temperature=args.temperature,
        seed=args.seed,
        timeout=args.timeout,
        max_retries=args.max_retries,
    )
    provider = "openai-compatible"

if args.defense == "evidenceshield":
    adapter = EvidenceShieldAdapter(adapter)

output = Path(args.output)
manifest_path = Path(args.manifest) if args.manifest else output.with_suffix(".manifest.json")
requested_bundle_ids = [bundle["bundle_id"] for bundle in bundles]
config = {
    "variant": args.variant,
    "limit": args.limit,
    "temperature": args.temperature,
    "seed": args.seed,
    "ollama_think": args.ollama_think if args.adapter == "ollama" else None,
    "timeout_seconds": args.timeout,
    "max_retries": args.max_retries,
    "base_url": args.base_url,
    "defense": args.defense,
    "prompt_version": prompt_version,
}

existing_rows: list[dict] = []
run_id: str | None = None
if args.resume:
    if not output.exists() or not manifest_path.exists():
        parser.error("--resume requires both the predictions file and its checkpoint manifest")
    failures = verify_manifest(ROOT, manifest_path)
    if failures:
        parser.error("Cannot resume: " + "; ".join(failures))
    previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {
        "adapter": args.adapter,
        "provider": provider,
        "model": adapter.name,
        "configuration": config,
        "requested_bundle_ids": requested_bundle_ids,
    }
    mismatches = [key for key, value in expected.items() if previous.get(key) != value]
    if mismatches:
        parser.error("Cannot resume because configuration changed: " + ", ".join(mismatches))
    existing_rows = read_jsonl(output)
    existing_ids = [str(row.get("bundle_id", "")) for row in existing_rows]
    if len(existing_ids) != len(set(existing_ids)):
        parser.error("Cannot resume: duplicate bundle_id values in predictions")
    if existing_ids != previous.get("bundle_ids", []):
        parser.error("Cannot resume: predictions and checkpoint bundle IDs disagree")
    run_id = previous.get("run_id")
    print(f"Resuming with {len(existing_rows)}/{len(bundles)} completed predictions.", flush=True)
else:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("", encoding="utf-8")

completed_ids = {str(row["bundle_id"]) for row in existing_rows}
unknown_ids = completed_ids - set(requested_bundle_ids)
if unknown_ids:
    parser.error(f"Predictions contain IDs outside this run: {sorted(unknown_ids)}")
pending = [bundle for bundle in bundles if bundle["bundle_id"] not in completed_ids]
rows = list(existing_rows)

def checkpoint(status: str) -> None:
    global run_id
    manifest = build_run_manifest(
        ROOT,
        output,
        adapter=args.adapter,
        model=adapter.name,
        provider=provider,
        config=config,
        bundle_ids=[str(row["bundle_id"]) for row in rows],
        prompt_file=f"prompts/auditor_system_{prompt_version}.txt",
    )
    if run_id is None:
        run_id = manifest["run_id"]
    else:
        manifest["run_id"] = run_id
    manifest["requested_bundle_count"] = len(requested_bundle_ids)
    manifest["requested_bundle_ids"] = requested_bundle_ids
    manifest["run_status"] = status
    write_manifest(manifest_path, manifest)

def persist(row: dict) -> None:
    append_jsonl(output, row)
    rows.append(row)
    checkpoint("complete" if len(rows) == len(bundles) else "in_progress")

if not args.resume:
    checkpoint("in_progress" if pending else "complete")

evaluate_adapter(
    adapter,
    pending,
    start_index=len(existing_rows),
    total=len(bundles),
    on_row=persist,
)
if not pending:
    checkpoint("complete")
print(f"Wrote {len(rows)} predictions to {output}")
print(f"Wrote reproducibility manifest to {manifest_path}")
