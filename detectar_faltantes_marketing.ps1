# Ruta a carpeta existente
$existingPath = "agents\marketing"
$targetJson = "agentes_marketing_faltantes.json"

# Detectar archivos existentes
$agentesActuales = Get-ChildItem $existingPath -Filter *.py | Select-Object -ExpandProperty BaseName

# Lista maestra sugerida (40 agentes posibles en marketing)
$agentesEsperados = @(
    "leadsOptimizerIA", "abTestingImpactIA", "brandsentimentia", "campaignoptimizeria",
    "cashofferfilteria", "competitorintelligenceia", "contactqualityia", "contentviralityia",
    "conversioncohortia", "emailautomationia", "fidelizedprofileia", "geosegmentationia",
    "influencermatchia", "minimalformia", "productaffinityia", "socialpostgeneratoria",
    "videoreelautogenia", "clientprofilingia", "promotionsengineia", "offerspersonalizationia",
    "retargetingoptimizeria", "multichannelattributionia", "marketsegmentationia", "budgetallocatoria",
    "roiattributionia", "adschanneloptimizeria", "searchintenttrackeria", "conversionpredictoria",
    "seasonalityanalyzeria", "contentengagementia", "leadretentionia", "funneloptimizeria",
    "contentgeneratoria", "messagepersonalizeria", "viralpotentialia", "channelblendia",
    "offersforecastia", "emotiontrackeria", "heatmapinsightia", "touchpointanalyzeria"
)

# Detectar faltantes
$faltantes = $agentesEsperados | Where-Object { $_ -notin $agentesActuales }

# Crear plantilla por faltante
$plantillas = @()
foreach ($nombre in $faltantes) {
    $plantillas += @{
        nombre_agente       = $nombre
        funcion_especifica  = "Descripción pendiente"
        tipo_modelo_ai      = "Por definir"
        fuentes_datos       = @("Por definir")
        output_esperado     = "Resultado esperado"
        modo_ejecucion      = "batch"
    }
}

# Exportar JSON
$plantillas | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $targetJson

Write-Host "✅ JSON generado: $targetJson" -ForegroundColor Green
Write-Host "🧩 Agentes faltantes detectados: $($faltantes.Count)" -ForegroundColor Cyan
notepad $targetJson
