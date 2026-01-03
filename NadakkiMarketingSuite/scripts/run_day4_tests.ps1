<#
================================================================================
 NADAKKI - DÍA 4 TESTS STANDALONE
================================================================================
#>

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogFile = "$ProjectRoot/logs/day4_tests.log"

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host " NADAKKI DAY 4 - TEST RUNNER STANDALONE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

Push-Location $ProjectRoot

# Limpiar log
if (Test-Path $LogFile) { Remove-Item $LogFile -Force }

$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"$ts | START | Day 4 Tests" | Out-File $LogFile -Encoding UTF8

# Ejecutar tests
Write-Host "`n--- Ejecutando tests Day 4 ---`n" -ForegroundColor Yellow

$output = python tests/test_day4.py 2>&1 | Tee-Object -Variable testOutput
$testOutput | Out-File $LogFile -Append -Encoding UTF8

# Verificar resultado
if ($testOutput -match "0 failed") {
    Write-Host "`n  ✅ TODOS LOS TESTS PASARON" -ForegroundColor Green
} else {
    Write-Host "`n  ⚠️  ALGUNOS TESTS FALLARON" -ForegroundColor Yellow
}

$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"$ts | END | Day 4 Tests" | Out-File $LogFile -Append -Encoding UTF8

Pop-Location

Write-Host "`nLog guardado en: $LogFile" -ForegroundColor Cyan
Write-Host ""
