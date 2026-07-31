param(
  [string]$Repo = "$env:USERPROFILE\Documents\GitHub\AuditPoison",
  [string]$Holdout = "$env:USERPROFILE\Documents\Research\AuditPoison-Holdout-v2",
  [string]$Key = "$env:USERPROFILE\Documents\Research\AuditPoison-Holdout-v2-Key\oracle_unlock.key",
  [string]$OutputRoot = "$env:USERPROFILE\Documents\Research\AuditPoison-Anonymous-Artifact"
)

$ErrorActionPreference = "Stop"

foreach ($p in @($Repo, $Holdout, $Key)) {
  if (-not (Test-Path $p)) { throw "Required path not found: $p" }
}

if (Test-Path $OutputRoot) {
  $archive = "$OutputRoot-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
  Rename-Item $OutputRoot $archive
  Write-Host "Previous artifact archived: $archive"
}

$software = Join-Path $OutputRoot "software"
$holdoutOut = Join-Path $OutputRoot "holdout_v2"
New-Item -ItemType Directory -Path $software -Force | Out-Null
New-Item -ItemType Directory -Path $holdoutOut -Force | Out-Null

# Copy software without Git history, author metadata, local outputs, or build caches.
$repoArgs = @(
  $Repo, $software, "/E",
  "/XD", ".git", ".venv", "venv", ".pytest_cache", "__pycache__", "build", "dist", "results",
  "/XF", "CITATION.cff", "README.md", "RELEASE_NOTES_v0.6.0.md",
  "/NFL", "/NDL", "/NJH", "/NJS", "/NP"
)
& robocopy @repoArgs | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed for software with code $LASTEXITCODE" }

# Exclude this builder because its identity-detection literals trigger the artifact scan.
Remove-Item (Join-Path $software "scripts\build_anonymous_artifact.ps1") -Force -ErrorAction SilentlyContinue

Copy-Item (Join-Path $Repo "ANONYMOUS_ARTIFACT_README.md") (Join-Path $OutputRoot "README.md") -Force -ErrorAction SilentlyContinue
if (-not (Test-Path (Join-Path $OutputRoot "README.md"))) {
  $fallback = Join-Path $Repo "scripts\..\ANONYMOUS_ARTIFACT_README.md"
  if (Test-Path $fallback) { Copy-Item $fallback (Join-Path $OutputRoot "README.md") -Force }
}
if (-not (Test-Path (Join-Path $OutputRoot "README.md"))) {
  @"
# AuditPoison Anonymous Reviewer Artifact

This directory contains an anonymized frozen software snapshot and blinded-study materials.
"@ | Set-Content (Join-Path $OutputRoot "README.md") -Encoding UTF8
}

# Copy completed holdout workspace while excluding local-path-bearing receipts and commitment listings.
$holdoutArgs = @(
  $Holdout, $holdoutOut, "/E",
  "/XD", "__pycache__", ".pytest_cache", "preflight",
  "/XF", "PRE_UNSEAL_V2_COMMITMENT.sha256", "KEY_VERIFICATION_RECEIPT.json",
  "/NFL", "/NDL", "/NJH", "/NJS", "/NP"
)
& robocopy @holdoutArgs | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed for holdout with code $LASTEXITCODE" }

Copy-Item $Key (Join-Path $holdoutOut "oracle_unlock.key") -Force

# Preserve digests of excluded commitment records without exposing absolute local paths.
$digests = @()
foreach ($name in @("PRE_UNSEAL_V2_COMMITMENT.sha256", "KEY_VERIFICATION_RECEIPT.json")) {
  $path = Join-Path $Holdout $name
  if (Test-Path $path) {
    $h = (Get-FileHash $path -Algorithm SHA256).Hash.ToLower()
    $digests += "$h  $name"
  }
}
$digests | Set-Content (Join-Path $OutputRoot "ORIGINAL_COMMITMENT_DIGESTS.txt") -Encoding ASCII

# Remove obvious author metadata from pyproject and documentation snapshot.
$pyproject = Join-Path $software "pyproject.toml"
if (Test-Path $pyproject) {
  $p = Get-Content $pyproject -Raw
  $p = [regex]::Replace($p, '(?m)^authors\s*=\s*\[.*\]\s*$', 'authors = [{name = "Anonymous Authors"}]')
  Set-Content $pyproject $p -Encoding UTF8
}

# Scrub identity-bearing strings from copied text metadata.
$userHomePattern = [regex]::Escape($env:USERPROFILE)
$replacements = @(
  @{Pattern=$userHomePattern; Replacement="<USER_HOME>"},
  @{Pattern="(?i)Anirudh Narendra Shandilya"; Replacement="Anonymous Author"},
  @{Pattern="(?i)Anirudh N Shandilya"; Replacement="Anonymous Author"},
  @{Pattern="(?i)anirudhnshandilya"; Replacement="anonymous-repository"},
  @{Pattern="(?i)10\.5281/zenodo\.21704967"; Replacement="<ANONYMIZED_DOI>"},
  @{Pattern="(?i)ACM AsiaCCS 2027"; Replacement="the target venue"}
)

$textExtensions = @(".md",".txt",".json",".jsonl",".yml",".yaml",".toml",".cff",".csv",".tex",".ps1",".py")
Get-ChildItem $OutputRoot -Recurse -File | Where-Object {
  $textExtensions -contains $_.Extension.ToLower()
} | ForEach-Object {
  $raw = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
  if ($null -ne $raw) {
    $updated = $raw
    foreach ($r in $replacements) {
      $updated = [regex]::Replace($updated, $r.Pattern, $r.Replacement)
    }
    if ($updated -ne $raw) {
      Set-Content $_.FullName $updated -Encoding UTF8
    }
  }
}

# Remove public project metadata that is unnecessary for anonymous review.
Remove-Item (Join-Path $software "CITATION.cff") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $software "RELEASE_NOTES_v0.6.0.md") -Force -ErrorAction SilentlyContinue

# Identity-leak scan.
$patterns = @(
  "Anirudh",
  "Shandilya",
  "anirudhnshandilya",
  [regex]::Escape($env:USERNAME),
  [regex]::Escape($env:USERPROFILE),
  "zenodo\.21704967",
  "github\.com/anirudhnshandilya"
)

$hits = @()
Get-ChildItem $OutputRoot -Recurse -File | Where-Object {
  $textExtensions -contains $_.Extension.ToLower()
} | ForEach-Object {
  foreach ($pattern in $patterns) {
    $match = Select-String -Path $_.FullName -Pattern $pattern -CaseSensitive:$false -ErrorAction SilentlyContinue
    if ($match) {
      $hits += "$($_.FullName): pattern=$pattern"
    }
  }
}

if ($hits.Count -gt 0) {
  $hits | Set-Content (Join-Path $OutputRoot "ANONYMIZATION_FAILURES.txt") -Encoding UTF8
  throw "Anonymization scan FAILED. Inspect ANONYMIZATION_FAILURES.txt."
}

@"
Anonymization scan PASSED
Generated: $(Get-Date -Format o)
Git history excluded: yes
Citation metadata excluded: yes
Public repository URL scrubbed: yes
Home path and username scrubbed: yes
Private paper workspace excluded: yes
"@ | Set-Content (Join-Path $OutputRoot "ANONYMIZATION_REPORT.txt") -Encoding UTF8

# Relative-path checksums.
$checksumFile = Join-Path $OutputRoot "ARTIFACT_SHA256SUMS.txt"
$lines = Get-ChildItem $OutputRoot -Recurse -File |
  Where-Object { $_.FullName -ne $checksumFile } |
  Sort-Object FullName |
  ForEach-Object {
    $relative = $_.FullName.Substring($OutputRoot.Length + 1).Replace("\","/")
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    "$hash  $relative"
  }
$lines | Set-Content $checksumFile -Encoding ASCII

$zip = "$OutputRoot.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $OutputRoot "*") -DestinationPath $zip -CompressionLevel Optimal

Write-Host "Anonymous artifact build PASSED"
Write-Host "Directory: $OutputRoot"
Write-Host "ZIP: $zip"
Write-Host "Files checksummed: $($lines.Count)"
Write-Host "Do not upload this ZIP until you inspect ANONYMIZATION_REPORT.txt and search it manually for identity clues."
