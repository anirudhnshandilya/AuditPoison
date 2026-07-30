#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from auditpoison.baseline import KeywordBaseline
from auditpoison.harness import evaluate_adapter
from auditpoison.io import load_bundles, write_jsonl

parser = ArgumentParser()
parser.add_argument('--output', default='baseline_predictions.jsonl')
args = parser.parse_args()

rows = evaluate_adapter(KeywordBaseline(), load_bundles(ROOT))
write_jsonl(args.output, rows)
print(f'Wrote {len(rows)} predictions to {args.output}')
