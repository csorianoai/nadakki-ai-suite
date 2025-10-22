# NADAKKI AI SUITE - COMPLETE AGENT INSPECTOR
Write-Host "NADAKKI AI SUITE - COMPLETE AGENT INSPECTION" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Initialize counters and collections
$totalAgents = 0
$completeAgents = 0
$incompleteAgents = 0
$errorAgents = 0
$agentDatabase = @()
$ecosystemStats = @{}
$sizeStats = @()

# Define expected ecosystems
$expectedEcosystems = @('originacion', 'decision', 'vigilancia', 'recuperacion', 'compliance', 'operacional', 'experiencia', 'inteligencia', 'fortaleza', 'legal', 'marketing', 'logistica', 'contabilidad', 'presupuesto', 'rrhh', 'ventascrm', 'investigacion', 'educacion', 'regtech')

Write-Host "Scanning agents directory..." -ForegroundColor Yellow

# Scan all Python files in agents directory
Get-ChildItem -Path "agents" -Recurse -Filter "*.py" | ForEach-Object {
    $filePath = $_.FullName
    $fileName = $_.Name
    $ecosystem = $_.Directory.Name
    $fileSize = [math]::Round($_.Length / 1KB, 1)
    $relativePath = $filePath.Replace((Get-Location).Path, "").TrimStart("\")
    
    $totalAgents++
    
    # Initialize agent info
    $agentInfo = @{
        FileName = $fileName
        Ecosystem = $ecosystem
        FilePath = $relativePath
        SizeKB = $fileSize
        Status = "Unknown"
        ClassName = "Not Found"
        Description = "Not Found"
        Algorithms = @()
        PerformanceTarget = "Not Specified"
        Methods = @()
        Imports = @()
        HasBaseAgent = $false
        HasAsyncMethods = $false
        HasErrorHandling = $false
        SyntaxErrors = @()
        LastModified = $_.LastWriteTime
        LineCount = 0
    }
    
    try {
        # Read file content
        $content = Get-Content $filePath -Raw -ErrorAction Stop
        $lines = Get-Content $filePath -ErrorAction Stop
        $agentInfo.LineCount = $lines.Count
        
        # Extract class name
        $classMatch = $lines | Select-String -Pattern "^class\s+(\w+)" | Select-Object -First 1
        if ($classMatch) {
            $agentInfo.ClassName = $classMatch.Matches[0].Groups[1].Value
        }
        
        # Extract description from docstring
        $docstringMatch = $content | Select-String -Pattern '"""(.*?)"""' | Select-Object -First 1
        if ($docstringMatch) {
            $docstring = $docstringMatch.Matches[0].Groups[1].Value
            # Get first line of docstring as description
            $agentInfo.Description = ($docstring -split "`n")[0].Trim()
        }
        
        # Check for BaseAgent inheritance
        if ($content -match "class.*BaseAgent" -or $content -match "from.*base_components") {
            $agentInfo.HasBaseAgent = $true
        }
        
        # Extract algorithms
        $algorithmMatches = $content | Select-String -Pattern "algorithms.*=.*\[(.*?)\]" -AllMatches
        foreach ($match in $algorithmMatches) {
            $algorithmsText = $match.Matches[0].Groups[1].Value
            $algorithms = $algorithmsText -split "," | ForEach-Object { $_.Trim().Trim("'").Trim('"') }
            $agentInfo.Algorithms += $algorithms
        }
        
        # Extract performance target
        $performanceMatch = $content | Select-String -Pattern "performance_target.*=.*(\d+\.?\d*)" | Select-Object -First 1
        if ($performanceMatch) {
            $agentInfo.PerformanceTarget = $performanceMatch.Matches[0].Groups[1].Value + "%"
        }
        
        # Extract method names
        $methodMatches = $lines | Select-String -Pattern "^\s*def\s+(\w+)" 
        $agentInfo.Methods = $methodMatches | ForEach-Object { $_.Matches[0].Groups[1].Value }
        
        # Extract imports
        $importMatches = $lines | Select-String -Pattern "^(import|from)\s+" | Select-Object -First 10
        $agentInfo.Imports = $importMatches | ForEach-Object { $_.Line.Trim() }
        
        # Check for async methods
        if ($content -match "async def") {
            $agentInfo.HasAsyncMethods = $true
        }
        
        # Check for error handling
        if ($content -match "try:" -and $content -match "except") {
            $agentInfo.HasErrorHandling = $true
        }
        
        # Determine status based on various factors
        if ($fileSize -lt 1) {
            $agentInfo.Status = "Empty"
            $errorAgents++
        } elseif ($agentInfo.ClassName -eq "Not Found" -or $agentInfo.Methods.Count -eq 0) {
            $agentInfo.Status = "Incomplete"
            $incompleteAgents++
        } elseif ($fileSize -gt 5 -and $agentInfo.Methods.Count -gt 3 -and $agentInfo.HasErrorHandling) {
            $agentInfo.Status = "Complete"
            $completeAgents++
        } else {
            $agentInfo.Status = "Partial"
            $incompleteAgents++
        }
        
    } catch {
        $agentInfo.Status = "Error"
        $agentInfo.SyntaxErrors += $_.Exception.Message
        $errorAgents++
    }
    
    # Add to database
    $agentDatabase += $agentInfo
    
    # Update ecosystem stats
    if (-not $ecosystemStats.ContainsKey($ecosystem)) {
        $ecosystemStats[$ecosystem] = @{
            Total = 0
            Complete = 0
            Incomplete = 0
            Error = 0
            TotalSize = 0
        }
    }
    
    $ecosystemStats[$ecosystem].Total++
    $ecosystemStats[$ecosystem].TotalSize += $fileSize
    
    switch ($agentInfo.Status) {
        "Complete" { $ecosystemStats[$ecosystem].Complete++ }
        "Error" { $ecosystemStats[$ecosystem].Error++ }
        default { $ecosystemStats[$ecosystem].Incomplete++ }
    }
}

# DISPLAY RESULTS
Write-Host "`n=== GLOBAL SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total Agents Found: $totalAgents" -ForegroundColor White
Write-Host "Complete Agents: $completeAgents" -ForegroundColor Green
Write-Host "Incomplete/Partial: $incompleteAgents" -ForegroundColor Yellow  
Write-Host "Error/Empty: $errorAgents" -ForegroundColor Red
$successRate = if ($totalAgents -gt 0) { [math]::Round(($completeAgents / $totalAgents) * 100, 1) } else { 0 }
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -gt 50) { "Green" } else { "Red" })

# ECOSYSTEM BREAKDOWN
Write-Host "`n=== ECOSYSTEM BREAKDOWN ===" -ForegroundColor Cyan
$ecosystemStats.GetEnumerator() | Sort-Object Name | ForEach-Object {
    $eco = $_.Key
    $stats = $_.Value
    $avgSize = if ($stats.Total -gt 0) { [math]::Round($stats.TotalSize / $stats.Total, 1) } else { 0 }
    $ecoSuccessRate = if ($stats.Total -gt 0) { [math]::Round(($stats.Complete / $stats.Total) * 100, 1) } else { 0 }
    
    Write-Host "$($eco.ToUpper()):" -ForegroundColor Yellow
    Write-Host "  Total: $($stats.Total) | Complete: $($stats.Complete) | Incomplete: $($stats.Incomplete) | Error: $($stats.Error)" -ForegroundColor White
    Write-Host "  Avg Size: $avgSize KB | Success Rate: $ecoSuccessRate%" -ForegroundColor Gray
}

# COMPLETE AGENTS DETAILS
if ($completeAgents -gt 0) {
    Write-Host "`n=== COMPLETE AGENTS (GOOD TEMPLATES) ===" -ForegroundColor Green
    $agentDatabase | Where-Object { $_.Status -eq "Complete" } | ForEach-Object {
        Write-Host "✅ $($_.Ecosystem)/$($_.FileName)" -ForegroundColor Green
        Write-Host "   Class: $($_.ClassName) | Size: $($_.SizeKB)KB | Methods: $($_.Methods.Count)" -ForegroundColor White
        if ($_.Description -ne "Not Found") {
            Write-Host "   Desc: $($_.Description)" -ForegroundColor Gray
        }
        if ($_.Algorithms.Count -gt 0) {
            Write-Host "   Algorithms: $($_.Algorithms -join ', ')" -ForegroundColor Cyan
        }
        Write-Host ""
    }
}

# ERROR AGENTS
if ($errorAgents -gt 0) {
    Write-Host "`n=== ERROR AGENTS (NEED FIXING) ===" -ForegroundColor Red
    $agentDatabase | Where-Object { $_.Status -eq "Error" -or $_.Status -eq "Empty" } | ForEach-Object {
        Write-Host "❌ $($_.Ecosystem)/$($_.FileName)" -ForegroundColor Red
        Write-Host "   Status: $($_.Status) | Size: $($_.SizeKB)KB" -ForegroundColor White
        if ($_.SyntaxErrors.Count -gt 0) {
            Write-Host "   Errors: $($_.SyntaxErrors -join '; ')" -ForegroundColor Red
        }
        Write-Host ""
    }
}

# SIZE ANALYSIS
Write-Host "`n=== SIZE ANALYSIS ===" -ForegroundColor Magenta
$sizeGroups = $agentDatabase | Group-Object { 
    if ($_.SizeKB -eq 0) { "Empty (0 KB)" }
    elseif ($_.SizeKB -lt 1) { "Tiny (< 1KB)" }
    elseif ($_.SizeKB -lt 3) { "Small (1-3KB)" }
    elseif ($_.SizeKB -lt 6) { "Medium (3-6KB)" }
    elseif ($_.SizeKB -lt 10) { "Large (6-10KB)" }
    else { "XLarge (>10KB)" }
}

$sizeGroups | Sort-Object Name | ForEach-Object {
    $color = switch ($_.Name) {
        {$_ -match "Empty|Tiny"} { "Red" }
        {$_ -match "Small"} { "Yellow" }
        {$_ -match "Medium"} { "White" }
        {$_ -match "Large|XLarge"} { "Green" }
        default { "White" }
    }
    Write-Host "$($_.Name): $($_.Count) agents" -ForegroundColor $color
}

# TOP PERFORMERS (LARGEST FILES)
Write-Host "`n=== TOP 10 LARGEST AGENTS (POTENTIAL TEMPLATES) ===" -ForegroundColor Green
$agentDatabase | Sort-Object SizeKB -Descending | Select-Object -First 10 | ForEach-Object {
    $status = switch ($_.Status) {
        "Complete" { "✅" }
        "Error" { "❌" }
        "Empty" { "🚫" }
        default { "⚠️" }
    }
    Write-Host "$status $($_.Ecosystem)/$($_.FileName) ($($_.SizeKB)KB) - $($_.ClassName)" -ForegroundColor $(
        if ($_.Status -eq "Complete") { "Green" } 
        elseif ($_.Status -eq "Error") { "Red" } 
        else { "Yellow" }
    )
}

# FRAMEWORK ANALYSIS
Write-Host "`n=== FRAMEWORK USAGE ANALYSIS ===" -ForegroundColor Cyan
$baseAgentUsers = ($agentDatabase | Where-Object { $_.HasBaseAgent }).Count
$asyncAgents = ($agentDatabase | Where-Object { $_.HasAsyncMethods }).Count
$errorHandlingAgents = ($agentDatabase | Where-Object { $_.HasErrorHandling }).Count

Write-Host "Agents using BaseAgent framework: $baseAgentUsers / $totalAgents" -ForegroundColor White
Write-Host "Agents with async methods: $asyncAgents / $totalAgents" -ForegroundColor White
Write-Host "Agents with error handling: $errorHandlingAgents / $totalAgents" -ForegroundColor White

# RECOMMENDATIONS
Write-Host "`n=== RECOMMENDATIONS ===" -ForegroundColor Yellow
Write-Host "IMMEDIATE ACTIONS:" -ForegroundColor Red
if ($errorAgents -gt 0) {
    Write-Host "1. 🚨 Fix $errorAgents error/empty agents first" -ForegroundColor Red
}
if ($completeAgents -gt 0) {
    Write-Host "2. ✅ Use $completeAgents complete agents as templates" -ForegroundColor Green
} else {
    Write-Host "2. 🔧 No complete agents found - create base template first" -ForegroundColor Red
}
if ($baseAgentUsers -lt ($totalAgents * 0.8)) {
    Write-Host "3. 🏗️ Migrate more agents to BaseAgent framework" -ForegroundColor Yellow
}

Write-Host "`nNEXT STEPS:" -ForegroundColor Cyan
Write-Host "• Focus on ecosystems with highest success rates" -ForegroundColor White
Write-Host "• Standardize agents to use BaseAgent framework" -ForegroundColor White
Write-Host "• Implement async methods for better performance" -ForegroundColor White
Write-Host "• Add error handling to all agents" -ForegroundColor White

Write-Host "`nCOMPLETE AGENT INSPECTION FINISHED!" -ForegroundColor Green
Write-Host "Database created with $totalAgents agents analyzed" -ForegroundColor Green