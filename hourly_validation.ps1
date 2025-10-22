$correctUrl = "https://6jbuszwhjd.execute-api.us-east-2.amazonaws.com/prod"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "[$timestamp] Validación horaria..." -ForegroundColor Cyan

$profile = @{
    client_id = "HOURLY_$(Get-Date -Format 'yyyyMMddHHmm')"
    income = 50000
    credit_score = 750
    age = 32
}

$json = $profile | ConvertTo-Json
$start = Get-Date

try {
    $response = Invoke-RestMethod -Uri "$correctUrl/api/v1/evaluate" -Method POST -Body $json -ContentType "application/json" -Headers @{"X-Tenant-ID" = "bank01"}
    $time = ((Get-Date) - $start).TotalMilliseconds
    
    $result = [PSCustomObject]@{
        Timestamp = $timestamp
        Success = $true
        ResponseTime = [math]::Round($time)
        Score = $response.quantum_similarity_score
        RiskLevel = $response.risk_level
        Source = $response.source
    }
    
    Write-Host "  OK - $([math]::Round($time))ms - $($response.risk_level)" -ForegroundColor Green
    
    # Guardar en log
    $result | Export-Csv "slo_validation_log.csv" -Append -NoTypeInformation
    
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
    
    [PSCustomObject]@{
        Timestamp = $timestamp
        Success = $false
        Error = $_.Exception.Message
    } | Export-Csv "slo_validation_log.csv" -Append -NoTypeInformation
}
