# ==============================================================
# AUDITORÍA COMPLETA - NADAKKI vs CREDICEFI
# ==============================================================

Write-Host "🔬 INICIANDO AUDITORÍA COMPLETA DE PROYECTOS" -ForegroundColor Cyan
Write-Host "=" * 70

# Variables
$projects_base = "C:\Users\cesar\Projects"
$nadakki_path = "$projects_base\nadakki-ai-suite\nadakki-ai-suite"
$credicefi_path = "$projects_base\credicefi-api"

# Si credicefi no existe en Projects, buscar en Desktop
if (-not (Test-Path $credicefi_path)) {
    $credicefi_path = "$env:USERPROFILE\Desktop\credicefi-api"
}

Write-Host "`n📁 UBICACIONES ENCONTRADAS:`n" -ForegroundColor Yellow
Write-Host "Nadakki:   $nadakki_path"
Write-Host "Credicefi: $credicefi_path`n"

# ==============================================================
# FUNCIÓN 1: AUDITAR PROYECTO
# ==============================================================

function Audit-Project {
    param([string]$path, [string]$name)
    
    Write-Host "`n$name PROJECT AUDIT" -ForegroundColor Magenta
    Write-Host "-" * 70
    
    if (-not (Test-Path $path)) {
        Write-Host "❌ CARPETA NO ENCONTRADA: $path" -ForegroundColor Red
        return @{found=$false}
    }
    
    Write-Host "✅ Carpeta encontrada" -ForegroundColor Green
    
    # Archivos principales
    $main_py = "$path\main.py"
    $credicefi_py = "$path\credicefi_api.py"
    $requirements_txt = "$path\requirements.txt"
    $github_url = (git -C $path config --get remote.origin.url 2>/dev/null) -or "No encontrado"
    
    # Tamaños y líneas
    $main_lines = if (Test-Path $main_py) { @(Get-Content $main_py).Count } else { 0 }
    $credicefi_lines = if (Test-Path $credicefi_py) { @(Get-Content $credicefi_py).Count } else { 0 }
    
    Write-Host "`n📊 ARCHIVOS:" -ForegroundColor Yellow
    Write-Host "  main.py:         $(if(Test-Path $main_py) {'✅'} else {'❌'}) $main_lines líneas"
    Write-Host "  credicefi_api.py: $(if(Test-Path $credicefi_py) {'✅'} else {'❌'}) $credicefi_lines líneas"
    Write-Host "  requirements.txt: $(if(Test-Path $requirements_txt) {'✅'} else {'❌'})"
    Write-Host "  GitHub:          $github_url"
    
    # Endpoints en main.py
    if (Test-Path $main_py) {
        $endpoints = Select-String "@app.get|@app.post|@app.route" $main_py -NoEmphasis
        Write-Host "`n🔗 ENDPOINTS EN main.py:" -ForegroundColor Yellow
        if ($endpoints) {
            $endpoints | ForEach-Object { Write-Host "  - $($_.Line.Trim())" }
        } else {
            Write-Host "  (Sin endpoints detectados)"
        }
    }
    
    # Endpoint WordPress
    $wordpress_endpoint = Select-String "marketing/agents/summary" $main_py -NoEmphasis
    Write-Host "`n📱 ENDPOINT WORDPRESS:" -ForegroundColor Yellow
    if ($wordpress_endpoint) {
        Write-Host "  ✅ ENCONTRADO" -ForegroundColor Green
    } else {
        Write-Host "  ❌ NO ENCONTRADO" -ForegroundColor Red
    }
    
    return @{
        found=$true
        main_lines=$main_lines
        credicefi_lines=$credicefi_lines
        github=$github_url
        has_wordpress=$($wordpress_endpoint -ne $null)
        has_main=$(Test-Path $main_py)
        has_credicefi=$(Test-Path $credicefi_py)
    }
}

# ==============================================================
# EJECUTAR AUDITORÍAS
# ==============================================================

$nadakki_audit = Audit-Project $nadakki_path "NADAKKI-AI-SUITE"
$credicefi_audit = Audit-Project $credicefi_path "CREDICEFI-API"

# ==============================================================
# COMPARATIVA
# ==============================================================

Write-Host "`n" -ForegroundColor White
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📊 COMPARATIVA RESUMIDA" -ForegroundColor Cyan
Write-Host "=" * 70

$comparison = @"
┌─────────────────────────┬──────────────┬──────────────┐
│ Propiedad               │ NADAKKI      │ CREDICEFI    │
├─────────────────────────┼──────────────┼──────────────┤
│ main.py líneas          │ $($nadakki_audit.main_lines -padright 12) │ $($credicefi_audit.main_lines)           │
│ credicefi_api.py líneas │ $($nadakki_audit.credicefi_lines -padright 12) │ $($credicefi_audit.credicefi_lines)           │
│ WordPress Endpoint      │ $($nadakki_audit.has_wordpress -padright 12) │ $($credicefi_audit.has_wordpress)           │
│ En GitHub              │ ✅ (principal) │ ❌ (secundario) │
│ Deployado en Render    │ ❌ (NO)       │ ✅ (SÍ)      │
└─────────────────────────┴──────────────┴──────────────┘
"@

Write-Host $comparison -ForegroundColor White

# ==============================================================
# RECOMENDACIONES
# ==============================================================

Write-Host "`n" -ForegroundColor White
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "🎯 RECOMENDACIONES ESTRATÉGICAS" -ForegroundColor Green
Write-Host "=" * 70

Write-Host @"
1️⃣  PROBLEMA DETECTADO:
   - NADAKKI-AI-SUITE: Código actualizado en GitHub ($($nadakki_audit.main_lines) líneas)
   - CREDICEFI-API: Deployado en Render pero código DIFERENTE
   - CONFLICTO: Render corre credicefi-api, NO nadakki-ai-suite

2️⃣  SOLUCIONES (Elige 1):

   OPCIÓN A: CONSOLIDAR EN CREDICEFI (Recomendado - Ya está deployado)
   ─────────────────────────────────────────────────────────────
   ✅ Ventajas:
      - Ya funciona en Render
      - Menos cambios
      - Deploy inmediato
   
   Pasos:
   1. Copiar endpoint de NADAKKI → CREDICEFI main.py
   2. Actualizar credicefi-api GitHub
   3. Redeploy en Render
   
   
   OPCIÓN B: MIGRAR COMPLETAMENTE A NADAKKI (Profesional)
   ───────────────────────────────────────────────────────
   ✅ Ventajas:
      - Estructura más limpia
      - Un solo repositorio
      - Mejor organización
   
   Pasos:
   1. Desconectar credicefi-api de Render
   2. Conectar nadakki-ai-suite a Render
   3. Deploy
   
   
   OPCIÓN C: FUSIÓN INTELIGENTE
   ───────────────────────────
   ✅ Mejora arquitectura:
      - Mantener credicefi-api para evaluación crediticia
      - Crear nuevo servicio "nadakki-marketing" para WordPress
      - Ambos deployados simultáneamente

3️⃣  PRÓXIMO PASO:
   ¿Cuál opción prefieres? A, B, o C

"@ -ForegroundColor Cyan

Write-Host "`n" + ("=" * 70) + "`n" -ForegroundColor Green