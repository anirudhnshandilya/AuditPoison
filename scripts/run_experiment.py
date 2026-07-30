#!/usr/bin/env python3
from argparse import ArgumentParser, REMAINDER
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from auditpoison.baseline import KeywordBaseline
from auditpoison.harness import CommandAdapter, evaluate_adapter
from auditpoison.io import load_bundles, write_jsonl
from auditpoison.prompting import load_system_prompt

parser = ArgumentParser(description='Run the benchmark through a built-in or external adapter.')
parser.add_argument('--adapter', choices=['keyword', 'command'], required=True)
parser.add_argument('--output', default='predictions.jsonl')
parser.add_argument('--model-name', default='external-command-model')
parser.add_argument('--variant', choices=['all', 'clean', 'attacked', 'benign'], default='all')
parser.add_argument('--command', nargs=REMAINDER, help='Command executable and arguments; must appear last')
args = parser.parse_args()

bundles = load_bundles(ROOT)
if args.variant != 'all':
    bundles = [b for b in bundles if b['variant'] == args.variant]
if args.adapter == 'keyword':
    adapter = KeywordBaseline()
else:
    if not args.command:
        parser.error('--command is required for command adapter and must appear last')
    adapter = CommandAdapter(args.command, load_system_prompt(ROOT), args.model_name)
rows = evaluate_adapter(adapter, bundles)
write_jsonl(args.output, rows)
print(f'Wrote {len(rows)} predictions from {adapter.name} to {args.output}')
