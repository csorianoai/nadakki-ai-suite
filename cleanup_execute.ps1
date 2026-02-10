# NADAKKI AI SUITE — CLEANUP EXECUTION
# Elimina archivos vacíos y mínimos (54 archivos)

param(
    [switch]$Confirm,
    [switch]$ShowOnly
)

Write-Host "`n" + "="*100
Write-Host "NADAKKI AI SUITE — LIMPIEZA DE ARCHIVOS BASURA"
Write-Host "="*100

# Cargar reporte
$reportPath = ".\agent_verification\detailed_verification_report.json"
if (-not (Test-Path $reportPath)) {
    Write-Host "❌ No se encontró: $reportPath" -ForegroundColor Red
    exit 1
}

$report = Get-Content $reportPath | ConvertFrom-Json

# Categorías a eliminar
$deleteCategories = @("ARCHIVO_MINIMO", "CLASE_VACIA")
$filesToDelete = @()

Write-Host "`n🔴 ARCHIVOS PARA ELIMINAR:" -ForegroundColor Red

foreach ($category in $deleteCategories) {
    if ($category -in $report.summary_by_category.PSObject.Properties.Name) {
        $files = $report.summary_by_category.$category.files
        $count = $report.summary_by_category.$category.count
        
        Write-Host "`n  $category ($count archivos):" -ForegroundColor Red
        
        foreach ($file in $files) {
            $fullPath = ".\agents\$file"
            if (Test-Path $fullPath) {
                $size = (Get-Item $fullPath).Length
                Write-Host "    ❌ $file ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Gray
                $filesToDelete += @{
                    path = $fullPath
                    file = $file
                    size = $size
                }
            }
        }
    }
}

Write-Host "`n📊 RESUMEN:" -ForegroundColor Yellow
$totalSize = ($filesToDelete | Measure-Object -Property size -Sum).Sum
Write-Host "  Total archivos a eliminar: $($filesToDelete.Count)" -ForegroundColor White
Write-Host "  Espacio a liberar: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor Green

if ($ShowOnly) {
    Write-Host "`n✅ Modo simulación completado" -ForegroundColor Green
    exit 0
}

if (-not $Confirm) {
    Write-Host "`n⚠️  ADVERTENCIA: Esto ELIMINARÁ archivos PERMANENTEMENTE" -ForegroundColor Red
    Write-Host "   Se creará BACKUP automático antes de eliminar" -ForegroundColor Yellow
    $response = Read-Host "`n¿Continuar? (escribir 'SI' para confirmar)"
    
    if ($response -ne "SI") {
        Write-Host "`n❌ Operación cancelada" -ForegroundColor Yellow
        exit 0
    }
}

# Crear backup PRIMERO
Write-Host "`n💾 Creando BACKUP..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = ".\backup_pre_cleanup_$timestamp"

try {
    Copy-Item -Path ".\agents" -Destination $backupDir -Recurse -Force -ErrorAction Stop
    Write-Host "   ✅ Backup creado en: $backupDir" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error creando backup: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🗑️  Eliminando archivos basura..." -ForegroundColor Cyan

$deletedCount = 0
$errors = @()

foreach ($item in $filesToDelete) {
    try {
        Remove-Item -Path $item.path -Force -ErrorAction Stop
        Write-Host "   ✅ $($item.file)" -ForegroundColor Green
        $deletedCount++
    } catch {
        $errors += @{
            file = $item.file
            error = $_
        }
        Write-Host "   ❌ $($item.file): $_" -ForegroundColor Red
    }
}

Write-Host "`n" + "="*100
Write-Host "✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
Write-Host "="*100

Write-Host "`n📊 RESULTADOS:" -ForegroundColor Cyan
Write-Host "   Archivos eliminados: $deletedCount / $($filesToDelete.Count)" -ForegroundColor Green
Write-Host "   Espacio liberado: $([math]::Round($totalSize/1MB, 3)) MB" -ForegroundColor Green
Write-Host "   Backup guardado: $backupDir" -ForegroundColor Gray

if ($errors.Count -gt 0) {
    Write-Host "`n⚠️  Errores ($($errors.Count)):" -ForegroundColor Yellow
    foreach ($err in $errors) {
        Write-Host "   - $($err.file)" -ForegroundColor Red
    }
}

Write-Host "`n📝 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "   1. ✅ Archivos basura eliminados (54)" -ForegroundColor Green
Write-Host "   2. ⏳ Quedan 234 ESQUELETO_AGENTE (decidir: keep o delete)" -ForegroundColor Yellow
Write-Host "   3. ⏳ Sincronizar backend con 49 agentes reales" -ForegroundColor Yellow
Write-Host "   4. ⏳ Implementar módulos faltantes (legal, contabilidad, etc.)" -ForegroundColor Yellow

Write-Host "`n" + "="*100 + "`n"
