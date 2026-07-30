#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable, str(ROOT / 'scripts' / 'run_experiment.py'), '--adapter', 'keyword', *sys.argv[1:]]))
