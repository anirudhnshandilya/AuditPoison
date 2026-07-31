# AuditPoison Anonymous Reviewer Artifact

This artifact accompanies an anonymized submission studying adversarial evidence attacks against LLM-based cybersecurity auditors.

## Contents

- `software/`: frozen benchmark and defence implementation;
- `holdout_v2/`: blinded holdout inputs, completed registered predictions, evaluation outputs, and analysis;
- `ARTIFACT_SHA256SUMS.txt`: relative-path SHA-256 inventory;
- `ANONYMIZATION_REPORT.txt`: identity-leak scan result;
- `ORIGINAL_COMMITMENT_DIGESTS.txt`: hashes of excluded path-bearing commitment records.

## Reproduce public checks

```bash
cd software
python -m pip install -e ".[dev]"
python scripts/validate_dataset.py
python -m pytest -q
```

## Verify artifact files

Use any SHA-256 utility to compare files against `ARTIFACT_SHA256SUMS.txt`.

## Evaluation boundary

The registered blinded matrix contains two local model families under unshielded, provenance-only, and deterministic predicate-adjudication conditions. The oracle was opened only after all registered runs were complete and a pre-unseal commitment was recorded.

## Anonymization

Git history, citation metadata, public repository URLs, author metadata, home-directory paths, usernames, and private paper files are excluded or replaced. The scientific JSONL prediction content and evaluation outputs are otherwise preserved.
