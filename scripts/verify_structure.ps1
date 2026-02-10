param([switch]$Fix)

$AI_SUITE  = "C:\Users\ramon\Projects\nadakki-ai-suite"
$DASHBOARD = "C:\Users\ramon\Projects\nadakki-dashboard"
$STAMP     = Get-Date -Format "yyyyMMdd_HHmmss"
$LEGACY_AI = Join-Path $AI_SUITE  "legacy\verify_fix_$STAMP"
$LEGACY_FE = Join-Path $DASHBOARD "legacy\verify_fix_$STAMP"

function OK($m)  { Write-Host "✅ $m" -ForegroundColor Green }
function WARN($m){ Write-Host "⚠️  $m" -ForegroundColor Yellow }
function BAD($m) { Write-Host "❌ $m" -ForegroundColor Red }

function MoveAI([string]$path){
  if (-not (Test-Path $path)) { return }
  New-Item -ItemType Directory -Force -Path $LEGACY_AI | Out-Null
  $name = Split-Path $path -Leaf
  Move-Item -Path $path -Destination (Join-Path $LEGACY_AI $name) -Force -ErrorAction SilentlyContinue
  OK "Movido a legacy AI: $name"
}

function MoveFE([string]$path){
  if (-not (Test-Path $path)) { return }
  New-Item -ItemType Directory -Force -Path $LEGACY_FE | Out-Null
  $name = Split-Path $path -Leaf
  Move-Item -Path $path -Destination (Join-Path $LEGACY_FE $name) -Force -ErrorAction SilentlyContinue
  OK "Movido a legacy FE: $name"
}

Write-Host "`n📊 VERIFICACIÓN DE ESTRUCTURA NADAKKI" -ForegroundColor Cyan
Write-Host ("="*60)

# Dashboard duplicado
$backendDash = Join-Path $AI_SUITE "dashboard"
if ((Test-Path $DASHBOARD) -and (Test-Path $backendDash)) {
  BAD "Conflicto: dashboard real + dashboard en backend"
  if ($Fix) { MoveAI $backendDash }
} else { OK "Dashboard único OK" }

# Sidebars duplicados
$sidebars = Get-ChildItem -Path $DASHBOARD -Filter "Sidebar.tsx" -Recurse -ErrorAction SilentlyContinue
if ($sidebars.Count -gt 1) {
  BAD "Múltiples Sidebar.tsx encontrados"
  $sidebars | ForEach-Object { Write-Host " - $($_.FullName)" -ForegroundColor Yellow }
  WARN "Por seguridad NO se elimina automáticamente. Revisa imports en layouts."
} else { OK "Sidebar único OK (o no encontrado)" }

# Backups internos
$backups = Get-ChildItem -Path $DASHBOARD -Directory -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -eq ".backups" }

if ($backups) {
  BAD ".backups detectado en frontend"
  if ($Fix) { $backups | ForEach-Object { MoveFE $_.FullName } }
} else { OK "Sin backups internos OK" }

Write-Host "`n✅ Verificación completada." -ForegroundColor Green
if ($Fix) {
  Write-Host "Legacy AI: $LEGACY_AI" -ForegroundColor Cyan
  Write-Host "Legacy FE: $LEGACY_FE" -ForegroundColor Cyan
}
