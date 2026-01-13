# NADAKKI AI SUITE - ECOSYSTEM MANAGER
param([switch]$Sync,[switch]$Test,[switch]$Status,[switch]$Setup,[switch]$Help)

$BACKEND_URL = "https://nadakki-ai-suite.onrender.com"
$FRONTEND_URL = "https://dashboard.nadakki.com"
$PROJECTS_PATH = "C:\Users\$env:USERNAME\Projects"
$BACKEND_PATH = "$PROJECTS_PATH\nadakki-ai-suite\nadakki-ai-suite"
$FRONTEND_PATH = "$PROJECTS_PATH\nadakki-dashboard"

function Show-Status {
    Write-Host "`n=== NADAKKI ECOSYSTEM STATUS ===" -ForegroundColor Blue
    
    # Backend
    Write-Host "`n1. BACKEND (Render)" -ForegroundColor Cyan
    try { Invoke-RestMethod "$BACKEND_URL/health" -TimeoutSec 30 | Out-Null; Write-Host "   Estado: OK" -ForegroundColor Green } 
    catch { Write-Host "   Estado: OFFLINE" -ForegroundColor Red }
    
    # Frontend
    Write-Host "`n2. FRONTEND (Vercel)" -ForegroundColor Cyan
    try { Invoke-WebRequest $FRONTEND_URL -TimeoutSec 30 -UseBasicParsing | Out-Null; Write-Host "   Estado: OK" -ForegroundColor Green }
    catch { Write-Host "   Estado: OFFLINE" -ForegroundColor Red }
    
    # Agents
    Write-Host "`n3. MARKETING AGENTS" -ForegroundColor Cyan
    try {
        $r = Invoke-RestMethod "$BACKEND_URL/agents" -TimeoutSec 30
        $m = ($r.agents | Where-Object { $_.core -eq "marketing" }).Count
        Write-Host "   Agentes: $m/35" -ForegroundColor $(if ($m -eq 35) {"Green"} else {"Yellow"})
    } catch { Write-Host "   Error" -ForegroundColor Red }
    
    # Git
    Write-Host "`n4. GIT STATUS" -ForegroundColor Cyan
    if (Test-Path $BACKEND_PATH) {
        Push-Location $BACKEND_PATH
        $s = git status --porcelain
        Write-Host "   Backend: $(if ([string]::IsNullOrEmpty($s)) {'OK'} else {'Cambios pendientes'})" -ForegroundColor $(if ([string]::IsNullOrEmpty($s)) {"Green"} else {"Yellow"})
        Pop-Location
    }
    if (Test-Path $FRONTEND_PATH) {
        Push-Location $FRONTEND_PATH
        $s = git status --porcelain
        Write-Host "   Frontend: $(if ([string]::IsNullOrEmpty($s)) {'OK'} else {'Cambios pendientes'})" -ForegroundColor $(if ([string]::IsNullOrEmpty($s)) {"Green"} else {"Yellow"})
        Pop-Location
    }
    Write-Host ""
}

function Sync-Repos {
    Write-Host "`n=== SINCRONIZANDO ===" -ForegroundColor Blue
    if (Test-Path $BACKEND_PATH) { Push-Location $BACKEND_PATH; git pull origin main; Pop-Location; Write-Host "Backend: OK" -ForegroundColor Green }
    if (Test-Path $FRONTEND_PATH) { Push-Location $FRONTEND_PATH; git pull origin main; Pop-Location; Write-Host "Frontend: OK" -ForegroundColor Green }
}

function Test-Agents {
    Write-Host "`n=== PROBANDO 35 AGENTES ===" -ForegroundColor Blue
    $r = Invoke-RestMethod "$BACKEND_URL/agents" -TimeoutSec 30
    $agents = $r.agents | Where-Object { $_.core -eq "marketing" }
    $passed = 0
    foreach ($a in $agents) {
        Write-Host "  $($a.id)... " -NoNewline
        try { Invoke-RestMethod "$BACKEND_URL/agents/marketing/$($a.id)/execute" -Method POST -Body '{"test":"data"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null; Write-Host "OK" -ForegroundColor Green; $passed++ }
        catch { Write-Host "FAIL" -ForegroundColor Red }
    }
    Write-Host "`nResultado: $passed/35" -ForegroundColor $(if ($passed -eq 35) {"Green"} else {"Yellow"})
}

function Setup-NewTerminal {
    Write-Host "`n=== SETUP NUEVA TERMINAL ===" -ForegroundColor Blue
    if (-not (Test-Path $PROJECTS_PATH)) { New-Item -ItemType Directory -Path $PROJECTS_PATH -Force | Out-Null }
    if (-not (Test-Path "$PROJECTS_PATH\nadakki-ai-suite")) { Push-Location $PROJECTS_PATH; git clone https://github.com/csorianoai/nadakki-ai-suite.git; Pop-Location }
    if (-not (Test-Path $FRONTEND_PATH)) { Push-Location $PROJECTS_PATH; git clone https://github.com/csorianoai/nadakki-dashboard.git; Pop-Location }
    Write-Host "Setup completado. Siguiente: cd $BACKEND_PATH && python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt" -ForegroundColor Green
}

if ($Status -or (-not $Sync -and -not $Test -and -not $Setup -and -not $Help)) { Show-Status }
elseif ($Sync) { Sync-Repos }
elseif ($Test) { Test-Agents }
elseif ($Setup) { Setup-NewTerminal }
elseif ($Help) { Write-Host "Uso: .\nadakki-manager.ps1 [-Status] [-Sync] [-Test] [-Setup]" }
