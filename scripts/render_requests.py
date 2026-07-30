#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from auditpoison.io import load_bundles, write_jsonl
from auditpoison.prompting import load_system_prompt, render_request

parser = ArgumentParser(description='Render provider-neutral model requests without oracle or attack metadata.')
parser.add_argument('--output', default='model_requests.jsonl')
parser.add_argument('--variant', choices=['all', 'clean', 'attacked', 'benign'], default='all')
args = parser.parse_args()

bundles = load_bundles(ROOT)
if args.variant != 'all':
    bundles = [b for b in bundles if b['variant'] == args.variant]
system = load_system_prompt(ROOT)
write_jsonl(args.output, [render_request(b, system) for b in bundles])
print(f'Wrote {len(bundles)} redacted requests to {args.output}')
