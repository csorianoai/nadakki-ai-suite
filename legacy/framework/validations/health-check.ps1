param([string]$Endpoint = "http://localhost:8000/health")
try {
    $response = Invoke-RestMethod -Uri $Endpoint -TimeoutSec 5
    Write-Host "✓ Health Check OK" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "✗ Health Check FAILED" -ForegroundColor Red
    exit 1
}
