# ════════════════════════════════════════════════════════
# NADAKKI AI SUITE - PHASE 2: VERIFICACIÓN POST CONSOLIDACIÓN
# Autor: César Soriano
# Fecha: 2025-10-23
# Objetivo: Verificar limpieza, ejecución y endpoints FastAPI
# ════════════════════════════════════════════════════════

Write-Host "`n🔎 INICIANDO PHASE 2 - VERIFICACIÓN POST CONSOLIDACIÓN..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$verifyLog = "logs/phase2_verification_$timestamp.log"

# 1️⃣ Confirmar branch y estado del repo
$branch = git branch --show-current
Add-Content $verifyLog "Branch actual: $branch"
Write-Host "📌 Branch actual: $branch" -ForegroundColor Yellow

# 2️⃣ Verificar carpeta legacy
if (Test-Path "legacy_flask") {
    $countLegacy = (Get-ChildItem -Recurse "legacy_flask" | Measure-Object).Count
    Add-Content $verifyLog "Archivos legacy encontrados: $countLegacy"
    Write-Host "📁 Archivos legacy aislados: $countLegacy" -ForegroundColor Green
} else {
    Write-Host "⚠️  No se encontró carpeta legacy_flask" -ForegroundColor Yellow
}

# 3️⃣ Buscar residuos Flask en el proyecto activo
Write-Host "`n🧹 Verificando que no queden residuos Flask..." -ForegroundColor Cyan
$flaskHits = Select-String -Path "*.py" -Pattern "from flask","Flask(" -ErrorAction SilentlyContinue
if ($flaskHits -and $flaskHits.Count -gt 0) {
    foreach ($hit in $flaskHits) {
        Add-Content $verifyLog "RESIDUO FLASK: $($hit.Path)"
    }
    Write-Host "⚠️  Se encontraron archivos Flask fuera de legacy_flask." -ForegroundColor Yellow
} else {
    Add-Content $verifyLog "Sin residuos Flask."
    Write-Host "✅ Sin referencias Flask activas." -ForegroundColor Green
}

# 4️⃣ Validar ejecución de FastAPI (modo test)
Write-Host "`n⚙️  Probando carga de main.py (modo silencioso)..." -ForegroundColor Cyan
try {
    python -c "import importlib; app = importlib.import_module('main'); print('FASTAPI_OK')" | Tee-Object -FilePath $verifyLog -Append
    Write-Host "✅ FastAPI importado correctamente." -ForegroundColor Green
} catch {
    Write-Host "❌ Error al importar main.py" -ForegroundColor Red
    Add-Content $verifyLog "Error al importar main.py: $($_.Exception.Message)"
}

# 5️⃣ Listar endpoints principales del servidor FastAPI
Write-Host "`n🔍 Extrayendo endpoints FastAPI..." -ForegroundColor Cyan
$routesFile = "out/fastapi_routes_postverify_$timestamp.txt"
try {
    $env:PYTHONIOENCODING = "utf-8"
    python scripts/advanced_web_audit.py | Out-File -FilePath $routesFile -Encoding utf8
    Add-Content $verifyLog "Rutas auditadas → $routesFile"
    Write-Host "✅ Auditoría de endpoints completada." -ForegroundColor Green
} catch {
    Write-Host "⚠️  Error auditando rutas: $($_.Exception.Message)" -ForegroundColor Yellow
    Add-Content $verifyLog "Error auditoría: $($_.Exception.Message)"
}

# 6️⃣ Validar que los endpoints principales existan
$requiredRoutes = @(
    "/health",
    "/api/admin/tenants",
    "/api/marketing/lead-scoring",
    "/api/marketing/customer-segmentation"
)

$found = @()
if (Test-Path $routesFile) {
    $fileContent = Get-Content $routesFile
    foreach ($route in $requiredRoutes) {
        $matches = $fileContent | Select-String -Pattern $route
        if ($matches) {
            $found += $matches
        }
    }
}

if ($found -and $found.Count -gt 0) {
    Add-Content $verifyLog "Endpoints críticos detectados:"
    foreach ($endpoint in $found) {
        if ($null -ne $endpoint) {
            Add-Content $verifyLog $endpoint
            Write-Host "   • $($endpoint.ToString().Trim())" -ForegroundColor White
        }
    }
    Write-Host "✅ Endpoints críticos confirmados." -ForegroundColor Green
} else {
    Write-Host "⚠️  No se detectaron endpoints críticos." -ForegroundColor Yellow
    Add-Content $verifyLog "Endpoints críticos ausentes."
}

# 7️⃣ Resultado final
Write-Host "`n✅ PHASE 2 COMPLETADA." -ForegroundColor Green
Write-Host "📄 Log verificación: $verifyLog" -ForegroundColor Cyan
Write-Host "📄 Rutas auditadas: $routesFile" -ForegroundColor Cyan
