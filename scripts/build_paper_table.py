#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.reporting import latex_table, load_metric_files, markdown_table

parser = ArgumentParser(description="Build Markdown and LaTeX result tables.")
parser.add_argument("metrics", nargs="+")
parser.add_argument("--latex", default="results/table_main.tex")
parser.add_argument("--markdown", default="results/table_main.md")
args = parser.parse_args()
rows = load_metric_files(args.metrics)
latex_path = Path(args.latex)
markdown_path = Path(args.markdown)
latex_path.parent.mkdir(parents=True, exist_ok=True)
markdown_path.parent.mkdir(parents=True, exist_ok=True)
latex_path.write_text(latex_table(rows), encoding="utf-8")
markdown_path.write_text(markdown_table(rows), encoding="utf-8")
print(f"Wrote {latex_path}")
print(f"Wrote {markdown_path}")
