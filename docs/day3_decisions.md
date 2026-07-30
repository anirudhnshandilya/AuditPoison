# Day-3 decisions

1. **One evolving repository.** Day 1, Day 2, and Day 3 are represented by commits and annotated tags (`v0.1.0`, `v0.2.0`, `v0.3.0`), not duplicated top-level folders.
2. **Two real-model paths.** Ollama provides a local, low-cost path; the OpenAI-compatible adapter covers hosted chat-completions endpoints without vendor SDK lock-in.
3. **No secret persistence.** API keys are read from an environment variable and are never stored in predictions or manifests.
4. **Frozen evaluation inputs.** Each run records cryptographic hashes for the dataset, prompt, and predictions.
5. **Exact run context.** Manifests record model, provider, generation settings, bundle IDs, Python/platform metadata, and the current Git commit when available.
6. **Paper output from raw metrics.** Tables are generated from metrics JSON rather than manually copied values.
7. **Pilot limitation remains explicit.** The 40-bundle set is suitable for pipeline development and preliminary experiments, not final statistical claims.
