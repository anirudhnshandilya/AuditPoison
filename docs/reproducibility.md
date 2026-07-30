# Reproducibility protocol

Every scientific run must retain four files:

1. `predictions.jsonl` — one canonical prediction per bundle;
2. `predictions.manifest.json` — model configuration and cryptographic hashes;
3. `metrics.json` — evaluation output;
4. generated table fragments used by the paper.

Use temperature 0 where supported. Record the provider, exact model identifier, base endpoint class, seed, timeout, retry count, dataset hash, prompt hash, package version, and Git commit. Never edit prediction files manually after a run. If parsing fails, preserve the original failed run and rerun under a new filename.

Verify an archived run with:

```cmd
python scripts\verify_run.py results\MODEL_predictions.manifest.json
```

A passing verification establishes that the dataset, prompt, and prediction bytes match the recorded run. It does not guarantee that a hosted provider serves the same model weights under the same name; record the provider-reported model identifier and run date in the paper.

## EvidenceShield runs

Run manifests record `defense` and `prompt_version` in the configuration and hash the exact selected prompt file. Unshielded and shielded predictions must use distinct output and manifest filenames.
