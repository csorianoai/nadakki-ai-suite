# Herramienta de limpieza simplificada para Windows
param(
    [string]$Action = "show",
    [switch]$Simulate,
    [switch]$Force
)

$reportPath = ".\agent_verification\detailed_verification_report.json"
if (-not (Test-Path $reportPath)) {
    Write-Host "❌ No se encontró el reporte de análisis" -ForegroundColor Red
    exit 1
}

$report = Get-Content $reportPath | ConvertFrom-Json

function Show-Summary {
    Write-Host "`n📊 RESUMEN DE AGENTES" -ForegroundColor Cyan
    Write-Host "-"*50
    
    $totalDelete = 0
    $totalReview = 0
    $totalKeep = 0
    
    foreach ($category in $report.recommendations.delete) {
        if ($category -in $report.summary_by_category.PSObject.Properties.Name) {
            $totalDelete += $report.summary_by_category.$category.count
        }
    }
    
    foreach ($category in $report.recommendations.review) {
        if ($category -in $report.summary_by_category.PSObject.Properties.Name) {
            $totalReview += $report.summary_by_category.$category.count
        }
    }
    
    foreach ($category in $report.recommendations.keep) {
        if ($category -in $report.summary_by_category.PSObject.Properties.Name) {
            $totalKeep += $report.summary_by_category.$category.count
        }
    }
    
    Write-Host "   ✅ Mantener: $totalKeep archivos" -ForegroundColor Green
    Write-Host "   ⚠️  Revisar: $totalReview archivos" -ForegroundColor Yellow
    Write-Host "   🗑️  Eliminar: $totalDelete archivos" -ForegroundColor Red
}

function Show-Files-To-Delete {
    Write-Host "`n📋 ARCHIVOS PARA ELIMINAR:" -ForegroundColor Yellow
    Write-Host "-"*70
    
    $allFiles = @()
    
    foreach ($category in $report.recommendations.delete) {
        if ($category -in $report.summary_by_category.PSObject.Properties.Name) {
            $files = $report.summary_by_category.$category.files
            $count = $report.summary_by_category.$category.count
            
            Write-Host "`n🔴 $category ($count archivos):" -ForegroundColor Red
            
            foreach ($file in $files) {
                Write-Host "   - agents/$file" -ForegroundColor Gray
                $allFiles += "agents/$file"
            }
        }
    }
    
    # Guardar lista
    $allFiles | Out-File -FilePath ".\agent_verification\files_to_delete.txt" -Encoding UTF8
    Write-Host "`n📄 Lista guardada en: .\agent_verification\files_to_delete.txt" -ForegroundColor Green
    
    return $allFiles
}

function Create-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = ".\backup_pre_cleanup_$timestamp"
    
    Write-Host "`n💾 Creando backup..." -ForegroundColor Cyan
    Copy-Item -Path ".\agents" -Destination $backupDir -Recurse -Force
    Write-Host "✅ Backup creado: $backupDir" -ForegroundColor Green
    
    return $backupDir
}

function Simulate-Cleanup {
    $files = Show-Files-To-Delete
    $totalSize = 0
    
    Write-Host "`n🔍 SIMULACIÓN DE LIMPIEZA:" -ForegroundColor Yellow
    Write-Host "-"*50
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            $size = (Get-Item $file).Length
            $totalSize += $size
            Write-Host "   [SIM] $file ($([math]::Round($size/1KB,2)) KB)" -ForegroundColor Gray
        }
    }
    
    Write-Host "`n📊 TOTAL SIMULACIÓN:" -ForegroundColor White
    Write-Host "   Archivos: $($files.Count)" -ForegroundColor Gray
    Write-Host "   Espacio: $([math]::Round($totalSize/1MB,2)) MB" -ForegroundColor Green
}

function Execute-Cleanup {
    param([switch]$SimulateOnly)
    
    $files = Show-Files-To-Delete
    
    if ($SimulateOnly) {
        Simulate-Cleanup
        return
    }
    
    Write-Host "`n⚠️  ADVERTENCIA: Esto ELIMINARÁ archivos permanentemente" -ForegroundColor Red
    $confirm = Read-Host "¿Continuar? (si/no)"
    
    if ($confirm -ne "si") {
        Write-Host "❌ Cancelado" -ForegroundColor Yellow
        return
    }
    
    # Crear backup primero
    $backupDir = Create-Backup
    
    # Crear carpeta de reciclaje
    $recycleDir = ".\agent_verification\recycled_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Force -Path $recycleDir | Out-Null
    
    $movedCount = 0
    $errors = @()
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            try {
                $filename = [System.IO.Path]::GetFileName($file)
                $dest = "$recycleDir\$filename"
                Move-Item -Path $file -Destination $dest -Force
                $movedCount++
                Write-Host "   ♻️  Movido: $filename" -ForegroundColor Gray
            }
            catch {
                $errors += $file
                Write-Host "   ❌ Error: $file" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "`n✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
    Write-Host "   Archivos movidos: $movedCount" -ForegroundColor White
    Write-Host "   Backup: $backupDir" -ForegroundColor Gray
    Write-Host "   Reciclaje: $recycleDir" -ForegroundColor Gray
    
    if ($errors.Count -gt 0) {
        Write-Host "`n⚠️  Errores ($($errors.Count)):" -ForegroundColor Yellow
        $errors | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    }
}

# Menú principal
switch ($Action) {
    "show" {
        Show-Summary
        Show-Files-To-Delete
    }
    "simulate" {
        Simulate-Cleanup
    }
    "cleanup" {
        if ($Simulate) {
            Execute-Cleanup -SimulateOnly
        } else {
            Execute-Cleanup
        }
    }
    default {
        Write-Host "`n🧹 HERRAMIENTA DE LIMPIEZA DE AGENTES" -ForegroundColor Cyan
        Write-Host "="*60
        Write-Host "Uso:" -ForegroundColor White
        Write-Host "  .\cleanup.ps1 show           - Mostrar resumen" -ForegroundColor Gray
        Write-Host "  .\cleanup.ps1 simulate       - Simular limpieza" -ForegroundColor Gray
        Write-Host "  .\cleanup.ps1 cleanup        - Ejecutar limpieza" -ForegroundColor Red
        Write-Host "  .\cleanup.ps1 cleanup -Simulate - Probar antes de limpiar" -ForegroundColor Yellow
    }
}
