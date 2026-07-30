# AuditPoison

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21704967.svg)](https://doi.org/10.5281/zenodo.21704967)

**Open-source benchmark and defence testbed for adversarial evidence attacks against LLM-based cybersecurity auditors, targeting ACM AsiaCCS 2027.**

AuditPoison evaluates whether an AI auditor can be manipulated into providing false compliance assurance when policies, logs, tickets, exports, and other audit evidence contain malicious, stale, irrelevant, contradictory, or out-of-scope content.

> **Research status:** version 0.5.0 is a development pilot. It is not production compliance advice, and pilot contract results are not evidence of real-world generalisation.

## EvidenceShield v0.2

Version `0.5.0` removes final compliance authority from the language model.

EvidenceShield now:

- screens provenance, scope, environment, and assessment-period validity;
- quarantines unsupported authority claims and untrusted instructions;
- sanitizes instruction-bearing comments inside verified technical exports;
- evaluates explicit control predicates as `satisfied`, `failed`, or `unresolved`;
- assigns the final label deterministically;
- records the model’s original advisory label for ablation analysis;
- preserves EvidenceShield v0.1 for reproducing the provenance-only defence.

Deterministic verdict policy:

```text
Any failed predicate        -> non_compliant
No failures, any unresolved -> insufficient_evidence
All predicates satisfied    -> compliant
```

## Benchmark composition

| Oracle label | Bundles |
|---|---:|
| Compliant | 20 |
| Non-compliant | 15 |
| Insufficient evidence | 5 |
| **Total** | **40** |

Attack families: instruction injection, authority spoofing, contradiction flooding, temporal rollback, scope substitution, and evidence omission.

Benign perturbations: formatting noise, evidence reordering, irrelevant context, duplicate support, semantic paraphrasing, and metadata noise.

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

## Validate

```bash
python scripts/validate_dataset.py
python -m pytest -q
```

Expected: 40 bundles, 20 pairs, and 31 tests passing.

## Inspect deterministic predicates

```bash
python scripts/inspect_predicates.py --bundle-id AP-IA2-005-attacked
```

## Run model experiments

Unshielded:

```bash
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --defense none --output results/model_unshielded.jsonl
```

Historical EvidenceShield v0.1 ablation:

```bash
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --defense evidenceshield-v0.1 --output results/model_v01.jsonl
```

EvidenceShield v0.2:

```bash
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --defense evidenceshield-v0.2 --output results/model_v02.jsonl
```

`--defense evidenceshield` is an alias for `evidenceshield-v0.2`.

## Important interpretation rule

The v0.2 predicate engine is explicitly designed for the frozen structured pilot. A 100% contract-test result on these 40 bundles demonstrates implementation consistency only. It must not be presented as benchmark generalisation or production effectiveness.

## Core metrics

- accuracy and macro F1;
- False Assurance Rate;
- paired Attack Success Rate and robust accuracy;
- benign consistency and both-correct rate;
- citation precision, recall, and F1;
- attack-evidence detection and benign false-flag rate;
- Brier score and expected calibration error.

## Repository layout

```text
data/pilot/           Evidence bundles
docs/                 Threat model, protocols, and EvidenceShield designs
prompts/              Frozen auditor and analyst prompts
results/              Local metrics and paper tables
schema/               Evidence-bundle JSON Schema
scripts/              Validation, experiments, inspection, and reporting
src/auditpoison/      Python package, screening, and predicate engine
tests/                Integrity, leakage, reproducibility, and defence tests
```

## Versions

- `v0.1.0` — threat model and adversarial pilot
- `v0.2.0` — balanced benchmark and evaluation pipeline
- `v0.3.0` — real-model adapters and reproducibility manifests
- `v0.4.0` — EvidenceShield v0.1 provenance firewall
- `v0.5.0` — EvidenceShield v0.2 deterministic predicate adjudication

## Licence and citation

AuditPoison is released under the MIT License. Citation metadata is provided in `CITATION.cff`.


## Blinded holdout protocol

The 40-bundle pilot is development data. The primary generalisation study uses a separately stored 60-bundle blinded holdout whose oracle labels and pair metadata are encrypted until all preregistered runs finish. The security-critical implementation is frozen through `scripts/freeze_holdout.py` before any holdout evaluation. See `docs/blinded_holdout_protocol.md`.
