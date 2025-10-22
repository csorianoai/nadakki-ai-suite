# ================================================================
# DEEP-AGENT-SEARCH.PS1
# Búsqueda exhaustiva de agentes crediticios y reorganización
# ================================================================

param(
    [string]$ProjectPath = ".",
    [string]$OutputFile = "deep_agent_inventory_$(Get-Date -Format 'yyyyMMdd_HHmmss').json",
    [switch]$ReorganizeAgents = $false,
    [switch]$CreateRegistry = $true
)

# Lista exhaustiva de todos los agentes posibles (expandida)
$ALL_POSSIBLE_AGENTS = @(
    # ORIGINACION
    'SentinelBot', 'SentinelBotAdvanced', 'DNAProfiler', 'IncomeOracle', 'BehaviorMiner', 
    'DocumentValidator', 'RiskAssessor', 'RiskAssessorBasic', 'FraudDetector',
    'KYCValidator', 'CreditScorer', 'ApplicationProcessor', 'DataEnricher',
    
    # DECISION
    'QuantumDecision', 'QuantumDecisionEngine', 'RiskOracle', 'RiskOracleBasic', 
    'PolicyGuardian', 'TurboApprover', 'TurboApproverBasic', 'DecisionEngine',
    'AutoApprover', 'RiskEvaluator', 'CreditDecision', 'ApprovalEngine',
    
    # VIGILANCIA
    'EarlyWarning', 'EarlyWarningSystem', 'PortfolioSentinel', 'StressTester', 
    'StressTesterBasic', 'MarketRadar', 'MarketRadarBasic', 'RiskMonitor',
    'ComplianceTracker', 'ComplianceTrackerBasic', 'AlertSystem', 'MonitorBot',
    'WatchdogAgent', 'PerformanceMonitor', 'ThresholdMonitor',
    
    # RECUPERACION
    'CollectionMaster', 'CollectionMasterBasic', 'ContactOrchestrator', 
    'PaymentTracker', 'RecoveryOptimizer', 'RecoveryOptimizerBasic',
    'DebtCollector', 'PaymentProcessor', 'NegotiationBot', 'LegalPathway',
    'RecoveryAgent', 'CollectionAgent', 'PaymentPlanner',
    
    # COMPLIANCE
    'ComplianceWatchdog', 'DocGuardian', 'AuditMaster', 'RegulatoryRadar',
    'LegalCompliance', 'ComplianceChecker', 'AuditAgent', 'RegulationBot',
    
    # OPERACIONAL
    'ProcessGenius', 'CostOptimizer', 'QualityController', 'WorkflowMaster',
    'WorkflowMasterBasic', 'EfficiencyAgent', 'OptimizationEngine', 'ProcessBot',
    'QualityAgent', 'PerformanceOptimizer',
    
    # EXPERIENCIA
    'CustomerExperience', 'NotificationBot', 'CommunicationHub', 'FeedbackAnalyzer',
    'SatisfactionTracker', 'UXOptimizer', 'CustomerJourney',
    
    # INTELIGENCIA
    'DataAnalyzer', 'PredictiveEngine', 'TrendAnalyzer', 'BusinessIntelligence',
    'ReportGenerator', 'InsightEngine', 'AnalyticsBot',
    
    # FORTALEZA/SEGURIDAD
    'SecurityGuard', 'CyberSentinel', 'DataProtector', 'AccessController',
    'EncryptionBot', 'SecurityMonitor', 'ThreatDetector'
)

# Patrones de búsqueda exhaustiva
$SEARCH_PATTERNS = @(
    # Patrones de clase
    'class\s+(\w*(?:Bot|Agent|Engine|Oracle|Guardian|Master|Tracker|Monitor|Analyzer|Controller|Optimizer|Processor|Validator|Detector|Generator|Hub|Sentinel|Watchdog|Genius|Radar)\w*)',
    
    # Patrones de función/método específicos
    'def\s+(\w*(?:bot|agent|engine|oracle|guardian|master|tracker|monitor|analyzer|controller|optimizer|processor|validator|detector|generator|hub|sentinel|watchdog|genius|radar)\w*)',
    
    # Patrones de variables/instancias
    '(\w*(?:Bot|Agent|Engine|Oracle|Guardian|Master|Tracker|Monitor|Analyzer|Controller|Optimizer|Processor|Validator|Detector|Generator|Hub|Sentinel|Watchdog|Genius|Radar)\w*)\s*=',
    
    # Patrones de importación
    'from\s+.*(?:agent|bot|engine)\s+import\s+(\w+)',
    'import\s+.*\.(\w*(?:Bot|Agent|Engine|Oracle|Guardian|Master|Tracker|Monitor|Analyzer|Controller|Optimizer|Processor|Validator|Detector|Generator|Hub|Sentinel|Watchdog|Genius|Radar)\w*)',
    
    # Patrones de comentarios/documentación
    '#.*(?:Agent|Bot|Engine):\s*(\w+)',
    '""".*(?:Agent|Bot|Engine):\s*(\w+)',
    
    # Patrones específicos del proyecto
    'register_agent\s*\(\s*[''"](\w+)[''"]',
    'agent_name\s*=\s*[''"](\w+)[''"]',
    'AGENT_TYPE\s*=\s*[''"](\w+)[''"]'
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    $Colors = @{
        Header = 'Cyan'; Success = 'Green'; Warning = 'Yellow'
        Error = 'Red'; Info = 'White'; Emphasis = 'Magenta'
    }
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Search-AgentsInFile {
    param([string]$FilePath)
    
    $foundAgents = @()
    $fileInfo = @{
        path = $FilePath
        size = (Get-Item $FilePath).Length
        agents_found = @()
        patterns_matched = @()
        content_preview = ""
    }
    
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
        if (-not $content) { return $fileInfo }
        
        # Guardar preview del contenido
        $fileInfo.content_preview = ($content -split "`n" | Select-Object -First 5) -join " | "
        
        # Buscar con cada patrón
        foreach ($pattern in $SEARCH_PATTERNS) {
            $matches = [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Multiline)
            
            foreach ($match in $matches) {
                if ($match.Groups.Count -gt 1 -and $match.Groups[1].Value) {
                    $agentName = $match.Groups[1].Value.Trim()
                    
                    # Filtrar nombres muy cortos o genéricos
                    if ($agentName.Length -gt 3 -and $agentName -notmatch '^(test|main|init|base|core|util|helper)$') {
                        $foundAgents += $agentName
                        $fileInfo.patterns_matched += @{
                            pattern = $pattern
                            match = $agentName
                            context = $match.Value
                        }
                    }
                }
            }
        }
        
        # Buscar agentes conocidos directamente en el texto
        foreach ($knownAgent in $ALL_POSSIBLE_AGENTS) {
            if ($content -match [regex]::Escape($knownAgent)) {
                $foundAgents += $knownAgent
            }
        }
        
        $fileInfo.agents_found = $foundAgents | Sort-Object -Unique
        
    } catch {
        Write-ColorOutput "Error procesando $FilePath`: $($_.Exception.Message)" "Warning"
    }
    
    return $fileInfo
}

function Get-FilesByExtension {
    param([string]$Path, [string[]]$Extensions, [string[]]$ExcludePaths = @())
    
    $allFiles = @()
    
    foreach ($ext in $Extensions) {
        $files = Get-ChildItem $Path -Filter "*.$ext" -Recurse -File | Where-Object {
            $excluded = $false
            foreach ($excludePath in $ExcludePaths) {
                if ($_.FullName -match [regex]::Escape($excludePath)) {
                    $excluded = $true
                    break
                }
            }
            -not $excluded
        }
        $allFiles += $files
    }
    
    return $allFiles
}

# ================================================================
# BÚSQUEDA EXHAUSTIVA
# ================================================================

Write-ColorOutput "INICIANDO BÚSQUEDA EXHAUSTIVA DE AGENTES" "Header"
Write-ColorOutput "Proyecto: $ProjectPath" "Info"
Write-ColorOutput "Timestamp: $(Get-Date)" "Info"
Write-ColorOutput "============================================================" "Header"

$searchResult = @{
    metadata = @{
        search_date = Get-Date
        project_path = (Resolve-Path $ProjectPath).Path
        total_patterns = $SEARCH_PATTERNS.Count
        total_known_agents = $ALL_POSSIBLE_AGENTS.Count
    }
    files_analyzed = @()
    agents_discovered = @{}
    summary = @{
        total_files_searched = 0
        total_agents_found = 0
        unique_agents = @()
        agents_by_category = @{}
        orphaned_agents = @()
        duplicate_agents = @()
    }
    reorganization_plan = @{}
}

# Excluir directorios problemáticos
$excludePaths = @('.venv', 'venv', '__pycache__', '.git', 'node_modules', '.env')

# Buscar en archivos Python
Write-ColorOutput "Buscando en archivos Python..." "Header"
$pythonFiles = Get-FilesByExtension $ProjectPath @('py') $excludePaths
$searchResult.summary.total_files_searched += $pythonFiles.Count

foreach ($file in $pythonFiles) {
    Write-ColorOutput "Analizando: $($file.Name)" "Info"
    $fileResult = Search-AgentsInFile $file.FullName
    
    if ($fileResult.agents_found.Count -gt 0) {
        $searchResult.files_analyzed += $fileResult
        
        foreach ($agent in $fileResult.agents_found) {
            if (-not $searchResult.agents_discovered.ContainsKey($agent)) {
                $searchResult.agents_discovered[$agent] = @()
            }
            $searchResult.agents_discovered[$agent] += @{
                file = $file.FullName
                file_name = $file.Name
                directory = $file.Directory.Name
            }
        }
    }
}

# Buscar en archivos de configuración
Write-ColorOutput "Buscando en archivos de configuración..." "Header"
$configFiles = Get-FilesByExtension $ProjectPath @('json', 'yaml', 'yml', 'toml', 'cfg', 'ini') $excludePaths
$searchResult.summary.total_files_searched += $configFiles.Count

foreach ($file in $configFiles) {
    Write-ColorOutput "Analizando: $($file.Name)" "Info"
    $fileResult = Search-AgentsInFile $file.FullName
    
    if ($fileResult.agents_found.Count -gt 0) {
        $searchResult.files_analyzed += $fileResult
        
        foreach ($agent in $fileResult.agents_found) {
            if (-not $searchResult.agents_discovered.ContainsKey($agent)) {
                $searchResult.agents_discovered[$agent] = @()
            }
            $searchResult.agents_discovered[$agent] += @{
                file = $file.FullName
                file_name = $file.Name
                directory = $file.Directory.Name
            }
        }
    }
}

# Buscar en documentos de texto
Write-ColorOutput "Buscando en documentación..." "Header"
$docFiles = Get-FilesByExtension $ProjectPath @('md', 'txt', 'rst') $excludePaths
$searchResult.summary.total_files_searched += $docFiles.Count

foreach ($file in $docFiles) {
    Write-ColorOutput "Analizando: $($file.Name)" "Info"
    $fileResult = Search-AgentsInFile $file.FullName
    
    if ($fileResult.agents_found.Count -gt 0) {
        $searchResult.files_analyzed += $fileResult
        
        foreach ($agent in $fileResult.agents_found) {
            if (-not $searchResult.agents_discovered.ContainsKey($agent)) {
                $searchResult.agents_discovered[$agent] = @()
            }
            $searchResult.agents_discovered[$agent] += @{
                file = $file.FullName
                file_name = $file.Name
                directory = $file.Directory.Name
            }
        }
    }
}

# Analizar resultados
Write-ColorOutput "Analizando resultados..." "Header"

$searchResult.summary.unique_agents = $searchResult.agents_discovered.Keys | Sort-Object
$searchResult.summary.total_agents_found = $searchResult.summary.unique_agents.Count

# Categorizar agentes encontrados
$categories = @{
    'originacion' = @('Sentinel', 'DNA', 'Income', 'Behavior', 'Document', 'Risk', 'Fraud', 'KYC', 'Credit', 'Application', 'Data')
    'decision' = @('Quantum', 'Decision', 'Oracle', 'Policy', 'Turbo', 'Approval', 'Auto', 'Evaluator')
    'vigilancia' = @('Early', 'Warning', 'Portfolio', 'Stress', 'Market', 'Monitor', 'Alert', 'Watchdog', 'Performance', 'Threshold')
    'recuperacion' = @('Collection', 'Contact', 'Payment', 'Recovery', 'Debt', 'Negotiation', 'Legal', 'Planner')
    'compliance' = @('Compliance', 'Audit', 'Regulatory', 'Legal', 'Regulation')
    'operacional' = @('Process', 'Cost', 'Quality', 'Workflow', 'Efficiency', 'Optimization', 'Performance')
    'experiencia' = @('Customer', 'Notification', 'Communication', 'Feedback', 'Satisfaction', 'UX', 'Journey')
    'inteligencia' = @('Data', 'Predictive', 'Trend', 'Business', 'Report', 'Insight', 'Analytics')
    'seguridad' = @('Security', 'Cyber', 'Protection', 'Access', 'Encryption', 'Threat')
}

foreach ($category in $categories.Keys) {
    $searchResult.summary.agents_by_category[$category] = @()
    foreach ($agent in $searchResult.summary.unique_agents) {
        foreach ($keyword in $categories[$category]) {
            if ($agent -match $keyword) {
                $searchResult.summary.agents_by_category[$category] += $agent
                break
            }
        }
    }
}

# Identificar duplicados y huérfanos
foreach ($agent in $searchResult.summary.unique_agents) {
    $locations = $searchResult.agents_discovered[$agent]
    if ($locations.Count -gt 1) {
        $searchResult.summary.duplicate_agents += @{
            agent = $agent
            locations = $locations
        }
    }
}

# Buscar agentes sin categoría clara
foreach ($agent in $searchResult.summary.unique_agents) {
    $categorized = $false
    foreach ($category in $categories.Keys) {
        if ($searchResult.summary.agents_by_category[$category] -contains $agent) {
            $categorized = $true
            break
        }
    }
    if (-not $categorized) {
        $searchResult.summary.orphaned_agents += $agent
    }
}

# ================================================================
# GENERAR PLAN DE REORGANIZACIÓN
# ================================================================

if ($ReorganizeAgents) {
    Write-ColorOutput "Generando plan de reorganización..." "Header"
    
    $searchResult.reorganization_plan = @{
        target_structure = @{
            'agents/originacion' = $searchResult.summary.agents_by_category['originacion']
            'agents/decision' = $searchResult.summary.agents_by_category['decision']
            'agents/vigilancia' = $searchResult.summary.agents_by_category['vigilancia']
            'agents/recuperacion' = $searchResult.summary.agents_by_category['recuperacion']
            'agents/compliance' = $searchResult.summary.agents_by_category['compliance']
            'agents/operacional' = $searchResult.summary.agents_by_category['operacional']
            'agents/experiencia' = $searchResult.summary.agents_by_category['experiencia']
            'agents/inteligencia' = $searchResult.summary.agents_by_category['inteligencia']
            'agents/seguridad' = $searchResult.summary.agents_by_category['seguridad']
            'agents/misc' = $searchResult.summary.orphaned_agents
        }
        move_operations = @()
        consolidation_needed = $searchResult.summary.duplicate_agents
    }
}

# ================================================================
# GENERAR REPORTE
# ================================================================

Write-ColorOutput "`nRESUMEN DE BÚSQUEDA EXHAUSTIVA" "Header"
Write-ColorOutput "==================================================" "Header"

Write-ColorOutput "Archivos analizados: $($searchResult.summary.total_files_searched)" "Info"
Write-ColorOutput "Agentes únicos encontrados: $($searchResult.summary.total_agents_found)" "Success"
Write-ColorOutput "Archivos con agentes: $($searchResult.files_analyzed.Count)" "Info"

Write-ColorOutput "`nAGENTES POR CATEGORÍA:" "Emphasis"
foreach ($category in $searchResult.summary.agents_by_category.Keys) {
    $count = $searchResult.summary.agents_by_category[$category].Count
    $color = if ($count -gt 5) { "Success" } elseif ($count -gt 2) { "Warning" } else { "Error" }
    Write-ColorOutput "$category`: $count agentes" $color
}

if ($searchResult.summary.orphaned_agents.Count -gt 0) {
    Write-ColorOutput "`nAGENTES SIN CATEGORÍA:" "Warning"
    foreach ($agent in $searchResult.summary.orphaned_agents) {
        Write-ColorOutput "  - $agent" "Warning"
    }
}

if ($searchResult.summary.duplicate_agents.Count -gt 0) {
    Write-ColorOutput "`nAGENTES DUPLICADOS:" "Error"
    foreach ($duplicate in $searchResult.summary.duplicate_agents) {
        Write-ColorOutput "  - $($duplicate.agent) (encontrado en $($duplicate.locations.Count) ubicaciones)" "Error"
    }
}

Write-ColorOutput "`nTOP 20 AGENTES ENCONTRADOS:" "Header"
$top20 = $searchResult.summary.unique_agents | Select-Object -First 20
foreach ($agent in $top20) {
    $locations = $searchResult.agents_discovered[$agent].Count
    Write-ColorOutput "  - $agent (en $locations archivo(s))" "Info"
}

# Guardar resultado completo
$jsonOutput = $searchResult | ConvertTo-Json -Depth 15
$outputPath = Join-Path $ProjectPath $OutputFile
$jsonOutput | Out-File -FilePath $outputPath -Encoding UTF8

Write-ColorOutput "`nInventario completo guardado en: $outputPath" "Success"
Write-ColorOutput "Búsqueda exhaustiva completada." "Header"

return $searchResult