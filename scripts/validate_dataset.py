#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from auditpoison.validator import validate_repository

errors = validate_repository(ROOT)
if errors:
    print('AuditPoison validation FAILED')
    for error in errors:
        print(f'- {error}')
    raise SystemExit(1)
print('AuditPoison validation PASSED: 20 bundles in 10 clean/attacked pairs.')
