# Reproducibility

## Public development benchmark

The public repository contains a 40-bundle development benchmark arranged into 20 paired scenarios. It is used for implementation validation, ablation development, and regression testing.

Development performance must not be described as independent generalization.

## Frozen software contract

A reproducible run should record:

- repository commit;
- model identifier and local runtime version;
- defence condition;
- prompt and dataset hashes;
- decoding parameters;
- prediction count and bundle identifiers;
- response and manifest hashes;
- validation status.

## Defence conditions

- `none`: the language model controls the verdict.
- `evidenceshield-v0.1`: provenance-aware filtering with model-controlled verdict.
- `evidenceshield-v0.2`: explicit predicate evaluation followed by deterministic verdict assignment.

## Deterministic verdict policy

```text
Any failed predicate        -> non_compliant
No failures, any unresolved -> insufficient_evidence
All predicates satisfied    -> compliant
```

## Local outputs

Generated model predictions, manifests, metrics, logs, holdout data, oracle files, keys, paper sources, and pre-unseal records are local research artifacts. They are excluded from the identifiable public repository unless a curated release explicitly states otherwise.

## Reviewer artifact

The reviewer artifact is built from a frozen repository commit and a completed blinded-study workspace. It is separately anonymized, scanned for identity leaks, checksummed using relative paths, and uploaded through an anonymous artifact service.

The identifiable public repository must not be linked from a double-blind manuscript.
