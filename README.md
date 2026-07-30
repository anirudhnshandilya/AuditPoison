# AuditPoison — Day-1 Pilot

AuditPoison is a benchmark for adversarial manipulation of LLM-based cybersecurity compliance auditors. The pilot asks whether attacker-controlled evidence can turn a demonstrably failed or unsupported control into false **Compliant** assurance.

## Day-1 contents

- 12 narrowed control requirements inspired by NIST SP 800-53 Rev. 5.1.1;
- 10 clean evidence bundles;
- 10 attacked variants covering six attack families;
- a JSON Schema and semantic dataset validator;
- annotation and threat-model documents;
- a model-adapter interface;
- prediction-file evaluation with accuracy, False Assurance Rate, paired Attack Success Rate, citation precision, and contradiction recall;
- a deliberately weak heuristic baseline for testing the pipeline.

NIST publishes SP 800-53 and official machine-readable OSCAL content. The benchmark requirements here are original operationalisations and not verbatim reproductions. OWASP’s prompt-injection guidance motivates treating external content as untrusted data rather than instructions.

## Repository layout

```text
schema/                         JSON Schema
data/controls.json              selected controls
data/manifest.json              clean/attack pairs
data/pilot/clean/               clean bundles
data/pilot/attacked/            attacked bundles
docs/                           threat model and annotation rules
prompts/                        frozen v0.1 auditor prompt
src/auditpoison/                validator, harness, metrics, baseline
scripts/                        runnable entry points
tests/                          integrity tests
examples/                       prediction format example
```

## Run

```bash
python scripts/validate_dataset.py
python scripts/run_baseline.py --output baseline_predictions.jsonl
python scripts/evaluate_predictions.py baseline_predictions.jsonl
pytest -q
```

No model API is required. Python 3.10+ is sufficient after installing the project dependencies:

```bash
python -m pip install -e .
```

## Prediction format

One JSON object per line:

```json
{"bundle_id":"AP-AC2-001-attacked","label":"non_compliant","confidence":0.91,"cited_evidence_ids":["E2","E3"],"contradictions_detected":["E4"]}
```

## Pilot warning

The current pilot is red-team heavy and contains no compliant oracle cases. It must not be used to claim final model accuracy. Its purpose is to validate the schema, attacks, metrics, and annotation logic before balanced expansion.

## Source references

- NIST SP 800-53 Rev. 5.1.1: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- NIST OSCAL content: https://github.com/usnistgov/oscal-content
- OWASP LLM Prompt Injection Prevention: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
