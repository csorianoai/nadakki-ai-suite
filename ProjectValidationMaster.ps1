# NADAKKI AI VALIDATION MASTER SCRIPT

$ValidationConfig = @{
    ProjectName = "NADAKKI AI ENTERPRISE SUITE"
    InstitutionName = "NADAKKI"
    Version = "1.0"
    ExecutionDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    ReportPath = "$PSScriptRoot\Validation_Reports"
    LogPath = "$PSScriptRoot\Logs"
    ConfigPath = "$PSScriptRoot\Config"
    EnvironmentFile = "$PSScriptRoot\Config\.env"
}

@($ValidationConfig.ReportPath, $ValidationConfig.LogPath) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

function Write-LogMessage {
    param(
        [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARNING", "ERROR")][string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logFile = "$($ValidationConfig.LogPath)\validation_$(Get-Date -Format 'yyyy-MM-dd').log"
    
    $colors = @{
        "SUCCESS" = "Green"
        "ERROR"   = "Red"
        "WARNING" = "Yellow"
        "INFO"    = "Cyan"
    }
    
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $colors[$Level]
    Add-Content -Path $logFile -Value $logMessage
}

function Test-EnvironmentVariable {
    param([string]$VariableName, [string]$Description)
    
    $value = [System.Environment]::GetEnvironmentVariable($VariableName, "User")
    
    if ($value) {
        Write-LogMessage "✓ $Description encontrada" "SUCCESS"
        return $true
    } else {
        Write-LogMessage "✗ $Description NO encontrada" "ERROR"
        return $false
    }
}

function Test-FileExists {
    param([string]$FilePath, [string]$Description)
    
    if (Test-Path $FilePath) {
        Write-LogMessage "✓ $Description existe" "SUCCESS"
        return $true
    } else {
        Write-LogMessage "✗ $Description NO existe" "ERROR"
        return $false
    }
}

function Test-DirectoryExists {
    param([string]$DirPath, [string]$Description)
    
    if (Test-Path $DirPath -PathType Container) {
        Write-LogMessage "✓ Directorio $Description existe" "SUCCESS"
        return $true
    } else {
        Write-LogMessage "✗ Directorio $Description NO existe" "ERROR"
        return $false
    }
}

function Load-EnvironmentVariables {
    Write-LogMessage "Cargando variables de entorno..." "INFO"
    
    if (Test-Path $ValidationConfig.EnvironmentFile) {
        Get-Content $ValidationConfig.EnvironmentFile | ForEach-Object {
            if ($_ -match '=') {
                $parts = $_ -split '=', 2
                if ($parts[0] -notmatch '^#') {
                    $key = $parts[0].Trim()
                    $value = $parts[1].Trim()
                    [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
                }
            }
        }
        Write-LogMessage "✓ Variables de entorno cargadas" "SUCCESS"
    } else {
        Write-LogMessage "⚠ Archivo .env no encontrado" "WARNING"
    }
}

$PhaseValidations = @{}

$PhaseValidations["76"] = {
    Write-LogMessage "Validando FASE 76: STRIPE INTEGRATION..." "INFO"
    $results = @{}
    $results["StripeKey"] = Test-EnvironmentVariable "STRIPE_SECRET_KEY" "STRIPE_SECRET_KEY"
    $results["StripeConfig"] = Test-FileExists "$($ValidationConfig.ConfigPath)\stripe.config.json" "Stripe Config"
    return $results
}

$PhaseValidations["78"] = {
    Write-LogMessage "Validando FASE 78: SENDGRID INTEGRATION..." "INFO"
    $results = @{}
    $results["SendGridKey"] = Test-EnvironmentVariable "SENDGRID_API_KEY" "SENDGRID_API_KEY"
    $results["SendGridConfig"] = Test-FileExists "$($ValidationConfig.ConfigPath)\sendgrid.config.json" "SendGrid Config"
    return $results
}

$PhaseValidations["80"] = {
    Write-LogMessage "Validando FASE 80: AUTH0 INTEGRATION..." "INFO"
    $results = @{}
    $results["Auth0Domain"] = Test-EnvironmentVariable "AUTH0_DOMAIN" "AUTH0_DOMAIN"
    $results["Auth0ClientId"] = Test-EnvironmentVariable "AUTH0_CLIENT_ID" "AUTH0_CLIENT_ID"
    $results["Auth0Config"] = Test-FileExists "$($ValidationConfig.ConfigPath)\auth0.config.json" "Auth0 Config"
    return $results
}

$PhaseValidations["81"] = {
    Write-LogMessage "Validando FASE 81: DATABASE SETUP..." "INFO"
    $results = @{}
    $results["DatabaseURL"] = Test-EnvironmentVariable "DATABASE_URL" "DATABASE_URL"
    $results["DbDir"] = Test-DirectoryExists "$($ValidationConfig.ConfigPath)\database" "Database Dir"
    return $results
}

$PhaseValidations["82"] = {
    Write-LogMessage "Validando FASE 82: API REST CORE..." "INFO"
    $results = @{}
    $results["BackendDir"] = Test-DirectoryExists "$PSScriptRoot\backend" "Backend"
    $results["BackendRoutes"] = Test-DirectoryExists "$PSScriptRoot\backend\src\routes" "Backend Routes"
    return $results
}

$PhaseValidations["83"] = {
    Write-LogMessage "Validando FASE 83: WEBHOOK PROCESSING..." "INFO"
    $results = @{}
    $results["WebhooksDir"] = Test-DirectoryExists "$PSScriptRoot\backend\src\webhooks" "Webhooks"
    $results["RedisURL"] = Test-EnvironmentVariable "REDIS_URL" "REDIS_URL"
    return $results
}

$PhaseValidations["84"] = {
    Write-LogMessage "Validando FASE 84: PAYMENT PROCESSING..." "INFO"
    $results = @{}
    $results["PaymentsModule"] = Test-DirectoryExists "$PSScriptRoot\backend\src\modules\payments" "Payments Module"
    return $results
}

$PhaseValidations["85"] = {
    Write-LogMessage "Validando FASE 85: NOTIFICATIONS..." "INFO"
    $results = @{}
    $results["NotificationsModule"] = Test-DirectoryExists "$PSScriptRoot\backend\src\modules\notifications" "Notifications"
    return $results
}

$PhaseValidations["86"] = {
    Write-LogMessage "Validando FASE 86: AUTHENTICATION UI..." "INFO"
    $results = @{}
    $results["FrontendDir"] = Test-DirectoryExists "$PSScriptRoot\frontend" "Frontend"
    $results["AuthComponents"] = Test-DirectoryExists "$PSScriptRoot\frontend\src\components\Auth" "Auth Components"
    return $results
}

$PhaseValidations["87"] = {
    Write-LogMessage "Validando FASE 87: DASHBOARD..." "INFO"
    $results = @{}
    $results["DashboardDir"] = Test-DirectoryExists "$PSScriptRoot\frontend\src\pages\Dashboard" "Dashboard"
    return $results
}

$PhaseValidations["88"] = {
    Write-LogMessage "Validando FASE 88: ADMIN PANEL..." "INFO"
    $results = @{}
    $results["AdminAuth"] = Test-DirectoryExists "$PSScriptRoot\frontend\src\auth" "Frontend Auth"
    return $results
}

$PhaseValidations["90"] = {
    Write-LogMessage "Validando FASE 90: MONITORING..." "INFO"
    $results = @{}
    $results["SentryDSN"] = Test-EnvironmentVariable "SENTRY_DSN" "SENTRY_DSN"
    return $results
}

$PhaseValidations["96"] = {
    Write-LogMessage "Validando FASE 96: CI/CD PIPELINE..." "INFO"
    $results = @{}
    $results["InfrastructureDir"] = Test-DirectoryExists "$PSScriptRoot\infrastructure" "Infrastructure"
    return $results
}

function Execute-AllValidations {
    Write-Host ""
    Write-LogMessage "INICIANDO VALIDACION COMPLETA DEL PROYECTO" "INFO"
    Write-LogMessage "Proyecto: $($ValidationConfig.ProjectName)" "INFO"
    Write-LogMessage "Institucion: $($ValidationConfig.InstitutionName)" "INFO"
    Write-Host ""
    
    $allResults = @{}
    $totalChecks = 0
    $passedChecks = 0
    
    Load-EnvironmentVariables
    Write-Host ""
    
    foreach ($phase in $PhaseValidations.Keys | Sort-Object {[int]$_}) {
        $phaseResults = & $PhaseValidations[$phase]
        $allResults["Fase_$phase"] = $phaseResults
        
        foreach ($check in $phaseResults.Values) {
            $totalChecks++
            if ($check) { $passedChecks++ }
        }
    }
    
    Write-Host ""
    
    return @{
        AllResults = $allResults
        TotalChecks = $totalChecks
        PassedChecks = $passedChecks
    }
}

function Generate-ValidationReport {
    param([hashtable]$ValidationResults)
    
    $reportDate = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $reportFile = "$($ValidationConfig.ReportPath)\ValidationReport_$reportDate.txt"
    
    $allResults = $ValidationResults.AllResults
    $totalChecks = $ValidationResults.TotalChecks
    $passedChecks = $ValidationResults.PassedChecks
    $failedChecks = $totalChecks - $passedChecks
    $successPercentage = if ($totalChecks -gt 0) { [math]::Round(($passedChecks / $totalChecks) * 100, 2) } else { 0 }
    
    $report = "REPORTE DE VALIDACION - NADAKKI AI ENTERPRISE SUITE`n"
    $report += "Institucion: $($ValidationConfig.InstitutionName)`n"
    $report += "Fecha: $($ValidationConfig.ExecutionDate)`n`n"
    $report += "RESUMEN GENERAL`n"
    $report += "Total de Validaciones: $totalChecks`n"
    $report += "Validaciones Pasadas: $passedChecks`n"
    $report += "Validaciones Fallidas: $failedChecks`n"
    $report += "Tasa de Exito: $successPercentage%`n`n"
    $report += "DETALLES POR FASE`n"
    $report += "=" * 80 + "`n"
    
    foreach ($phaseKey in $allResults.Keys | Sort-Object {[int]($_ -replace 'Fase_', '')}) {
        $phaseNum = $phaseKey -replace 'Fase_', ''
        $phaseChecks = $allResults[$phaseKey]
        
        $phasePassed = ($phaseChecks.Values | Where-Object { $_ -eq $true } | Measure-Object).Count
        $phaseTotal = $phaseChecks.Count
        
        $report += "`nFASE $phaseNum (Pasadas: $phasePassed/$phaseTotal)`n"
        
        foreach ($checkName in $phaseChecks.Keys) {
            $checkStatus = $phaseChecks[$checkName]
            $checkIcon = if ($checkStatus) { "✓" } else { "✗" }
            $report += "  $checkIcon $checkName`n"
        }
    }
    
    $report | Out-File -FilePath $reportFile -Encoding UTF8 -Force
    Write-LogMessage "Reporte generado: $reportFile" "SUCCESS"
    
    return $reportFile
}

function Main {
    Clear-Host
    
    Write-Host ""
    Write-Host "NADAKKI AI VALIDATION MASTER SCRIPT" -ForegroundColor Cyan
    Write-Host ""
    
    $results = Execute-AllValidations
    $reportFile = Generate-ValidationReport $results
    
    Write-LogMessage "VALIDACION COMPLETADA" "SUCCESS"
    Write-Host ""
    
    Write-Host "RESUMEN FINAL:" -ForegroundColor Cyan
    Write-Host "  Total Validaciones: $($results.TotalChecks)" -ForegroundColor White
    Write-Host "  Pasadas: $($results.PassedChecks)" -ForegroundColor Green
    Write-Host "  Fallidas: $($results.TotalChecks - $results.PassedChecks)" -ForegroundColor Red
    
    $percentage = if ($results.TotalChecks -gt 0) { [math]::Round(($results.PassedChecks / $results.TotalChecks) * 100, 2) } else { 0 }
    Write-Host "  Tasa Exito: $percentage%" -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "Reporte: $reportFile" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $reportFile) {
        Start-Process $reportFile
    }
}

Main
