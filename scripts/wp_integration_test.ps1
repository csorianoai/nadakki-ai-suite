<#
=====================================================================================
 NADAKKI AI SUITE v3.3.3 — WordPress Integration Test Script
 Prueba automática de los 3 endpoints principales:
   1. /api/v1/wp/auth
   2. /api/v1/wp/agents
   3. /api/v1/wp/evaluate
 Ejecuta este script en PowerShell (modo administrador o normal)
=====================================================================================
#>

# ==========================================================
# CONFIGURACIÓN INICIAL
# ==========================================================
$BaseUrl = "http://127.0.0.1:8000/api/v1/wp"
$Headers = @{ "X-Token" = "nadakki-secure" }

Write-Host "`n🔍 INICIANDO TEST DE INTEGRACIÓN WORDPRESS ↔ NADAKKI AI SUITE" -ForegroundColor Cyan
$startTime = Get-Date

# ==========================================================
# TEST 1: AUTH
# ==========================================================
Write-Host "`n[1️⃣] PROBANDO ENDPOINT: /auth ..." -ForegroundColor Yellow
try {
    $authBody = @{ source = "WordPress" } | ConvertTo-Json
    $authResponse = Invoke-RestMethod -Uri "$BaseUrl/auth" -Method POST -Headers $Headers -Body $authBody -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ AUTH OK:" -ForegroundColor Green
    $authResponse | ConvertTo-Json -Depth 4
} catch {
    Write-Host "❌ ERROR AUTH:" $_.Exception.Message -ForegroundColor Red
}

# ==========================================================
# TEST 2: AGENTS
# ==========================================================
Write-Host "`n[2️⃣] PROBANDO ENDPOINT: /agents ..." -ForegroundColor Yellow
try {
    $agentsResponse = Invoke-RestMethod -Uri "$BaseUrl/agents" -Method GET -Headers $Headers -TimeoutSec 10
    Write-Host "✅ AGENTS OK:" -ForegroundColor Green
    $agentsResponse | ConvertTo-Json -Depth 4
} catch {
    Write-Host "❌ ERROR AGENTS:" $_.Exception.Message -ForegroundColor Red
}

# ==========================================================
# TEST 3: EVALUATE
# ==========================================================
Write-Host "`n[3️⃣] PROBANDO ENDPOINT: /evaluate ..." -ForegroundColor Yellow
try {
    $evaluateBody = @{
        agent_id = "lead_scoring"
        data = @{ cliente = "prueba"; score = 720 }
    } | ConvertTo-Json
    $evaluateResponse = Invoke-RestMethod -Uri "$BaseUrl/evaluate" -Method POST -Headers $Headers -Body $evaluateBody -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ EVALUATE OK:" -ForegroundColor Green
    $evaluateResponse | ConvertTo-Json -Depth 4
} catch {
    Write-Host "❌ ERROR EVALUATE:" $_.Exception.Message -ForegroundColor Red
}

# ==========================================================
# RESULTADO FINAL
# ==========================================================
$endTime = Get-Date
$duration = [math]::Round(($endTime - $startTime).TotalSeconds, 2)

Write-Host "`n==============================================================" -ForegroundColor Cyan
Write-Host "🧠 TEST COMPLETADO EN $duration SEGUNDOS" -ForegroundColor Cyan
Write-Host "✅ Si los 3 endpoints devolvieron datos → Integración correcta" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Cyan
