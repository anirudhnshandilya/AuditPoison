# Day-1 Design Decisions

## Locked decisions

- Working title: **AuditPoison: Adversarial Evidence Attacks Against LLM-Based Cybersecurity Auditors**.
- Primary failure: false **Compliant** assurance.
- Output labels: `compliant`, `non_compliant`, `insufficient_evidence`.
- Framework seed: NIST SP 800-53 Rev. 5.1.1, using original narrowed benchmark requirements rather than copied control text.
- Pilot: ten clean/attacked pairs across ten controls.
- Reserved expansion controls: IR-4 and CA-7.
- Unit of evaluation: one scoped evidence bundle for one control decision.
- Evidence remains natural language plus explicit provenance metadata.
- Final decisions are predicate based; document count is never a voting rule.

## Pilot limitations

This first slice intentionally contains only attack-target cases: non-compliant and insufficient-evidence bundles. It is suitable for validating attack logic and False Assurance Rate, not for reporting final clean accuracy. The next expansion must add matched compliant controls and benign perturbations to avoid a negative-label shortcut.

## Next acceptance gate

Before model experiments, add at least:

- ten compliant clean bundles;
- benign paraphrase and formatting variants;
- duplicate-evidence controls;
- cross-annotator review;
- a frozen prompt and model-output schema.
