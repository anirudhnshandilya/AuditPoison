# AuditPoison v0.6.0

AuditPoison v0.6.0 is a submission-ready research software release focused on reproducibility and safe artifact separation.

## Highlights

- EvidenceShield v0.2 deterministic predicate adjudication.
- Preservation of EvidenceShield v0.1 as a provenance-only ablation.
- Public development benchmark validation and regression tests.
- Clear separation between public software, anonymous reviewer artifacts, and private research records.
- Security, contribution, issue, pull-request, and reproducibility guidance.
- Local anonymous-artifact builder and identity-leak scan.

## Deliberately excluded

This identifiable release does not contain:

- the blinded holdout oracle;
- unlock keys;
- local model prediction files;
- the private manuscript;
- author-identifying experimental paths;
- pre-unseal records containing local filesystem paths.

Those materials belong in the separately anonymized reviewer artifact or private research archive.

## Validation

```bash
python scripts/validate_dataset.py
python -m pytest -q
git diff --check
```
