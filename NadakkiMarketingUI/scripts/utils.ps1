# ============================================================
# NADAKKI UTILS MODULE v1.0
# Funciones reutilizables para scripts de setup
# ============================================================

function Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$LogFile = $null
    )
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "$ts | $Level | $Message"
    
    if ($LogFile) {
        $logLine | Out-File -FilePath $LogFile -Append -Encoding UTF8
    }
    
    switch ($Level) {
        "OK"      { Write-Host $Message -ForegroundColor Green }
        "ERROR"   { Write-Host $Message -ForegroundColor Red }
        "WARNING" { Write-Host $Message -ForegroundColor Yellow }
        "INFO"    { Write-Host $Message -ForegroundColor Cyan }
        default   { Write-Host $Message }
    }
}

function Write-Banner {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 75) -ForegroundColor Magenta
    Write-Host "  $Text" -ForegroundColor Magenta
    Write-Host ("=" * 75) -ForegroundColor Magenta
    Write-Host ""
}

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host "--- $Text ---" -ForegroundColor Cyan
    Write-Host ""
}

function Check {
    param(
        [string]$Name,
        [bool]$Condition,
        [int]$CheckNum,
        [int]$TotalChecks,
        [string]$LogFile = $null
    )
    
    $status = if ($Condition) { "OK" } else { "FAIL" }
    $result = @{
        check = $CheckNum
        name = $Name
        status = $status
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
    
    if ($Condition) {
        Write-Host "[$CheckNum/$TotalChecks] OK   $Name" -ForegroundColor Green
        if ($LogFile) { Log -Message "[OK] $Name" -Level "OK" -LogFile $LogFile }
    } else {
        Write-Host "[$CheckNum/$TotalChecks] FAIL $Name" -ForegroundColor Red
        if ($LogFile) { Log -Message "[FAIL] $Name" -Level "ERROR" -LogFile $LogFile }
    }
    
    return $result
}

function Test-ApiEndpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            ContentType = "application/json"
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-RestMethod @params
        return @{ Success = $true; Data = $response; Error = $null }
    }
    catch {
        return @{ Success = $false; Data = $null; Error = $_.Exception.Message }
    }
}

function Get-ExecutionSummary {
    param(
        [datetime]$StartTime,
        [int]$Passed,
        [int]$Failed,
        [int]$Total
    )
    
    $duration = (Get-Date) - $StartTime
    $percentage = [math]::Round(($Passed / $Total) * 100, 2)
    
    return @{
        duration_seconds = [math]::Round($duration.TotalSeconds, 2)
        passed = $Passed
        failed = $Failed
        total = $Total
        percentage = $percentage
        status = if ($Failed -eq 0) { "SUCCESS" } else { "FAILED" }
    }
}

Export-ModuleMember -Function Log, Write-Banner, Write-Section, Check, Test-ApiEndpoint, Get-ExecutionSummary
