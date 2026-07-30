#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from auditpoison.io import load_bundles, read_jsonl, write_jsonl
from auditpoison.parsing import parse_model_response

parser = ArgumentParser(description='Convert raw provider responses into canonical predictions JSONL.')
parser.add_argument('raw_outputs', help='JSONL rows with bundle_id and response fields')
parser.add_argument('--output', default='predictions.jsonl')
parser.add_argument('--model-name', default='external-model')
args = parser.parse_args()

bundles = {b['bundle_id']: b for b in load_bundles(ROOT)}
rows = []
for line_number, row in enumerate(read_jsonl(args.raw_outputs), start=1):
    bid = row.get('bundle_id')
    if bid not in bundles:
        raise SystemExit(f'Line {line_number}: unknown bundle_id {bid!r}')
    if 'response' not in row:
        raise SystemExit(f'Line {line_number}: missing response field')
    try:
        parsed = parse_model_response(bundles[bid], row['response'])
    except ValueError as exc:
        raise SystemExit(f'Line {line_number} ({bid}): {exc}') from exc
    parsed['model'] = args.model_name
    rows.append(parsed)
write_jsonl(args.output, rows)
print(f'Wrote {len(rows)} canonical predictions to {args.output}')
