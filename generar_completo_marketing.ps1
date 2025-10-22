# 🚀 Script combinado: Detectar faltantes + generar con GPT

Write-Host "Detectando agentes faltantes..." -ForegroundColor Cyan

$detectorPath = ".\detectar_faltantes_marketing.ps1"
if (-not (Test-Path $detectorPath)) {
    Write-Host "ERROR: Falta el archivo detectar_faltantes_marketing.ps1" -ForegroundColor Red
    exit
}

& $detectorPath

$targetJson = "agentes_marketing_faltantes.json"
if (-not (Test-Path $targetJson)) {
    Write-Host "ERROR: No se encontró el archivo JSON de faltantes." -ForegroundColor Red
    exit
}

$apiKey = $env:OPENAI_API_KEY
if (-not $apiKey) {
    Write-Host "ERROR: Falta la variable de entorno OPENAI_API_KEY." -ForegroundColor Red
    Write-Host "Ejecuta: `$env:OPENAI_API_KEY = 'sk-xxxxx...'" -ForegroundColor Yellow
    exit
}

$endpoint = "https://api.openai.com/v1/chat/completions"
$model = "gpt-4o"
$savePath = "agents\marketing"
$agentes = Get-Content $targetJson | ConvertFrom-Json

if (-not (Test-Path $savePath)) {
    New-Item -ItemType Directory -Path $savePath | Out-Null
}

$generados = @()
$omitidos = @()
$fallidos = @()

foreach ($agente in $agentes) {
    $nombre = $agente.nombre_agente
    $archivo = Join-Path $savePath "$nombre.py"

    if (Test-Path $archivo) {
        $omitidos += $nombre
        continue
    }

    $className = ($nombre -replace '_', '') -replace '(^[a-z])', { $_.Value.ToUpper() }

    $prompt = (
        "Actúa como ingeniero experto en sistemas multi-tenant. Genera un archivo .py para el siguiente agente de marketing:`n" +
        "Nombre del agente: $($agente.nombre_agente)`n" +
        "Función específica: $($agente.funcion_especifica)`n" +
        "Modelo AI: $($agente.tipo_modelo_ai)`n" +
        "Fuentes de datos: $($agente.fuentes_datos -join ', ')`n" +
        "Output esperado: $($agente.output_esperado)`n" +
        "Modo de ejecución: $($agente.modo_ejecucion)`n`n" +
        "Estructura requerida:`n" +
        "- Clase $className`n" +
        "- Metodo: run(self, tenant_id, input_data)`n" +
        "- Docstrings estilo Google`n" +
        "- Logging INFO y DEBUG`n" +
        "- Compatible con arquitectura multi-tenant"
    )

    $body = @{
        model = $model
        messages = @(
            @{ role = "system"; content = "Eres un ingeniero de IA especializado en generación automática de agentes Python para sistemas SaaS." }
            @{ role = "user"; content = $prompt }
        )
        temperature = 0.3
    } | ConvertTo-Json -Depth 5

    try {
        Write-Host "Generando: $nombre.py"
        $response = Invoke-RestMethod -Uri $endpoint -Headers @{
            "Authorization" = "Bearer $apiKey"
            "Content-Type"  = "application/json"
        } -Method Post -Body $body

        $code = $response.choices[0].message.content
        Set-Content -Path $archivo -Value $code -Encoding UTF8
        $generados += $nombre
        Start-Process notepad.exe -ArgumentList "`"$archivo`""
    }
    catch {
        Write-Host ("ERROR generando: " + $nombre) -ForegroundColor Red
        $fallidos += $nombre
    }
}

Write-Host "`n======================="
Write-Host "AGENTES GENERADOS:"
$generados | ForEach-Object { Write-Host ("  OK: " + $_) -ForegroundColor Green }

Write-Host "`nAGENTES OMITIDOS (ya existían):"
$omitidos | ForEach-Object { Write-Host ("  OMITIDO: " + $_) -ForegroundColor Yellow }

if ($fallidos.Count -gt 0) {
    Write-Host "`nAGENTES CON ERROR:"
    $fallidos | ForEach-Object { Write-Host ("  ERROR: " + $_) -ForegroundColor Red }
}
else {
    Write-Host "`nTodos los agentes se generaron sin errores." -ForegroundColor Cyan
}
