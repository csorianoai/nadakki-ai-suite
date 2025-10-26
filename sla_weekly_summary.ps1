# ==========================================================
# NADAKKI AI SUITE - PHASE 3-C: SLA WEEKLY CONSOLIDATION
# Autor: César Soriano
# Fecha: 2025-10-23
# Objetivo: Consolidar métricas SLA semanales en CSV + gráfico + resumen MD
# ==========================================================

Write-Host ""
Write-Host "INICIANDO PHASE 3-C - CONSOLIDACION SEMANAL..." -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$projectPath = Get-Location
$performanceDir = Join-Path $projectPath "logs/performance"
$weeklyDir = Join-Path $projectPath "logs/weekly"

if (-not (Test-Path $weeklyDir)) {
    New-Item -ItemType Directory -Path $weeklyDir | Out-Null
}

# Recolectar CSVs previos
$csvFiles = Get-ChildItem $performanceDir -Filter "sla_data_*.csv"

if ($csvFiles.Count -eq 0) {
    Write-Host "ADVERTENCIA: No hay CSVs en logs/performance." -ForegroundColor Yellow
    exit
}

# Combinar CSVs
$allData = @()
foreach ($csv in $csvFiles) {
    $content = Import-Csv $csv.FullName
    $allData += $content
}

# Calcular promedios por endpoint
$grouped = $allData | Group-Object Endpoint | ForEach-Object {
    [PSCustomObject]@{
        Endpoint  = $_.Name
        Count     = $_.Group.Count
        AvgLatency = [math]::Round( ($_.Group | Measure-Object -Property LatencyMS -Average).Average , 2)
        MinLatency = ($_.Group | Measure-Object -Property LatencyMS -Minimum).Minimum
        MaxLatency = ($_.Group | Measure-Object -Property LatencyMS -Maximum).Maximum
    }
}

# Exportar CSV consolidado
$weeklyCsv = Join-Path $weeklyDir ("sla_weekly_summary_" + $timestamp + ".csv")
$grouped | Export-Csv -Path $weeklyCsv -NoTypeInformation -Encoding UTF8
Write-Host ("CSV consolidado generado: " + $weeklyCsv) -ForegroundColor Green

# Crear gráfico de barras
Add-Type -AssemblyName System.Windows.Forms.DataVisualization
$chart = New-Object System.Windows.Forms.DataVisualization.Charting.Chart
$chart.Width = 900
$chart.Height = 550
$chart.BackColor = [System.Drawing.Color]::FromArgb(30,30,30)

$area = New-Object System.Windows.Forms.DataVisualization.Charting.ChartArea
$area.BackColor = [System.Drawing.Color]::FromArgb(45,45,45)
$area.AxisX.MajorGrid.LineColor = "Gray"
$area.AxisY.MajorGrid.LineColor = "Gray"
$area.AxisX.LabelStyle.ForeColor = "White"
$area.AxisY.LabelStyle.ForeColor = "White"
$chart.ChartAreas.Add($area)

$series = New-Object System.Windows.Forms.DataVisualization.Charting.Series
$series.Name = "Average Latency (ms)"
$series.ChartType = [System.Windows.Forms.DataVisualization.Charting.SeriesChartType]::Column
$series.Color = [System.Drawing.Color]::FromArgb(0,200,255)
$chart.Series.Add($series)

foreach ($row in $grouped) {
    $chart.Series["Average Latency (ms)"].Points.AddXY($row.Endpoint, $row.AvgLatency) | Out-Null
}

$chart.Titles.Add("NADAKKI AI SUITE - SLA WEEKLY PERFORMANCE (" + $timestamp + ")")
$chart.Titles[0].ForeColor = "White"
$chart.Titles[0].Font = New-Object System.Drawing.Font("Segoe UI",14,[System.Drawing.FontStyle]::Bold)

$weeklyChart = Join-Path $weeklyDir ("sla_weekly_chart_" + $timestamp + ".png")
$chart.SaveImage($weeklyChart, "Png")
Write-Host ("Gráfico semanal generado: " + $weeklyChart) -ForegroundColor Green

# Crear resumen Markdown
$weekNum = (Get-Date).GetWeekOfYear([System.Globalization.CalendarWeekRule]::FirstFourDayWeek, [DayOfWeek]::Monday)
$summaryMd = Join-Path $weeklyDir ("summary_2025-W" + $weekNum + ".md")

$avgOverall = [math]::Round(($grouped | Measure-Object -Property AvgLatency -Average).Average, 2)

$mdContent = @"
# NADAKKI AI SUITE - SEMANAL SLA SUMMARY (W$weekNum)
**Fecha:** $(Get-Date)
**Promedio General:** ${avgOverall} ms  
**Total Endpoints:** $($grouped.Count)

| Endpoint | Promedio (ms) | Mínimo | Máximo | Muestras |
|-----------|---------------|--------|---------|-----------|
"@

foreach ($row in $grouped) {
    $mdContent += "| $($row.Endpoint) | $($row.AvgLatency) | $($row.MinLatency) | $($row.MaxLatency) | $($row.Count) |`r`n"
}

$mdContent += "`r`n![Gráfico Semanal]($(Split-Path $weeklyChart -Leaf))`r`n"
$mdContent | Out-File -FilePath $summaryMd -Encoding UTF8

Write-Host ""
Write-Host "PHASE 3-C COMPLETADA." -ForegroundColor Green
Write-Host ("Resumen Markdown: " + $summaryMd)
Write-Host ("CSV Semanal: " + $weeklyCsv)
Write-Host ("Gráfico: " + $weeklyChart)
