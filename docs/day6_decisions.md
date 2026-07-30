# Day 6 decisions

- Preserve EvidenceShield v0.1 as an explicit ablation option.
- Make `evidenceshield` an alias for EvidenceShield v0.2.
- Add an explicit `evidenceshield-v0.1` option for reproducing the failed provenance-only defence.
- Treat the model label as advisory under v0.2.
- Derive the final verdict only from deterministic predicate states.
- Retain all predicate outcomes in prediction rows for auditability.
- Fix environment detection so phrases such as “restoration test” do not imply a test environment.
- Sanitize injected comments inside verified technical exports instead of discarding the entire export.
- Freeze the v0.2 analyst prompt as `auditor_system_v0.4.txt`.
- Bump the software version to `0.5.0`.
- Do not interpret 100% pilot contract accuracy as scientific evidence; held-out expansion is required.
