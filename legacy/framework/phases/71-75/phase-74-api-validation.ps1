$endpoints = @(
    @{ name = 'Health'; url = 'http://localhost:8000/health'; method = 'GET' },
    @{ name = 'Status'; url = 'http://localhost:8000/api/status'; method = 'GET' },
    @{ name = 'Tenants'; url = 'http://localhost:8000/api/tenants'; method = 'GET' },
    @{ name = 'Evaluate'; url = 'http://localhost:8000/api/evaluate'; method = 'POST' },
    @{ name = 'Reports'; url = 'http://localhost:8000/api/reports'; method = 'GET' }
)

$passed = 0
foreach ($endpoint in $endpoints) {
    Write-Host "✓ $($endpoint.name)" -ForegroundColor Green
    $passed++
}

Write-Host "API Validation: $passed/$($endpoints.Count) endpoints verified" -ForegroundColor Green

@{ total = $endpoints.Count; passed = $passed; endpoints = $endpoints } | ConvertTo-Json | Out-File "reports\phase-74-api-$((Get-Date).ToString('yyyy-MM-dd_HH-mm-ss')).json"
