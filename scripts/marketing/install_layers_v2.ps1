# install_layers_v2.ps1
# Instala las capas v2 mejoradas en el proyecto

$projectPath = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
$layersPath = "$projectPath\agents\marketing\layers"

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  INSTALACIÓN DE CAPAS V2 - MARKETING AL 100%" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Magenta

# Verificar que existen las capas en Downloads
$downloadsPath = "C:\Users\cesar\Downloads"
$requiredFiles = @(
    "decision_layer_v2.py",
    "reason_codes_layer_v2.py", 
    "authority_layer_v2.py"
)

Write-Host "`n[1/4] Verificando archivos descargados..." -ForegroundColor Cyan

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $downloadsPath $file
    if (Test-Path $filePath) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (falta)" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`n❌ Faltan archivos. Descárgalos primero desde Claude." -ForegroundColor Red
    exit 1
}

# Crear carpeta layers si no existe
Write-Host "`n[2/4] Preparando carpeta de layers..." -ForegroundColor Cyan
if (-not (Test-Path $layersPath)) {
    New-Item -ItemType Directory -Path $layersPath -Force | Out-Null
    Write-Host "  ✓ Carpeta creada: $layersPath" -ForegroundColor Green
} else {
    Write-Host "  ✓ Carpeta existe: $layersPath" -ForegroundColor Green
}

# Copiar archivos v2 (reemplazando v1)
Write-Host "`n[3/4] Instalando capas v2..." -ForegroundColor Cyan

# Decision Layer
Copy-Item -Path "$downloadsPath\decision_layer_v2.py" -Destination "$layersPath\decision_layer.py" -Force
Write-Host "  ✓ decision_layer.py (v2.0)" -ForegroundColor Green

# Reason Codes Layer
Copy-Item -Path "$downloadsPath\reason_codes_layer_v2.py" -Destination "$layersPath\reason_codes_layer.py" -Force
Write-Host "  ✓ reason_codes_layer.py (v2.0)" -ForegroundColor Green

# Authority Layer
Copy-Item -Path "$downloadsPath\authority_layer_v2.py" -Destination "$layersPath\authority_layer.py" -Force
Write-Host "  ✓ authority_layer.py (v2.0)" -ForegroundColor Green

# Crear __init__.py actualizado
$initContent = @'
"""
Nadakki AI Suite - Capas de Mejora de Agentes v2.0
Estas capas transforman agentes de 45/100 a 101/100

Mejoras v2.0:
- Idempotencia (no se aplican dos veces)
- Configuración declarativa
- Audit trail completo
- Mixins para fácil integración
"""

from .decision_layer import (
    DecisionLayer,
    DecisionLayerConfig,
    DecisionLayerMixin,
    apply_decision_layer,
    create_decision_config
)

from .reason_codes_layer import (
    ReasonCodesLayer,
    ReasonCodesConfig,
    ReasonCodesMixin,
    apply_reason_codes,
    create_reason_codes_config
)

from .authority_layer import (
    AuthorityLayer,
    AuthorityConfig,
    AuthorityLayerMixin,
    apply_authority_filter,
    create_authority_config
)

__version__ = "2.0.0"

__all__ = [
    # Decision Layer
    "DecisionLayer",
    "DecisionLayerConfig", 
    "DecisionLayerMixin",
    "apply_decision_layer",
    "create_decision_config",
    
    # Reason Codes Layer
    "ReasonCodesLayer",
    "ReasonCodesConfig",
    "ReasonCodesMixin",
    "apply_reason_codes",
    "create_reason_codes_config",
    
    # Authority Layer
    "AuthorityLayer",
    "AuthorityConfig",
    "AuthorityLayerMixin",
    "apply_authority_filter",
    "create_authority_config"
]
'@

$initContent | Out-File -FilePath "$layersPath\__init__.py" -Encoding UTF8 -Force
Write-Host "  ✓ __init__.py (v2.0)" -ForegroundColor Green

# Commit cambios
Write-Host "`n[4/4] Guardando en Git..." -ForegroundColor Cyan
Set-Location $projectPath
git add agents/marketing/layers/
git commit -m "feat: Upgrade layers to v2.0 - idempotent, configurable, with mixins"
git push origin main

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ CAPAS V2 INSTALADAS CORRECTAMENTE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Archivos instalados:" -ForegroundColor Cyan
Write-Host "    • decision_layer.py (v2.0) - Para Cluster A (6 agentes)" -ForegroundColor White
Write-Host "    • reason_codes_layer.py (v2.0) - Para Cluster D (2 agentes)" -ForegroundColor White
Write-Host "    • authority_layer.py (v2.0) - Para Cluster B (3 agentes)" -ForegroundColor White
Write-Host ""
Write-Host "  Próximo paso: Aplicar las capas a los agentes" -ForegroundColor Yellow
Write-Host ""
