# EvidenceShield v0.1

EvidenceShield is AuditPoison's first defence architecture. It treats evidence as an adversarial input surface rather than trusted prompt context.

## Pipeline

1. **Scope check** — identifies records that do not overlap the assessed asset set.
2. **Temporal check** — isolates records whose effective period does not overlap the assessment period.
3. **Instruction firewall** — quarantines evidence containing instruction-like language.
4. **Authority check** — rejects unsupported claims of external-auditor or regulator approval.
5. **Provenance labelling** — marks unverified and self-attested records as caution evidence.
6. **Positive-assurance gate** — a compliant verdict must cite verified, in-scope technical or operational evidence.

Quarantined content is withheld from the auditor and replaced with a reason code. Caution evidence remains visible but cannot independently justify compliance.

## Non-oracle design

The implementation does not inspect the bundle's oracle, attack metadata, perturbation metadata, expected answer, or bundle-name suffix. Screening uses only the model-visible control scope, evidence metadata, provenance, and content. Tests enforce this property.

## Intended claim

Version 0.1 is a reproducible reference defence and ablation component, not a claim that prompt injection or compliance automation is solved. Its conservative positive gate may trade clean utility for lower false-assurance risk.

## Run

```bash
python scripts/run_model.py --adapter keyword --defense evidenceshield --output results/keyword_shield_predictions.jsonl
python scripts/evaluate_predictions.py results/keyword_shield_predictions.jsonl --output results/keyword_shield_metrics.json
python scripts/compare_defenses.py results/keyword_smoke_metrics.json results/keyword_shield_metrics.json
```
