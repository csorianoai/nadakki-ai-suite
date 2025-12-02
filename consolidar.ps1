param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CONSOLIDACIÓN AUTOMÁTICA - DIRECTORIOS NADAKKI           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$projectMain = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
$backupRoot = "D:\Backups"
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupDir = "$backupRoot\nadakki-backup-$timestamp"
$migrationLog = "$projectMain\MIGRATION_LOG_$timestamp.md"

$dirToDelete = @(
    "C:\Nadakki",
    "C:\nadakki-banreservas",
    "C:\nadakki-deployment",
    "C:\nadakki-enterprise",
    "C:\nadakki-platform",
    "C:\NadakkiAI",
    "C:\Users\cesar\Desktop\nadakki-ai-suite-complete"
)

Write-Host "CONFIGURACIÓN:" -ForegroundColor Yellow
Write-Host "  Proyecto: $projectMain" -ForegroundColor Gray
Write-Host "  Backup: $backupDir" -ForegroundColor Gray
Write-Host "  Modo DryRun: $(if ($DryRun) { 'SÍ' } else { 'NO' })" -ForegroundColor Gray
Write-Host ""

if (-not (Test-Path $backupRoot)) {
    Write-Host "Creando carpeta de backups: $backupRoot" -ForegroundColor Yellow
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    }
}

Write-Host "PASO 1: CREAR BACKUP" -ForegroundColor Magenta
Write-Host "─" * 70 -ForegroundColor Magenta
Write-Host ""

Write-Host "📦 Creando backup: $backupDir" -ForegroundColor Cyan
if (-not $DryRun) {
    Copy-Item -Path $projectMain -Destination $backupDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Backup completado" -ForegroundColor Green
} else {
    Write-Host "   [DRY RUN] Se crearía backup en: $backupDir" -ForegroundColor Gray
}
Write-Host ""

Write-Host "PASO 2: CREAR legacy/ PARA FRAMEWORK" -ForegroundColor Magenta
Write-Host "─" * 70 -ForegroundColor Magenta
Write-Host ""

$frameworkDir = "C:\nadakki-framework"
if (Test-Path $frameworkDir) {
    $legacyFramework = "$projectMain\legacy\framework"
    Write-Host "✓ Respaldando framework..." -ForegroundColor Cyan
    if (-not $DryRun) {
        New-Item -ItemType Directory -Path $legacyFramework -Force | Out-Null
        Copy-Item -Path "$frameworkDir\*" -Destination $legacyFramework -Recurse -Force
    }
    Write-Host "  Framework respaldado en: $legacyFramework" -ForegroundColor Green
} else {
    Write-Host "⚠️  C:\nadakki-framework no encontrado" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "PASO 3: CONSOLIDAR C:\Nadakki" -ForegroundColor Magenta
Write-Host "─" * 70 -ForegroundColor Magenta
Write-Host ""

$nadakkiRoot = "C:\Nadakki"
if (Test-Path $nadakkiRoot) {
    $scriptsDest = "$projectMain\scripts\integrations"
    New-Item -ItemType Directory -Path $scriptsDest -Force | Out-Null
    
    @("NADAKKI_INTELIGENTE.ps1", "NADAKKI_SUPER_SIMPLE.ps1", "SUPER_SCRIPT.ps1") | ForEach-Object {
        $src = "$nadakkiRoot\$_"
        if (Test-Path $src) {
            if (-not $DryRun) {
                Copy-Item -Path $src -Destination $scriptsDest -Force
            }
            Write-Host "  ✓ $_" -ForegroundColor Green
        }
    }
    
    $logsSrc = "$nadakkiRoot\logs"
    if (Test-Path $logsSrc) {
        $logsDest = "$projectMain\logs-backup-$timestamp"
        if (-not $DryRun) {
            Copy-Item -Path $logsSrc -Destination $logsDest -Recurse -Force
        }
        Write-Host "  ✓ logs (respaldado)" -ForegroundColor Green
    }
    
    $reportsSrc = "$nadakkiRoot\reports"
    if (Test-Path $reportsSrc) {
        $reportsDest = "$projectMain\reports-backup-$timestamp"
        if (-not $DryRun) {
            Copy-Item -Path $reportsSrc -Destination $reportsDest -Recurse -Force
        }
        Write-Host "  ✓ reports (respaldado)" -ForegroundColor Green
    }
}
Write-Host ""

Write-Host "PASO 4: ELIMINAR DIRECTORIOS" -ForegroundColor Magenta
Write-Host "─" * 70 -ForegroundColor Magenta
Write-Host ""

foreach ($dir in $dirToDelete) {
    if (Test-Path $dir) {
        Write-Host "  ♻️  $dir" -ForegroundColor Yellow
        if (-not $DryRun) {
            Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "      ✓ Eliminado" -ForegroundColor Green
        } else {
            Write-Host "      [DRY RUN] Se eliminaría" -ForegroundColor Gray
        }
    }
}
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✓ PROCESO COMPLETADO                                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "RESUMEN:" -ForegroundColor Cyan
Write-Host "  Proyecto: $projectMain" -ForegroundColor Gray
Write-Host "  Backup: $backupDir" -ForegroundColor Gray
Write-Host ""

if ($DryRun) {
    Write-Host "⚠️  MODO DRY RUN - Sin cambios reales" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para ejecutar de verdad:" -ForegroundColor Cyan
    Write-Host "  .\consolidar.ps1" -ForegroundColor Gray
}

Write-Host ""