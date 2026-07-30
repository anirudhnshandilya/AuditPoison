# Changelog

## [0.5.0] - 2026-07-30

### Added
- EvidenceShield v0.2 deterministic predicate adjudication for all ten pilot controls.
- Predicate traces, advisory-model labels, and decision-source fields in prediction rows.
- EvidenceShield v0.1/v0.2 ablation options and frozen analyst prompt v0.4.
- Predicate inspection tooling and seven regression tests.

### Fixed
- Environment false positives caused by ordinary uses of the word “test”.
- Destructive quarantine of verified technical exports containing injected comments.
- Unsafe model-label and rationale inconsistencies in final verdicts.

## [0.4.0] - 2026-07-30

### Added
- EvidenceShield v0.1 evidence screening and positive-assurance gate.
- Scope, temporal, instruction, authority, and provenance checks.
- Defence inspection and metric-comparison scripts.
- Frozen EvidenceShield auditor prompt v0.3.
- Defence regression and non-oracle leakage tests.

### Changed
- Reproducibility manifests now record the selected frozen prompt and defence configuration.
- Public documentation now uses repository-clone instructions.

## 0.3.0 — Day 3

- Added native Ollama and OpenAI-compatible HTTP adapters.
- Added retry handling, latency and token telemetry, and response hashes.
- Added dataset, prompt, prediction, environment, and Git commit manifests.
- Added manifest verification and paper-ready Markdown/LaTeX table generation.
- Added GitHub Actions CI and a PowerShell history-bootstrap script.

## 0.2.0 — Day 2

- Expanded the benchmark to 40 bundles and 20 paired scenarios.
- Added 10 compliant clean/benign pairs and six benign perturbation families.
- Added three-class, paired robustness, citation, evidence detection, and calibration metrics.
- Removed model-visible variant identifiers and metadata leakage.

## 0.1.0 — Day 1

- Defined the threat model, evidence schema, annotation rules, and 12-control pilot scope.
- Added 10 clean/attacked pairs spanning six adversarial evidence families.
- Added validation, tests, a frozen prompt, and an offline keyword smoke baseline.
