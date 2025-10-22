param(
  [string]$ProjectRoot = "."
)

Write-Host "Iniciando validacion QA de agentes Nadakki AI Suite"

$agents = Get-ChildItem -Path "$ProjectRoot\agents" -Recurse -Filter *.py `
    | Where-Object { $_.Name -notmatch "__init__|coordinator|test" }

$summary = @()
$countValid = 0

foreach ($file in $agents) {
  $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
  $hasClass = $content -match "class\s+\w+"
  $hasEvaluate = $content -match "evaluate|execute"
  $status = if ($hasClass -and $hasEvaluate) { "Funcional" } else { "Incompleto" }
  if ($status -eq "Funcional") { $countValid++ }

  $summary += [pscustomobject]@{
    Ecosistema = $file.Directory.Name
    Archivo = $file.Name
    TamanoKb = [math]::Round((Get-Item $file.FullName).Length / 1Kb, 1)
    Estado = $status
  }
}

$total = $agents.Count
$rate = [math]::Round(($countValid / $total) * 100, 1)

Write-Host "`nAgentes verificados: $total"
Write-Host "Funcionales: $countValid ($rate`%)"

$summaryPath = Join-Path $ProjectRoot "qa_summary.json"
$summary | ConvertTo-Json -Depth 3 | Out-File $summaryPath -Encoding utf8

Write-Host "`nReporte QA guardado en $summaryPath"

if ($countValid -ne $total) {
  Write-Host "Algunos agentes no pasaron la validacion. Ver qa_summary.json."
} else {
  Write-Host "Todos los agentes pasaron la validacion QA."
}

exit 0
