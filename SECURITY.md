# Security Policy

## Scope

AuditPoison is a research benchmark and testbed. It is not a production compliance engine, certification service, or substitute for professional audit judgment.

## Reporting a vulnerability

Use GitHub's private vulnerability-reporting feature when the report includes an exploitable software weakness, secret, or sensitive reproduction detail. Use a normal GitHub issue for non-sensitive correctness bugs.

Please include:

- affected version or commit;
- operating system and Python version;
- minimal reproduction steps;
- expected and observed behavior;
- whether the issue could create false compliance assurance.

## Data safety

Never upload:

- real credentials, API keys, tokens, or private keys;
- customer or employee records;
- production logs containing personal or regulated information;
- confidential audit evidence;
- active exploit payloads against systems you do not own or have permission to test.

Use synthetic or properly authorized data only.

## Supported versions

Security fixes are applied to the latest tagged research release.
