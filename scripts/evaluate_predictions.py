#!/usr/bin/env python3
from argparse import ArgumentParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from auditpoison.io import load_bundles, read_jsonl
from auditpoison.metrics import evaluate_predictions

parser = ArgumentParser()
parser.add_argument('predictions')
args = parser.parse_args()

result = evaluate_predictions(load_bundles(ROOT), read_jsonl(args.predictions))
print(json.dumps(result, indent=2))
