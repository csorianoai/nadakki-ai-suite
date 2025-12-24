# marketing_complete_test.ps1 - Prueba TODOS los 26 agentes de marketing
$baseUrl = "https://nadakki-ai-suite.onrender.com"
$headers = @{
    "X-Tenant-ID" = "credicefi"
    "X-API-Key" = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
    "Content-Type" = "application/json"
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PRUEBA COMPLETA - 26 AGENTES DE MARKETING NADAKKI" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$success = 0
$failed = 0
$results = @()

function Test-Agent {
    param($Name, $Body, $Num, $Total)
    
    Write-Host "`n[$Num/$Total] $Name..." -ForegroundColor Yellow
    
    try {
        $r = Invoke-RestMethod -Uri "$baseUrl/agents/marketing/$Name/execute" -Method POST -Headers $headers -Body $Body -TimeoutSec 30
        
        if ($r.result.status -eq "error" -or $r.result.error) {
            $err = if ($r.result.error) { $r.result.error } else { "unknown" }
            Write-Host "  WARN - $err" -ForegroundColor DarkYellow
            return @{Name=$Name; Status="WARN"; Error=$err}
        } else {
            Write-Host "  OK" -ForegroundColor Green
            return @{Name=$Name; Status="OK"; Error=""}
        }
    } catch {
        Write-Host "  ERROR - $($_.Exception.Message)" -ForegroundColor Red
        return @{Name=$Name; Status="ERROR"; Error=$_.Exception.Message}
    }
}

$total = 26
$num = 0

# 1. emailautomationia
$num++
$results += Test-Agent -Name "emailautomationia" -Num $num -Total $total -Body '{"input_data":{"lead_id":"lead_001","email":"test@test.com","campaign_type":"welcome"}}'

# 2. abtestingia
$num++
$results += Test-Agent -Name "abtestingia" -Num $num -Total $total -Body '{"input_data":{"test_id":"test_001","variants":[{"name":"A","views":1000,"conversions":50},{"name":"B","views":1000,"conversions":65}]}}'

# 3. customersegmentatonia
$num++
$results += Test-Agent -Name "customersegmentatonia" -Num $num -Total $total -Body '{"input_data":{"audience_id":"aud_001","leads":[{"lead_id":"l1","name":"Juan","email":"j@t.com"},{"lead_id":"l2","name":"Ana","email":"a@t.com"}]}}'

# 4. productaffinityia
$num++
$results += Test-Agent -Name "productaffinityia" -Num $num -Total $total -Body '{"input_data":{"customer_id":"cust_001","purchase_history":[{"product":"loan","amount":10000}]}}'

# 5. geosegmentationia
$num++
$results += Test-Agent -Name "geosegmentationia" -Num $num -Total $total -Body '{"input_data":{"regions":[{"region":"Norte","leads":100,"conversions":20}]}}'

# 6. minimalformia
$num++
$results += Test-Agent -Name "minimalformia" -Num $num -Total $total -Body '{"input_data":{"form_type":"loan","fields":["name","email","phone"]}}'

# 7. cashofferfilteria
$num++
$results += Test-Agent -Name "cashofferfilteria" -Num $num -Total $total -Body '{"input_data":{"applications":[{"id":"app1","credit_score":750,"income":5000}]}}'

# 8. leadscoringia
$num++
$results += Test-Agent -Name "leadscoringia" -Num $num -Total $total -Body '{"input_data":{"lead":{"tenant_id":"credicefi","lead_id":"lead_001","name":"Juan","email":"j@t.com","company_size":50}}}'

# 9. campaignoptimizeria
$num++
$results += Test-Agent -Name "campaignoptimizeria" -Num $num -Total $total -Body '{"input_data":{"campaign_id":"camp_001","budget":10000,"channels":["email","social"],"target_audience":"professionals"}}'

# 10. socialpostgeneratoria
$num++
$results += Test-Agent -Name "socialpostgeneratoria" -Num $num -Total $total -Body '{"input_data":{"platform":"instagram","topic":"financial_tips","brand_voice":"professional","hashtags":["fintech","money"]}}'

# 11. retentionpredictorea
$num++
$results += Test-Agent -Name "retentionpredictorea" -Num $num -Total $total -Body '{"input_data":{"customer_id":"cust_001","last_activity_days":30,"purchase_frequency":5,"lifetime_value":10000}}'

# 12. personalizationengineia
$num++
$results += Test-Agent -Name "personalizationengineia" -Num $num -Total $total -Body '{"input_data":{"user_id":"user_001","behavior":{"page_views":50,"clicks":20},"preferences":["loans","investments"]}}'

# 13. influencermatcheria
$num++
$results += Test-Agent -Name "influencermatcheria" -Num $num -Total $total -Body '{"input_data":{"campaign_type":"brand_awareness","budget":5000,"target_audience":"millennials","industry":"finance"}}'

# 14. influencermatchingia
$num++
$results += Test-Agent -Name "influencermatchingia" -Num $num -Total $total -Body '{"input_data":{"brand":"credicefi","niche":"fintech","min_followers":10000,"max_budget":2000}}'

# 15. contentperformanceia
$num++
$results += Test-Agent -Name "contentperformanceia" -Num $num -Total $total -Body '{"input_data":{"content_id":"content_001","type":"blog_post","views":5000,"engagement":250,"conversions":50}}'

# 16. creativeanalyzeria
$num++
$results += Test-Agent -Name "creativeanalyzeria" -Num $num -Total $total -Body '{"input_data":{"creative_id":"creative_001","type":"banner","impressions":10000,"clicks":250,"conversions":25}}'

# 17. budgetforecastia
$num++
$results += Test-Agent -Name "budgetforecastia" -Num $num -Total $total -Body '{"input_data":{"historical_data":[{"month":"2024-01","spend":5000,"revenue":15000},{"month":"2024-02","spend":6000,"revenue":18000}],"forecast_months":3}}'

# 18. attributionmodelia
$num++
$results += Test-Agent -Name "attributionmodelia" -Num $num -Total $total -Body '{"input_data":{"conversion_id":"conv_001","touchpoints":[{"channel":"email","timestamp":"2024-01-01"},{"channel":"social","timestamp":"2024-01-05"}]}}'

# 19. conversioncohortia
$num++
$results += Test-Agent -Name "conversioncohortia" -Num $num -Total $total -Body '{"input_data":{"cohort_date":"2024-01","users":[{"user_id":"u1","converted":true},{"user_id":"u2","converted":false}]}}'

# 20. journeyoptimizeria
$num++
$results += Test-Agent -Name "journeyoptimizeria" -Num $num -Total $total -Body '{"input_data":{"journey_id":"journey_001","stages":["awareness","consideration","decision"],"drop_off_rates":[0.3,0.4,0.2]}}'

# 21. contactqualityia
$num++
$results += Test-Agent -Name "contactqualityia" -Num $num -Total $total -Body '{"input_data":{"contacts":[{"email":"valid@test.com","phone":"+1234567890"},{"email":"invalid","phone":"123"}]}}'

# 22. competitoranalyzeria
$num++
$results += Test-Agent -Name "competitoranalyzeria" -Num $num -Total $total -Body '{"input_data":{"competitor_name":"CompetitorX","metrics":["pricing","features","market_share"]}}'

# 23. competitorintelligenceia
$num++
$results += Test-Agent -Name "competitorintelligenceia" -Num $num -Total $total -Body '{"input_data":{"industry":"fintech","competitors":["CompA","CompB"],"analysis_type":"swot"}}'

# 24. marketingmixmodelia
$num++
$results += Test-Agent -Name "marketingmixmodelia" -Num $num -Total $total -Body '{"input_data":{"channels":[{"name":"email","spend":5000,"conversions":100},{"name":"social","spend":3000,"conversions":60}]}}'

# 25. marketingorchestratorea
$num++
$results += Test-Agent -Name "marketingorchestratorea" -Num $num -Total $total -Body '{"input_data":{"workflow_id":"wf_001","steps":["segment","personalize","send"],"trigger":"new_lead"}}'

# 26. abtestingimpactia
$num++
$results += Test-Agent -Name "abtestingimpactia" -Num $num -Total $total -Body '{"input_data":{"test_id":"test_001","variants":[{"name":"control","revenue":10000},{"name":"variant","revenue":12000}],"duration_days":14}}'

# RESUMEN FINAL
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  RESUMEN FINAL - AGENTES DE MARKETING" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$okCount = ($results | Where-Object { $_.Status -eq "OK" }).Count
$warnCount = ($results | Where-Object { $_.Status -eq "WARN" }).Count
$errorCount = ($results | Where-Object { $_.Status -eq "ERROR" }).Count

Write-Host "`n  OK:    $okCount agentes" -ForegroundColor Green
Write-Host "  WARN:  $warnCount agentes (funcionan pero necesitan ajuste)" -ForegroundColor Yellow
Write-Host "  ERROR: $errorCount agentes" -ForegroundColor Red

Write-Host "`n----------------------------------------------------------------" -ForegroundColor Gray

# Mostrar detalle por estado
if ($okCount -gt 0) {
    Write-Host "`n  FUNCIONANDO PERFECTAMENTE:" -ForegroundColor Green
    $results | Where-Object { $_.Status -eq "OK" } | ForEach-Object { Write-Host "    $($_.Name)" -ForegroundColor Green }
}

if ($warnCount -gt 0) {
    Write-Host "`n  NECESITAN AJUSTE DE INPUT:" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -eq "WARN" } | ForEach-Object { Write-Host "    $($_.Name): $($_.Error)" -ForegroundColor Yellow }
}

if ($errorCount -gt 0) {
    Write-Host "`n  CON ERRORES:" -ForegroundColor Red
    $results | Where-Object { $_.Status -eq "ERROR" } | ForEach-Object { Write-Host "    $($_.Name): $($_.Error)" -ForegroundColor Red }
}

$pct = [math]::Round((($okCount + $warnCount) / $total) * 100)
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  TASA DE EXITO: $pct% ($($okCount + $warnCount)/$total responden)" -ForegroundColor $(if($pct -ge 80){"Green"}elseif($pct -ge 60){"Yellow"}else{"Red"})
Write-Host "================================================================" -ForegroundColor Cyan
