# ============================================================================
# NADAKKI PROJECT AUDIT SCRIPT - COMPREHENSIVE FILE SYSTEM ANALYSIS
# Versión: 2.0
# Propósito: Auditoría completa del proyecto para identificar arquitectura real
# ============================================================================

param(
    [string]$RootPath = ".",
    [switch]$Detailed = $false,
    [switch]$ExportJson = $true,
    [switch]$ScanAllDrives = $false
)

$ErrorActionPreference = "Continue"
$WarningPreference = "Continue"

# Colores para output
$Colors = @{
    Header = "Cyan"
    Success = "Green" 
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
    Critical = "Magenta"
}

function Write-ColorOutput {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Get-FileHash-Safe {
    param([string]$Path)
    try {
        if (Test-Path $Path -PathType Leaf) {
            $hash = Get-FileHash -Path $Path -Algorithm SHA256 -ErrorAction SilentlyContinue
            return $hash.Hash
        }
    }
    catch {
        return "ERROR"
    }
    return "N/A"
}

function Get-DirectorySize {
    param([string]$Path)
    try {
        $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1MB, 2)
    }
    catch {
        return 0
    }
}

function Scan-ForNadakkiProjects {
    Write-ColorOutput "`n🔍 SCANNING FOR NADAKKI PROJECTS..." "Header"
    
    $potentialPaths = @()
    
    # Rutas conocidas de los documentos
    $knownPaths = @(
        "C:\Users\cesar\Projects\nadakki-ai-suite",
        "C:\Users\elena\nadakki-ai-suite", 
        "C:\Users\elena\credicefi-dashboard-public",
        "$env:USERPROFILE\Projects\nadakki-ai-suite",
        "$env:USERPROFILE\Documents\nadakki*",
        "$env:USERPROFILE\Desktop\nadakki*"
    )
    
    # Buscar en ubicaciones conocidas
    foreach ($path in $knownPaths) {
        if ($path -like "*`**") {
            # Búsqueda con wildcard
            $basePath = Split-Path $path -Parent
            $pattern = Split-Path $path -Leaf
            if (Test-Path $basePath) {
                $matches = Get-ChildItem -Path $basePath -Directory -Filter $pattern -ErrorAction SilentlyContinue
                foreach ($match in $matches) {
                    $potentialPaths += $match.FullName
                }
            }
        } else {
            if (Test-Path $path) {
                $potentialPaths += $path
            }
        }
    }
    
    # Búsqueda en drives si se solicita
    if ($ScanAllDrives) {
        Write-ColorOutput "🔎 Scanning all drives for Nadakki projects..." "Info"
        $drives = Get-PSDrive -PSProvider FileSystem
        foreach ($drive in $drives) {
            try {
                $nadakkiDirs = Get-ChildItem -Path "$($drive.Name):\" -Directory -Filter "*nadakki*" -ErrorAction SilentlyContinue
                foreach ($dir in $nadakkiDirs) {
                    $potentialPaths += $dir.FullName
                }
            }
            catch {
                # Continuar si no se puede acceder al drive
            }
        }
    }
    
    return $potentialPaths | Sort-Object | Get-Unique
}

function Analyze-Project {
    param([string]$ProjectPath)
    
    Write-ColorOutput "`n📂 ANALYZING: $ProjectPath" "Info"
    
    $analysis = @{
        Path = $ProjectPath
        Exists = Test-Path $ProjectPath
        Type = "Unknown"
        Files = @()
        Structure = @{}
        Technologies = @()
        Agents = @()
        Size = 0
        LastModified = $null
    }
    
    if (-not $analysis.Exists) {
        Write-ColorOutput "❌ Path does not exist" "Error"
        return $analysis
    }
    
    $analysis.Size = Get-DirectorySize -Path $ProjectPath
    $analysis.LastModified = (Get-Item $ProjectPath).LastWriteTime
    
    # Analizar archivos principales
    $keyFiles = @(
        @{Pattern = "*.html"; Type = "Frontend"},
        @{Pattern = "*.php"; Type = "WordPress"},
        @{Pattern = "*.py"; Type = "Python"},
        @{Pattern = "app.py"; Type = "Flask"},
        @{Pattern = "main.py"; Type = "FastAPI"},
        @{Pattern = "package.json"; Type = "Node.js"},
        @{Pattern = "requirements.txt"; Type = "Python"},
        @{Pattern = "composer.json"; Type = "PHP"},
        @{Pattern = "*.sql"; Type = "Database"},
        @{Pattern = "*.json"; Type = "Config"},
        @{Pattern = "*.yaml"; Type = "Config"},
        @{Pattern = "*.yml"; Type = "Config"}
    )
    
    foreach ($fileType in $keyFiles) {
        $files = Get-ChildItem -Path $ProjectPath -Filter $fileType.Pattern -Recurse -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $analysis.Files += @{
                Name = $file.Name
                Path = $file.FullName.Replace($ProjectPath, "")
                Type = $fileType.Type
                Size = [math]::Round($file.Length / 1KB, 2)
                Hash = Get-FileHash-Safe -Path $file.FullName
                LastModified = $file.LastWriteTime
            }
            
            if ($analysis.Technologies -notcontains $fileType.Type) {
                $analysis.Technologies += $fileType.Type
            }
        }
    }
    
    # Detectar tipo de proyecto
    if ($analysis.Files | Where-Object {$_.Name -like "*.php" -and $_.Name -like "*nadakki*"}) {
        $analysis.Type = "WordPress Plugin"
    }
    elseif ($analysis.Files | Where-Object {$_.Name -eq "app.py"}) {
        $analysis.Type = "Flask Application"
    }
    elseif ($analysis.Files | Where-Object {$_.Name -eq "main.py"}) {
        $analysis.Type = "FastAPI Application"
    }
    elseif ($analysis.Files | Where-Object {$_.Name -like "*enterprise*.html"}) {
        $analysis.Type = "Frontend Dashboard"
    }
    
    # Buscar agentes
    $agentPatterns = @("agent", "Agent", "AGENT")
    foreach ($pattern in $agentPatterns) {
        $agentFiles = $analysis.Files | Where-Object {$_.Name -like "*$pattern*"}
        foreach ($agentFile in $agentFiles) {
            if ($analysis.Agents -notcontains $agentFile.Name) {
                $analysis.Agents += $agentFile.Name
            }
        }
    }
    
    # Analizar estructura de directorios
    try {
        $dirs = Get-ChildItem -Path $ProjectPath -Directory -ErrorAction SilentlyContinue
        foreach ($dir in $dirs) {
            $fileCount = (Get-ChildItem -Path $dir.FullName -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
            $analysis.Structure[$dir.Name] = @{
                FileCount = $fileCount
                Size = Get-DirectorySize -Path $dir.FullName
            }
        }
    }
    catch {
        Write-ColorOutput "⚠️ Could not analyze directory structure" "Warning"
    }
    
    return $analysis
}

function Export-AuditReport {
    param([array]$Projects, [string]$OutputPath)
    
    $report = @{
        AuditTimestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        TotalProjects = $Projects.Count
        Projects = $Projects
        Summary = @{
            TotalFiles = ($Projects | ForEach-Object {$_.Files.Count} | Measure-Object -Sum).Sum
            TotalSize = [math]::Round(($Projects | ForEach-Object {$_.Size} | Measure-Object -Sum).Sum, 2)
            Technologies = ($Projects | ForEach-Object {$_.Technologies} | Sort-Object | Get-Unique)
            ProjectTypes = ($Projects | ForEach-Object {$_.Type} | Sort-Object | Get-Unique)
        }
    }
    
    try {
        $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
        Write-ColorOutput "✅ Report exported to: $OutputPath" "Success"
    }
    catch {
        Write-ColorOutput "❌ Failed to export report: $_" "Error"
    }
}

function Show-ProjectSummary {
    param([object]$Project)
    
    Write-ColorOutput "`n" + "="*60 "Info"
    Write-ColorOutput "📁 PROJECT: $(Split-Path $Project.Path -Leaf)" "Header"
    Write-ColorOutput "="*60 "Info"
    Write-ColorOutput "📍 Path: $($Project.Path)" "Info"
    Write-ColorOutput "🏷️  Type: $($Project.Type)" "Info"
    Write-ColorOutput "💾 Size: $($Project.Size) MB" "Info"
    Write-ColorOutput "📄 Files: $($Project.Files.Count)" "Info"
    Write-ColorOutput "🔧 Technologies: $($Project.Technologies -join ', ')" "Info"
    Write-ColorOutput "🤖 Agents Found: $($Project.Agents.Count)" "Info"
    Write-ColorOutput "📅 Last Modified: $($Project.LastModified)" "Info"
    
    if ($Project.Structure.Count -gt 0) {
        Write-ColorOutput "`n📂 DIRECTORY STRUCTURE:" "Header"
        foreach ($dir in $Project.Structure.GetEnumerator()) {
            Write-ColorOutput "  └── $($dir.Key) ($($dir.Value.FileCount) files, $($dir.Value.Size) MB)" "Info"
        }
    }
    
    if ($Detailed -and $Project.Files.Count -gt 0) {
        Write-ColorOutput "`n📄 KEY FILES:" "Header"
        $Project.Files | Sort-Object Type, Name | ForEach-Object {
            Write-ColorOutput "  [$($_.Type)] $($_.Name) ($($_.Size) KB)" "Info"
        }
    }
    
    if ($Project.Agents.Count -gt 0) {
        Write-ColorOutput "`n🤖 AGENTS DETECTED:" "Header"
        $Project.Agents | ForEach-Object {
            Write-ColorOutput "  🔹 $_" "Success"
        }
    }
}

function Find-CriticalFiles {
    param([array]$Projects)
    
    Write-ColorOutput "`n🔍 CRITICAL FILES ANALYSIS" "Header"
    Write-ColorOutput "="*60 "Info"
    
    $criticalPatterns = @{
        "HTML Dashboards" = "*enterprise*.html"
        "Main Applications" = @("app.py", "main.py")
        "Configuration" = @("config.py", "*.json", "*.yaml")
        "Agent Files" = "*agent*.py"
        "WordPress Plugins" = "*nadakki*.php"
        "Requirements" = @("requirements.txt", "package.json")
    }
    
    foreach ($category in $criticalPatterns.GetEnumerator()) {
        Write-ColorOutput "`n📋 $($category.Key):" "Header"
        $found = $false
        
        foreach ($project in $Projects) {
            foreach ($pattern in $category.Value) {
                $matches = $project.Files | Where-Object {$_.Name -like $pattern}
                foreach ($match in $matches) {
                    Write-ColorOutput "  ✅ $($match.Path) ($(Split-Path $project.Path -Leaf))" "Success"
                    $found = $true
                }
            }
        }
        
        if (-not $found) {
            Write-ColorOutput "  ❌ No files found" "Error"
        }
    }
}

function Check-ProjectHealth {
    param([array]$Projects)
    
    Write-ColorOutput "`n🏥 PROJECT HEALTH CHECK" "Header"
    Write-ColorOutput "="*60 "Info"
    
    foreach ($project in $Projects) {
        Write-ColorOutput "`n🔍 Checking: $(Split-Path $project.Path -Leaf)" "Info"
        
        $health = @{
            Score = 0
            Issues = @()
            Strengths = @()
        }
        
        # Check for main application files
        if ($project.Files | Where-Object {$_.Name -in @("app.py", "main.py")}) {
            $health.Score += 20
            $health.Strengths += "Has main application file"
        } else {
            $health.Issues += "Missing main application file"
        }
        
        # Check for configuration
        if ($project.Files | Where-Object {$_.Name -like "*.json" -or $_.Name -like "*.yaml"}) {
            $health.Score += 15
            $health.Strengths += "Has configuration files"
        } else {
            $health.Issues += "Missing configuration files"
        }
        
        # Check for agents
        if ($project.Agents.Count -gt 0) {
            $health.Score += 25
            $health.Strengths += "$($project.Agents.Count) agents detected"
        } else {
            $health.Issues += "No agents detected"
        }
        
        # Check for dependencies
        if ($project.Files | Where-Object {$_.Name -in @("requirements.txt", "package.json")}) {
            $health.Score += 15
            $health.Strengths += "Has dependency management"
        } else {
            $health.Issues += "Missing dependency files"
        }
        
        # Check project size
        if ($project.Size -gt 10) {
            $health.Score += 15
            $health.Strengths += "Substantial project size ($($project.Size) MB)"
        }
        
        # Check recent activity
        if ($project.LastModified -gt (Get-Date).AddDays(-30)) {
            $health.Score += 10
            $health.Strengths += "Recently modified"
        } else {
            $health.Issues += "Not modified recently"
        }
        
        # Display health status
        $healthColor = if ($health.Score -ge 80) { "Success" } 
                      elseif ($health.Score -ge 60) { "Warning" } 
                      else { "Error" }
        
        Write-ColorOutput "  Health Score: $($health.Score)/100" $healthColor
        
        if ($health.Strengths.Count -gt 0) {
            Write-ColorOutput "  ✅ Strengths:" "Success"
            $health.Strengths | ForEach-Object { Write-ColorOutput "    • $_" "Success" }
        }
        
        if ($health.Issues.Count -gt 0) {
            Write-ColorOutput "  ⚠️ Issues:" "Warning"
            $health.Issues | ForEach-Object { Write-ColorOutput "    • $_" "Warning" }
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                           NADAKKI PROJECT AUDIT                             ║
║                         Comprehensive File Analysis                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ "Header"

Write-ColorOutput "🚀 Starting comprehensive audit..." "Info"
Write-ColorOutput "📅 Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Info"

# Buscar proyectos Nadakki
$projectPaths = Scan-ForNadakkiProjects

if ($projectPaths.Count -eq 0) {
    Write-ColorOutput "`n❌ No Nadakki projects found!" "Error"
    Write-ColorOutput "💡 Try running with -ScanAllDrives switch for comprehensive search" "Info"
    exit 1
}

Write-ColorOutput "`n✅ Found $($projectPaths.Count) potential Nadakki project(s)" "Success"

# Analizar cada proyecto
$projects = @()
foreach ($path in $projectPaths) {
    $analysis = Analyze-Project -ProjectPath $path
    $projects += $analysis
    Show-ProjectSummary -Project $analysis
}

# Análisis de archivos críticos
Find-CriticalFiles -Projects $projects

# Health check
Check-ProjectHealth -Projects $projects

# Exportar reporte
if ($ExportJson) {
    $reportPath = "nadakki_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    Export-AuditReport -Projects $projects -OutputPath $reportPath
}

# Resumen final
Write-ColorOutput "`n" + "="*80 "Header"
Write-ColorOutput "📊 AUDIT SUMMARY" "Header"
Write-ColorOutput "="*80 "Header"
Write-ColorOutput "🏗️  Total Projects: $($projects.Count)" "Info"
Write-ColorOutput "📄 Total Files: $(($projects | ForEach-Object {$_.Files.Count} | Measure-Object -Sum).Sum)" "Info"
Write-ColorOutput "💾 Total Size: $([math]::Round(($projects | ForEach-Object {$_.Size} | Measure-Object -Sum).Sum, 2)) MB" "Info"
Write-ColorOutput "🤖 Total Agents: $(($projects | ForEach-Object {$_.Agents.Count} | Measure-Object -Sum).Sum)" "Info"
Write-ColorOutput "🔧 Technologies: $(($projects | ForEach-Object {$_.Technologies} | Sort-Object | Get-Unique) -join ', ')" "Info"

Write-ColorOutput "`n✅ Audit completed successfully!" "Success"

if ($ExportJson) {
    Write-ColorOutput "📄 Detailed report saved to: $reportPath" "Info"
}

Write-ColorOutput "`n💡 Next steps:" "Info"
Write-ColorOutput "  1. Review the health scores above" "Info"
Write-ColorOutput "  2. Focus on projects with highest scores" "Info"
Write-ColorOutput "  3. Address missing components in lower-scoring projects" "Info"
Write-ColorOutput "  4. Consider consolidating redundant projects" "Info"