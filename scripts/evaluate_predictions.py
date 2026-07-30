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
parser.add_argument('--variant', choices=['all', 'clean', 'attacked', 'benign'], default='all')
args = parser.parse_args()
bundles = load_bundles(ROOT)
if args.variant != 'all':
    bundles = [b for b in bundles if b['variant'] == args.variant]
result = evaluate_predictions(bundles, read_jsonl(args.predictions))
print(json.dumps(result, indent=2))
