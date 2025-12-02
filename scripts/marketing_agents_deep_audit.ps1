Write-Host "`n🚀 INICIANDO AUDITORÍA COMPLETA DE AGENTES MARKETING AI (v3)..." -ForegroundColor Cyan

# === CONFIGURACIÓN ===
$basePath = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
$agentsDirs = @("agents", "agents_backup", "agents_consolidated")
$reportDir = Join-Path $basePath "reports"
if (!(Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$reportFile = "$reportDir\marketing_agents_full_audit_$timestamp.md"
$factoryFile = Join-Path $basePath "services\agent_factory.py"

# === VERIFICAR AgentFactory ===
if (Test-Path $factoryFile) {
    $factoryImports = Get-Content $factoryFile | Select-String -Pattern "import" | ForEach-Object { $_.ToString() }
} else {
    $factoryImports = @()
}

# === RECOLECTAR ARCHIVOS ===
$agents = @()
foreach ($dir in $agentsDirs) {
    $path = Join-Path $basePath $dir
    if (Test-Path $path) {
        $found = Get-ChildItem -Path $path -Filter *.py -Recurse | Where-Object { $_.Name -notmatch "(__init__|test|schema)" }
        $agents += $found
    }
}

Write-Host "📦 Agentes encontrados: $($agents.Count)" -ForegroundColor Yellow

# === AUDITORÍA ===
$results = @()
foreach ($agent in $agents) {
    Write-Host "🔎 Verificando $($agent.Name)..." -ForegroundColor Yellow
    $status = "Activo"
    $score = 100
    $recommendation = "✅ Sin observaciones"

    try {
        & python -m py_compile $agent.FullName 2>$null
    } catch {
        $status = "Error"
        $score = 60
        $recommendation = "❌ Error de sintaxis"
    }

    # Verificar si está importado en AgentFactory
    $imported = $false
    foreach ($line in $factoryImports) {
        if ($line -match [Regex]::Escape($agent.BaseName)) {
            $imported = $true
            break
        }
    }

    if (-not $imported) {
        $status = "No vinculado"
        $score -= 10
        $recommendation = "⚠️ No detectado en AgentFactory"
    }

    # Verificar tamaño mínimo
    if ($agent.Length -lt 4096) {
        $score -= 5
        if ($recommendation -eq "✅ Sin observaciones") {
            $recommendation = "🧩 Posible agente incompleto"
        }
    }

    $results += [pscustomobject]@{
        Agente = $agent.Name
        Carpeta = $agent.Directory.Name
        Estado = $status
        Score = $score
        Recomendacion = $recommendation
        Ultima_Modificacion = $agent.LastWriteTime
        Tamaño_KB = [math]::Round($agent.Length / 1KB, 2)
    }
}

# === GENERAR REPORTE ===
$header = @("# 🧠 Nadakki Marketing AI - Auditoría Completa de Agentes ($($results.Count))",
"| Carpeta | Agente | Estado | Score | Recomendación | Última Modificación | Tamaño (KB) |",
"|----------|---------|---------|--------|----------------|---------------------|--------------|")

$body = $results | Sort-Object Score -Descending | ForEach-Object {
    "| $($_.Carpeta) | $($_.Agente) | $($_.Estado) | $($_.Score) | $($_.Recomendacion) | $($_.Ultima_Modificacion) | $($_.Tamaño_KB) |"
}

# === RESUMEN CORRECTO ===
$activeCount = ($results | Where-Object { $_.Estado -eq "Activo" }).Count
$notLinkedCount = ($results | Where-Object { $_.Estado -eq "No vinculado" }).Count
$errorCount = ($results | Where-Object { $_.Estado -eq "Error" }).Count

$summary = @("`n## 📊 Resumen general",
"- 🟢 Activos: $activeCount",
"- 🟡 No vinculados: $notLinkedCount",
"- 🔴 Con errores: $errorCount")

$header + $body + $summary | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n✅ Auditoría completa finalizada." -ForegroundColor Green
Write-Host "📄 Reporte generado: $reportFile" -ForegroundColor Yellow
Write-Host "💡 Ábrelo con: notepad $reportFile" -ForegroundColor Green
