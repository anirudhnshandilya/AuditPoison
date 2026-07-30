# AuditPoison — Day-2 Balanced Pilot

AuditPoison evaluates whether LLM-based cybersecurity auditors provide false compliance assurance when evidence is adversarial, and whether their decisions remain stable under harmless presentation changes.

## Day-2 contents

- 40 evidence bundles across 20 paired scenarios;
- 10 Day-1 clean/attacked red-team pairs;
- 10 new compliant clean/benign-stability pairs;
- all six attack families and six benign perturbation families;
- schema v0.2.0 and stricter semantic validation;
- a frozen auditor prompt that treats evidence as untrusted data;
- prompt rendering that excludes oracle, attack, and perturbation metadata;
- provider-neutral command and file-import evaluation paths;
- three-class metrics, False Assurance Rate, paired Attack Success Rate, benign consistency, citation metrics, evidence-flagging metrics, and calibration diagnostics.

## Composition

| Oracle label | Bundles |
|---|---:|
| Compliant | 20 |
| Non-compliant | 15 |
| Insufficient evidence | 5 |

This is balanced at the false-assurance boundary: 20 compliant bundles and 20 bundles for which a compliant decision would be unsafe.

## Windows setup

If the ZIP extracts into an extra folder, enter the inner project directory containing `pyproject.toml`.

```cmd
cd AuditPoison-Day2
python -m pip install -e .
python scripts\validate_dataset.py
python -m pytest -q
```

## Offline smoke test

```cmd
python scripts\run_experiment.py --adapter keyword --output baseline_predictions.jsonl
python scripts\evaluate_predictions.py baseline_predictions.jsonl
```

## Provider-neutral model workflow

### Option A: command adapter

Create a wrapper that reads this object from stdin:

```json
{"bundle_id":"...","system_prompt":"...","user_prompt":"..."}
```

and writes a model response:

```json
{"label":"non_compliant","confidence":0.91,"cited_evidence_ids":["E2","E3"],"flagged_evidence_ids":["E4"],"rationale":"..."}
```

Test the contract offline:

```cmd
python scripts\run_experiment.py --adapter command --output demo_predictions.jsonl --model-name demo --command python examples\demo_command_adapter.py
python scripts\evaluate_predictions.py demo_predictions.jsonl
```

Replace the demo script with your API or local-model wrapper for a real run.

### Option B: render and import

```cmd
python scripts\render_requests.py --output model_requests.jsonl
```

Send those requests through any provider. Store one response per line using the format in `examples/raw_outputs.template.jsonl`, then run:

```cmd
python scripts\import_model_outputs.py raw_outputs.jsonl --output predictions.jsonl --model-name YOUR_MODEL
python scripts\evaluate_predictions.py predictions.jsonl
```

## Scientific-use warning

The keyword baseline and demo adapter only verify the software pipeline. The current dataset is a development pilot, not the final benchmark, and its scores must not be presented as final evidence about model security.

## Repository layout

```text
schema/                         evidence-bundle schema v0.2
data/pilot/clean/              20 clean bundles
data/pilot/attacked/           10 adversarial variants
data/pilot/benign/             10 harmless variants
 prompts/                       frozen auditor system prompt
 src/auditpoison/               loader, validator, parser, harness, metrics
 scripts/                       validation, rendering, import, run, evaluation
 docs/                          threat model, annotation, evaluation protocol
 examples/                      adapter and JSONL contracts
 tests/                         integrity and leakage tests
```
