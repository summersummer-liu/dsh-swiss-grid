# Install the bundled skill without the DSH plugin system.
# Usage: powershell -ExecutionPolicy Bypass -File scripts/install-skill.ps1 [-Destination <dir>]
param(
    [string]$Destination = (Join-Path $HOME ".dsh\skills")
)

$ErrorActionPreference = "Stop"
$source = Join-Path $PSScriptRoot "..\skills\swiss-grid-design"
$source = (Resolve-Path $source).Path
if (-not (Test-Path $source)) { throw "skill folder not found: $source" }

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$target = Join-Path $Destination "swiss-grid-design"
if (Test-Path $target) { Remove-Item -Recurse -Force $target }
Copy-Item -Recurse -Path $source -Destination $target

Write-Host "installed skill -> $target"
Write-Host "open a new DSH session and invoke: /swiss-grid-design"
