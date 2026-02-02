# ============================================================
# NADAKKI - One-Click GitHub Setup
# Run this in PowerShell as:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\SETUP_AND_PUSH.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$PROJECT_DIR = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki-google-ads-mvp"
$DOWNLOADS = "C:\Users\cesar\Downloads"
$ZIP_NAME = "nadakki-google-ads-mvp-day7-FINAL.zip"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NADAKKI - GitHub Setup Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: Apply the latest zip
# ============================================================
Write-Host "[1/6] Applying latest build from zip..." -ForegroundColor Yellow

$zipPath = Join-Path $DOWNLOADS $ZIP_NAME
if (-not (Test-Path $zipPath)) {
    Write-Host "  ERROR: $zipPath not found!" -ForegroundColor Red
    Write-Host "  Please download the zip first from Claude chat" -ForegroundColor Red
    exit 1
}

$tempDir = Join-Path $DOWNLOADS "temp-nadakki-setup"
if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }

Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
Copy-Item -Path (Join-Path $tempDir "nadakki-google-ads-mvp\*") -Destination $PROJECT_DIR -Recurse -Force
Remove-Item $tempDir -Recurse -Force

Write-Host "  [OK] Files updated from zip" -ForegroundColor Green

# ============================================================
# STEP 2: Verify the fix
# ============================================================
Write-Host "[2/6] Verifying Windows compatibility..." -ForegroundColor Yellow

$mainPy = Join-Path $PROJECT_DIR "main.py"
$testPy = Join-Path $PROJECT_DIR "tests\test_all.py"

# Check main.py has encoding fix
$mainContent = Get-Content $mainPy -Raw
if ($mainContent -match 'encoding="utf-8"') {
    Write-Host "  [OK] main.py has UTF-8 encoding fix" -ForegroundColor Green
} else {
    Write-Host "  WARNING: main.py missing encoding fix" -ForegroundColor Red
}

# Check test_all.py for non-ASCII
$testBytes = [System.IO.File]::ReadAllBytes($testPy)
$nonAscii = ($testBytes | Where-Object { $_ -gt 127 }).Count
if ($nonAscii -eq 0) {
    Write-Host "  [OK] test_all.py is pure ASCII ($nonAscii non-ASCII bytes)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: test_all.py has $nonAscii non-ASCII bytes" -ForegroundColor Red
}

# Check main.py for non-ASCII
$mainBytes = [System.IO.File]::ReadAllBytes($mainPy)
$nonAsciiMain = ($mainBytes | Where-Object { $_ -gt 127 }).Count
if ($nonAsciiMain -eq 0) {
    Write-Host "  [OK] main.py is pure ASCII ($nonAsciiMain non-ASCII bytes)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: main.py has $nonAsciiMain non-ASCII bytes" -ForegroundColor Red
}

# ============================================================
# STEP 3: Run tests
# ============================================================
Write-Host "[3/6] Running 64 tests..." -ForegroundColor Yellow

Set-Location $PROJECT_DIR
$env:DATABASE_URL = ""

try {
    $output = python main.py 2>&1 | Out-String
    if ($output -match "ALL DAYS 1-7 TESTS PASSED") {
        Write-Host "  [OK] All 64 tests PASSED" -ForegroundColor Green
    } else {
        Write-Host "  Tests output (last 10 lines):" -ForegroundColor Red
        $output -split "`n" | Select-Object -Last 10 | ForEach-Object { Write-Host "    $_" }
        Write-Host ""
        Write-Host "  Fix any issues before pushing to GitHub" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ERROR running tests: $_" -ForegroundColor Red
    exit 1
}

# ============================================================
# STEP 4: Initialize Git
# ============================================================
Write-Host "[4/6] Initializing Git repository..." -ForegroundColor Yellow

Set-Location $PROJECT_DIR

# Check if git is installed
try {
    git --version | Out-Null
} catch {
    Write-Host "  ERROR: Git not installed. Install from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Init if needed
if (-not (Test-Path ".git")) {
    git init
    Write-Host "  [OK] Git initialized" -ForegroundColor Green
} else {
    Write-Host "  [OK] Git already initialized" -ForegroundColor Green
}

# ============================================================
# STEP 5: Stage and commit
# ============================================================
Write-Host "[5/6] Staging and committing files..." -ForegroundColor Yellow

git add .
$status = git status --porcelain
if ($status) {
    git commit -m "NADAKKI Google Ads MVP - Day 7 Final Build

- 19 components, 64 tests, 43 API endpoints
- 5 workflows, 4 agents + orchestrator
- Multi-tenant architecture for financial institutions
- Windows cp1252 compatible (pure ASCII)"
    Write-Host "  [OK] Changes committed" -ForegroundColor Green
} else {
    Write-Host "  [OK] No changes to commit (already up to date)" -ForegroundColor Green
}

# ============================================================
# STEP 6: Push to GitHub
# ============================================================
Write-Host "[6/6] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "  BEFORE CONTINUING:" -ForegroundColor Cyan
Write-Host "  1. Go to https://github.com/new" -ForegroundColor White
Write-Host "  2. Repo name: nadakki-google-ads-mvp" -ForegroundColor White
Write-Host "  3. Set to PRIVATE" -ForegroundColor White
Write-Host "  4. DO NOT add README or .gitignore" -ForegroundColor White
Write-Host "  5. Click 'Create repository'" -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""

$ghUser = Read-Host "Enter your GitHub username"
if (-not $ghUser) {
    Write-Host "  No username provided. Skipping push." -ForegroundColor Yellow
    Write-Host "  You can push later with:" -ForegroundColor Yellow
    Write-Host "    git remote add origin https://github.com/YOUR_USER/nadakki-google-ads-mvp.git" -ForegroundColor White
    Write-Host "    git branch -M main" -ForegroundColor White
    Write-Host "    git push -u origin main" -ForegroundColor White
    exit 0
}

# Remove existing remote if present
git remote remove origin 2>$null

git remote add origin "https://github.com/$ghUser/nadakki-google-ads-mvp.git"
git branch -M main

Write-Host "  Pushing to https://github.com/$ghUser/nadakki-google-ads-mvp ..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DONE! Repository pushed to GitHub" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Repo: https://github.com/$ghUser/nadakki-google-ads-mvp" -ForegroundColor White
Write-Host ""
Write-Host "  To clone on another PC:" -ForegroundColor Cyan
Write-Host "    git clone https://github.com/$ghUser/nadakki-google-ads-mvp.git" -ForegroundColor White
Write-Host "    cd nadakki-google-ads-mvp" -ForegroundColor White
Write-Host "    pip install -r requirements.txt" -ForegroundColor White
Write-Host "    python main.py" -ForegroundColor White
Write-Host ""
Write-Host "  To start API server:" -ForegroundColor Cyan
Write-Host "    uvicorn main:app --reload --port 8000" -ForegroundColor White
Write-Host "    # Open http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
