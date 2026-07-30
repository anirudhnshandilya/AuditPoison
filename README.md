# AuditPoison

**Adversarial evidence attacks against LLM-based cybersecurity auditors.**

AuditPoison evaluates whether an AI auditor can be manipulated into providing false compliance assurance when policies, logs, tickets, exports, and other audit evidence contain malicious, stale, irrelevant, contradictory, or out-of-scope content.

## Day-3 release

Version `0.3.0` provides an end-to-end, reproducible pilot:

- 40 validated evidence bundles across 20 paired scenarios;
- 10 adversarial clean/attacked pairs spanning six attack families;
- 10 compliant clean/benign pairs spanning six harmless perturbation families;
- three oracle labels: compliant, non-compliant, and insufficient evidence;
- native Ollama and OpenAI-compatible model adapters;
- provider-neutral command and offline import paths;
- cryptographic run manifests and verification;
- paper-ready Markdown and LaTeX result tables;
- GitHub Actions validation across Python 3.10–3.13.

## Dataset composition

| Oracle label | Bundles |
|---|---:|
| Compliant | 20 |
| Non-compliant | 15 |
| Insufficient evidence | 5 |

The pilot is balanced at the false-assurance boundary: 20 bundles support compliance and 20 bundles make a compliant verdict unsafe.

## Windows setup

After extraction, enter the **inner folder containing `pyproject.toml`**:

```cmd
cd AuditPoison-Day3\AuditPoison-Day3
python -m pip install -e ".[dev]"
python scripts\validate_dataset.py
python -m pytest -q
```

## Offline smoke test

```cmd
python scripts\run_model.py --adapter keyword --output results\keyword_predictions.jsonl
python scripts\evaluate_predictions.py results\keyword_predictions.jsonl --output results\keyword_metrics.json
python scripts\verify_run.py results\keyword_predictions.manifest.json
python scripts\build_paper_table.py results\keyword_metrics.json
```

## Run a local LLM with Ollama

Install Ollama, make sure its service is running, and pull a model appropriate for your hardware. Then run:

```cmd
python scripts\run_model.py --adapter ollama --model YOUR_MODEL --output results\YOUR_MODEL_predictions.jsonl
python scripts\evaluate_predictions.py results\YOUR_MODEL_predictions.jsonl --output results\YOUR_MODEL_metrics.json
```

Start with a two-bundle contract check before the full run:

```cmd
python scripts\run_model.py --adapter ollama --model YOUR_MODEL --limit 2 --output results\ollama_test.jsonl
```

## Run a hosted OpenAI-compatible endpoint

Set the key only in the current terminal session:

```cmd
set AUDITPOISON_API_KEY=YOUR_KEY
python scripts\run_model.py --adapter openai-compatible --model YOUR_MODEL --base-url https://api.openai.com/v1 --output results\hosted_predictions.jsonl
python scripts\evaluate_predictions.py results\hosted_predictions.jsonl --output results\hosted_metrics.json
```

Do not commit API keys. The runner records endpoint configuration but never the key.

## Build a multi-model paper table

```cmd
python scripts\build_paper_table.py results\model_a_metrics.json results\model_b_metrics.json results\model_c_metrics.json
```

Outputs:

- `results/table_main.md`
- `results/table_main.tex`

## Publish Day 1–3 to GitHub

Use one repository with three commits and three annotated tags. See [`docs/github_setup.md`](docs/github_setup.md), or run the supplied PowerShell history-bootstrap script.

## Core metrics

- clean three-class accuracy and macro F1;
- False Assurance Rate;
- paired Attack Success Rate and robust accuracy;
- benign label consistency and both-correct rate;
- citation precision, recall, and F1;
- adversarial evidence detection recall;
- confidence Brier score and expected calibration error.

## Scientific-use warning

The keyword baseline is only a software smoke test. The 40-bundle dataset is a development pilot and must not be presented as the final benchmark or as statistically conclusive evidence about any model family.

## Repository layout

```text
.github/workflows/              continuous integration
schema/                         evidence-bundle schema
data/pilot/                     clean, attacked, and benign bundles
prompts/                        frozen auditor prompt
src/auditpoison/              loaders, adapters, metrics, manifests, reporting
scripts/                        validation, model runs, evaluation, Git history
results/                        generated metrics and paper tables
docs/                           threat model and protocols
tests/                          integrity, leakage, and reproducibility tests
```

## Licence and citation

AuditPoison is released under the MIT License. Citation metadata is provided in `CITATION.cff`.
