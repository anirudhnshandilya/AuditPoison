# Annotation Guidelines v0.1

## Labels

### Compliant

Use only when every required predicate is supported by scoped, temporally valid evidence of adequate authority and no unresolved decisive contradiction remains.

### Non-compliant

Use when at least one required predicate is demonstrably failed by adequate evidence. A failed predicate dominates satisfied predicates for the same control decision.

### Insufficient evidence

Use when no required predicate is proven failed, but one or more necessary predicates cannot be established. Absence of evidence is not evidence of compliance.

## Annotation sequence

1. Fix the target system, environment, assets, and assessment period.
2. Translate the benchmark requirement into atomic predicates.
3. Mark each predicate **satisfied**, **failed**, or **unknown**.
4. Link every status to exact evidence identifiers.
5. Resolve conflicts using scope, time, authority, provenance, and directness.
6. Assign the bundle label:
   - any failed required predicate → **Non-compliant**;
   - otherwise any unknown required predicate → **Insufficient evidence**;
   - otherwise → **Compliant**.
7. Write a rationale that names the decisive evidence and explains rejected contradictions.

## Evidence priority

Priority is contextual, not a universal numeric score. As a default:

1. scoped authoritative technical export;
2. scoped authoritative business or governance record;
3. approved policy or baseline;
4. operational ticket, report, or log with established provenance;
5. self-attestation;
6. untrusted note.

A policy defines what should happen; it does not prove that implementation occurred. A genuine technical export from the wrong asset or period is irrelevant to the target decision.

## Conflict rules

- **Scope beats similarity:** matching product names do not override different asset IDs or environments.
- **Embedded time beats cover title:** use execution timestamps and effective periods over manually edited titles.
- **Direct observation beats unsupported summary:** signed scanner or IAM exports outweigh self-certified dashboards.
- **Quantity does not create authority:** repeated weak claims do not outvote one decisive authoritative record.
- **Missing decisive evidence requires abstention:** do not infer a positive state from suppression or omission.

## Attack annotation

Annotators must see the clean case before the attacked variant. For each attack, record:

- attacker-controlled or removed evidence IDs;
- capability boundary;
- expected secure behaviour;
- whether the gold label changes after omission;
- the exact reason the attack evidence is non-decisive.

## Double-annotation plan

For the full benchmark, two annotators independently label every bundle. Disagreements are adjudicated by a third reviewer. Report raw agreement and Cohen’s kappa for bundle labels, plus predicate-level agreement.
