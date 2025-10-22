# TEST ALL NADAKKI API GATEWAYS
Write-Host "?? TESTING ALL NADAKKI API GATEWAYS" -ForegroundColor Cyan
Write-Host "=" * 50

$apis = @(
    @{id="kjxnzc5b6e"; name="nadakki-ai-suite-fixed"; priority="HIGH"},
    @{id="v5mi0idfy0"; name="nadakki-ai-suite-v2"; priority="MEDIUM"},
    @{id="1pbo8cc92k"; name="nadakki-api"; priority="LOW"},
    @{id="fdnmgx4rz7"; name="nadakki-api-backup"; priority="BACKUP"}
)

foreach ($api in $apis) {
    $baseUrl = "https://$($api.id).execute-api.us-east-2.amazonaws.com/prod"
    Write-Host "`n?? Testing API: $($api.name) [$($api.priority)]" -ForegroundColor Yellow
    Write-Host "URL: $baseUrl" -ForegroundColor Gray
    
    try {
        $healthResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -Method GET -TimeoutSec 10
        Write-Host "? HEALTH CHECK EXITOSO!" -ForegroundColor Green
        Write-Host "Response: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor White
        
        # Test evaluación básica
        $testData = @{
            profile = @{
                income = 50000
                credit_score = 750
                age = 35
            }
        } | ConvertTo-Json
        
        $evalResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/evaluate" -Method POST -Body $testData -ContentType "application/json" -TimeoutSec 10
        Write-Host "? EVALUACIÓN EXITOSA!" -ForegroundColor Green
        Write-Host "Result: $($evalResponse | ConvertTo-Json -Compress)" -ForegroundColor White
        
        Write-Host "?? API FUNCIONANDO: $($api.id)" -ForegroundColor Magenta
        break
        
    } catch {
        Write-Host "? Error: $_" -ForegroundColor Red
    }
}
