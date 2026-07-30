# AuditPoison v0.4.0 — EvidenceShield

AuditPoison v0.4.0 adds EvidenceShield v0.1, a provenance-aware defence wrapper for LLM-based cybersecurity audit pipelines.

## Added

- Evidence scope and assessment-period screening
- Instruction-like content quarantine
- Unsupported authority-claim detection
- Provenance and integrity trust labels
- Conservative positive-assurance gate
- Frozen defended auditor prompt v0.3
- Defence inspection and comparison commands
- Reproducibility manifest support for defended runs
- Nine new defence and non-oracle tests

## Pilot status

The benchmark remains a 40-bundle development pilot. Included keyword results verify the software path and illustrate the security–utility trade-off; they are not scientific model results. Real-model experiments and repeated trials are required before paper claims are made.

## Verification

```bash
python -m pip install -e ".[dev]"
python scripts/validate_dataset.py
python -m pytest -q
```

Expected: 40 bundles, 20 pairs, and 20 passing tests.
