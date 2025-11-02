# ACC Livery Manifest Builder - PowerShell Script
# Usage: .\rebuild_manifest.ps1 -LiveriesFolder "C:\path\to\liveries" [-League "League Name"] [-Version "1.0.0"]

param(
    [Parameter(Mandatory=$true, HelpMessage="Path to folder containing .zip livery files")]
    [string]$LiveriesFolder,

    [Parameter(Mandatory=$false, HelpMessage="League name for manifest")]
    [string]$League = "GT3 Championship",

    [Parameter(Mandatory=$false, HelpMessage="Manifest version")]
    [string]$Version = "1.0.0"
)

$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "ACC Livery Manifest Builder" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Liveries Folder: $LiveriesFolder" -ForegroundColor Yellow
Write-Host "League Name:     $League" -ForegroundColor Yellow
Write-Host "Version:         $Version" -ForegroundColor Yellow
Write-Host ""

# Verify liveries folder exists
if (-not (Test-Path -Path $LiveriesFolder)) {
    Write-Host "Error: Liveries folder not found" -ForegroundColor Red
    exit 1
}

# Run the Python script
& python "$ScriptDir\build_manifest.py" "$LiveriesFolder" -l "$League" -v "$Version" -o "$ScriptDir"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "Manifest built successfully!" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "Error building manifest" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
    exit 1
}

Write-Host ""
