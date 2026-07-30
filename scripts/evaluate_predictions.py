#!/usr/bin/env python3
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.io import load_bundles, read_jsonl
from auditpoison.metrics import evaluate_predictions

parser = ArgumentParser()
parser.add_argument("predictions")
parser.add_argument("--variant", choices=["all", "clean", "attacked", "benign"], default="all")
parser.add_argument("--output", default=None)
args = parser.parse_args()
bundles = load_bundles(ROOT)
if args.variant != "all":
    bundles = [bundle for bundle in bundles if bundle["variant"] == args.variant]
predictions = read_jsonl(args.predictions)
result = evaluate_predictions(bundles, predictions)
models = sorted({str(row.get("model", "unknown")) for row in predictions})
providers = sorted({str(row.get("provider", "unknown")) for row in predictions})
result["model"] = models[0] if len(models) == 1 else ", ".join(models)
result["provider"] = providers[0] if len(providers) == 1 else ", ".join(providers)
result["predictions_file"] = str(args.predictions)
rendered = json.dumps(result, indent=2)
print(rendered)
if args.output:
    Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote metrics to {args.output}")
