param(
    [ValidateSet("analyze", "move", "delete", "activate")]
    [string]$Action = "analyze",
    [int]$Threshold = 50,
    [string]$TargetModule = "*",
    [switch]$Confirm
)

$reportPath = ".\agent_verification\detailed_verification_report.json"
if (-not (Test-Path $reportPath)) {
    Write-Host "ERROR: No se encontro el reporte" -ForegroundColor Red
    exit 1
}

$report = Get-Content $reportPath | ConvertFrom-Json
$skeletons = $report.detailed_analysis | Where-Object {
    $_.final_category -eq "ESQUELETO_AGENTE" -and
    $_.module -like $TargetModule
}

function Show-Analysis {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "ANALISIS DE ESQUELETOS DE AGENTES" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $total = $skeletons.Count
    $aboveThreshold = ($skeletons | Where-Object { $_.score -ge $Threshold }).Count
    $belowThreshold = $total - $aboveThreshold

    Write-Host "`nRESUMEN:" -ForegroundColor White
    Write-Host "  Total esqueletos: $total" -ForegroundColor White
    Write-Host "  Score mayor/igual $Threshold : $aboveThreshold (MANTENER)" -ForegroundColor Green
    Write-Host "  Score menor $Threshold : $belowThreshold (ELIMINAR)" -ForegroundColor Red

    Write-Host "`nDISTRIBUCION POR MODULO:" -ForegroundColor White
    $moduleStats = $skeletons | Group-Object module | Sort-Object Count -Descending

    foreach ($mod in $moduleStats) {
        $avgScore = [math]::Round(($mod.Group.score | Measure-Object -Average).Average, 1)
        $color = if ($avgScore -ge $Threshold) { "Green" } else { "Red" }
        $decision = if ($avgScore -ge $Threshold) { "MANTENER" } else { "ELIMINAR" }
        Write-Host "  $($mod.Name.PadRight(20)): $($mod.Count.ToString().PadLeft(3)) | Score: $avgScore | $decision" -ForegroundColor $color
    }

    Write-Host "`nTOP 5 ESQUELETOS (score mas alto):" -ForegroundColor Yellow
    $skeletons | Sort-Object score -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "  [OK] $($_.relative_path) (Score: $($_.score)/100)" -ForegroundColor Green
    }

    Write-Host "`nBOTTOM 5 ESQUELETOS (score mas bajo):" -ForegroundColor Red
    $skeletons | Sort-Object score | Select-Object -First 5 | ForEach-Object {
        Write-Host "  [XX] $($_.relative_path) (Score: $($_.score)/100)" -ForegroundColor Red
    }
}

function Delete-LowQuality {
    param([int]$Threshold = 50)

    $lowQuality = $skeletons | Where-Object { $_.score -lt $Threshold }
    $count = $lowQuality.Count

    if ($count -eq 0) {
        Write-Host "`nINFO: No hay esqueletos con score menor que $Threshold" -ForegroundColor Yellow
        return
    }

    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "ADVERTENCIA: ELIMINARA $count ESQUELETOS" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red

    if (-not $Confirm) {
        $answer = Read-Host "`nContinuar? (escribir SI para confirmar)"
        if ($answer -ne "SI") {
            Write-Host "CANCELADO" -ForegroundColor Yellow
            return
        }
    }

    $backupDir = ".\backup_skeletons_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "`nCreando backup..." -ForegroundColor Cyan
    Copy-Item -Path ".\agents" -Destination $backupDir -Recurse -Force
    Write-Host "[OK] Backup creado: $backupDir" -ForegroundColor Green

    $recycleDir = ".\agent_verification\recycled_skeletons_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Force -Path $recycleDir | Out-Null

    $deletedCount = 0
    $errors = @()

    Write-Host "`nEliminando archivos..." -ForegroundColor Cyan

    foreach ($skeleton in $lowQuality) {
        $filePath = ".\agents\$($skeleton.relative_path)"

        if (Test-Path $filePath) {
            try {
                Remove-Item -Path $filePath -Force -ErrorAction Stop
                $deletedCount++
                Write-Host "  [OK] $($skeleton.relative_path)" -ForegroundColor Green
            }
            catch {
                $errors += $skeleton.relative_path
                Write-Host "  [ERROR] $($skeleton.relative_path)" -ForegroundColor Red
            }
        }
    }

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "ELIMINACION COMPLETADA" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nResultados:" -ForegroundColor White
    Write-Host "  Esqueletos eliminados: $deletedCount / $count" -ForegroundColor Green
    Write-Host "  Backup: $backupDir" -ForegroundColor Gray
    Write-Host "  Reciclaje: $recycleDir" -ForegroundColor Gray
}

function Create-Activation-Plan {
    param([int]$TopN = 20)

    $topSkeletons = $skeletons | Sort-Object score -Descending | Select-Object -First $TopN

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PLAN DE ACTIVACION - TOP $TopN" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $planContent = @"
# PLAN DE ACTIVACION DE AGENTES
# Generado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Total esqueletos: $($skeletons.Count)
# Top $TopN para activar primero

## PASOS PARA ACTIVAR CADA AGENTE:
1. Agregar metodo execute() o run()
2. Implementar logica de negocio
3. Agregar manejo de errores
4. Agregar logging
5. Crear tests basicos

## LISTA DE PRIORIDAD:

"@

    $i = 1
    foreach ($skeleton in $topSkeletons) {
        $planContent += "`n### $i. $($skeleton.relative_path)`n"
        $planContent += "- Score: $($skeleton.score)/100`n"
        $planContent += "- Lineas: $($skeleton.lines)`n"
        $planContent += "- Modulo: $($skeleton.module)`n"

        $needs = @()
        if (-not $skeleton.structure_analysis.has_def_execute -and -not $skeleton.structure_analysis.has_def_run) {
            $needs += "metodo execute()"
        }
        if (-not $skeleton.structure_analysis.has_try_except) {
            $needs += "manejo de errores"
        }
        if (-not $skeleton.structure_analysis.has_logging) {
            $needs += "logging"
        }
        if (-not $skeleton.structure_analysis.has_docstring) {
            $needs += "documentacion"
        }

        if ($needs.Count -gt 0) {
            $planContent += "- Necesita: " + ($needs -join ", ") + "`n"
        }

        $planContent += "- Accion: Implementar funcionalidad completa`n"
        $i++
    }

    $planPath = ".\agent_verification\activation_plan.md"
    $planContent | Out-File -FilePath $planPath -Encoding UTF8

    Write-Host "`n[OK] Plan de activacion: $planPath" -ForegroundColor Green
    Write-Host "`nTop 5 esqueletos:" -ForegroundColor White
    $topSkeletons | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $($_.relative_path) (Score: $($_.score))" -ForegroundColor Yellow
    }
}

switch ($Action) {
    "analyze" {
        Show-Analysis
    }
    "delete" {
        Delete-LowQuality -Threshold $Threshold
    }
    "activate" {
        Create-Activation-Plan
    }
    default {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "HERRAMIENTA DE GESTION DE ESQUELETOS" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "`nComandos:" -ForegroundColor White
        Write-Host "  .\manage_skeletons.ps1 analyze           - Analizar esqueletos" -ForegroundColor Gray
        Write-Host "  .\manage_skeletons.ps1 delete -Threshold 40 - Eliminar baja calidad" -ForegroundColor Red
        Write-Host "  .\manage_skeletons.ps1 activate          - Plan de activacion" -ForegroundColor Green
    }
}
