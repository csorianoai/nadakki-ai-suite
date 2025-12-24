# marketing_fix_final_v2.ps1
# Inputs EXACTOS basados en los errores específicos

$BaseUrl = "https://nadakki-ai-suite.onrender.com"
$Headers = @{
    "X-Tenant-ID" = "credicefi"
    "X-API-Key" = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
    "Content-Type" = "application/json"
}

Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  CORRECCIÓN DEFINITIVA - 4 AGENTES" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta

# 1. productaffinityia - necesita customer.income y customer.age
Write-Host "`n[1/4] productaffinityia" -ForegroundColor Cyan
Write-Host "  Requiere: customer.income, customer.age" -ForegroundColor Gray

$body1 = '{"input_data":{"customer_id":"cust_001","customer":{"customer_id":"cust_001","name":"Juan","email":"j@t.com","income":50000,"age":35},"purchase_history":[{"product":"loan","amount":10000}]}}'

try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/productaffinityia/execute" -Method POST -Headers $Headers -Body $body1 -TimeoutSec 30
    if ($r.result.error) { Write-Host "  ⚠️ $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  ✅ OK" -ForegroundColor Green }
} catch { Write-Host "  ❌ $($_.Exception.Message)" -ForegroundColor Red }

# 2. geosegmentationia - necesita optimization_level válido
Write-Host "`n[2/4] geosegmentationia" -ForegroundColor Cyan
Write-Host "  Requiere: optimization_level válido (no optimization_metric)" -ForegroundColor Gray

$body2 = '{"input_data":{"segmentation_id":"seg_001","geo_data":[{"region":"Norte","leads":100,"conversions":20},{"region":"Sur","leads":80,"conversions":25}],"optimization_level":"high"}}'

try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/geosegmentationia/execute" -Method POST -Headers $Headers -Body $body2 -TimeoutSec 30
    if ($r.result.error) { Write-Host "  ⚠️ $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  ✅ OK" -ForegroundColor Green }
} catch { Write-Host "  ❌ $($_.Exception.Message)" -ForegroundColor Red }

# 3. minimalformia - necesita product soportado
Write-Host "`n[3/4] minimalformia" -ForegroundColor Cyan
Write-Host "  Requiere: product válido (loan, card, etc)" -ForegroundColor Gray

$body3 = '{"input_data":{"form_id":"form_001","product":"personal_loan","profile":{"tenant_id":"credicefi","name":"Solicitud"},"fields":["name","email","phone"]}}'

try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/minimalformia/execute" -Method POST -Headers $Headers -Body $body3 -TimeoutSec 30
    if ($r.result.error) { Write-Host "  ⚠️ $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  ✅ OK" -ForegroundColor Green }
} catch { Write-Host "  ❌ $($_.Exception.Message)" -ForegroundColor Red }

# 4. cashofferfilteria - necesita customer.credit_score y customer.income
Write-Host "`n[4/4] cashofferfilteria" -ForegroundColor Cyan
Write-Host "  Requiere: customer.credit_score, customer.income" -ForegroundColor Gray

$body4 = '{"input_data":{"customer_id":"cust_001","customer":{"customer_id":"cust_001","name":"Roberto","credit_score":750,"income":8500},"applications":[{"id":"app1","amount":20000}]}}'

try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/cashofferfilteria/execute" -Method POST -Headers $Headers -Body $body4 -TimeoutSec 30
    if ($r.result.error) { Write-Host "  ⚠️ $($r.result.error)" -ForegroundColor Yellow }
    else { Write-Host "  ✅ OK" -ForegroundColor Green }
} catch { Write-Host "  ❌ $($_.Exception.Message)" -ForegroundColor Red }

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  PRUEBA COMPLETADA" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
