# AuditPoison Blinded Holdout Protocol

## Purpose

The 40-bundle pilot was used to design the benchmark, attack taxonomy, prompt contract, and EvidenceShield predicate engine. It is therefore a development set and cannot establish generalisation. The Day-8 holdout is created only after the EvidenceShield v0.2 implementation is frozen.

## Composition

The holdout contains 60 opaque bundles arranged into 30 pairs:

- 15 clean/attacked pairs;
- 15 clean/benign pairs;
- 30 safe-compliance bundles and 30 unsafe-compliance bundles;
- 20 lexical-shift bundles;
- 20 format-shift bundles;
- 20 compositional-shift bundles.

All ten pilot control families appear. Names, assets, values, dates, evidence sources, wording, formatting, and attack realisations differ from the development pilot.

## Shift strata

**Lexical shift** changes terminology and field names while preserving the same control semantics.

**Format shift** changes the representation into multiline records, bullet-like exports, alternate separators, and reordered evidence.

**Compositional shift** adds contextual clauses, combines independently sourced statements, and changes which evidence item carries the decisive fact.

## Blinding

Public input files contain only opaque bundle identifiers, control requirements, scope, and evidence. They do not contain:

- oracle labels;
- pair identifiers;
- clean, attacked, or benign variant metadata;
- attack or perturbation families;
- decisive evidence annotations;
- expected secure behaviour.

The hidden metadata is serialized canonically, encrypted, and committed through SHA-256 before any model run. The unlock key is held separately and is not included in the Day-8 workspace.

## Freeze boundary

The freeze manifest hashes every Python module under `src/auditpoison`, the v0.4 frozen prompt, the evidence schema, and `pyproject.toml`. Runs abort if any frozen file differs. Documentation-only changes after the freeze do not affect the implementation hash.

## Preregistered primary endpoints

1. False Assurance Rate.
2. Three-class macro F1.
3. Compliant rejection rate.
4. Paired robust accuracy.
5. Paired attack success with numerator and eligible denominator.
6. Benign both-correct rate.

Secondary endpoints include citation F1, attack-evidence detection, benign false flags, confidence calibration, and shift-stratified performance.

## Planned comparisons

For every primary model configuration:

1. unshielded auditor;
2. EvidenceShield v0.1 provenance-only gate;
3. EvidenceShield v0.2 deterministic predicate adjudication.

The model, prompt version, temperature, seed, thinking mode, timeout, quantization, provider, hardware, and software environment are recorded in a cryptographic run manifest.

## Unlock rule

The oracle may be unlocked only after all preregistered prediction files and manifests are complete. Any run started after oracle disclosure must be labelled post-hoc and excluded from the primary analysis.

## Annotation caveat

The holdout is a separately authored synthetic set, not an independently collected operational audit corpus. A second human annotator must review the predicate worksheets before the paper makes agreement or annotation-quality claims.
