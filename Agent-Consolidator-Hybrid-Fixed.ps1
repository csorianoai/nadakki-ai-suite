# ================================================================
# AGENT-CONSOLIDATOR.PS1
# Consolidación automática de agentes dispersos en estructura estándar
# ================================================================

param(
    [string]$ProjectPath = ".",
    [string]$ConsolidatedPath = ".\agents_consolidated",
    [string]$BackupPath = ".\agents_backup",
    [switch]$DryRun = $false,
    [switch]$CreateBackup = $true
)

# Configuración de colores
$Colors = @{
    Header = 'Cyan'; Success = 'Green'; Warning = 'Yellow'
    Error = 'Red'; Info = 'White'; Emphasis = 'Magenta'
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

# Mapeo de agentes core crediticios a ecosistemas
$CORE_AGENTS_MAP = @{
    'originacion' = @(
        @{pattern='SentinelBot'; filename='sentinel_bot.py'; priority=1},
        @{pattern='DNAProfiler'; filename='dna_profiler.py'; priority=1},
        @{pattern='IncomeOracle'; filename='income_oracle.py'; priority=1},
        @{pattern='BehaviorMiner'; filename='behavior_miner.py'; priority=1},
        @{pattern='DocumentValidator'; filename='document_validator.py'; priority=2},
        @{pattern='RiskAssessor'; filename='risk_assessor.py'; priority=2}
    )
    'decision' = @(
        @{pattern='QuantumDecision'; filename='quantum_decision.py'; priority=1},
        @{pattern='RiskOracle'; filename='risk_oracle.py'; priority=1},
        @{pattern='PolicyGuardian'; filename='policy_guardian.py'; priority=1},
        @{pattern='TurboApprover'; filename='turbo_approver.py'; priority=1}
    )
    'vigilancia' = @(
        @{pattern='EarlyWarning'; filename='early_warning.py'; priority=1},
        @{pattern='PortfolioSentinel'; filename='portfolio_sentinel.py'; priority=1},
        @{pattern='MarketRadar'; filename='market_radar.py'; priority=1},
        @{pattern='StressTester'; filename='stress_tester.py'; priority=1},
        @{pattern='RiskMonitor'; filename='risk_monitor.py'; priority=2},
        @{pattern='ComplianceTracker'; filename='compliance_tracker.py'; priority=2}
    )
    'recuperacion' = @(
        @{pattern='CollectionMaster'; filename='collection_master.py'; priority=1},
        @{pattern='RecoveryOptimizer'; filename='recovery_optimizer.py'; priority=1},
        @{pattern='NegotiationBot'; filename='negotiation_bot.py'; priority=1},
        @{pattern='LegalPathway'; filename='legal_pathway.py'; priority=1}
    )
    'compliance' = @(
        @{pattern='ComplianceWatchdog'; filename='compliance_watchdog.py'; priority=1},
        @{pattern='AuditMaster'; filename='audit_master.py'; priority=1},
        @{pattern='DocGuardian'; filename='doc_guardian.py'; priority=1},
        @{pattern='RegulatoryRadar'; filename='regulatory_radar.py'; priority=1}
    )
    'operacional' = @(
        @{pattern='ProcessGenius'; filename='process_genius.py'; priority=1},
        @{pattern='CostOptimizer'; filename='cost_optimizer.py'; priority=1},
        @{pattern='QualityController'; filename='quality_controller.py'; priority=1},
        @{pattern='WorkflowMaster'; filename='workflow_master.py'; priority=1}
    )
}

function Get-FileComplexity {
    param([string]$FilePath)
    
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
        if (-not $content) { return 0 }
        
        $complexity = 0
        $lines = ($content -split "`n").Count
        $classes = ([regex]::Matches($content, 'class\s+\w+')).Count
        $functions = ([regex]::Matches($content, 'def\s+\w+')).Count
        $comments = ([regex]::Matches($content, '#.*')).Count
        
        # Scoring: líneas + clases*10 + funciones*5 + comentarios*2
        $complexity = $lines + ($classes * 10) + ($functions * 5) + ($comments * 2)
        
        return $complexity
    }
    catch {
        return 0
    }
}

function Find-BestAgentImplementation {
    param([string]$AgentPattern, [array]$CandidateFiles)
    
    $bestFile = $null
    $bestScore = 0
    
    foreach ($file in $CandidateFiles) {
        $score = 0
        
        # Factor 1: Complejidad del archivo (40%)
        $complexity = Get-FileComplexity $file.FullName
        $score += $complexity * 0.4
        
        # Factor 2: Fecha de modificación (20%)
        $daysSinceModified = ((Get-Date) - $file.LastWriteTime).Days
        $freshnessScore = [Math]::Max(0, 365 - $daysSinceModified)
        $score += $freshnessScore * 0.2
        
        # Factor 3: Nombre del archivo (20%)
        $nameScore = 0
        if ($file.Name -match $AgentPattern -and $file.Name -notmatch 'test|temp|backup|old') {
            $nameScore = 100
        }
        $score += $nameScore * 0.2
        
        # Factor 4: Ubicación del archivo (20%)
        $pathScore = 0
        if ($file.Directory.Name -match 'agents|core|main') {
            $pathScore = 100
        } elseif ($file.Directory.Name -match 'test|temp|backup') {
            $pathScore = 0
        } else {
            $pathScore = 50
        }
        $score += $pathScore * 0.2
        
        if ($score -gt $bestScore) {
            $bestScore = $score
            $bestFile = $file
        }
    }
    
    return @{
        file = $bestFile
        score = $bestScore
        complexity = if ($bestFile) { Get-FileComplexity $bestFile.FullName } else { 0 }
    }
}

function Compare-FileContent {
    param([string]$File1, [string]$File2)
    
    try {
        $content1 = Get-Content $File1 -Raw | ForEach-Object { $_ -replace '\s+', ' ' }
        $content2 = Get-Content $File2 -Raw | ForEach-Object { $_ -replace '\s+', ' ' }
        
        # Comparar contenido normalizado (sin espacios)
        return $content1 -eq $content2
    }
    catch {
        return $false
    }
}

function Create-ConsolidatedAgent {
    param(
        [string]$AgentPattern,
        [string]$TargetFilename,
        [array]$SourceFiles,
        [string]$OutputPath
    )
    
    # Agrupar archivos idénticos usando diff
    $uniqueImplementations = @()
    $duplicateGroups = @{}
    
    foreach ($file in $SourceFiles) {
        $foundMatch = $false
        foreach ($unique in $uniqueImplementations) {
            if (Compare-FileContent $file.FullName $unique.FullName) {
                if (-not $duplicateGroups.ContainsKey($unique.FullName)) {
                    $duplicateGroups[$unique.FullName] = @()
                }
                $duplicateGroups[$unique.FullName] += $file
                $foundMatch = $true
                break
            }
        }
        if (-not $foundMatch) {
            $uniqueImplementations += $file
        }
    }
    
    Write-ColorOutput "  Implementaciones únicas: $($uniqueImplementations.Count)" "Info"
    Write-ColorOutput "  Duplicados exactos: $($SourceFiles.Count - $uniqueImplementations.Count)" "Warning"
    
    # Seleccionar la mejor implementación única
    $bestImplementation = Find-BestAgentImplementation $AgentPattern $uniqueImplementations
    
    if (-not $bestImplementation.file) {
        Write-ColorOutput "No se encontró implementación válida para $AgentPattern" "Warning"
        return $null
    }
    
    $sourceFile = $bestImplementation.file
    $targetPath = Join-Path $OutputPath $TargetFilename
    
    try {
        # Leer contenido del mejor archivo
        $content = Get-Content $sourceFile.FullName -Raw
        
        # Aplicar naming conventions
        $content = $content -replace 'def\s+([A-Z][a-zA-Z0-9_]*)\s*\(', 'def ${1,,}('
        $content = $content -replace 'class\s+([a-z][a-zA-Z0-9_]*)', 'class ${1^}'
        
        # Header con información de consolidación y trazabilidad
        $duplicatesList = if ($duplicateGroups.ContainsKey($sourceFile.FullName)) {
            ($duplicateGroups[$sourceFile.FullName] | ForEach-Object { $_.FullName }) -join "`n# - "
        } else { "Ninguno" }
        
        $consolidationHeader = @"
# ================================================================
# $($TargetFilename.ToUpper().Replace('.PY', ''))
# Agente consolidado automáticamente con deduplicación inteligente
# ================================================================
# Migrated from: $($sourceFile.FullName)
# Complejidad: $($bestImplementation.complexity)
# Score: $([Math]::Round($bestImplementation.score, 2))
# Consolidado: $(Get-Date)
# Duplicados eliminados:
# - $duplicatesList
# ================================================================

"@
        
        # Combinar header con contenido
        $finalContent = $consolidationHeader + $content
        
        if (-not $DryRun) {
            # Crear directorio si no existe
            $targetDir = Split-Path $targetPath -Parent
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            # Escribir archivo consolidado
            $finalContent | Out-File -FilePath $targetPath -Encoding UTF8
            
            # Crear archivos de referencia para los duplicados (idempotencia)
            $refDir = Join-Path $OutputPath "_references"
            if (-not (Test-Path $refDir)) {
                New-Item -ItemType Directory -Path $refDir -Force | Out-Null
            }
            
            $refContent = @"
# REFERENCIA AUTOMATICA - NO EDITAR
# Este archivo fue consolidado en: $targetPath
# Fecha: $(Get-Date)

from agents.$($OutputPath | Split-Path -Leaf).$($TargetFilename.Replace('.py', '')) import *

# End of reference
"@
            
            # Crear referencias para cada duplicado
            if ($duplicateGroups.ContainsKey($sourceFile.FullName)) {
                foreach ($duplicate in $duplicateGroups[$sourceFile.FullName]) {
                    $refFileName = "$($duplicate.BaseName)_ref.py"
                    $refFilePath = Join-Path $refDir $refFileName
                    $refContent | Out-File -FilePath $refFilePath -Encoding UTF8
                }
            }
        }
        
        return @{
            source = $sourceFile.FullName
            target = $targetPath
            complexity = $bestImplementation.complexity
            score = $bestImplementation.score
            alternatives = $SourceFiles.Count - 1
            unique_implementations = $uniqueImplementations.Count
            exact_duplicates = $SourceFiles.Count - $uniqueImplementations.Count
            duplicate_files = if ($duplicateGroups.ContainsKey($sourceFile.FullName)) { $duplicateGroups[$sourceFile.FullName] } else { @() }
        }
    }
    catch {
        Write-ColorOutput "Error consolidando $AgentPattern`: $($_.Exception.Message)" "Error"
        return $null
    }
}

function Create-AgentRegistry {
    param([hashtable]$ConsolidatedAgents, [string]$OutputPath)
    
    $registryContent = @"
# ================================================================
# AGENT_REGISTRY.PY
# Registro centralizado de agentes consolidados
# ================================================================
# Generado automáticamente: $(Get-Date)
# ================================================================

from typing import Dict, List, Any
import importlib
import os

class AgentRegistry:
    def __init__(self):
        self.agents = {}
        self.load_agents()
    
    def load_agents(self):
        """Carga automática de todos los agentes consolidados"""
        
"@

    foreach ($ecosystem in $ConsolidatedAgents.Keys) {
        $registryContent += "`n        # Ecosystem: $ecosystem`n"
        foreach ($agent in $ConsolidatedAgents[$ecosystem]) {
            if ($agent) {
                $agentName = $agent.target | Split-Path -Leaf
                $modulePath = "$ecosystem.$agentName"
                $registryContent += "        self.register_agent('$agentName', '$modulePath')`n"
            }
        }
    }

    $registryContent += @"

    def register_agent(self, name: str, module_path: str):
        """Registra un agente en el registry"""
        try:
            module = importlib.import_module(f'agents.{module_path}')
            self.agents[name] = {
                'module': module,
                'path': module_path,
                'status': 'loaded'
            }
        except Exception as e:
            self.agents[name] = {
                'module': None,
                'path': module_path,
                'status': f'error: {str(e)}'
            }
    
    def get_agent(self, name: str):
        """Obtiene un agente por nombre"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """Lista todos los agentes registrados"""
        return list(self.agents.keys())
    
    def get_agent_status(self, name: str) -> str:
        """Obtiene el status de un agente"""
        agent = self.agents.get(name)
        return agent['status'] if agent else 'not_found'
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica la salud de todos los agentes"""
        healthy = []
        errors = []
        
        for name, agent in self.agents.items():
            if agent['status'] == 'loaded':
                healthy.append(name)
            else:
                errors.append({'name': name, 'error': agent['status']})
        
        return {
            'total_agents': len(self.agents),
            'healthy_agents': len(healthy),
            'error_agents': len(errors),
            'healthy_list': healthy,
            'error_list': errors
        }

# Instancia global del registry
registry = AgentRegistry()

# Funciones de conveniencia
def get_agent(name: str):
    return registry.get_agent(name)

def list_agents():
    return registry.list_agents()

def health_check():
    return registry.health_check()
"@

    $registryPath = Join-Path (Join-Path OutputPath "registry") "agent_registry.py"
    
    if (-not $DryRun) {
        $registryDir = Split-Path $registryPath -Parent
        if (-not (Test-Path $registryDir)) {
            New-Item -ItemType Directory -Path $registryDir -Force | Out-Null
        }
        $registryContent | Out-File -FilePath $registryPath -Encoding UTF8
    }
    
    return $registryPath
}

# ================================================================
# EJECUCIÓN PRINCIPAL
# ================================================================

Write-ColorOutput "INICIANDO CONSOLIDACION AUTOMATICA DE AGENTES" "Header"
Write-ColorOutput "Proyecto: $ProjectPath" "Info"
Write-ColorOutput "Destino: $ConsolidatedPath" "Info"
Write-ColorOutput "Modo: $(if ($DryRun) { 'DRY RUN' } else { 'EJECUCION' })" "Warning"
Write-ColorOutput "============================================================" "Header"

$consolidationResults = @{
    metadata = @{
        start_time = Get-Date
        source_path = (Resolve-Path $ProjectPath).Path
        target_path = $ConsolidatedPath
        dry_run = $DryRun
    }
    consolidated_agents = @{}
    statistics = @{
        total_ecosystems = 0
        total_agents_processed = 0
        successful_consolidations = 0
        failed_consolidations = 0
        total_source_files = 0
        duplicates_eliminated = 0
    }
    registry_path = ""
}

# Crear backup si se solicita
if ($CreateBackup -and -not $DryRun) {
    Write-ColorOutput "Creando backup..." "Info"
    if (Test-Path $BackupPath) {
        Remove-Item $BackupPath -Recurse -Force
    }
    
    $pythonFiles = Get-ChildItem $ProjectPath -Filter "*.py" -Recurse | Where-Object {
        $_.FullName -notmatch '\\\.venv\\' -and $_.FullName -notmatch '\\venv\\'
    }
    
    foreach ($file in $pythonFiles) {
        $relativePath = $file.FullName.Replace((Resolve-Path $ProjectPath).Path, "")
        $backupFilePath = Join-Path $BackupPath $relativePath
        $backupDir = Split-Path $backupFilePath -Parent
        
        if (-not (Test-Path $backupDir)) {
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        }
        
        Copy-Item $file.FullName $backupFilePath
    }
    
    Write-ColorOutput "Backup creado en: $BackupPath" "Success"
}

# Obtener todos los archivos Python del proyecto
Write-ColorOutput "Escaneando archivos Python..." "Info"
$allPythonFiles = Get-ChildItem $ProjectPath -Filter "*.py" -Recurse | Where-Object {
    $_.FullName -notmatch '\\\.venv\\' -and 
    $_.FullName -notmatch '\\venv\\' -and 
    $_.FullName -notmatch '\\__pycache__\\' -and
    $_.FullName -notmatch '\\.git\\'
}

$consolidationResults.statistics.total_source_files = $allPythonFiles.Count
Write-ColorOutput "Archivos Python encontrados: $($allPythonFiles.Count)" "Info"

# Procesar cada ecosistema
foreach ($ecosystem in $CORE_AGENTS_MAP.Keys) {
    Write-ColorOutput "`nProcesando ecosistema: $ecosystem" "Header"
    
    $ecosystemPath = Join-Path $ConsolidatedPath $ecosystem
    $consolidationResults.consolidated_agents[$ecosystem] = @()
    
    foreach ($agentConfig in $CORE_AGENTS_MAP[$ecosystem]) {
        $pattern = $agentConfig.pattern
        $filename = $agentConfig.filename
        
        Write-ColorOutput "Buscando implementaciones de: $pattern" "Info"
        
        # Buscar archivos que coincidan con el patrón
        $candidateFiles = $allPythonFiles | Where-Object {
            $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
            $content -and $content -match $pattern
        }
        
        if ($candidateFiles.Count -gt 0) {
            Write-ColorOutput "  Encontradas $($candidateFiles.Count) implementaciones" "Success"
            
            $consolidatedAgent = Create-ConsolidatedAgent $pattern $filename $candidateFiles $ecosystemPath
            
            if ($consolidatedAgent) {
                $consolidationResults.consolidated_agents[$ecosystem] += $consolidatedAgent
                $consolidationResults.statistics.successful_consolidations++
                $consolidationResults.statistics.duplicates_eliminated += $consolidatedAgent.alternatives
                
                Write-ColorOutput "  Consolidado: $filename (Score: $([Math]::Round($consolidatedAgent.score, 2)))" "Success"
                Write-ColorOutput "  Fuente: $($consolidatedAgent.source | Split-Path -Leaf)" "Info"
                
                if ($consolidatedAgent.alternatives -gt 0) {
                    Write-ColorOutput "  Eliminados: $($consolidatedAgent.alternatives) duplicados" "Warning"
                }
            } else {
                $consolidationResults.statistics.failed_consolidations++
                Write-ColorOutput "  Error consolidando $pattern" "Error"
            }
        } else {
            Write-ColorOutput "  No se encontraron implementaciones de $pattern" "Warning"
            $consolidationResults.statistics.failed_consolidations++
        }
        
        $consolidationResults.statistics.total_agents_processed++
    }
}

$consolidationResults.statistics.total_ecosystems = $CORE_AGENTS_MAP.Keys.Count

# Crear registry centralizado
Write-ColorOutput "`nCreando registry centralizado..." "Header"
$registryPath = Create-AgentRegistry $consolidationResults.consolidated_agents $ConsolidatedPath
$consolidationResults.registry_path = $registryPath

if (-not $DryRun) {
    Write-ColorOutput "Registry creado: $registryPath" "Success"
}

# Crear __init__.py files
Write-ColorOutput "`nCreando archivos __init__.py..." "Info"
foreach ($ecosystem in $CORE_AGENTS_MAP.Keys) {
    $initPath = Join-Path $ConsolidatedPath $ecosystem "__init__.py"
    if (-not $DryRun) {
        $initDir = Split-Path $initPath -Parent
        if (-not (Test-Path $initDir)) {
            New-Item -ItemType Directory -Path $initDir -Force | Out-Null
        }
        "# $ecosystem agents" | Out-File -FilePath $initPath -Encoding UTF8
    }
}

# Root __init__.py
$rootInitPath = Join-Path $ConsolidatedPath "__init__.py"
if (-not $DryRun) {
    "# Consolidated Agents Package" | Out-File -FilePath $rootInitPath -Encoding UTF8
}

# ================================================================
# REPORTE FINAL
# ================================================================

Write-ColorOutput "`nRESUMEN DE CONSOLIDACION" "Header"
Write-ColorOutput "==================================================" "Header"

Write-ColorOutput "Ecosistemas procesados: $($consolidationResults.statistics.total_ecosystems)" "Info"
Write-ColorOutput "Agentes procesados: $($consolidationResults.statistics.total_agents_processed)" "Info"
Write-ColorOutput "Consolidaciones exitosas: $($consolidationResults.statistics.successful_consolidations)" "Success"
Write-ColorOutput "Consolidaciones fallidas: $($consolidationResults.statistics.failed_consolidations)" "Error"
Write-ColorOutput "Archivos fuente totales: $($consolidationResults.statistics.total_source_files)" "Info"
Write-ColorOutput "Duplicados eliminados: $($consolidationResults.statistics.duplicates_eliminated)" "Warning"

$successRate = if ($consolidationResults.statistics.total_agents_processed -gt 0) {
    [Math]::Round(($consolidationResults.statistics.successful_consolidations / $consolidationResults.statistics.total_agents_processed) * 100, 1)
} else { 0 }

Write-ColorOutput "Tasa de éxito: $successRate%" "Emphasis"

if ($DryRun) {
    Write-ColorOutput "`nEJECUTA SIN -DryRun PARA APLICAR CAMBIOS" "Warning"
} else {
    Write-ColorOutput "`nCONSOLIDACION COMPLETADA EXITOSAMENTE" "Success"
    Write-ColorOutput "Agentes consolidados disponibles en: $ConsolidatedPath" "Success"
}

# Guardar reporte
$reportPath = Join-Path $ProjectPath "consolidation_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$consolidationResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
Write-ColorOutput "Reporte guardado en: $reportPath" "Info"

return $consolidationResults
