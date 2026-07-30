# EvidenceShield v0.2

EvidenceShield v0.2 removes final compliance authority from the language model.

## Decision architecture

1. **Evidence screening** classifies each item as trusted, sanitized, caution, or quarantined.
2. **Instruction sanitization** preserves verified factual fields while removing instruction-bearing comments.
3. **Control-specific predicate evaluation** maps admissible evidence to `satisfied`, `failed`, or `unresolved` outcomes.
4. **Deterministic adjudication** assigns the final label:

```text
Any failed predicate        -> non_compliant
No failures, any unresolved -> insufficient_evidence
All predicates satisfied    -> compliant
```

The model still produces an advisory assessment for experimentation and explanation analysis, but its label cannot change the deterministic verdict.

## Security invariants

- Oracle labels, attack metadata, perturbation metadata, and bundle-name suffixes are never read by the predicate engine.
- Quarantined evidence cannot satisfy a predicate.
- Self-attestation cannot independently establish control effectiveness.
- Verified technical evidence containing an injected comment is sanitized rather than discarded wholesale.
- Every final verdict records predicate outcomes and decisive evidence identifiers.
- A compliant verdict is impossible when any required predicate is failed or unresolved.

## Pilot coverage

Version 0.2 includes explicit evaluators for the ten pilot controls:

`AC-2`, `AC-6`, `AU-2`, `AU-6`, `CM-2`, `CM-6`, `CP-9`, `IA-2`, `RA-5`, and `SI-2`.

These evaluators are intentionally narrow and operate on the structured synthetic evidence language used by the pilot. Perfect performance on the frozen pilot is a software contract check, not evidence of generalisation to real audit documents.

## Important limitation

EvidenceShield v0.2 is a hybrid research prototype, not a production compliance engine. The deterministic parsers are control-specific and must be evaluated on independently authored held-out bundles, paraphrases, noisy exports, and real evidence before any general security claim is made.
