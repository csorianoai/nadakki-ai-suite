# marketing_evaluation_scoring.ps1
# Evaluación profesional con puntuación 0-100 para cada agente

$BaseUrl = "https://nadakki-ai-suite.onrender.com"
$TenantId = "credicefi"
$ApiKey = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
$Headers = @{
    "X-Tenant-ID" = $TenantId
    "X-API-Key" = $ApiKey
    "Content-Type" = "application/json"
}

$OutputFile = "marketing_evaluation_scores_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# =============================================================================
# DEFINICIÓN DE AGENTES CON FUNCIÓN, INPUT CORRECTO Y CRITERIOS DE EVALUACIÓN
# =============================================================================
$AgentDefinitions = @(
    @{
        Id = "emailautomationia"
        Function = "Genera emails personalizados con IA, optimiza subject lines, determina mejor hora de envío"
        Category = "Email Marketing"
        Complexity = "Alta"
        Input = @{ input_data = @{ lead_id = "lead_001"; email = "test@test.com"; campaign_type = "welcome"; recipient_name = "Juan" } }
        ExpectedFields = @("subject_line", "optimal_send_time", "estimated_open_rate")
    },
    @{
        Id = "abtestingia"
        Function = "Analiza experimentos A/B con significancia estadística, determina ganador y recomienda acciones"
        Category = "Optimization"
        Complexity = "Alta"
        Input = @{ input_data = @{ test_id = "test_001"; variants = @(@{ name = "A"; views = 1000; conversions = 50 }, @{ name = "B"; views = 1000; conversions = 65 }) } }
        ExpectedFields = @("test_status", "recommendation", "alpha")
    },
    @{
        Id = "customersegmentatonia"
        Function = "Segmenta clientes usando RFM y ML, identifica grupos de alto valor"
        Category = "Segmentation"
        Complexity = "Alta"
        Input = @{ input_data = @{ audience_id = "aud_001"; leads = @(@{ lead_id = "l1"; name = "Juan"; email = "j@t.com" }, @{ lead_id = "l2"; name = "Ana"; email = "a@t.com" }) } }
        ExpectedFields = @("segments")
    },
    @{
        Id = "leadscoringia"
        Function = "Califica leads con scoring predictivo basado en comportamiento e interacciones"
        Category = "Lead Management"
        Complexity = "Alta"
        Input = @{ input_data = @{ lead = @{ tenant_id = "credicefi"; lead_id = "lead_001"; name = "Juan"; email = "j@t.com"; company_size = 50 } } }
        ExpectedFields = @("score", "classification")
    },
    @{
        Id = "campaignoptimizeria"
        Function = "Optimiza campañas multicanal, ajusta presupuestos y recomienda mejoras"
        Category = "Campaign Management"
        Complexity = "Alta"
        Input = @{ input_data = @{ campaign_id = "camp_001"; budget = 10000; channels = @("email", "social"); target_audience = "professionals" } }
        ExpectedFields = @("recommendations", "optimized_budget")
    },
    @{
        Id = "socialpostgeneratoria"
        Function = "Genera contenido optimizado para redes sociales según plataforma y audiencia"
        Category = "Content"
        Complexity = "Media"
        Input = @{ input_data = @{ platform = "instagram"; topic = "financial_tips"; brand_voice = "professional"; hashtags = @("fintech") } }
        ExpectedFields = @("posts", "best_time_to_post")
    },
    @{
        Id = "retentionpredictorea"
        Function = "Predice probabilidad de churn y recomienda acciones de retención"
        Category = "Analytics"
        Complexity = "Alta"
        Input = @{ input_data = @{ customer_id = "cust_001"; last_activity_days = 30; purchase_frequency = 5; lifetime_value = 10000 } }
        ExpectedFields = @("churn_probability", "retention_actions")
    },
    @{
        Id = "personalizationengineia"
        Function = "Motor de personalización en tiempo real basado en comportamiento del usuario"
        Category = "Personalization"
        Complexity = "Alta"
        Input = @{ input_data = @{ user_id = "user_001"; behavior = @{ page_views = 50; clicks = 20 }; preferences = @("loans") } }
        ExpectedFields = @("personalized_content", "recommendations")
    },
    @{
        Id = "influencermatcheria"
        Function = "Encuentra influencers ideales para campañas según audiencia y presupuesto"
        Category = "Influencer Marketing"
        Complexity = "Media"
        Input = @{ input_data = @{ campaign_type = "brand_awareness"; budget = 5000; target_audience = "millennials"; industry = "finance" } }
        ExpectedFields = @("influencers", "match_score")
    },
    @{
        Id = "influencermatchingia"
        Function = "Matching avanzado de influencers con análisis de engagement y ROI esperado"
        Category = "Influencer Marketing"
        Complexity = "Media"
        Input = @{ input_data = @{ brand = "credicefi"; niche = "fintech"; min_followers = 10000; max_budget = 2000 } }
        ExpectedFields = @("matches", "engagement_rate")
    },
    @{
        Id = "contentperformanceia"
        Function = "Analiza rendimiento de contenido, identifica top performers y áreas de mejora"
        Category = "Analytics"
        Complexity = "Media"
        Input = @{ input_data = @{ content_id = "content_001"; channel = "blog"; views = 5000; engagement = 250; conversions = 50 } }
        ExpectedFields = @("performance_score", "recommendations")
    },
    @{
        Id = "creativeanalyzeria"
        Function = "Analiza creatividades publicitarias, mide efectividad y sugiere optimizaciones"
        Category = "Creative"
        Complexity = "Media"
        Input = @{ input_data = @{ creative_id = "creative_001"; type = "banner"; impressions = 10000; clicks = 250; conversions = 25 } }
        ExpectedFields = @("effectiveness_score", "suggestions")
    },
    @{
        Id = "budgetforecastia"
        Function = "Proyecta presupuestos de marketing basado en históricos y objetivos"
        Category = "Finance"
        Complexity = "Alta"
        Input = @{ input_data = @{ historical_data = @(@{ month = "2024-01"; spend = 5000; revenue = 15000 }); forecast_months = 3 } }
        ExpectedFields = @("forecast", "recommended_budget")
    },
    @{
        Id = "attributionmodelia"
        Function = "Atribución multicanal avanzada, asigna crédito a touchpoints de conversión"
        Category = "Analytics"
        Complexity = "Alta"
        Input = @{ input_data = @{ conversion_id = "conv_001"; touchpoints = @(@{ channel = "email"; timestamp = "2024-01-01" }, @{ channel = "social"; timestamp = "2024-01-05" }) } }
        ExpectedFields = @("attribution", "channel_weights")
    },
    @{
        Id = "conversioncohortia"
        Function = "Análisis de cohortes de conversión, tracking de retención por grupo"
        Category = "Analytics"
        Complexity = "Alta"
        Input = @{ input_data = @{ cohort_date = "2024-01"; users = @(@{ user_id = "u1"; converted = $true }, @{ user_id = "u2"; converted = $false }) } }
        ExpectedFields = @("cohort_analysis", "conversion_rate")
    },
    @{
        Id = "journeyoptimizeria"
        Function = "Optimiza customer journey, reduce drop-offs y mejora conversión por etapa"
        Category = "Customer Experience"
        Complexity = "Alta"
        Input = @{ input_data = @{ journey_id = "journey_001"; stages = @("awareness", "consideration", "decision"); drop_off_rates = @(0.3, 0.4, 0.2) } }
        ExpectedFields = @("optimized_journey", "recommendations")
    },
    @{
        Id = "contactqualityia"
        Function = "Valida calidad de contactos, detecta emails/teléfonos inválidos"
        Category = "Data Quality"
        Complexity = "Baja"
        Input = @{ input_data = @{ contacts = @(@{ email = "valid@test.com"; phone = "+1234567890" }, @{ email = "invalid"; phone = "123" }) } }
        ExpectedFields = @("valid_contacts", "invalid_contacts", "quality_score")
    },
    @{
        Id = "competitoranalyzeria"
        Function = "Analiza competidores, compara precios, features y posicionamiento"
        Category = "Competitive Intelligence"
        Complexity = "Media"
        Input = @{ input_data = @{ competitor_name = "CompetitorX"; metrics = @("pricing", "features", "market_share") } }
        ExpectedFields = @("analysis", "competitive_position")
    },
    @{
        Id = "competitorintelligenceia"
        Function = "Inteligencia competitiva avanzada con análisis SWOT y tendencias"
        Category = "Competitive Intelligence"
        Complexity = "Alta"
        Input = @{ input_data = @{ industry = "fintech"; competitors = @("CompA", "CompB"); analysis_type = "swot" } }
        ExpectedFields = @("swot", "market_trends")
    },
    @{
        Id = "marketingmixmodelia"
        Function = "Modelo de marketing mix (MMM), optimiza distribución de presupuesto por canal"
        Category = "Analytics"
        Complexity = "Alta"
        Input = @{ input_data = @{ channels = @(@{ name = "email"; spend = 5000; conversions = 100 }, @{ name = "social"; spend = 3000; conversions = 60 }) } }
        ExpectedFields = @("optimal_mix", "roi_by_channel")
    },
    @{
        Id = "marketingorchestratorea"
        Function = "Orquesta workflows de marketing automatizados, coordina agentes"
        Category = "Automation"
        Complexity = "Alta"
        Input = @{ input_data = @{ workflow_id = "wf_001"; steps = @("segment", "personalize", "send"); trigger = "new_lead" } }
        ExpectedFields = @("workflow_status", "next_actions")
    },
    @{
        Id = "abtestingimpactia"
        Function = "Mide impacto de tests A/B en revenue y métricas de negocio"
        Category = "Optimization"
        Complexity = "Alta"
        Input = @{ input_data = @{ test_id = "test_001"; variants = @(@{ name = "control"; revenue = 10000 }, @{ name = "variant"; revenue = 12000 }); duration_days = 14 } }
        ExpectedFields = @("impact_analysis", "revenue_lift")
    },
    @{
        Id = "productaffinityia"
        Function = "Analiza afinidad de productos, recomienda cross-sell y up-sell"
        Category = "Recommendations"
        Complexity = "Alta"
        Input = @{ input_data = @{ customer_id = "cust_001"; customer = @{ customer_id = "cust_001"; name = "Juan"; email = "j@t.com"; income = 50000; age = 35 }; purchase_history = @(@{ product = "loan"; amount = 10000 }) } }
        ExpectedFields = @("recommendations", "affinity_score")
    },
    @{
        Id = "geosegmentationia"
        Function = "Segmentación geográfica, detecta clusters por performance regional"
        Category = "Segmentation"
        Complexity = "Alta"
        Input = @{ input_data = @{ segmentation_id = "seg_001"; optimization_level = "region"; total_budget = 50000; geo_data = @(@{ geo_id = "g1"; region = "Norte"; roas = 3.0; conversion_rate = 0.05; spend = 5000; revenue = 15000; clicks = 400 }) } }
        ExpectedFields = @("clusters", "budget_allocations", "performance_summary")
    },
    @{
        Id = "minimalformia"
        Function = "Optimiza formularios de captación, reduce fricción y mejora conversión"
        Category = "Lead Capture"
        Complexity = "Alta"
        Input = @{ input_data = @{ form_id = "form_001"; profile = @{ product = "personal_loan"; jurisdiction = "DO"; channel = "web" }; current_fields = @(); optimization_goal = "balanced" } }
        ExpectedFields = @("recommended_fields", "estimated_metrics", "compliance")
    },
    @{
        Id = "cashofferfilteria"
        Function = "Filtra y prioriza ofertas de crédito según perfil de riesgo"
        Category = "Credit"
        Complexity = "Alta"
        Input = @{ input_data = @{ customer_id = "cust_001"; customer = @{ customer_id = "cust_001"; name = "Roberto"; credit_score = 750; income = 8500 }; applications = @(@{ id = "app1"; amount = 20000 }) } }
        ExpectedFields = @("filtered_offers", "risk_assessment")
    }
)

# =============================================================================
# FUNCIÓN DE EVALUACIÓN Y PUNTUACIÓN
# =============================================================================
function Evaluate-Agent {
    param (
        [hashtable]$AgentDef
    )
    
    $agentId = $AgentDef.Id
    $startTime = Get-Date
    
    try {
        $body = $AgentDef.Input | ConvertTo-Json -Depth 10 -Compress
        $response = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/$agentId/execute" -Method POST -Headers $Headers -Body $body -TimeoutSec 30
        $latency = ((Get-Date) - $startTime).TotalMilliseconds
        
        # Calcular puntuación
        $score = Calculate-Score -Response $response -AgentDef $AgentDef -Latency $latency
        
        return @{
            agent_id = $agentId
            function = $AgentDef.Function
            category = $AgentDef.Category
            complexity = $AgentDef.Complexity
            status = "evaluated"
            latency_ms = [math]::Round($latency)
            score = $score
            response = $response.result
            needs_retraining = $score.total -lt 70
        }
    }
    catch {
        return @{
            agent_id = $agentId
            function = $AgentDef.Function
            category = $AgentDef.Category
            complexity = $AgentDef.Complexity
            status = "failed"
            latency_ms = 0
            score = @{ total = 0; breakdown = @{} }
            error = $_.Exception.Message
            needs_retraining = $true
        }
    }
}

function Calculate-Score {
    param (
        $Response,
        [hashtable]$AgentDef,
        [double]$Latency
    )
    
    $breakdown = @{}
    
    # 1. Funcionalidad (40 puntos) - ¿Responde sin error?
    if ($Response.result.error -or $Response.result.status -eq "error") {
        $breakdown["functionality"] = 0
    } else {
        $breakdown["functionality"] = 40
    }
    
    # 2. Completitud (25 puntos) - ¿Tiene los campos esperados?
    $expectedFields = $AgentDef.ExpectedFields
    $resultKeys = @()
    if ($Response.result -is [PSCustomObject]) {
        $resultKeys = $Response.result.PSObject.Properties.Name
    }
    $foundFields = ($expectedFields | Where-Object { $_ -in $resultKeys }).Count
    $completeness = if ($expectedFields.Count -gt 0) { $foundFields / $expectedFields.Count } else { 1 }
    $breakdown["completeness"] = [math]::Round($completeness * 25)
    
    # 3. Performance (20 puntos) - Latencia
    if ($Latency -lt 300) { $breakdown["performance"] = 20 }
    elseif ($Latency -lt 500) { $breakdown["performance"] = 15 }
    elseif ($Latency -lt 1000) { $breakdown["performance"] = 10 }
    elseif ($Latency -lt 2000) { $breakdown["performance"] = 5 }
    else { $breakdown["performance"] = 0 }
    
    # 4. Robustez (15 puntos) - ¿Tiene version, tenant_id, decision_trace?
    $robustnessFields = @("version", "tenant_id", "latency_ms")
    $robustnessFound = ($robustnessFields | Where-Object { $_ -in $resultKeys }).Count
    $breakdown["robustness"] = [math]::Round(($robustnessFound / 3) * 15)
    
    $total = $breakdown.Values | Measure-Object -Sum | Select-Object -ExpandProperty Sum
    
    return @{
        total = [math]::Min(100, $total)
        breakdown = $breakdown
        grade = Get-Grade -Score $total
    }
}

function Get-Grade {
    param ([int]$Score)
    
    if ($Score -ge 90) { return "A+" }
    elseif ($Score -ge 85) { return "A" }
    elseif ($Score -ge 80) { return "B+" }
    elseif ($Score -ge 75) { return "B" }
    elseif ($Score -ge 70) { return "C+" }
    elseif ($Score -ge 65) { return "C" }
    elseif ($Score -ge 60) { return "D" }
    else { return "F" }
}

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  EVALUACIÓN Y PUNTUACIÓN DE AGENTES DE MARKETING" -ForegroundColor Magenta
Write-Host "  Criterios: Funcionalidad, Completitud, Performance, Robustez" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  Tenant: $TenantId" -ForegroundColor Gray
Write-Host "  Total agentes: $($AgentDefinitions.Count)" -ForegroundColor Gray
Write-Host "================================================================" -ForegroundColor Magenta

$Results = @()
$index = 0

foreach ($agentDef in $AgentDefinitions) {
    $index++
    Write-Host "`n[$index/$($AgentDefinitions.Count)] $($agentDef.Id)" -ForegroundColor Cyan
    
    $result = Evaluate-Agent -AgentDef $agentDef
    $Results += $result
    
    $color = if ($result.score.total -ge 80) { "Green" } elseif ($result.score.total -ge 70) { "Yellow" } else { "Red" }
    $icon = if ($result.needs_retraining) { "⚠️" } else { "✅" }
    
    Write-Host "  $icon Score: $($result.score.total)/100 ($($result.score.grade)) | Latency: $($result.latency_ms)ms" -ForegroundColor $color
    Write-Host "     Función: $($result.function.Substring(0, [Math]::Min(70, $result.function.Length)))..." -ForegroundColor Gray
    
    Start-Sleep -Milliseconds 300
}

# =============================================================================
# RESUMEN Y ANÁLISIS
# =============================================================================
Write-Host "`n================================================================" -ForegroundColor Magenta
Write-Host "  📊 RESUMEN DE EVALUACIÓN" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta

$avgScore = [math]::Round(($Results | Measure-Object -Property { $_.score.total } -Average).Average)
$needsRetraining = $Results | Where-Object { $_.needs_retraining -eq $true }
$topPerformers = $Results | Sort-Object { $_.score.total } -Descending | Select-Object -First 5
$lowPerformers = $Results | Sort-Object { $_.score.total } | Select-Object -First 5

Write-Host ""
Write-Host "  📈 PUNTUACIÓN PROMEDIO: $avgScore/100" -ForegroundColor $(if($avgScore -ge 80){"Green"}elseif($avgScore -ge 70){"Yellow"}else{"Red"})
Write-Host ""

# Por categoría
Write-Host "  POR CATEGORÍA:" -ForegroundColor White
$categories = $Results | Group-Object -Property category
foreach ($cat in ($categories | Sort-Object { ($_.Group | Measure-Object -Property { $_.score.total } -Average).Average } -Descending)) {
    $catAvg = [math]::Round(($cat.Group | Measure-Object -Property { $_.score.total } -Average).Average)
    Write-Host "    $($cat.Name): $catAvg/100" -ForegroundColor $(if($catAvg -ge 80){"Green"}elseif($catAvg -ge 70){"Yellow"}else{"Red"})
}

Write-Host ""
Write-Host "  🏆 TOP 5 PERFORMERS:" -ForegroundColor Green
foreach ($agent in $topPerformers) {
    Write-Host "    $($agent.score.total)/100 - $($agent.agent_id) ($($agent.score.grade))" -ForegroundColor Green
}

if ($needsRetraining.Count -gt 0) {
    Write-Host ""
    Write-Host "  ⚠️ NECESITAN REENTRENAMIENTO ($($needsRetraining.Count)):" -ForegroundColor Yellow
    foreach ($agent in $needsRetraining) {
        Write-Host "    $($agent.score.total)/100 - $($agent.agent_id)" -ForegroundColor Yellow
        Write-Host "       → $($agent.function.Substring(0, [Math]::Min(60, $agent.function.Length)))..." -ForegroundColor DarkYellow
    }
} else {
    Write-Host ""
    Write-Host "  ✅ TODOS LOS AGENTES ESTÁN BIEN ENTRENADOS" -ForegroundColor Green
}

# =============================================================================
# TABLA COMPLETA DE FUNCIONES
# =============================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  📋 FUNCIÓN DE CADA AGENTE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$Results | Sort-Object { $_.score.total } -Descending | ForEach-Object {
    $icon = if ($_.score.total -ge 80) { "🟢" } elseif ($_.score.total -ge 70) { "🟡" } else { "🔴" }
    Write-Host ""
    Write-Host "  $icon $($_.agent_id) [$($_.score.total)/100]" -ForegroundColor White
    Write-Host "     Categoría: $($_.category) | Complejidad: $($_.complexity)" -ForegroundColor Gray
    Write-Host "     Función: $($_.function)" -ForegroundColor Cyan
}

# =============================================================================
# GUARDAR RESULTADOS
# =============================================================================
$output = @{
    evaluation_date = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    tenant_id = $TenantId
    summary = @{
        total_agents = $Results.Count
        average_score = $avgScore
        needs_retraining = $needsRetraining.Count
        top_performer = $topPerformers[0].agent_id
        top_score = $topPerformers[0].score.total
    }
    agents = $Results | ForEach-Object {
        @{
            agent_id = $_.agent_id
            function = $_.function
            category = $_.category
            complexity = $_.complexity
            score = $_.score.total
            grade = $_.score.grade
            breakdown = $_.score.breakdown
            latency_ms = $_.latency_ms
            needs_retraining = $_.needs_retraining
        }
    }
}

$output | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  💾 RESULTADOS GUARDADOS: $OutputFile" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
