## Summary

Describe the change and its purpose.

## Validation

- [ ] `python scripts/validate_dataset.py`
- [ ] `python -m pytest -q`
- [ ] `git diff --check`

## Research contract

- [ ] No model-visible oracle or variant leakage was introduced.
- [ ] EvidenceShield v0.2 deterministic verdict semantics remain explicit.
- [ ] Frozen prompts, schemas, or metrics changed only when documented.
- [ ] No private results, manuscript files, keys, credentials, or local paths are included.

## Compatibility and limitations

Describe any behavior, schema, benchmark, or reproducibility implications.
