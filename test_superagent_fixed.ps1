Write-Host "🚀 PRUEBA SUPER-AGENT v5.0 - VERSIÓN CORREGIDA" -ForegroundColor Green
Write-Host "=" * 60

try {
    # 1. Health Check
    Write-Host "`n🩺 Health Check:" -ForegroundColor Yellow
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Headers @{"accept" = "application/json"}
    Write-Host "   Status: $($health.status)" -ForegroundColor White
    Write-Host "   Version: $($health.version)" -ForegroundColor White

    # 2. Status del Agente
    Write-Host "`n📊 Status del Agente:" -ForegroundColor Yellow
    $status = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/status" -Headers @{"accept" = "application/json"}
    Write-Host "   Agent ID: $($status.agent_id)" -ForegroundColor White
    Write-Host "   Total Requests: $($status.performance_metrics.total_requests)" -ForegroundColor White
    Write-Host "   ML Predictions: $($status.performance_metrics.ml_predictions_made)" -ForegroundColor White

    # 3. Análisis de Contenido (CORREGIDO)
    Write-Host "`n📝 Análisis de Contenido:" -ForegroundColor Yellow
    
    # Crear objeto PowerShell y convertirlo a JSON
    $bodyObject = @(
        @{
            content_id = "powershell_fixed_1"
            content_type = "blog_post"
            channel = "blog"
            publish_date = "2024-01-15T10:00:00"
            title = "Super-Agent v5.0 funcionando correctamente desde PowerShell"
            metrics = @{
                impressions = 18000
                reach = 9500
                engagement = 1500
                clicks = 600
                shares = 180
                comments = 95
                saves = 75
            }
            topic_tags = @("powershell", "fixed", "success")
            marketing_consent = $true
        }
    )

    $jsonBody = $bodyObject | ConvertTo-Json -Depth 10
    Write-Host "   JSON Body enviado:" -ForegroundColor Gray
    Write-Host $jsonBody -ForegroundColor DarkGray

    $analysis = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze" -Method Post -ContentType "application/json" -Body $jsonBody
    
    Write-Host "   ✅ Análisis completado exitosamente!" -ForegroundColor Green
    Write-Host "   Request ID: $($analysis.request_id)" -ForegroundColor White
    Write-Host "   Tiempo: $($analysis.processing_time_ms)ms" -ForegroundColor White
    
    $result = $analysis.performance_analyses[0]
    Write-Host "   Performance: $($result.performance_level)" -ForegroundColor White
    Write-Host "   Engagement: $($result.engagement_rate)%" -ForegroundColor White
    Write-Host "   Virality: $([math]::Round($result.virality_score, 2))" -ForegroundColor White
    Write-Host "   ML Confidence: $($result.ml_confidence)" -ForegroundColor White
    Write-Host "   Blockchain Hash: $($result.blockchain_hash)" -ForegroundColor White

    if ($result.optimization_suggestions.Count -gt 0) {
        Write-Host "   Sugerencias:" -ForegroundColor Cyan
        foreach ($suggestion in $result.optimization_suggestions) {
            Write-Host "     - $suggestion" -ForegroundColor Gray
        }
    }

    # 4. Verificar auditoría actualizada
    Write-Host "`n⛓️ Verificando nueva auditoría:" -ForegroundColor Yellow
    $audit = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/audit/trail?limit=1" -Headers @{"accept" = "application/json"}
    Write-Host "   Último registro: $($audit[0].event_type)" -ForegroundColor White
    Write-Host "   Timestamp: $($audit[0].timestamp)" -ForegroundColor White

    Write-Host "`n🎉 ¡PRUEBA EXITOSA! Super-Agent v5.0 funcionando perfectamente en PowerShell" -ForegroundColor Green

} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Detalles completos:" -ForegroundColor Red
    Write-Host $_.Exception.ToString() -ForegroundColor DarkRed
}