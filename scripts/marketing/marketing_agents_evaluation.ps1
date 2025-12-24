# marketing_agents_evaluation.ps1
# Evaluación completa de todos los agentes de marketing con salida JSON

# =========================
# CONFIGURACIÓN
# =========================
$BaseUrl   = "https://nadakki-ai-suite.onrender.com"
$TenantId  = "credicefi"
$ApiKey    = "nadakki_klbJUiJetf-5hH1rpCsLfqRIHPdirm0gUajAUkxov8I"
$Headers = @{
    "X-Tenant-ID"  = $TenantId
    "X-API-Key"    = $ApiKey
    "Content-Type" = "application/json"
}
$OutputFile = "marketing_agents_evaluation_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$Results = @()

# =========================
# DEFINICIÓN DE AGENTES CON INPUTS CORRECTOS
# =========================
$AgentDefinitions = @(
    @{
        Name = "emailautomationia"
        Description = "Genera emails personalizados con IA"
        Category = "Email Marketing"
        Input = @{
            input_data = @{
                lead_id = "lead_001"
                email = "cliente@empresa.com"
                campaign_type = "welcome"
                recipient_name = "Juan Pérez"
                variables = @{
                    offer = "15% descuento"
                    product = "Préstamo Personal"
                }
            }
        }
    },
    @{
        Name = "abtestingia"
        Description = "Analiza experimentos A/B con significancia estadística"
        Category = "Optimization"
        Input = @{
            input_data = @{
                test_id = "test_001"
                test_name = "Landing Page Test"
                variants = @(
                    @{ name = "Control"; views = 1000; conversions = 50; revenue = 5000 },
                    @{ name = "Variante B"; views = 1000; conversions = 65; revenue = 6500 }
                )
                confidence_level = 0.95
            }
        }
    },
    @{
        Name = "customersegmentatonia"
        Description = "Segmenta clientes usando RFM y machine learning"
        Category = "Segmentation"
        Input = @{
            input_data = @{
                audience_id = "aud_001"
                leads = @(
                    @{ lead_id = "l1"; name = "Juan"; email = "juan@test.com"; income = 50000 },
                    @{ lead_id = "l2"; name = "Ana"; email = "ana@test.com"; income = 80000 }
                )
                segmentation_type = "rfm"
            }
        }
    },
    @{
        Name = "leadscoringia"
        Description = "Califica leads con scoring predictivo"
        Category = "Lead Management"
        Input = @{
            input_data = @{
                lead = @{
                    tenant_id = "credicefi"
                    lead_id = "lead_001"
                    name = "Juan Pérez"
                    email = "juan@empresa.com"
                    company_size = 50
                    industry = "technology"
                }
            }
        }
    },
    @{
        Name = "campaignoptimizeria"
        Description = "Optimiza campañas multicanal con IA"
        Category = "Campaign Management"
        Input = @{
            input_data = @{
                campaign_id = "camp_001"
                budget = 10000
                channels = @("email", "social", "display")
                target_audience = "professionals"
                objective = "conversions"
            }
        }
    },
    @{
        Name = "socialpostgeneratoria"
        Description = "Genera contenido para redes sociales"
        Category = "Content"
        Input = @{
            input_data = @{
                platform = "instagram"
                topic = "financial_tips"
                brand_voice = "professional"
                hashtags = @("fintech", "money", "savings")
                post_type = "carousel"
            }
        }
    },
    @{
        Name = "retentionpredictorea"
        Description = "Predice churn y retención de clientes"
        Category = "Analytics"
        Input = @{
            input_data = @{
                customer_id = "cust_001"
                last_activity_days = 30
                purchase_frequency = 5
                lifetime_value = 10000
                support_tickets = 2
            }
        }
    },
    @{
        Name = "personalizationengineia"
        Description = "Motor de personalización en tiempo real"
        Category = "Personalization"
        Input = @{
            input_data = @{
                user_id = "user_001"
                behavior = @{ page_views = 50; clicks = 20; time_on_site = 300 }
                preferences = @("loans", "investments")
                context = @{ device = "mobile"; location = "LATAM" }
            }
        }
    },
    @{
        Name = "influencermatcheria"
        Description = "Encuentra influencers ideales para campañas"
        Category = "Influencer Marketing"
        Input = @{
            input_data = @{
                campaign_type = "brand_awareness"
                budget = 5000
                target_audience = "millennials"
                industry = "finance"
                min_engagement_rate = 0.03
            }
        }
    },
    @{
        Name = "influencermatchingia"
        Description = "Matching avanzado de influencers"
        Category = "Influencer Marketing"
        Input = @{
            input_data = @{
                brand = "credicefi"
                niche = "fintech"
                min_followers = 10000
                max_budget = 2000
                platforms = @("instagram", "tiktok")
            }
        }
    },
    @{
        Name = "contentperformanceia"
        Description = "Analiza rendimiento de contenido"
        Category = "Analytics"
        Input = @{
            input_data = @{
                content_id = "content_001"
                channel = "blog"
                views = 5000
                engagement = 250
                conversions = 50
                time_period = "30d"
            }
        }
    },
    @{
        Name = "creativeanalyzeria"
        Description = "Analiza creatividades publicitarias"
        Category = "Creative"
        Input = @{
            input_data = @{
                creative_id = "creative_001"
                type = "banner"
                impressions = 10000
                clicks = 250
                conversions = 25
                cost = 500
            }
        }
    },
    @{
        Name = "budgetforecastia"
        Description = "Proyecta presupuestos de marketing"
        Category = "Finance"
        Input = @{
            input_data = @{
                historical_data = @(
                    @{ month = "2024-01"; spend = 5000; revenue = 15000 },
                    @{ month = "2024-02"; spend = 6000; revenue = 18000 },
                    @{ month = "2024-03"; spend = 7000; revenue = 22000 }
                )
                forecast_months = 3
                growth_target = 0.15
            }
        }
    },
    @{
        Name = "attributionmodelia"
        Description = "Atribución multicanal avanzada"
        Category = "Analytics"
        Input = @{
            input_data = @{
                conversion_id = "conv_001"
                touchpoints = @(
                    @{ channel = "email"; timestamp = "2024-01-01T10:00:00Z" },
                    @{ channel = "social"; timestamp = "2024-01-05T14:00:00Z" },
                    @{ channel = "direct"; timestamp = "2024-01-07T09:00:00Z" }
                )
                model = "time_decay"
            }
        }
    },
    @{
        Name = "conversioncohortia"
        Description = "Análisis de cohortes de conversión"
        Category = "Analytics"
        Input = @{
            input_data = @{
                cohort_date = "2024-01"
                users = @(
                    @{ user_id = "u1"; signup_date = "2024-01-01"; converted = $true; conversion_date = "2024-01-15" },
                    @{ user_id = "u2"; signup_date = "2024-01-02"; converted = $false }
                )
                analysis_period = "90d"
            }
        }
    },
    @{
        Name = "journeyoptimizeria"
        Description = "Optimiza customer journey"
        Category = "Customer Experience"
        Input = @{
            input_data = @{
                journey_id = "journey_001"
                stages = @("awareness", "consideration", "decision", "purchase")
                drop_off_rates = @(0.3, 0.4, 0.2, 0.1)
                optimization_goal = "reduce_dropoff"
            }
        }
    },
    @{
        Name = "contactqualityia"
        Description = "Valida calidad de contactos"
        Category = "Data Quality"
        Input = @{
            input_data = @{
                contacts = @(
                    @{ email = "valid@empresa.com"; phone = "+1234567890"; name = "Juan" },
                    @{ email = "invalid-email"; phone = "123"; name = "" }
                )
                validation_rules = @("email", "phone", "completeness")
            }
        }
    },
    @{
        Name = "competitoranalyzeria"
        Description = "Analiza competidores"
        Category = "Competitive Intelligence"
        Input = @{
            input_data = @{
                competitor_name = "CompetitorX"
                metrics = @("pricing", "features", "market_share", "sentiment")
                sources = @("social", "reviews", "news")
            }
        }
    },
    @{
        Name = "competitorintelligenceia"
        Description = "Inteligencia competitiva avanzada"
        Category = "Competitive Intelligence"
        Input = @{
            input_data = @{
                industry = "fintech"
                competitors = @("BankA", "FintechB", "LenderC")
                analysis_type = "swot"
                time_period = "quarterly"
            }
        }
    },
    @{
        Name = "marketingmixmodelia"
        Description = "Modelo de marketing mix (MMM)"
        Category = "Analytics"
        Input = @{
            input_data = @{
                channels = @(
                    @{ name = "email"; spend = 5000; conversions = 100; revenue = 15000 },
                    @{ name = "social"; spend = 3000; conversions = 60; revenue = 9000 },
                    @{ name = "display"; spend = 2000; conversions = 30; revenue = 4500 }
                )
                optimization_budget = 15000
            }
        }
    },
    @{
        Name = "marketingorchestratorea"
        Description = "Orquesta workflows de marketing"
        Category = "Automation"
        Input = @{
            input_data = @{
                workflow_id = "wf_001"
                workflow_name = "Lead Nurturing"
                steps = @("segment", "personalize", "send", "track")
                trigger = "new_lead"
                conditions = @{ min_score = 50 }
            }
        }
    },
    @{
        Name = "abtestingimpactia"
        Description = "Mide impacto de tests A/B"
        Category = "Optimization"
        Input = @{
            input_data = @{
                test_id = "test_impact_001"
                variants = @(
                    @{ name = "control"; revenue = 10000; conversions = 100 },
                    @{ name = "variant"; revenue = 12000; conversions = 120 }
                )
                duration_days = 14
                traffic_split = 0.5
            }
        }
    },
    @{
        Name = "productaffinityia"
        Description = "Analiza afinidad de productos"
        Category = "Recommendations"
        Input = @{
            input_data = @{
                customer = @{
                    customer_id = "cust_001"
                    name = "Juan Pérez"
                    email = "juan@test.com"
                    segment = "high_value"
                }
                purchase_history = @(
                    @{ product = "personal_loan"; amount = 10000; date = "2024-01-15" },
                    @{ product = "credit_card"; amount = 5000; date = "2024-02-01" }
                )
            }
        }
    },
    @{
        Name = "geosegmentationia"
        Description = "Segmentación geográfica"
        Category = "Segmentation"
        Input = @{
            input_data = @{
                segmentation_id = "seg_geo_001"
                regions = @(
                    @{ region = "Norte"; leads = 100; conversions = 20; revenue = 50000 },
                    @{ region = "Sur"; leads = 80; conversions = 25; revenue = 62500 }
                )
                optimization_metric = "roi"
            }
        }
    },
    @{
        Name = "minimalformia"
        Description = "Genera formularios optimizados"
        Category = "Lead Capture"
        Input = @{
            input_data = @{
                form_id = "form_001"
                form_type = "loan_application"
                fields = @("name", "email", "phone", "loan_amount")
                optional_fields = @("company", "income")
                submit_action = "create_lead"
            }
        }
    },
    @{
        Name = "cashofferfilteria"
        Description = "Filtra ofertas de efectivo/crédito"
        Category = "Credit"
        Input = @{
            input_data = @{
                customer_id = "cust_001"
                applications = @(
                    @{ id = "app1"; credit_score = 750; income = 5000; requested_amount = 20000 },
                    @{ id = "app2"; credit_score = 650; income = 3000; requested_amount = 10000 }
                )
                filter_rules = @{
                    min_credit_score = 700
                    max_dti = 0.45
                }
            }
        }
    }
)

# =========================
# FUNCIÓN DE PRUEBA
# =========================
function Test-MarketingAgent {
    param(
        [hashtable]$AgentDef,
        [int]$Index,
        [int]$Total
    )
    
    $startTime = Get-Date
    $agentName = $AgentDef.Name
    
    Write-Host "`n[$Index/$Total] $agentName" -ForegroundColor Cyan
    Write-Host "  Categoría: $($AgentDef.Category)" -ForegroundColor Gray
    
    $result = @{
        agent_name = $agentName
        description = $AgentDef.Description
        category = $AgentDef.Category
        input_schema = $AgentDef.Input.input_data
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        status = "unknown"
        response = $null
        error = $null
        latency_ms = 0
    }
    
    try {
        $body = $AgentDef.Input | ConvertTo-Json -Depth 10 -Compress
        $response = Invoke-RestMethod -Uri "$BaseUrl/agents/marketing/$agentName/execute" -Method POST -Headers $Headers -Body $body -TimeoutSec 30
        
        $endTime = Get-Date
        $result.latency_ms = [math]::Round(($endTime - $startTime).TotalMilliseconds)
        
        if ($response.result.status -eq "error" -or $response.result.error) {
            $result.status = "warning"
            $result.error = $response.result.error
            $result.response = $response.result
            Write-Host "  ⚠️  WARN: $($response.result.error)" -ForegroundColor Yellow
        } else {
            $result.status = "success"
            $result.response = $response.result
            Write-Host "  ✅ OK ($($result.latency_ms)ms)" -ForegroundColor Green
        }
    }
    catch {
        $endTime = Get-Date
        $result.latency_ms = [math]::Round(($endTime - $startTime).TotalMilliseconds)
        $result.status = "error"
        $result.error = $_.Exception.Message
        Write-Host "  ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $result
}

# =========================
# EJECUCIÓN PRINCIPAL
# =========================
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  EVALUACIÓN COMPLETA - AGENTES DE MARKETING NADAKKI" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  Tenant: $TenantId" -ForegroundColor Gray
Write-Host "  URL: $BaseUrl" -ForegroundColor Gray
Write-Host "  Agentes a evaluar: $($AgentDefinitions.Count)" -ForegroundColor Gray
Write-Host "  Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "================================================================" -ForegroundColor Magenta

$totalAgents = $AgentDefinitions.Count
$index = 0

foreach ($agentDef in $AgentDefinitions) {
    $index++
    $result = Test-MarketingAgent -AgentDef $agentDef -Index $index -Total $totalAgents
    $Results += $result
    Start-Sleep -Milliseconds 500  # Rate limiting
}

# =========================
# RESUMEN Y ESTADÍSTICAS
# =========================
$successCount = ($Results | Where-Object { $_.status -eq "success" }).Count
$warningCount = ($Results | Where-Object { $_.status -eq "warning" }).Count
$errorCount = ($Results | Where-Object { $_.status -eq "error" }).Count
$avgLatency = [math]::Round(($Results | Measure-Object -Property latency_ms -Average).Average)

Write-Host "`n================================================================" -ForegroundColor Magenta
Write-Host "  RESUMEN DE EVALUACIÓN" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  ✅ Exitosos:    $successCount" -ForegroundColor Green
Write-Host "  ⚠️  Warnings:   $warningCount" -ForegroundColor Yellow
Write-Host "  ❌ Errores:     $errorCount" -ForegroundColor Red
Write-Host ""
Write-Host "  📊 Latencia promedio: ${avgLatency}ms" -ForegroundColor Cyan
Write-Host "  📈 Tasa de éxito: $([math]::Round(($successCount / $totalAgents) * 100))%" -ForegroundColor Cyan
Write-Host ""

# Agrupar por categoría
Write-Host "  POR CATEGORÍA:" -ForegroundColor White
$categories = $Results | Group-Object -Property category
foreach ($cat in $categories) {
    $catSuccess = ($cat.Group | Where-Object { $_.status -eq "success" }).Count
    $catTotal = $cat.Count
    Write-Host "    $($cat.Name): $catSuccess/$catTotal" -ForegroundColor Gray
}

# =========================
# GUARDAR RESULTADOS JSON
# =========================
$outputData = @{
    evaluation_date = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    tenant_id = $TenantId
    base_url = $BaseUrl
    summary = @{
        total_agents = $totalAgents
        successful = $successCount
        warnings = $warningCount
        errors = $errorCount
        success_rate = [math]::Round(($successCount / $totalAgents) * 100, 2)
        avg_latency_ms = $avgLatency
    }
    agents = $Results
}

$outputData | ConvertTo-Json -Depth 20 | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  💾 RESULTADOS GUARDADOS" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Archivo: $OutputFile" -ForegroundColor Cyan
Write-Host "  Ubicación: $(Get-Location)\$OutputFile" -ForegroundColor Gray
Write-Host ""

# Mostrar agentes con problemas
if ($warningCount -gt 0 -or $errorCount -gt 0) {
    Write-Host "  AGENTES QUE NECESITAN ATENCIÓN:" -ForegroundColor Yellow
    $Results | Where-Object { $_.status -ne "success" } | ForEach-Object {
        $icon = if ($_.status -eq "warning") { "⚠️" } else { "❌" }
        Write-Host "    $icon $($_.agent_name): $($_.error)" -ForegroundColor $(if ($_.status -eq "warning") { "Yellow" } else { "Red" })
    }
}

Write-Host ""
Write-Host "  Evaluación completada." -ForegroundColor Green
