# ================================================================
# AUDIT-CREDITOSCORE-FINAL.PS1
# Análisis completo del estado actual del proyecto Nadakki AI Suite
# ================================================================

param(
    [string]$ProjectPath = ".",
    [string]$OutputFile = "creditos_core_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').json",
    [switch]$Detailed = $true,
    [switch]$GenerateReport = $true
)

# Configuración de colores para output
$Colors = @{
    Header = 'Cyan'
    Success = 'Green'
    Warning = 'Yellow'
    Error = 'Red'
    Info = 'White'
    Emphasis = 'Magenta'
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Get-FileHash256 {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        return (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash
    }
    return $null
}

function Analyze-PythonFile {
    param([string]$FilePath)
    
    $analysis = @{
        path = $FilePath
        size = (Get-Item $FilePath).Length
        hash = Get-FileHash256 $FilePath
        classes = @()
        functions = @()
        imports = @()
        agents_detected = @()
        lines_of_code = 0
        has_main = $false
        last_modified = (Get-Item $FilePath).LastWriteTime
    }
    
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        $lines = Get-Content $FilePath
        $analysis.lines_of_code = $lines.Count
        
        # Detectar clases
        $analysis.classes = ($content | Select-String -Pattern "^class\s+(\w+)" -AllMatches).Matches | ForEach-Object { $_.Groups[1].Value }
        
        # Detectar funciones
        $analysis.functions = ($content | Select-String -Pattern "^def\s+(\w+)" -AllMatches).Matches | ForEach-Object { $_.Groups[1].Value }
        
        # Detectar imports
        $analysis.imports = ($content | Select-String -Pattern "^(?:from\s+\S+\s+)?import\s+(.+)" -AllMatches).Matches | ForEach-Object { $_.Groups[1].Value }
        
        # Detectar agentes específicos (patrones comunes)
        $agentPatterns = @(
            'SentinelBot', 'DNAProfiler', 'IncomeOracle', 'BehaviorMiner', 'DocumentValidator',
            'QuantumDecision', 'RiskOracle', 'PolicyGuardian', 'TurboApprover',
            'EarlyWarning', 'PortfolioSentinel', 'StressTester', 'MarketRadar', 'RiskMonitor',
            'CollectionMaster', 'ContactOrchestrator', 'PaymentTracker', 'RecoveryOptimizer',
            'ComplianceTracker', 'ProcessGenius', 'CostOptimizer', 'QualityController', 'WorkflowMaster'
        )
        
        foreach ($pattern in $agentPatterns) {
            if ($content -match $pattern) {
                $analysis.agents_detected += $pattern
            }
        }
        
        # Verificar si tiene función main (CORREGIDO)
        $analysis.has_main = $content -match 'if\s+__name__\s*==\s*[''"]__main__[''"]'
    }
    
    return $analysis
}

function Analyze-ConfigFile {
    param([string]$FilePath)
    
    $analysis = @{
        path = $FilePath
        type = [System.IO.Path]::GetExtension($FilePath)
        size = (Get-Item $FilePath).Length
        hash = Get-FileHash256 $FilePath
        valid_json = $false
        config_keys = @()
        agents_configured = @()
        tenants_configured = @()
        last_modified = (Get-Item $FilePath).LastWriteTime
    }
    
    if ($analysis.type -eq '.json') {
        try {
            $jsonContent = Get-Content $FilePath -Raw | ConvertFrom-Json
            $analysis.valid_json = $true
            $analysis.config_keys = ($jsonContent | Get-Member -MemberType NoteProperty).Name
            
            # Buscar configuraciones de agentes
            if ($jsonContent.agents) {
                $analysis.agents_configured = ($jsonContent.agents | Get-Member -MemberType NoteProperty).Name
            }
            
            # Buscar configuraciones de tenants
            if ($jsonContent.tenants) {
                $analysis.tenants_configured = ($jsonContent.tenants | Get-Member -MemberType NoteProperty).Name
            }
        }
        catch {
            $analysis.valid_json = $false
        }
    }
    
    return $analysis
}

# ================================================================
# INICIO DEL ANÁLISIS
# ================================================================

Write-ColorOutput "INICIANDO AUDITORIA COMPLETA DEL CORE DE CREDITOS" "Header"
Write-ColorOutput "Proyecto: $ProjectPath" "Info"
Write-ColorOutput "Timestamp: $(Get-Date)" "Info"
Write-ColorOutput "============================================================" "Header"

$auditResult = @{
    metadata = @{
        audit_date = Get-Date
        project_path = (Resolve-Path $ProjectPath).Path
        powershell_version = $PSVersionTable.PSVersion.ToString()
        user = $env:USERNAME
        computer = $env:COMPUTERNAME
    }
    summary = @{
        total_files = 0
        python_files = 0
        config_files = 0
        agents_implemented = 0
        agents_missing = 0
        total_lines_of_code = 0
        directory_structure_health = "Unknown"
    }
    directory_structure = @{}
    agents_status = @{
        implemented = @()
        missing = @()
        ecosystems = @{}
    }
    files_analysis = @()
    dependencies = @{
        requirements_found = $false
        virtual_env = $false
        python_version = "Unknown"
    }
    recommendations = @()
}

# Verificar estructura de directorios esperada
$expectedDirs = @(
    'agents', 'config', 'src', 'tests', 'docs', 'scripts',
    'agents/originacion', 'agents/decision', 'agents/vigilancia', 
    'agents/recuperacion', 'agents/compliance', 'agents/operacional'
)

Write-ColorOutput "ANALIZANDO ESTRUCTURA DE DIRECTORIOS..." "Header"

foreach ($dir in $expectedDirs) {
    $fullPath = Join-Path $ProjectPath $dir
    $exists = Test-Path $fullPath
    $auditResult.directory_structure[$dir] = @{
        exists = $exists
        path = $fullPath
        file_count = if ($exists) { (Get-ChildItem $fullPath -File -Recurse).Count } else { 0 }
    }
    
    $status = if ($exists) { "[OK]" } else { "[NO]" }
    Write-ColorOutput "$status $dir ($($auditResult.directory_structure[$dir].file_count) archivos)" "Info"
}

# Buscar todos los archivos Python
Write-ColorOutput "`nANALIZANDO ARCHIVOS PYTHON..." "Header"

$pythonFiles = Get-ChildItem $ProjectPath -Filter "*.py" -Recurse -File
$auditResult.summary.python_files = $pythonFiles.Count

foreach ($file in $pythonFiles) {
    Write-ColorOutput "Analizando: $($file.FullName)" "Info"
    $analysis = Analyze-PythonFile $file.FullName
    $auditResult.files_analysis += $analysis
    $auditResult.summary.total_lines_of_code += $analysis.lines_of_code
    
    # Detectar agentes implementados
    if ($analysis.agents_detected.Count -gt 0) {
        $auditResult.agents_status.implemented += $analysis.agents_detected
        $auditResult.summary.agents_implemented += $analysis.agents_detected.Count
    }
}

# Buscar archivos de configuración
Write-ColorOutput "`nANALIZANDO ARCHIVOS DE CONFIGURACION..." "Header"

$configFiles = Get-ChildItem $ProjectPath -Include @("*.json", "*.yaml", "*.yml", "*.ini", "*.cfg", "*.toml") -Recurse -File
$auditResult.summary.config_files = $configFiles.Count

foreach ($file in $configFiles) {
    Write-ColorOutput "Analizando: $($file.FullName)" "Info"
    $analysis = Analyze-ConfigFile $file.FullName
    $auditResult.files_analysis += $analysis
}

# Verificar dependencias
Write-ColorOutput "`nVERIFICANDO DEPENDENCIAS..." "Header"

$requirementsFile = Join-Path $ProjectPath "requirements.txt"
if (Test-Path $requirementsFile) {
    $auditResult.dependencies.requirements_found = $true
    Write-ColorOutput "[OK] requirements.txt encontrado" "Success"
} else {
    Write-ColorOutput "[NO] requirements.txt NO encontrado" "Warning"
}

# Verificar entorno virtual
$venvPaths = @("venv", ".venv", "env", ".env", "nadakki_env", "nadakki_env_clean")
foreach ($venvPath in $venvPaths) {
    $fullVenvPath = Join-Path $ProjectPath $venvPath
    if (Test-Path $fullVenvPath) {
        $auditResult.dependencies.virtual_env = $true
        Write-ColorOutput "[OK] Entorno virtual encontrado: $venvPath" "Success"
        break
    }
}

if (-not $auditResult.dependencies.virtual_env) {
    Write-ColorOutput "[NO] Entorno virtual NO encontrado" "Warning"
}

# Verificar versión de Python disponible
try {
    $pythonVersion = python --version 2>&1
    $auditResult.dependencies.python_version = $pythonVersion
    Write-ColorOutput "[OK] Python disponible: $pythonVersion" "Success"
} catch {
    Write-ColorOutput "[ERROR] Python no disponible en PATH" "Error"
}

# Definir agentes esperados y verificar cuáles faltan
$expectedAgents = @(
    'SentinelBot', 'DNAProfiler', 'IncomeOracle', 'BehaviorMiner', 'DocumentValidator', 'RiskAssessor',
    'QuantumDecision', 'RiskOracle', 'PolicyGuardian', 'TurboApprover',
    'EarlyWarning', 'PortfolioSentinel', 'StressTester', 'MarketRadar', 'RiskMonitor', 'ComplianceTracker',
    'CollectionMaster', 'ContactOrchestrator', 'PaymentTracker', 'RecoveryOptimizer',
    'ProcessGenius', 'CostOptimizer', 'QualityController', 'WorkflowMaster'
)

$implementedAgents = $auditResult.agents_status.implemented | Sort-Object -Unique
$missingAgents = $expectedAgents | Where-Object { $_ -notin $implementedAgents }

$auditResult.agents_status.missing = $missingAgents
$auditResult.summary.agents_missing = $missingAgents.Count

# Organizar agentes por ecosistemas
$ecosystems = @{
    'originacion' = @('SentinelBot', 'DNAProfiler', 'IncomeOracle', 'BehaviorMiner', 'DocumentValidator', 'RiskAssessor')
    'decision' = @('QuantumDecision', 'RiskOracle', 'PolicyGuardian', 'TurboApprover')
    'vigilancia' = @('EarlyWarning', 'PortfolioSentinel', 'StressTester', 'MarketRadar', 'RiskMonitor', 'ComplianceTracker')
    'recuperacion' = @('CollectionMaster', 'ContactOrchestrator', 'PaymentTracker', 'RecoveryOptimizer')
    'operacional' = @('ProcessGenius', 'CostOptimizer', 'QualityController', 'WorkflowMaster')
}

foreach ($ecosystem in $ecosystems.Keys) {
    $ecosystemAgents = $ecosystems[$ecosystem]
    $implemented = $ecosystemAgents | Where-Object { $_ -in $implementedAgents }
    $missing = $ecosystemAgents | Where-Object { $_ -notin $implementedAgents }
    
    $auditResult.agents_status.ecosystems[$ecosystem] = @{
        total = $ecosystemAgents.Count
        implemented = $implemented
        missing = $missing
        completion_percent = [math]::Round(($implemented.Count / $ecosystemAgents.Count) * 100, 1)
    }
}

# Generar recomendaciones
Write-ColorOutput "`nGENERANDO RECOMENDACIONES..." "Header"

if ($auditResult.summary.agents_implemented -eq 0) {
    $auditResult.recommendations += "CRITICO: No se encontraron agentes implementados. Proyecto en fase inicial."
}

if ($auditResult.summary.agents_missing -gt 20) {
    $auditResult.recommendations += "ALTO: Faltan mas de 20 agentes por implementar."
}

if (-not $auditResult.dependencies.requirements_found) {
    $auditResult.recommendations += "Crear archivo requirements.txt con dependencias del proyecto."
}

if (-not $auditResult.dependencies.virtual_env) {
    $auditResult.recommendations += "Configurar entorno virtual para el proyecto."
}

foreach ($ecosystem in $auditResult.agents_status.ecosystems.Keys) {
    $ecoData = $auditResult.agents_status.ecosystems[$ecosystem]
    if ($ecoData.completion_percent -lt 50) {
        $auditResult.recommendations += "Ecosistema '$ecosystem': Solo $($ecoData.completion_percent)% completo. Priorizar implementacion."
    }
}

# Calcular estadísticas finales
$auditResult.summary.total_files = $auditResult.files_analysis.Count
$auditResult.summary.directory_structure_health = if ($expectedDirs | ForEach-Object { $auditResult.directory_structure[$_].exists } | Where-Object { $_ -eq $false }) { "Incompleta" } else { "Completa" }

# ================================================================
# GENERAR REPORTE FINAL
# ================================================================

Write-ColorOutput "`nRESUMEN EJECUTIVO" "Header"
Write-ColorOutput "==================================================" "Header"

Write-ColorOutput "Archivos totales analizados: $($auditResult.summary.total_files)" "Info"
Write-ColorOutput "Archivos Python: $($auditResult.summary.python_files)" "Info"
Write-ColorOutput "Archivos de configuracion: $($auditResult.summary.config_files)" "Info"
Write-ColorOutput "Lineas de codigo total: $($auditResult.summary.total_lines_of_code)" "Info"
Write-ColorOutput "Estructura de directorios: $($auditResult.summary.directory_structure_health)" "Info"

Write-ColorOutput "`nESTADO DE AGENTES:" "Emphasis"
Write-ColorOutput "Implementados: $($auditResult.summary.agents_implemented)" "Success"
Write-ColorOutput "Faltantes: $($auditResult.summary.agents_missing)" "Warning"

foreach ($ecosystem in $auditResult.agents_status.ecosystems.Keys) {
    $ecoData = $auditResult.agents_status.ecosystems[$ecosystem]
    $color = if ($ecoData.completion_percent -ge 80) { "Success" } elseif ($ecoData.completion_percent -ge 50) { "Warning" } else { "Error" }
    Write-ColorOutput "$ecosystem`: $($ecoData.completion_percent)% ($($ecoData.implemented.Count)/$($ecoData.total))" $color
}

if ($auditResult.recommendations.Count -gt 0) {
    Write-ColorOutput "`nRECOMENDACIONES:" "Emphasis"
    foreach ($rec in $auditResult.recommendations) {
        Write-ColorOutput "   $rec" "Warning"
    }
}

# Guardar resultado en JSON
$jsonOutput = $auditResult | ConvertTo-Json -Depth 10
$outputPath = Join-Path $ProjectPath $OutputFile
$jsonOutput | Out-File -FilePath $outputPath -Encoding UTF8

Write-ColorOutput "`nReporte completo guardado en: $outputPath" "Success"
Write-ColorOutput "Auditoria completada exitosamente." "Header"

# Si se solicita, mostrar agentes faltantes detalladamente
if ($Detailed -and $auditResult.agents_status.missing.Count -gt 0) {
    Write-ColorOutput "`nAGENTES FALTANTES DETALLADOS:" "Header"
    foreach ($ecosystem in $auditResult.agents_status.ecosystems.Keys) {
        $missing = $auditResult.agents_status.ecosystems[$ecosystem].missing
        if ($missing.Count -gt 0) {
            Write-ColorOutput "`n$ecosystem`:" "Emphasis"
            foreach ($agent in $missing) {
                Write-ColorOutput "   - $agent" "Error"
            }
        }
    }
}

# Retornar el objeto de auditoría para uso programático
return $auditResult