Write-Host "`n🚀 INICIANDO AUDITORÍA MULTI-ECOSISTEMA NADAKKI AI SUITE..." -ForegroundColor Cyan

$basePath = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\agents"
$reportDir = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\reports"
if (!(Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$reportFile = "$reportDir\ecosystem_deep_audit_$timestamp.md"

# Ecosistemas esperados
$ecosystems = @(
    "marketing","legal","logistica","contabilidad","presupuesto","rrhh",
    "originacion","ventascrm","investigacion","educacion","regtech",
    "orchestration","recuperacion","decision","inteligencia","fortaleza",
    "experiencia","operacional","compliance","vigilancia"
)

$summary = @()
$totalAgents = 0

Write-Host "`n📦 Escaneando ecosistemas..." -ForegroundColor Yellow
foreach ($eco in $ecosystems) {
    $ecoPath = Join-Path $basePath $eco
    if (!(Test-Path $ecoPath)) {
        Write-Host "⚠️ $eco no encontrado" -ForegroundColor Red
        continue
    }

    $agents = Get-ChildItem -Path $ecoPath -Filter *.py | Where-Object { $_.Name -notmatch "__init__" }
    $count = $agents.Count
    $totalAgents += $count

    $summary += [pscustomobject]@{
        Ecosistema = $eco
        Cantidad = $count
        Ubicacion = $ecoPath
    }
    Write-Host "✅ $eco - $count agentes encontrados" -ForegroundColor Green
}

# === Generar reporte ===
$header = @("# 🧠 Nadakki AI Suite - Auditoría Multi-Ecosistema",
"**Fecha:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')",
"**Ubicación:** $basePath","---","## 1️⃣ RESUMEN GENERAL",
"Total ecosistemas: $($summary.Count)",
"Total agentes analizados: $totalAgents","---",
"| Ecosistema | Cantidad | Ubicación |",
"|-------------|-----------|-----------|")

$body = $summary | Sort-Object Ecosistema | ForEach-Object {
    "| $($_.Ecosistema) | $($_.Cantidad) | $($_.Ubicacion) |"
}

$header + $body | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n✅ Auditoría completa generada correctamente." -ForegroundColor Green
Write-Host "📄 Reporte: $reportFile" -ForegroundColor Yellow
Write-Host "💡 Ábrelo con: notepad $reportFile" -ForegroundColor Green
