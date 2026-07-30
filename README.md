# AuditPoison

**Adversarial evidence attacks against LLM-based cybersecurity auditors.**

AuditPoison evaluates whether an AI auditor can be manipulated into providing false compliance assurance when policies, logs, tickets, exports, and other audit evidence contain malicious, stale, irrelevant, contradictory, or out-of-scope content.

> **Development status:** AuditPoison is currently an experimental research pilot. Its results must not be treated as production compliance advice.

## Overview

Version `0.3.0` provides an end-to-end reproducible benchmark pilot with:

* 40 validated evidence bundles across 20 paired scenarios
* 10 adversarial clean/attacked pairs spanning six attack families
* 10 compliant clean/benign pairs spanning six harmless perturbation families
* Three oracle labels: `compliant`, `non_compliant`, and `insufficient_evidence`
* Native Ollama and OpenAI-compatible model adapters
* Provider-neutral command and offline-import interfaces
* Cryptographic experiment manifests and result verification
* Paper-ready Markdown and LaTeX result tables
* Continuous integration across Python 3.10–3.13

## Research question

AuditPoison studies whether an attacker who controls part of an audit evidence bundle can cause an LLM-based auditor to confidently certify a control that is unsupported, ineffective, stale, or outside the relevant scope.

The primary failure is **false assurance**: a `compliant` verdict issued for a case whose oracle label is `non_compliant` or `insufficient_evidence`.

## Dataset composition

| Oracle label          | Bundles |
| --------------------- | ------: |
| Compliant             |      20 |
| Non-compliant         |      15 |
| Insufficient evidence |       5 |
| **Total**             |  **40** |

The pilot is balanced at the false-assurance boundary:

* 20 bundles support a compliant decision.
* 20 bundles make a compliant decision unsafe.

## Attack families

AuditPoison currently includes six adversarial evidence attacks:

1. **Instruction injection** — malicious instructions embedded inside evidence.
2. **Authority spoofing** — unsupported claims of auditor or management approval.
3. **Contradiction flooding** — numerous weak claims used to overwhelm stronger contradictory evidence.
4. **Temporal rollback** — stale favourable evidence presented as current.
5. **Scope substitution** — valid evidence from the wrong asset, account, system, or period.
6. **Evidence omission** — decisive evidence removed to encourage unsupported compliance.

## Benign perturbations

The benchmark also measures stability under harmless changes:

* Formatting noise
* Evidence reordering
* Irrelevant context
* Duplicated supporting evidence
* Semantic paraphrasing
* Metadata noise

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/anirudhnshandilya/AuditPoison.git
cd AuditPoison
```

Create an optional virtual environment.

### Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Validate the benchmark

```bash
python scripts/validate_dataset.py
python -m pytest -q
```

Expected result:

```text
AuditPoison validation PASSED: 40 bundles in 20 paired scenarios.
11 passed
```

## Offline smoke test

Run the deterministic keyword adapter to verify the complete pipeline:

```bash
python scripts/run_model.py --adapter keyword --output results/keyword_predictions.jsonl
python scripts/evaluate_predictions.py results/keyword_predictions.jsonl --output results/keyword_metrics.json
python scripts/verify_run.py results/keyword_predictions.manifest.json
python scripts/build_paper_table.py results/keyword_metrics.json
```

The keyword adapter is only a software smoke test. It is not a scientific model baseline.

## Run a local model with Ollama

Install Ollama, start its service, and pull a model suitable for your hardware.

Begin with a two-bundle contract test:

```bash
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --limit 2 --output results/ollama_test.jsonl
```

Run the full benchmark:

```bash
python scripts/run_model.py --adapter ollama --model YOUR_MODEL --output results/YOUR_MODEL_predictions.jsonl
python scripts/evaluate_predictions.py results/YOUR_MODEL_predictions.jsonl --output results/YOUR_MODEL_metrics.json
python scripts/verify_run.py results/YOUR_MODEL_predictions.manifest.json
```

## Run an OpenAI-compatible endpoint

Set the API key only for the current terminal session.

### Windows Command Prompt

```cmd
set AUDITPOISON_API_KEY=YOUR_KEY
```

### Windows PowerShell

```powershell
$env:AUDITPOISON_API_KEY = "YOUR_KEY"
```

### Linux and macOS

```bash
export AUDITPOISON_API_KEY="YOUR_KEY"
```

Run the experiment:

```bash
python scripts/run_model.py --adapter openai-compatible --model YOUR_MODEL --base-url YOUR_BASE_URL --output results/hosted_predictions.jsonl
python scripts/evaluate_predictions.py results/hosted_predictions.jsonl --output results/hosted_metrics.json
python scripts/verify_run.py results/hosted_predictions.manifest.json
```

Never commit API keys. AuditPoison records experiment configuration but does not write the key into result files or manifests.

## Build a multi-model results table

```bash
python scripts/build_paper_table.py results/model_a_metrics.json results/model_b_metrics.json results/model_c_metrics.json
```

Generated files:

```text
results/table_main.md
results/table_main.tex
```

## Core metrics

AuditPoison reports:

* Three-class accuracy
* Macro F1
* False Assurance Rate
* Paired Attack Success Rate
* Robust accuracy
* Benign label consistency
* Benign both-correct rate
* Citation precision, recall, and F1
* Adversarial evidence detection recall
* Confidence Brier score
* Expected calibration error

## Repository layout

```text
.github/workflows/    Continuous integration
data/pilot/           Clean, attacked, and benign evidence bundles
docs/                 Threat model and evaluation protocols
examples/             Example adapter and prediction files
prompts/              Frozen auditor prompts
results/              Generated metrics and paper tables
schema/               Evidence-bundle JSON Schema
scripts/              Validation, experiment, and reporting commands
src/auditpoison/      Python package
tests/                Integrity, leakage, and reproducibility tests
```

## Version history

The repository preserves the project’s development through annotated Git tags:

* `v0.1.0` — threat model and adversarial pilot
* `v0.2.0` — balanced benchmark and evaluation pipeline
* `v0.3.0` — real-model adapters and reproducibility infrastructure

See `CHANGELOG.md` for details.

## Scientific-use warning

The current 40-bundle dataset is a development pilot. It must not be presented as a final benchmark or as statistically conclusive evidence about any model, provider, or model family.

Research claims should be based on a substantially expanded dataset, repeated model runs, documented model versions, frozen prompts, complete run manifests, and appropriate uncertainty analysis.

## Licence

AuditPoison is released under the MIT License.

## Citation

Citation metadata is available in `CITATION.cff`.
