# AuditPoison

[![CI](https://github.com/anirudhnshandilya/AuditPoison/actions/workflows/ci.yml/badge.svg)](https://github.com/anirudhnshandilya/AuditPoison/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21704967.svg)](https://doi.org/10.5281/zenodo.21704967)

**A reproducible benchmark and defence testbed for adversarial evidence attacks against LLM-based cybersecurity auditors.**

AuditPoison studies a failure mode that ordinary prompt-injection benchmarks miss: an AI auditor can produce unsafe compliance assurance when apparently legitimate policies, logs, tickets, exports, and attestations contain malicious, stale, contradictory, irrelevant, or out-of-scope evidence.

> **Research status:** `v0.6.0` is a research release. It is not production compliance advice. The public repository contains the development benchmark and reproducible defence implementation; blinded-study materials are distributed separately through an anonymized review artifact.

## Why AuditPoison

Compliance-oriented AI systems do more than summarize text. They combine evidence from multiple sources and issue high-impact judgments such as `compliant`, `non_compliant`, or `insufficient_evidence`. AuditPoison tests whether those judgments remain safe when evidence is adversarially manipulated.

The benchmark covers:

- instruction injection inside audit evidence;
- authority spoofing;
- contradiction flooding;
- temporal rollback;
- scope substitution;
- evidence omission;
- benign formatting, ordering, metadata, paraphrase, duplication, and irrelevant-context changes.

## EvidenceShield

EvidenceShield separates evidence interpretation from final authorization to certify compliance.

### EvidenceShield v0.1

A provenance-aware wrapper that screens scope, assessment period, provenance, integrity, unsupported authority claims, and instruction-bearing content. The language model still controls the final verdict.

### EvidenceShield v0.2

A deterministic predicate adjudicator:

```text
Any failed predicate        -> non_compliant
No failures, any unresolved -> insufficient_evidence
All predicates satisfied    -> compliant
```

The model can assist with evidence extraction, but it cannot directly authorize a positive compliance verdict.

## Public development benchmark

| Oracle label | Bundles |
|---|---:|
| Compliant | 20 |
| Non-compliant | 15 |
| Insufficient evidence | 5 |
| **Total** | **40** |

The 40 bundles form 20 paired scenarios. Public pilot results are contract and implementation checks, not evidence of production generalization.

## Installation

```bash
git clone https://github.com/anirudhnshandilya/AuditPoison.git
cd AuditPoison
python -m venv .venv
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Linux and macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Validate the repository

```bash
python scripts/validate_dataset.py
python -m pytest -q
```

Expected public-release checks:

```text
40 bundles
20 paired scenarios
31 tests passing
```

## Inspect predicate decisions

```bash
python scripts/inspect_predicates.py --bundle-id AP-IA2-005-attacked
```

## Run an experiment

Unshielded:

```bash
python scripts/run_model.py \
  --adapter ollama \
  --model YOUR_MODEL \
  --defense none \
  --output results/model_unshielded.jsonl
```

EvidenceShield v0.1 ablation:

```bash
python scripts/run_model.py \
  --adapter ollama \
  --model YOUR_MODEL \
  --defense evidenceshield-v0.1 \
  --output results/model_v01.jsonl
```

EvidenceShield v0.2:

```bash
python scripts/run_model.py \
  --adapter ollama \
  --model YOUR_MODEL \
  --defense evidenceshield-v0.2 \
  --output results/model_v02.jsonl
```

`--defense evidenceshield` is an alias for `evidenceshield-v0.2`.

## Metrics

AuditPoison reports:

- accuracy and macro F1;
- False Assurance Rate;
- paired attack success and robust accuracy;
- benign consistency and both-correct rate;
- citation precision, recall, and F1;
- attack-evidence detection and benign false-flag rate;
- Brier score and expected calibration error.

## Repository layout

```text
data/pilot/           Public development evidence bundles
docs/                 Threat model, protocols, and defence designs
examples/             Minimal usage examples
prompts/              Frozen auditor and analyst prompts
results/              Curated public smoke-test outputs only
schema/               Evidence-bundle JSON Schema
scripts/              Validation, experiments, and reporting
src/auditpoison/      Python package and EvidenceShield
tests/                Integrity, leakage, reproducibility, and defence tests
```

## Reproducibility and release boundaries

See [`docs/reproducibility.md`](docs/reproducibility.md) for the frozen software contract, environment recording, and result-manifest requirements.

Local model outputs, blinded holdouts, oracle keys, manuscripts, and pre-unseal records must not be committed to this identifiable public repository. The anonymized reviewer artifact is built separately.

## Limitations

AuditPoison is a controlled research benchmark. It does not certify real organizations, replace professional auditors, or demonstrate coverage of every compliance framework, model family, document type, or operational environment.

## Security

Please read [`SECURITY.md`](SECURITY.md). Do not submit real credentials, customer evidence, secrets, regulated data, or production audit material.

## Contributing

Contributions are welcome. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and preserve the benchmark’s leakage, provenance, and deterministic-verdict invariants.

## Citation

AuditPoison is released under the MIT License. Citation metadata is provided in [`CITATION.cff`](CITATION.cff).
