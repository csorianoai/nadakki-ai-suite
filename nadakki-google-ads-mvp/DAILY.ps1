# ============================================================
# NADAKKI - Daily Sync & Dev Script
# Use this every day before starting work
# ============================================================

param(
    [switch]$Push,
    [switch]$Test,
    [switch]$Serve,
    [string]$Message = "Update"
)

$ErrorActionPreference = "Stop"
$PROJECT_DIR = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\nadakki-google-ads-mvp"

Set-Location $PROJECT_DIR
$env:DATABASE_URL = ""

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NADAKKI - Daily Dev Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Pull latest
Write-Host ""
Write-Host "[SYNC] Pulling latest from GitHub..." -ForegroundColor Yellow
git pull origin main 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Up to date" -ForegroundColor Green
} else {
    Write-Host "  [!] No remote yet or pull failed" -ForegroundColor Yellow
}

# Run tests if requested
if ($Test) {
    Write-Host ""
    Write-Host "[TEST] Running 64 tests..." -ForegroundColor Yellow
    python main.py 2>&1 | Select-Object -Last 15
}

# Push if requested
if ($Push) {
    Write-Host ""
    Write-Host "[PUSH] Committing and pushing..." -ForegroundColor Yellow
    git add .
    $status = git status --porcelain
    if ($status) {
        git commit -m $Message
        git push origin main
        Write-Host "  [OK] Pushed: $Message" -ForegroundColor Green
    } else {
        Write-Host "  [OK] Nothing to push" -ForegroundColor Green
    }
}

# Start server if requested
if ($Serve) {
    Write-Host ""
    Write-Host "[API] Starting server on http://localhost:8000" -ForegroundColor Yellow
    Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray
    uvicorn main:app --reload --port 8000
}

# Show usage if no flags
if (-not $Push -and -not $Test -and -not $Serve) {
    Write-Host ""
    Write-Host "  Usage:" -ForegroundColor Gray
    Write-Host "    .\DAILY.ps1 -Test              # Pull + run tests" -ForegroundColor White
    Write-Host "    .\DAILY.ps1 -Serve             # Pull + start API" -ForegroundColor White
    Write-Host "    .\DAILY.ps1 -Push -Message 'fix bug'  # Commit + push" -ForegroundColor White
    Write-Host "    .\DAILY.ps1 -Test -Serve       # Pull + test + serve" -ForegroundColor White
    Write-Host ""
}
