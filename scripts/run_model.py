#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from argparse import ArgumentParser, REMAINDER
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.baseline import KeywordBaseline
from auditpoison.defense import EvidenceShieldAdapter
from auditpoison.harness import CommandAdapter, evaluate_adapter
from auditpoison.io import load_bundles, write_jsonl
from auditpoison.prompting import load_system_prompt
from auditpoison.providers import OllamaAdapter, OpenAICompatibleAdapter
from auditpoison.repro import build_run_manifest, write_manifest

parser = ArgumentParser(description="Run AuditPoison with a reproducible model configuration.")
parser.add_argument("--adapter", choices=["keyword", "command", "ollama", "openai-compatible"], required=True)
parser.add_argument("--defense", choices=["none", "evidenceshield"], default="none")
parser.add_argument("--model", default="keyword-smoke")
parser.add_argument("--output", default="predictions.jsonl")
parser.add_argument("--manifest", default=None)
parser.add_argument("--variant", choices=["all", "clean", "attacked", "benign"], default="all")
parser.add_argument("--limit", type=int, default=None)
parser.add_argument("--base-url", default=None)
parser.add_argument("--api-key-env", default="AUDITPOISON_API_KEY")
parser.add_argument("--temperature", type=float, default=0.0)
parser.add_argument("--seed", type=int, default=7)
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

rows = evaluate_adapter(adapter, bundles)
output = Path(args.output)
write_jsonl(output, rows)
manifest_path = Path(args.manifest) if args.manifest else output.with_suffix(".manifest.json")
config = {
    "variant": args.variant,
    "limit": args.limit,
    "temperature": args.temperature,
    "seed": args.seed,
    "timeout_seconds": args.timeout,
    "max_retries": args.max_retries,
    "base_url": args.base_url,
    "defense": args.defense,
    "prompt_version": prompt_version,
}
manifest = build_run_manifest(
    ROOT,
    output,
    adapter=args.adapter,
    model=adapter.name,
    provider=provider,
    config=config,
    bundle_ids=[bundle["bundle_id"] for bundle in bundles],
    prompt_file=f"prompts/auditor_system_{prompt_version}.txt",
)
write_manifest(manifest_path, manifest)
print(f"Wrote {len(rows)} predictions to {output}")
print(f"Wrote reproducibility manifest to {manifest_path}")
