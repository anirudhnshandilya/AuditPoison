# AuditPoison Blinded Holdout v2 Protocol

## Reason for replacement

Holdout v1 completed its blinded model runs, but its separately generated unlock key was not delivered with the artifact. The encrypted oracle is therefore unrecoverable. No v1 oracle metrics are used in the paper. The inputs, predictions, manifests, logs, and ciphertext remain preserved as an aborted protocol record.

## Holdout v2

Holdout v2 contains 60 newly authored opaque bundles arranged into 30 pairs: 15 clean/attacked and 15 clean/benign. It was generated after v1 was abandoned and uses different organisations, systems, assets, dates, values, wording, evidence compositions, and opaque identifiers.

- 30 compliant bundles and 30 unsafe-compliance bundles.
- 20 lexical-shift bundles, 20 format-shift bundles, and 20 compositional-shift bundles.
- All ten control families.
- Six attack families and six benign perturbation families.

## Key handling

The Fernet unlock key is delivered as a separate file before any v2 model run. Its SHA-256 is committed in `commitment.json`. The setup process stores two offline copies outside the holdout directory. `verify_unlock_key.py` authenticates the ciphertext and plaintext commitment without printing oracle contents, then writes a verification receipt.

## Registered matrix

The primary matrix is reduced to Gemma 3 4B and Llama 3.2 3B under unshielded, EvidenceShield v0.1, and EvidenceShield v0.2 conditions: six configurations and 360 blinded assessments. No model or condition may be added after oracle disclosure.

## Unlock rule

The oracle may be unsealed only after all six registered runs have complete 60-bundle manifests and the pre-unseal commitment is recorded.
