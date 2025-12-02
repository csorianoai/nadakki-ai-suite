Write-Host "🚀 PRUEBA SUPER-AGENT v5.0 - VERSIÓN DEFINITIVA" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

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

    # 3. Análisis de Contenido - FORMA MÁS SIMPLE
    Write-Host "`n📝 Análisis de Contenido:" -ForegroundColor Yellow
    
    # Crear JSON manualmente para evitar problemas de formato
    $jsonBody = @'
[
  {
    "content_id": "final_test_1",
    "content_type": "blog_post",
    "channel": "blog",
    "publish_date": "2024-01-15T10:00:00",
    "title": "Super-Agent v5.0 funcionando perfectamente en PowerShell",
    "metrics": {
      "impressions": 15000,
      "reach": 8000,
      "engagement": 1200,
      "clicks": 450,
      "shares": 120,
      "comments": 80,
      "saves": 60
    },
    "topic_tags": ["powershell", "final", "test"],
    "marketing_consent": true
  }
]
'@

    Write-Host "   Enviando solicitud..." -ForegroundColor Gray
    
    # Usar Invoke-WebRequest para mejor control de errores
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/analyze" -Method Post -ContentType "application/json" -Body $jsonBody
    
    if ($response.StatusCode -eq 200) {
        $analysis = $response.Content | ConvertFrom-Json
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

        Write-Host "`n🎉 ¡PRUEBA EXITOSA! Super-Agent v5.0 funcionando perfectamente" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Error HTTP: $($response.StatusCode)" -ForegroundColor Red
        Write-Host "   Respuesta: $($response.Content)" -ForegroundColor Red
    }

} catch {
    Write-Host "`n❌ Error en la prueba:" -ForegroundColor Red
    Write-Host "   Mensaje: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $errorStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorStream)
        $errorContent = $reader.ReadToEnd()
        Write-Host "   Detalles: $errorContent" -ForegroundColor DarkRed
    }
}