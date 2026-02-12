$ErrorActionPreference = "Stop"

$latest = Get-ChildItem ".\audit_reports\node_projects_*.json" -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latest) {
  Write-Host "❌ No existe audit_reports\node_projects_*.json. Primero hay que generarlo." -ForegroundColor Red
  exit 1
}

Write-Host "`nUSANDO: $($latest.FullName)`n" -ForegroundColor Cyan

$report = Get-Content $latest.FullName -Raw | ConvertFrom-Json
$report | Format-Table dir, isNext, hasBuild, scripts -AutoSize

$targets = $report | Where-Object { $_.hasBuild -eq $true }

if (-not $targets) {
  Write-Host "`n⚠️ Ninguna carpeta tiene script build." -ForegroundColor Yellow
  Write-Host "👉 Eso significa que ESTE repo no es el del Next/Dashboard, o el build está en otro repo/carpeta." -ForegroundColor Yellow
  exit 0
}

foreach ($t in $targets) {
  Write-Host "`n══════════════════════════════════════" -ForegroundColor DarkCyan
  Write-Host "🏗️ BUILD TARGET: $($t.dir)" -ForegroundColor Green
  Write-Host "══════════════════════════════════════" -ForegroundColor DarkCyan

  Push-Location $t.dir
  try {
    if (Test-Path ".\pnpm-lock.yaml") {
      pnpm install
      pnpm run build
    } elseif (Test-Path ".\yarn.lock") {
      yarn install
      yarn build
    } else {
      npm install
      npm run build
    }
    Write-Host "✅ BUILD OK: $($t.dir)" -ForegroundColor Green
  } catch {
    Write-Host "❌ BUILD FALLÓ: $($t.dir) -> $($_.Exception.Message)" -ForegroundColor Red
  } finally {
    Pop-Location
  }
}
