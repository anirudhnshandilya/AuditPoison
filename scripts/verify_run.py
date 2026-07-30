#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from auditpoison.repro import verify_manifest

parser = ArgumentParser(description="Verify dataset, prompt, and prediction hashes in a run manifest.")
parser.add_argument("manifest")
args = parser.parse_args()
failures = verify_manifest(ROOT, args.manifest)
if failures:
    print("Run verification FAILED:")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)
print("Run verification PASSED")
