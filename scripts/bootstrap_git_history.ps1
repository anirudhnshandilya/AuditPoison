param(
    [Parameter(Mandatory=$true)][string]$Day1Path,
    [Parameter(Mandatory=$true)][string]$Day2Path,
    [Parameter(Mandatory=$true)][string]$Day3Path,
    [string]$Destination = (Join-Path (Get-Location) "AuditPoison")
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not on PATH."
}
if (-not (git config --global user.name) -or -not (git config --global user.email)) {
    throw 'Configure Git first: git config --global user.name "Your Name" and git config --global user.email "you@example.com"'
}
if (Test-Path $Destination) {
    throw "Destination already exists: $Destination"
}

New-Item -ItemType Directory -Path $Destination | Out-Null

function Copy-Snapshot([string]$Source, [string]$Target) {
    if (-not (Test-Path (Join-Path $Source "pyproject.toml"))) {
        throw "No pyproject.toml found in $Source. Enter the inner extracted project folder."
    }
    $code = robocopy $Source $Target /MIR /XD .git .pytest_cache __pycache__ /XF *.pyc *.pyo
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed with exit code $LASTEXITCODE"
    }
}

Copy-Snapshot $Day1Path $Destination
Push-Location $Destination
git init
git branch -M main
git add .
git commit -m "feat: establish AuditPoison threat model and adversarial pilot"
git tag -a v0.1.0 -m "Day 1 adversarial pilot"
Pop-Location

Copy-Snapshot $Day2Path $Destination
Push-Location $Destination
git add -A
git commit -m "feat: add balanced controls, benign perturbations, and evaluation metrics"
git tag -a v0.2.0 -m "Day 2 balanced pilot"
Pop-Location

Copy-Snapshot $Day3Path $Destination
Push-Location $Destination
git add -A
git commit -m "feat: add real-model adapters and reproducible experiment reporting"
git tag -a v0.3.0 -m "Day 3 reproducible model evaluation"
Write-Host "Created Git repository at $Destination"
Write-Host "Next: create an empty GitHub repository, then add its remote and push main plus tags."
Pop-Location
