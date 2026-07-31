# Changelog

## 0.6.0 — Research release hygiene

- Added public-release and anonymous-artifact boundaries.
- Added reproducibility, security, contribution, issue, and pull-request guidance.
- Documented that local model outputs, blinded holdouts, oracle material, and manuscripts must not enter the identifiable public repository.
- Preserved EvidenceShield v0.1 as the provenance-only ablation.
- Preserved EvidenceShield v0.2 as the deterministic predicate adjudicator.
- Updated package and citation metadata to version 0.6.0.
- Added a local builder for a separately anonymized reviewer artifact.
- No blinded oracle labels, private manuscript files, unlock keys, or local model outputs are included in this public release.

## 0.5.0 — EvidenceShield v0.2

- Added explicit control predicates with `satisfied`, `failed`, and `unresolved` outcomes.
- Removed final compliance authority from the language model.
- Added deterministic verdict adjudication and advisory-label logging.
- Added predicate inspection and regression tests.
- Preserved EvidenceShield v0.1 for ablation.

## 0.4.0 — EvidenceShield v0.1

- Added provenance, scope, assessment-period, integrity, and authority screening.
- Added instruction-like content quarantine and model-visible trust annotations.
- Added the historical positive-assurance gate and defence-comparison tooling.

## 0.3.0 — Reproducible model execution

- Added native Ollama and OpenAI-compatible adapters.
- Added retry handling, latency and token telemetry, response hashes, and manifests.
- Added GitHub Actions CI and paper-table generation.

## 0.2.0 — Balanced development benchmark

- Expanded the benchmark to 40 bundles and 20 paired scenarios.
- Added compliant clean/benign pairs and six benign perturbation families.
- Added three-class, paired-robustness, citation, evidence-detection, and calibration metrics.
- Removed model-visible variant identifiers and metadata leakage.

## 0.1.0 — Initial threat model

- Defined the threat model, evidence schema, annotation rules, and pilot scope.
- Added clean/attacked pairs spanning six adversarial evidence families.
- Added validation, tests, a frozen prompt, and an offline keyword smoke baseline.
