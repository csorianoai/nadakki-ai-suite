# ============================================================
# NADAKKI - New PC Setup
# Run this on any new computer to get started
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUser
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NADAKKI - New PC Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Prerequisites check
Write-Host ""
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Yellow

# Git
try { git --version | Out-Null; Write-Host "  [OK] Git installed" -ForegroundColor Green }
catch { Write-Host "  [X] Git missing - install from https://git-scm.com" -ForegroundColor Red; exit 1 }

# Python
try { python --version | Out-Null; Write-Host "  [OK] Python installed" -ForegroundColor Green }
catch { Write-Host "  [X] Python missing - install from https://python.org" -ForegroundColor Red; exit 1 }

# Clone
Write-Host ""
Write-Host "[2/4] Cloning repository..." -ForegroundColor Yellow
$cloneDir = "C:\Users\$env:USERNAME\Projects\nadakki-google-ads-mvp"

if (Test-Path $cloneDir) {
    Write-Host "  Directory exists. Pulling latest..." -ForegroundColor Yellow
    Set-Location $cloneDir
    git pull origin main
} else {
    New-Item -ItemType Directory -Path (Split-Path $cloneDir) -Force | Out-Null
    git clone "https://github.com/$GitHubUser/nadakki-google-ads-mvp.git" $cloneDir
    Set-Location $cloneDir
}
Write-Host "  [OK] Repository ready at $cloneDir" -ForegroundColor Green

# Install deps
Write-Host ""
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "  [OK] Dependencies installed" -ForegroundColor Green

# Test
Write-Host ""
Write-Host "[4/4] Running tests..." -ForegroundColor Yellow
$env:DATABASE_URL = ""
python main.py 2>&1 | Select-Object -Last 15

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Start API:  uvicorn main:app --reload --port 8000" -ForegroundColor White
Write-Host "  Run tests:  .\DAILY.ps1 -Test" -ForegroundColor White
Write-Host "  Push code:  .\DAILY.ps1 -Push -Message 'description'" -ForegroundColor White
Write-Host ""
