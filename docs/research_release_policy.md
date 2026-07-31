# Research Release Policy

AuditPoison separates three classes of material.

## Public software release

May contain:

- benchmark code and schema;
- development pilot bundles;
- frozen prompts;
- tests;
- deterministic defence implementation;
- curated smoke-test outputs;
- public documentation.

## Anonymous reviewer artifact

May contain:

- frozen code snapshot;
- blinded holdout inputs;
- completed prediction files and manifests;
- evaluation scripts and aggregate metrics;
- failure-analysis tables;
- oracle material needed to verify the completed experiment;
- relative-path checksums.

It must not contain author names, affiliations, usernames, emails, DOI metadata, identifiable repository URLs, local home paths, or Git history.

## Private research archive

Contains:

- aborted protocol records;
- original pre-unseal commitments;
- local environment details;
- paper workspace and author metadata;
- key backups;
- any files whose publication could reveal identity or sensitive paths.

Private archives must not be committed to the public repository.
