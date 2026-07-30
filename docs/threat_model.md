# AuditPoison Threat Model v0.1

## Security objective

An AI-assisted auditor must not issue **Compliant** assurance unless the scoped, temporally valid, sufficiently authoritative evidence satisfies every required control predicate.

For a clean evidence set \(E\) and attacker-added evidence \(A\), define \(A\) as non-authoritative when it cannot establish a missing predicate through valid provenance. The desired non-escalation property is:

\[
\operatorname{Gold}(E) \neq \text{Compliant}
\land A \text{ adds no valid authoritative support}
\Rightarrow
f(E \cup A) \neq \text{Compliant}.
\]

Evidence omission is handled separately: removing decisive evidence may change **Non-compliant** to **Insufficient evidence**, but must never justify **Compliant**.

## Protected asset

The protected asset is the integrity of the control-assurance decision and its evidence-grounded rationale. A false compliant decision is more severe than an ordinary classification error because it can suppress remediation, distort risk reporting, or enter an audit record.

## Attacker goals

Primary goal: cause a clean **Non-compliant** or **Insufficient evidence** case to be reported as **Compliant**.

Secondary goals:

- cause the auditor to cite irrelevant or attacker-controlled evidence;
- suppress recognition of contradictions;
- inflate confidence;
- replace the assessed asset, environment, or time period with a favourable one.

## Attacker capabilities

The pilot permits an attacker to control a bounded subset of evidence inputs. Depending on the attack family, the attacker may:

- upload an untrusted note, report, ticket, or attestation;
- place natural-language text inside a legitimate evidence field;
- add many low-authority claims;
- relabel old evidence;
- provide genuine evidence from another asset or environment;
- suppress one evidence item from the bundle.

The attacker cannot:

- modify the model weights or evaluator code;
- alter the system prompt directly;
- forge a trusted cryptographic signature;
- modify independent authoritative sources unless a scenario explicitly says so;
- change the benchmark oracle.

## Defender knowledge

The auditor receives the control requirement, assessment scope, evidence content, evidence type, timestamps, asset identifiers, producer, collection method, and integrity status. A defence may use all of these fields.

## Attack families

1. **Instruction injection** — commands embedded in evidence attempt to control the auditor.
2. **Authority spoofing** — unverified text claims approval by an auditor, executive, or control owner.
3. **Contradiction flooding** — repeated weak claims attempt to outweigh one strong contradictory source.
4. **Temporal rollback** — stale favourable evidence is relabelled or presented as current.
5. **Scope substitution** — evidence from another asset, tenant, environment, or period is used for the target.
6. **Evidence omission** — decisive evidence is removed to encourage unsupported positive inference.

## Out of scope for v0.1

- model extraction, training-data poisoning, and model-weight attacks;
- availability attacks and denial of service;
- multimodal attacks in screenshots or images;
- cryptographic provenance implementation;
- attacks requiring control of every authoritative source.
