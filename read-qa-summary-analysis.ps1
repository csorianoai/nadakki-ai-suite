# 🔍 ANÁLISIS COMPLETO DEL REPORTE QA - qa_summary.json
# Lee y analiza el reporte de 18,762 bytes para identificar problemas específicos

Write-Host "🔍 ANÁLISIS COMPLETO DEL REPORTE QA" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Verificar archivo
if (-not (Test-Path "qa_summary.json")) {
    Write-Host "❌ ERROR: qa_summary.json no encontrado" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item "qa_summary.json").Length
Write-Host "📊 Archivo encontrado: qa_summary.json ($fileSize bytes)" -ForegroundColor Green

# Leer el reporte JSON
Write-Host "`n📖 LEYENDO REPORTE JSON..." -ForegroundColor Yellow
try {
    $qaData = Get-Content "qa_summary.json" -Raw | ConvertFrom-Json
    Write-Host "✅ JSON parseado exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error parseando JSON: $_" -ForegroundColor Red
    Write-Host "📄 Mostrando primeras líneas del archivo:" -ForegroundColor Yellow
    Get-Content "qa_summary.json" -Head 20 | ForEach-Object { Write-Host "   $_" }
    exit 1
}

# Análisis del resumen general
Write-Host "`n📊 RESUMEN GENERAL:" -ForegroundColor White
Write-Host "=" * 30 -ForegroundColor White

if ($qaData.total_agents) {
    Write-Host "   🤖 Total agentes: $($qaData.total_agents)" -ForegroundColor Cyan
}
if ($qaData.functional_agents) {
    Write-Host "   ✅ Funcionales: $($qaData.functional_agents)" -ForegroundColor Green
}
if ($qaData.success_rate) {
    Write-Host "   📈 Tasa éxito: $($qaData.success_rate)%" -ForegroundColor Yellow
}

$problemAgents = $qaData.total_agents - $qaData.functional_agents
Write-Host "   ❌ Con problemas: $problemAgents" -ForegroundColor Red

# Análisis por ecosistema
Write-Host "`n🌳 ANÁLISIS POR ECOSISTEMA:" -ForegroundColor White
Write-Host "=" * 40 -ForegroundColor White

$ecosystemStats = @{}
$allErrors = @()
$functionalAgents = @()
$brokenAgents = @()

foreach ($property in $qaData.PSObject.Properties) {
    if ($property.Name -like "*ecosystem*" -or $property.Name -in @("originacion", "decision", "vigilancia", "recuperacion", "compliance", "operacional", "experiencia", "inteligencia", "fortaleza")) {
        $ecosystemName = $property.Name
        $ecosystemData = $property.Value
        
        Write-Host "`n📁 $ecosystemName.ToUpper():" -ForegroundColor Cyan
        
        if ($ecosystemData.agents) {
            $total = $ecosystemData.agents.Count
            $functional = ($ecosystemData.agents | Where-Object { $_.functional -eq $true }).Count
            $broken = $total - $functional
            
            $successRate = if ($total -gt 0) { [math]::Round($functional / $total * 100, 1) } else { 0 }
            
            $status = if ($successRate -eq 0) { "🔴 CRÍTICO" } 
                     elseif ($successRate -lt 25) { "🟠 MUY MALO" }
                     elseif ($successRate -lt 50) { "🟡 MALO" }
                     elseif ($successRate -lt 75) { "🟢 REGULAR" }
                     else { "✅ BUENO" }
            
            Write-Host "   $status $functional/$total agentes ($successRate%)" -ForegroundColor White
            
            $ecosystemStats[$ecosystemName] = @{
                total = $total
                functional = $functional
                broken = $broken
                success_rate = $successRate
            }
            
            # Recopilar agentes funcionales
            $ecosystemData.agents | Where-Object { $_.functional -eq $true } | ForEach-Object {
                $functionalAgents += [PSCustomObject]@{
                    ecosystem = $ecosystemName
                    name = $_.name
                    file = $_.file
                    size = $_.size_bytes
                }
            }
            
            # Recopilar agentes problemáticos y errores
            $ecosystemData.agents | Where-Object { $_.functional -eq $false } | ForEach-Object {
                $brokenAgents += [PSCustomObject]@{
                    ecosystem = $ecosystemName
                    name = $_.name
                    file = $_.file
                    error = $_.error
                    size = $_.size_bytes
                }
                
                if ($_.error) {
                    $allErrors += $_.error
                }
            }
            
            # Mostrar primeros 3 errores únicos por ecosistema
            $ecosystemErrors = $ecosystemData.agents | Where-Object { $_.error } | Select-Object -ExpandProperty error | Sort-Object | Get-Unique | Select-Object -First 3
            foreach ($error in $ecosystemErrors) {
                $shortError = if ($error.Length -gt 70) { $error.Substring(0, 70) + "..." } else { $error }
                Write-Host "      ⚠️  $shortError" -ForegroundColor Red
            }
        }
    }
}

# Top errores más comunes
Write-Host "`n🔥 TOP 10 ERRORES MÁS COMUNES:" -ForegroundColor Red
Write-Host "=" * 40 -ForegroundColor Red

$errorCounts = @{}
foreach ($error in $allErrors) {
    # Extraer el tipo de error principal
    $errorType = if ($error -match "(.+?)[:.]") { $matches[1] } else { $error.Split(" ")[0] }
    
    if ($errorCounts[$errorType]) {
        $errorCounts[$errorType]++
    } else {
        $errorCounts[$errorType] = 1
    }
}

$sortedErrors = $errorCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10
$rank = 1
foreach ($errorEntry in $sortedErrors) {
    $percentage = [math]::Round($errorEntry.Value / $problemAgents * 100, 1)
    Write-Host "   $rank. $($errorEntry.Name): $($errorEntry.Value) agentes ($percentage%)" -ForegroundColor White
    $rank++
}

# Agentes funcionales (casos de éxito)
Write-Host "`n✅ AGENTES FUNCIONALES (CASES DE ÉXITO):" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

if ($functionalAgents.Count -gt 0) {
    foreach ($agent in $functionalAgents) {
        Write-Host "   🎯 $($agent.ecosystem)/$($agent.name) ($($agent.size) bytes)" -ForegroundColor Green
    }
    
    # Análisis del primer agente funcional como template
    $templateAgent = $functionalAgents[0]
    $templateFile = "agents\$($templateAgent.ecosystem)\$($templateAgent.file)"
    
    if (Test-Path $templateFile) {
        Write-Host "`n📝 TEMPLATE - AGENTE FUNCIONAL ($($templateAgent.name)):" -ForegroundColor Green
        Write-Host "   📁 Archivo: $templateFile" -ForegroundColor White
        
        $templateContent = Get-Content $templateFile -Raw
        
        # Análisis de estructura
        $hasClass = $templateContent -match "class\s+(\w+)"
        $hasInit = $templateContent -match "def __init__"
        $hasExecute = $templateContent -match "def execute"
        $imports = ([regex]::Matches($templateContent, "^(import|from)\s+[\w.]+", 'Multiline')).Count
        
        Write-Host "   ✅ Estructura válida:" -ForegroundColor White
        Write-Host "      - Clase principal: $hasClass" -ForegroundColor Gray
        Write-Host "      - Método __init__: $hasInit" -ForegroundColor Gray
        Write-Host "      - Método execute: $hasExecute" -ForegroundColor Gray
        Write-Host "      - Imports: $imports líneas" -ForegroundColor Gray
        
        Write-Host "`n   📄 Primeras 15 líneas (TEMPLATE):" -ForegroundColor White
        Get-Content $templateFile -Head 15 | ForEach-Object { 
            Write-Host "      $_" -ForegroundColor Gray 
        }
    }
} else {
    Write-Host "   ❌ NO HAY AGENTES FUNCIONALES PARA USAR COMO TEMPLATE" -ForegroundColor Red
}

# Análisis de agentes problemáticos
Write-Host "`n❌ PRIMEROS 5 AGENTES PROBLEMÁTICOS:" -ForegroundColor Red
Write-Host "=" * 45 -ForegroundColor Red

$sampleBrokenAgents = $brokenAgents | Select-Object -First 5
foreach ($agent in $sampleBrokenAgents) {
    Write-Host "`n   🔴 $($agent.ecosystem)/$($agent.name)" -ForegroundColor Red
    Write-Host "      📄 Archivo: $($agent.file)" -ForegroundColor White
    Write-Host "      ❌ Error: $($agent.error)" -ForegroundColor Red
    
    $agentFile = "agents\$($agent.ecosystem)\$($agent.file)"
    if (Test-Path $agentFile) {
        Write-Host "      📝 Primeras 5 líneas:" -ForegroundColor White
        Get-Content $agentFile -Head 5 | ForEach-Object {
            Write-Host "         $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "      ❌ ARCHIVO NO EXISTE" -ForegroundColor Red
    }
}

# Recomendaciones específicas
Write-Host "`n🔧 RECOMENDACIONES ESPECÍFICAS:" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

Write-Host "`n🚀 ACCIÓN INMEDIATA:" -ForegroundColor Yellow
if ($functionalAgents.Count -gt 0) {
    Write-Host "   1. ✅ Usar $($functionalAgents[0].name) como TEMPLATE" -ForegroundColor Green
    Write-Host "   2. 🔧 Regenerar agentes problemáticos con estructura válida" -ForegroundColor White
    Write-Host "   3. 🧪 Validar por lotes (10 agentes por vez)" -ForegroundColor White
} else {
    Write-Host "   1. ❌ CREAR TEMPLATE desde cero (ningún agente funcional)" -ForegroundColor Red
    Write-Host "   2. 🏗️ Regenerar TODOS los agentes con estructura correcta" -ForegroundColor White
    Write-Host "   3. 🧪 Implementar validación durante generación" -ForegroundColor White
}

Write-Host "`n🎯 PLAN DE RECUPERACIÓN:" -ForegroundColor Yellow
Write-Host "   FASE 1: Análisis de template funcional (si existe)" -ForegroundColor White
Write-Host "   FASE 2: Fix de errores más comunes (top 3)" -ForegroundColor White
Write-Host "   FASE 3: Regeneración masiva con validación" -ForegroundColor White
Write-Host "   FASE 4: Testing incremental hasta >90% éxito" -ForegroundColor White

# Estadísticas finales
Write-Host "`n📊 ESTADÍSTICAS FINALES:" -ForegroundColor White
Write-Host "=" * 30 -ForegroundColor White

$totalEcosystems = $ecosystemStats.Keys.Count
$criticalEcosystems = ($ecosystemStats.Values | Where-Object { $_.success_rate -eq 0 }).Count
$avgSuccessRate = if ($ecosystemStats.Values.Count -gt 0) { 
    ($ecosystemStats.Values | Measure-Object -Property success_rate -Average).Average 
} else { 0 }

Write-Host "   🌳 Total ecosistemas: $totalEcosystems" -ForegroundColor Cyan
Write-Host "   🔴 Ecosistemas críticos: $criticalEcosystems" -ForegroundColor Red
Write-Host "   📈 Promedio éxito global: $([math]::Round($avgSuccessRate, 1))%" -ForegroundColor Yellow

Write-Host "`n💾 ARCHIVOS ÚTILES GENERADOS:" -ForegroundColor Green
Write-Host "   📄 qa_summary.json (análisis completo)" -ForegroundColor White

Write-Host "`n🎯 PRÓXIMO PASO:" -ForegroundColor Cyan
if ($functionalAgents.Count -gt 0) {
    Write-Host "   Analizar en detalle agente funcional: $($functionalAgents[0].ecosystem)/$($functionalAgents[0].name)" -ForegroundColor White
    Write-Host "   Comando: notepad agents\$($functionalAgents[0].ecosystem)\$($functionalAgents[0].file)" -ForegroundColor Gray
} else {
    Write-Host "   Crear template de agente desde cero y regenerar todo el sistema" -ForegroundColor White
}

Write-Host "`n⚡ ANÁLISIS QA COMPLETO FINALIZADO ⚡" -ForegroundColor Cyan