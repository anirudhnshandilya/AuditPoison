#!/usr/bin/env python3
from __future__ import annotations
import json
from argparse import ArgumentParser
from pathlib import Path
KEYS=("accuracy","macro_f1","false_assurance_rate","paired_attack_success_rate","paired_attack_robust_accuracy","compliant_rejection_rate","benign_label_consistency","citation_f1","attack_evidence_detection_recall","benign_evidence_false_flag_rate")
p=ArgumentParser(description="Compare unshielded and EvidenceShield metric files.")
p.add_argument("unshielded")
p.add_argument("shielded")
p.add_argument("--output",default="results/defense_comparison.md")
a=p.parse_args()
base=json.loads(Path(a.unshielded).read_text(encoding="utf-8"))
shield=json.loads(Path(a.shielded).read_text(encoding="utf-8"))
lines=["| Metric | Unshielded | EvidenceShield | Delta |","|---|---:|---:|---:|"]
for k in KEYS:
    x=float(base.get(k,0)); y=float(shield.get(k,0))
    lines.append(f"| {k.replace('_',' ').title()} | {100*x:.1f} | {100*y:.1f} | {100*(y-x):+.1f} |")
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
Path(a.output).write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"Wrote {a.output}")
