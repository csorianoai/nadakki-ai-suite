# ==========================================================
# NADAKKI AI SUITE - PHASE 3-B: SLA VISUAL REPORT (ASCII SAFE)
# Autor: César Soriano
# Fecha: 2025-10-23
# Objetivo: Exportar resultados SLA a CSV + generar gráfico visual
# ==========================================================

Write-Host ""
Write-Host "INICIANDO PHASE 3-B - SLA VISUAL REPORT..." -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$projectPath = Get-Location
$reportDir = Join-Path $projectPath "logs/performance"

# Crear carpeta de reportes si no existe
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

# Buscar el último log SLA
$lastLog = Get-ChildItem $reportDir -Filter "sla_report_*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $lastLog) {
    Write-Host "ADVERTENCIA: No se encontró ningún archivo de SLA previo." -ForegroundColor Yellow
    exit
}

Write-Host ("Analizando archivo: " + $lastLog.Name) -ForegroundColor Yellow

$csvFile = Join-Path $reportDir ("sla_data_" + $timestamp + ".csv")
$chartFile = Join-Path $reportDir ("sla_chart_" + $timestamp + ".png")

# Extraer datos del log
$data = @()
Get-Content $lastLog.FullName | ForEach-Object {
    if ($_ -match "^\[(?<time>[\d:]+)\]\s+(?<endpoint>/\S+)\s+- Status:\s+(?<status>\S+)\s+- (?<latency>[-\d\.]+)\s+ms") {
        $data += [PSCustomObject]@{
            Timestamp = $matches['time']
            Endpoint  = $matches['endpoint']
            Status    = $matches['status']
            LatencyMS = [double]$matches['latency']
        }
    }
}

if ($data.Count -eq 0) {
    Write-Host "No se detectaron datos válidos en el log." -ForegroundColor Yellow
    exit
}

# Guardar CSV
$data | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8
Write-Host ("Datos exportados a CSV: " + $csvFile) -ForegroundColor Green

# Crear gráfico de barras
Add-Type -AssemblyName System.Windows.Forms.DataVisualization
$chart = New-Object System.Windows.Forms.DataVisualization.Charting.Chart
$chart.Width = 800
$chart.Height = 500
$chart.BackColor = [System.Drawing.Color]::FromArgb(30,30,30)

$area = New-Object System.Windows.Forms.DataVisualization.Charting.ChartArea
$area.BackColor = [System.Drawing.Color]::FromArgb(45,45,45)
$area.AxisX.MajorGrid.LineColor = "Gray"
$area.AxisY.MajorGrid.LineColor = "Gray"
$area.AxisX.LabelStyle.ForeColor = "White"
$area.AxisY.LabelStyle.ForeColor = "White"
$chart.ChartAreas.Add($area)

$series = New-Object System.Windows.Forms.DataVisualization.Charting.Series
$series.Name = "Latency (ms)"
$series.ChartType = [System.Windows.Forms.DataVisualization.Charting.SeriesChartType]::Column
$series.Color = [System.Drawing.Color]::FromArgb(0,180,255)
$chart.Series.Add($series)

foreach ($row in $data) {
    if ($row.LatencyMS -gt 0) {
        $chart.Series["Latency (ms)"].Points.AddXY($row.Endpoint, $row.LatencyMS) | Out-Null
    }
}

$chart.Titles.Add("NADAKKI AI SUITE - SLA Performance Report (" + $timestamp + ")")
$chart.Titles[0].ForeColor = "White"
$chart.Titles[0].Font = New-Object System.Drawing.Font("Segoe UI",14,[System.Drawing.FontStyle]::Bold)

# Guardar imagen
$chart.SaveImage($chartFile, "Png")
Write-Host ("Grafico generado: " + $chartFile) -ForegroundColor Green

# Abrir automáticamente CSV
Invoke-Item $csvFile

Write-Host ""
Write-Host "PHASE 3-B COMPLETADA." -ForegroundColor Green
Write-Host ("CSV: " + $csvFile)
Write-Host ("Grafico: " + $chartFile)
