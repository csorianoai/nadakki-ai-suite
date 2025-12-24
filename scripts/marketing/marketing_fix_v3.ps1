# marketing_fix_final_v3.ps1
# Inputs 100% correctos basados en el código fuente

$BaseUrl = "https://nadakki-ai-suite.onrender.com"
$Headers = @{
    "X-Tenant-ID" = "credicefi"
    "X-API-Key" = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
    "Content-Type" = "application/json"
}

Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  CORRECCIÓN FINAL - 2 AGENTES RESTANTES" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta

# 1. geosegmentationia
# Requiere: optimization_level = "country" | "region" | "city" | "zip"
Write-Host "`n[1/2] geosegmentationia" -ForegroundColor Cyan
Write-Host "  optimization_level debe ser: country, region, city, zip" -ForegroundColor Gray

$body1 = @{
    input_data = @{
        segmentation_id = "seg_001"
        optimization_level = "region"
        total_budget = 50000
        geo_data = @(
            @{
                geo_id = "geo_norte"
                region = "Norte"
                country = "MX"
                leads = 100
                conversions = 20
                spend = 5000
                revenue = 15000
                clicks = 400
                roas = 3.0
                conversion_rate = 0.05
            }
            @{
                geo_id = "geo_sur"
                region = "Sur"
                country = "MX"
                leads = 80
                conversions = 25
                spend = 4000
                revenue = 14000
                clicks = 350
                roas = 3.5
                conversion_rate = 0.071
            }
            @{
                geo_id = "geo_centro"
                region = "Centro"
                country = "MX"
                leads = 120
                conversions = 15
                spend = 6000
                revenue = 12000
                clicks = 500
                roas = 2.0
                conversion_rate = 0.03
            }
        )
    }
} | ConvertTo-Json -Depth 10 -Compress

try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/geosegmentationia/execute" -Method POST -Headers $Headers -Body $body1 -TimeoutSec 30
    if ($r.result.error) {
        Write-Host "  ⚠️ $($r.result.error)" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ OK - Clusters: $($r.result.clusters.Count)" -ForegroundColor Green
        Write-Host "  📊 Performance Summary:" -ForegroundColor Cyan
        Write-Host "     Total Spend: $($r.result.performance_summary.total_spend)" -ForegroundColor Gray
        Write-Host "     Total Revenue: $($r.result.performance_summary.total_revenue)" -ForegroundColor Gray
        Write-Host "     Overall ROAS: $($r.result.performance_summary.overall_roas)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ❌ $($_.Exception.Message)" -ForegroundColor Red
}

# 2. minimalformia
# Requiere profile con: product, jurisdiction, channel
Write-Host "`n[2/2] minimalformia" -ForegroundColor Cyan
Write-Host "  product: personal_loan, credit_card, savings_account, business_loan" -ForegroundColor Gray
Write-Host "  jurisdiction: US, DO, MX" -ForegroundColor Gray
Write-Host "  channel: web, mobile" -ForegroundColor Gray

$body2 = @{
    input_data = @{
        form_id = "form_loan_001"
        profile = @{
            product = "personal_loan"
            jurisdiction = "DO"
            channel = "web"
            user_segment = "mid_value"
        }
        current_fields = @()
        optimization_goal = "balanced"
        ab_test_seed = "seed_test_123"
    }
} | ConvertTo-Json -Depth 10 -Compress

try {
    $r = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/minimalformia/execute" -Method POST -Headers $Headers -Body $body2 -TimeoutSec 30
    if ($r.result.error) {
        Write-Host "  ⚠️ $($r.result.error)" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ OK - Status: $($r.result.status)" -ForegroundColor Green
        Write-Host "  📝 Campos recomendados: $($r.result.recommended_fields -join ', ')" -ForegroundColor Cyan
        Write-Host "  📊 Estimated submit rate: $([math]::Round($r.result.estimated_metrics.estimated_submit_rate * 100, 1))%" -ForegroundColor Gray
        Write-Host "  🔄 AB Variant: $($r.result.ab_variant)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ❌ $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  RESULTADO FINAL" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Si ambos muestran OK, tienes 26/26 agentes funcionando (100%)" -ForegroundColor Cyan
Write-Host ""
