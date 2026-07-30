#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from auditpoison.defense import screen_evidence
from auditpoison.io import load_bundles

p=ArgumentParser(description="Inspect EvidenceShield screening decisions without running a model.")
p.add_argument("--bundle-id", default=None)
p.add_argument("--output", default=None)
a=p.parse_args()
bundles=load_bundles(ROOT)
if a.bundle_id:
    bundles=[b for b in bundles if b["bundle_id"]==a.bundle_id]
    if not bundles: p.error("unknown bundle id")
rows=[]
for b in bundles:
    report=screen_evidence(b)
    rows.append({"bundle_id":b["bundle_id"],"screening":report})
counts=Counter(r["status"] for row in rows for r in row["screening"].values())
obj={"bundle_count":len(rows),"status_counts":dict(counts),"bundles":rows}
text=json.dumps(obj,indent=2)
if a.output:
    Path(a.output).write_text(text+"\n",encoding="utf-8")
    print(f"Wrote {a.output}")
else:
    print(text)
