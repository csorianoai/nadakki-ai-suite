Write-Host "`n🚀 INICIANDO AUDITORÍA MARKETING CORE v4.5..." -ForegroundColor Cyan

# === CONFIGURACIÓN ===
$basePath   = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
$agentsPath = Join-Path $basePath "agents\marketing"
$reportDir  = Join-Path $basePath "reports"
if (!(Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }

$timestamp  = Get-Date -Format "yyyy-MM-dd_HHmm"
$reportFile = "$reportDir\marketing_core_audit_$timestamp.md"
$csvFile    = "$reportDir\marketing_core_audit_$timestamp.csv"
$factoryFile = Join-Path $basePath "services\agent_factory.py"

# === CARGAR IMPORTACIONES DE AGENT FACTORY ===
if (Test-Path $factoryFile) {
    $factoryImports = Get-Content $factoryFile | Select-String -Pattern "import" | ForEach-Object { $_.ToString() }
} else {
    $factoryImports = @()
}

# === ESCANEAR AGENTES DE MARKETING ===
Write-Host "`n📦 Escaneando agentes de Marketing..." -ForegroundColor Yellow
$agents = Get-ChildItem -Path $agentsPath -Filter *.py | Where-Object { $_.Name -notmatch "__init__" }
Write-Host "🔎 Agentes detectados: $($agents.Count)" -ForegroundColor Green

# === PROCESAR CADA AGENTE ===
$results = @()
foreach ($agent in $agents) {
    Write-Host "🧩 Evaluando $($agent.Name)..." -ForegroundColor Yellow

    $status = "Activo"
    $score = 100
    $priority = "🟢 OPTIMAL"
    $recommendation = "✅ Sin observaciones"

    # 1️⃣ Verificar sintaxis
    try {
        & python -m py_compile $agent.FullName 2>$null
    } catch {
        $status = "Error"
        $score = 60
        $priority = "🔴 REDESIGN"
        $recommendation = "❌ Error de sintaxis"
    }

    # 2️⃣ Verificar vinculación con AgentFactory
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
        if ($priority -eq "🟢 OPTIMAL") { $priority = "🟡 REVIEW" }
        $recommendation = "⚠️ No detectado en AgentFactory"
    }

    # 3️⃣ Verificar tamaño y antigüedad
    if ($agent.Length -lt 4096) {
        $score -= 5
        if ($priority -eq "🟢 OPTIMAL") { $priority = "🟡 REVIEW" }
        if ($recommendation -eq "✅ Sin observaciones") {
            $recommendation = "🧩 Posible agente incompleto"
        }
    }

    # 4️⃣ Evaluar prioridad final
    if ($score -lt 70) { $priority = "🔴 REDESIGN" }
    elseif ($score -lt 85) { $priority = "🟡 REVIEW" }
    else { $priority = "🟢 OPTIMAL" }

    $results += [pscustomobject]@{
        Agente = $agent.Name
        Estado = $status
        Score  = $score
        Prioridad = $priority
        Recomendacion = $recommendation
        Ultima_Modificacion = $agent.LastWriteTime
        Tamaño_KB = [math]::Round($agent.Length / 1KB, 2)
    }
}

# === GENERAR REPORTES ===
$header = @(
"# 🧠 Nadakki Marketing AI - Auditoría Profunda ($($results.Count) agentes)",
"**Fecha:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')",
"**Ubicación:** $agentsPath",
"---",
"| Agente | Estado | Score | Prioridad | Recomendación | Última Modificación | Tamaño (KB) |",
"|---------|---------|--------|------------|----------------|---------------------|--------------|"
)
$body = $results | Sort-Object Score -Descending | ForEach-Object {
    "| $($_.Agente) | $($_.Estado) | $($_.Score) | $($_.Prioridad) | $($_.Recomendacion) | $($_.Ultima_Modificacion) | $($_.Tamaño_KB) |"
}

# Guardar en Markdown
$header + $body | Out-File -FilePath $reportFile -Encoding UTF8
# Guardar en CSV
$results | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8

# === MOSTRAR RESUMEN ===
$opt = ($results | Where-Object { $_.Prioridad -eq "🟢 OPTIMAL" }).Count
$rev = ($results | Where-Object { $_.Prioridad -eq "🟡 REVIEW" }).Count
$red = ($results | Where-Object { $_.Prioridad -eq "🔴 REDESIGN" }).Count

Write-Host "`n✅ Auditoría completada." -ForegroundColor Green
Write-Host "📄 Reporte Markdown: $reportFile" -ForegroundColor Yellow
Write-Host "📊 Reporte CSV: $csvFile" -ForegroundColor Yellow
Write-Host "`nResumen:" -ForegroundColor Cyan
Write-Host "   🟢 OPTIMAL : $opt"
Write-Host "   🟡 REVIEW  : $rev"
Write-Host "   🔴 REDESIGN: $red"
