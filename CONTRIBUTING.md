# Contributing to AuditPoison

AuditPoison welcomes reproducible benchmark, defence, validation, documentation, and test improvements.

## Before opening a pull request

1. Create a focused branch.
2. Install the development dependencies.
3. Run the dataset validator and complete test suite.
4. Confirm that no private results, keys, manuscripts, credentials, or local paths are included.
5. Explain how the change affects the threat model, benchmark contract, or deterministic verdict policy.

```bash
python -m pip install -e ".[dev]"
python scripts/validate_dataset.py
python -m pytest -q
git diff --check
```

## Benchmark invariants

A contribution must not:

- expose oracle labels in model-visible inputs;
- leak pair, variant, attack-family, or expected-verdict metadata;
- silently alter frozen prompts or evaluation semantics;
- allow an advisory model response to bypass v0.2 deterministic adjudication;
- treat missing evidence as satisfied;
- commit generated local-model outputs as benchmark ground truth.

## New evidence bundles

New bundles should include:

- an explicit control and assessment period;
- a documented oracle rationale;
- evidence provenance and scope;
- a clean, attacked, or benign relationship where applicable;
- tests for leakage and schema validity.

Do not use real organizational evidence without documented authorization and appropriate de-identification.

## Pull-request description

State:

- what changed;
- why it is needed;
- tests run;
- compatibility or benchmark-contract implications;
- whether any generated data is included.
