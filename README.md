# AuditPoison

**Open-source benchmark and defence testbed for adversarial evidence attacks against LLM-based cybersecurity auditors, targeting ACM AsiaCCS 2027.**

AuditPoison evaluates whether an AI auditor can be manipulated into providing false compliance assurance when policies, logs, tickets, exports, and other audit evidence contain malicious, stale, irrelevant, contradictory, or out-of-scope content.

> **Research status:** version 0.4.0 is a development pilot. It is not production compliance advice and its smoke-test results are not scientific model comparisons.

## Version 0.4.0

This release adds **EvidenceShield v0.1**, a provenance-aware defence wrapper with:

- scope and assessment-period screening;
- instruction-like content quarantine;
- unsupported authority-claim detection;
- provenance and integrity labelling;
- model-visible trust annotations;
- a conservative positive-assurance gate;
- defence comparison tooling and regression tests.

The benchmark remains frozen at 40 bundles across 20 paired scenarios so the defence can be evaluated without changing the underlying pilot.

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

Expected: 40 bundles, 20 pairs, and 20 tests passing.

## Inspect EvidenceShield

```bash
python scripts/inspect_defense.py --bundle-id AP-AC2-001-attacked
```

## Compare unshielded and shielded smoke tests

```bash
python scripts/run_model.py --adapter keyword --output results/keyword_raw_predictions.jsonl
python scripts/evaluate_predictions.py results/keyword_raw_predictions.jsonl --output results/keyword_raw_metrics.json

python scripts/run_model.py --adapter keyword --defense evidenceshield --output results/keyword_shield_predictions.jsonl
python scripts/evaluate_predictions.py results/keyword_shield_predictions.jsonl --output results/keyword_shield_metrics.json

python scripts/compare_defenses.py results/keyword_raw_metrics.json results/keyword_shield_metrics.json
python scripts/build_paper_table.py results/keyword_raw_metrics.json results/keyword_shield_metrics.json
```

The keyword adapter is a deterministic software smoke test, not a research baseline.

## Run a real local model

```bash
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --limit 2 --output results/ollama_test.jsonl
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --defense evidenceshield --output results/ollama_shield_predictions.jsonl
```

## Run an OpenAI-compatible endpoint

Set `AUDITPOISON_API_KEY` only in the current shell, then run:

```bash
python scripts/run_model.py --adapter openai-compatible --model YOUR_MODEL --base-url YOUR_BASE_URL --defense evidenceshield --output results/hosted_shield_predictions.jsonl
```

AuditPoison never writes the API key to predictions or manifests.

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
docs/                 Threat model, protocols, and EvidenceShield design
prompts/              Frozen auditor prompts
results/              Metrics and paper tables
schema/               Evidence-bundle JSON Schema
scripts/              Validation, experiments, comparison, and reporting
src/auditpoison/      Python package and defence implementation
tests/                Integrity, leakage, reproducibility, and defence tests
```

## Versions

- `v0.1.0` — threat model and adversarial pilot
- `v0.2.0` — balanced benchmark and evaluation pipeline
- `v0.3.0` — real-model adapters and reproducibility manifests
- `v0.4.0` — EvidenceShield provenance firewall and assurance gate

## Licence and citation

AuditPoison is released under the MIT License. Citation metadata is provided in `CITATION.cff`.
