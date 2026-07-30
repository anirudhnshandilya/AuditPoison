# AuditPoison v0.5.0 — EvidenceShield v0.2

This release replaces model-controlled compliance verdicts with deterministic predicate adjudication.

## Added

- Control-specific predicate engine for all ten pilot controls.
- `satisfied`, `failed`, and `unresolved` predicate states.
- Deterministic three-class verdict policy.
- Prediction-level predicate traces and advisory-model labels.
- EvidenceShield v0.1/v0.2 ablation support.
- Standalone predicate inspection command.
- Frozen EvidenceShield v0.2 analyst prompt.
- Seven new defence and non-leakage tests.

## Fixed

- False environment mismatches caused by ordinary phrases such as “restoration test”.
- Loss of decisive technical facts when an injected instruction appeared inside a verified export.
- Model–rationale contradictions producing unsafe final labels.

## Verification

```bash
python -m pip install -e ".[dev]"
python scripts/validate_dataset.py
python -m pytest -q
```

Expected result:

```text
AuditPoison validation PASSED: 40 bundles in 20 paired scenarios.
31 passed
```

## Research warning

The predicate engine is deliberately aligned to the structured pilot evidence language. Its perfect pilot contract result is not a claim of generalisation. The next benchmark phase must use independently authored held-out cases and real-world evidence transformations.
