#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.defense import shield_bundle
from auditpoison.io import load_bundles
from auditpoison.predicate_engine import adjudicate_predicates, deterministic_confidence, deterministic_label

parser = ArgumentParser(description="Inspect EvidenceShield v0.2 predicate adjudication without calling a model.")
parser.add_argument("--bundle-id", required=True)
parser.add_argument("--output", default=None)
args = parser.parse_args()

bundle = next((item for item in load_bundles(ROOT) if item["bundle_id"] == args.bundle_id), None)
if bundle is None:
    parser.error("unknown bundle id")

screened, screening = shield_bundle(bundle)
outcomes = adjudicate_predicates(screened, screening)
result = {
    "bundle_id": bundle["bundle_id"],
    "control_id": bundle["control"]["control_id"],
    "screening": screening,
    "predicate_outcomes": [item.to_dict() for item in outcomes],
    "deterministic_label": deterministic_label(outcomes),
    "deterministic_confidence": deterministic_confidence(outcomes),
}
text = json.dumps(result, indent=2, ensure_ascii=False)
if args.output:
    Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
else:
    print(text)
