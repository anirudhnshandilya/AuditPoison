# GitHub publication workflow

Use one repository named `AuditPoison`. Do not upload `AuditPoison-Day1`, `AuditPoison-Day2`, and `AuditPoison-Day3` as three folders.

## Reconstruct the three development commits on Windows

Run the included PowerShell script from the Day-3 project directory. Supply the **inner extracted folders** containing each `pyproject.toml`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_git_history.ps1 `
  -Day1Path "C:\Users\aniru\Downloads\AuditPoison-Day1\AuditPoison-Day1" `
  -Day2Path "C:\Users\aniru\Downloads\AuditPoison-Day2\AuditPoison-Day2" `
  -Day3Path "C:\Users\aniru\Downloads\AuditPoison-Day3\AuditPoison-Day3" `
  -Destination "C:\Users\aniru\Documents\GitHub\AuditPoison"
```

The script creates:

- Day 1 commit and tag `v0.1.0`;
- Day 2 commit and tag `v0.2.0`;
- Day 3 commit and tag `v0.3.0`.

## Push to GitHub

Create an empty public repository named `AuditPoison` without a generated README, licence, or `.gitignore`. Then run inside the generated repository:

```cmd
git remote add origin https://github.com/anirudhnshandilya/AuditPoison.git
git push -u origin main
git push origin --tags
```

Before public release, keep experimental model outputs out of Git if provider terms or paper anonymity require it. Commit aggregate metrics and scripts; archive raw results privately until the double-blind submission policy permits release.
