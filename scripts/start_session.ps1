param(
    [string]$Phase = "0",
    [string]$Day = "1"
)

$today = Get-Date -Format "yyyy-MM-dd"
$logDir = "logs\daily"

if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }

$sessionFile = "$logDir\Nadakki_Phase${Phase}_Day${Day}_$today.md"

$template = @"
# **NADAKKI AI SUITE — PHASE $Phase – DAY $Day ($today)**

## **📋 CONTEXTO**
Describe brevemente qué hiciste o qué quieres lograr hoy.

---

## **🧮 RESULTADOS / INPUTS**
\`\`\`python
# Variables o resultados del día anterior
\`\`\`

---

## **⚙️ COMANDOS EJECUTADOS**
\`\`\`powershell
# POWERSHELL
\`\`\`

---

## **📊 OUTPUT DEL POWERSHELL / PYTHON**
\`\`\`
(Pega aquí el output completo de la consola)
\`\`\`

---

## **🧠 AI ANALYSIS (BY GPT-5)**
Análisis técnico profesional:
- Qué indican los resultados
- Decisiones tomadas
- Riesgos o inconsistencias detectadas
- Próximos pasos recomendados

---

## **🎯 NEXT ACTIONS (72h PLAN)**
| Día | Acción | Herramienta / LLM | Entregable |
|-----|---------|------------------|-------------|
| D+1 | ... | ... | ... |
"@

$template | Out-File -FilePath $sessionFile -Encoding utf8 -Force

Write-Host "`n✅ Plantilla diaria creada: $sessionFile" -ForegroundColor Green
Write-Host "📂 Puedes abrirla con: notepad $sessionFile" -ForegroundColor Cyan
# ────────────────────────────────────────────────
# NADAKKI WEEKLY LOGGER MODULE
# Genera resumen semanal automático de los logs diarios
# ────────────────────────────────────────────────

function New-WeeklySummary {
    $today = Get-Date
    $weekNumber = (Get-Date -UFormat %V)
    $year = $today.Year
    $weekDir = "logs\weekly"
    if (!(Test-Path $weekDir)) { New-Item -ItemType Directory -Force -Path $weekDir | Out-Null }

    $summaryFile = "$weekDir\summary_${year}-W${weekNumber}.md"

    $header = @"
# **NADAKKI AI SUITE — WEEKLY SUMMARY ($year - Week $weekNumber)**
Generated automatically on $(Get-Date -Format "yyyy-MM-dd HH:mm")

---

## 📋 DAILY LOGS CONSOLIDATED
"@

    # Obtener todos los logs de la semana actual
    $startOfWeek = $today.AddDays(-($today.DayOfWeek.value__))
    $files = Get-ChildItem -Path "logs\daily" -Filter "*.md" | 
        Where-Object { $_.LastWriteTime -ge $startOfWeek }

    $content = ""
    foreach ($f in $files) {
        $content += "`n### 🗓️ $($f.Name)`n"
        $content += (Get-Content $f.FullName | Out-String)
        $content += "`n---`n"
    }

    $full = $header + $content
    $full | Out-File -FilePath $summaryFile -Encoding utf8 -Force

    Write-Host "📊 Resumen semanal actualizado: $summaryFile" -ForegroundColor Green
}

# Ejecutar resumen solo si es domingo o si no existe resumen de esta semana
$dayOfWeek = (Get-Date).DayOfWeek
$weekNumber = (Get-Date -UFormat %V)
$year = (Get-Date).Year
$summaryPath = "logs\weekly\summary_${year}-W${weekNumber}.md"

if ($dayOfWeek -eq 'Sunday' -or !(Test-Path $summaryPath)) {
    New-WeeklySummary
}

