# ReRAM-SMU V1 — fetch datasheet scaffold (manufacturer-first)
# Usage: .\tools\scripts\fetch_datasheet.ps1 -Manufacturer "Analog Devices" -Part "AD5686R" -Url "https://www.analog.com/..."
param(
  [Parameter(Mandatory=$true)][string]$Manufacturer,
  [Parameter(Mandatory=$true)][string]$Part,
  [Parameter(Mandatory=$true)][string]$Url
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = "E:\ReRAM-SMU V1"
$refDir = Join-Path $root "docs/references"
New-Item -ItemType Directory -Force -Path $refDir | Out-Null

$safeMan = ($Manufacturer -replace '[^A-Za-z0-9]+','_').Trim('_')
$safePart = ($Part -replace '[^A-Za-z0-9]+','_').Trim('_')
$out = Join-Path $refDir "${safeMan}_${safePart}_download.pdf"

Write-Host "Manufacturer: $Manufacturer"
Write-Host "Part: $Part"
Write-Host "Source (primary manufacturer expected): $Url"
Write-Host "Destination: $out"
Write-Host "Hierarchy reminder: manufacturer datasheet > app note > ref design > standard > authorized distributor > secondary only if unavoidable."
Write-Host "Provenance to record: Manufacturer | Part | Document title | Rev/Date | Page/Section | URL or $out"

# Attempt download (kept simple; no auth). If it fails, report fallback.
try {
  Invoke-WebRequest -Uri $Url -OutFile $out -UseBasicParsing -TimeoutSec 30
  Write-Host "Downloaded." -ForegroundColor Green
  Write-Host "Next: open $out, note doc title/rev/date, page/section, and commit with citation."
} catch {
  Write-Host "Download failed: $($_.Exception.Message)" -ForegroundColor Yellow
  Write-Host "Fallback: download manually and place at $out, then record provenance."
  exit 1
}
