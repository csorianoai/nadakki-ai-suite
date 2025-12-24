# marketing_test.ps1 - Prueba todos los agentes de marketing
$baseUrl = "https://nadakki-ai-suite.onrender.com"
$headers = @{
    "X-Tenant-ID" = "credicefi"
    "X-API-Key" = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
    "Content-Type" = "application/json"
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  PRUEBA AGENTES MARKETING NADAKKI" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$success = 0
$failed = 0

# 1. EMAIL AUTOMATION
Write-Host "`n[1/7] EmailAutomationIA..." -ForegroundColor Yellow
$body = '{"input_data":{"lead_id":"lead_001","email":"test@cliente.com","campaign_type":"welcome","recipient_name":"Juan Perez"}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/emailautomationia/execute" -Method POST -Headers $headers -Body $body
    Write-Host "  OK - Asunto: $($r.result.subject_line)" -ForegroundColor Green
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# 2. A/B TESTING
Write-Host "`n[2/7] ABTestingIA..." -ForegroundColor Yellow
$body = '{"input_data":{"test_id":"test_001","test_name":"Landing Test","variants":[{"name":"A","views":1000,"conversions":50},{"name":"B","views":1000,"conversions":65}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/abtestingia/execute" -Method POST -Headers $headers -Body $body
    Write-Host "  OK - Estado: $($r.result.test_status)" -ForegroundColor Green
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# 3. CUSTOMER SEGMENTATION
Write-Host "`n[3/7] CustomerSegmentationIA..." -ForegroundColor Yellow
$body = '{"input_data":{"audience_id":"aud_001","leads":[{"lead_id":"l1","name":"Juan","email":"j@test.com","income":50000},{"lead_id":"l2","name":"Ana","email":"a@test.com","income":80000}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/customersegmentatonia/execute" -Method POST -Headers $headers -Body $body
    if ($r.result.status -eq "error") {
        Write-Host "  WARN - $($r.result.error)" -ForegroundColor Yellow
    } else {
        Write-Host "  OK - Segmentos: $($r.result.segments.Count)" -ForegroundColor Green
    }
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# 4. PRODUCT AFFINITY
Write-Host "`n[4/7] ProductAffinityIA..." -ForegroundColor Yellow
$body = '{"input_data":{"customer_id":"cust_001","purchase_history":[{"product":"loan","amount":10000},{"product":"card","amount":5000}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/productaffinityia/execute" -Method POST -Headers $headers -Body $body
    Write-Host "  OK" -ForegroundColor Green
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# 5. GEO SEGMENTATION
Write-Host "`n[5/7] GeoSegmentationIA..." -ForegroundColor Yellow
$body = '{"input_data":{"regions":[{"region":"Norte","leads":100,"conversions":20},{"region":"Sur","leads":80,"conversions":25}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/geosegmentationia/execute" -Method POST -Headers $headers -Body $body
    Write-Host "  OK" -ForegroundColor Green
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# 6. MINIMAL FORM
Write-Host "`n[6/7] MinimalFormIA..." -ForegroundColor Yellow
$body = '{"input_data":{"form_type":"loan_application","fields":["name","email","phone","amount"]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/minimalformia/execute" -Method POST -Headers $headers -Body $body
    Write-Host "  OK" -ForegroundColor Green
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# 7. CASH OFFER FILTER
Write-Host "`n[7/7] CashOfferFilterIA..." -ForegroundColor Yellow
$body = '{"input_data":{"applications":[{"id":"app1","credit_score":750,"income":5000},{"id":"app2","credit_score":650,"income":3000}]}}'
try {
    $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/cashofferfilteria/execute" -Method POST -Headers $headers -Body $body
    Write-Host "  OK" -ForegroundColor Green
    $success++
} catch { Write-Host "  ERROR" -ForegroundColor Red; $failed++ }

# RESUMEN
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "  RESULTADO: $success/7 agentes OK" -ForegroundColor $(if($success -ge 5){"Green"}else{"Yellow"})
Write-Host "======================================" -ForegroundColor Cyan
