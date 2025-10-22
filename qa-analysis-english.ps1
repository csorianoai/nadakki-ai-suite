# NADAKKI AI SUITE - QA REPORT ANALYSIS
# English version without special characters to avoid encoding issues

Write-Host "NADAKKI AI SUITE - QA REPORT ANALYSIS" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if report exists
if (-not (Test-Path "qa_summary.json")) {
    Write-Host "ERROR: qa_summary.json not found" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item "qa_summary.json").Length
Write-Host "Report file found: qa_summary.json ($fileSize bytes)" -ForegroundColor Green

# Read JSON report
Write-Host "`nReading JSON report..." -ForegroundColor Yellow
try {
    $qaData = Get-Content "qa_summary.json" -Raw | ConvertFrom-Json
    Write-Host "JSON parsed successfully" -ForegroundColor Green
} catch {
    Write-Host "Error parsing JSON: $_" -ForegroundColor Red
    Write-Host "Showing first lines of file:" -ForegroundColor Yellow
    Get-Content "qa_summary.json" -Head 20 | ForEach-Object { Write-Host "   $_" }
    exit 1
}

# General summary analysis
Write-Host "`nGENERAL SUMMARY:" -ForegroundColor White
Write-Host "================" -ForegroundColor White

if ($qaData.total_agents) {
    Write-Host "   Total agents: $($qaData.total_agents)" -ForegroundColor Cyan
}
if ($qaData.functional_agents) {
    Write-Host "   Functional: $($qaData.functional_agents)" -ForegroundColor Green
}
if ($qaData.success_rate) {
    Write-Host "   Success rate: $($qaData.success_rate)%" -ForegroundColor Yellow
}

$problemAgents = $qaData.total_agents - $qaData.functional_agents
Write-Host "   With problems: $problemAgents" -ForegroundColor Red

# Ecosystem analysis
Write-Host "`nECOSYSTEM ANALYSIS:" -ForegroundColor White
Write-Host "===================" -ForegroundColor White

$ecosystemStats = @{}
$allErrors = @()
$functionalAgents = @()
$brokenAgents = @()

# Search for ecosystem data in JSON
$ecosystemNames = @("originacion", "decision", "vigilancia", "recuperacion", "compliance", "operacional", "experiencia", "inteligencia", "fortaleza")

foreach ($ecoName in $ecosystemNames) {
    if ($qaData.PSObject.Properties.Name -contains $ecoName) {
        $ecosystemData = $qaData.$ecoName
        
        Write-Host "`n$($ecoName.ToUpper()):" -ForegroundColor Cyan
        
        if ($ecosystemData.agents) {
            $total = $ecosystemData.agents.Count
            $functional = ($ecosystemData.agents | Where-Object { $_.functional -eq $true }).Count
            $broken = $total - $functional
            
            $successRate = if ($total -gt 0) { [math]::Round($functional / $total * 100, 1) } else { 0 }
            
            $status = if ($successRate -eq 0) { "[CRITICAL]" } 
                     elseif ($successRate -lt 25) { "[VERY BAD]" }
                     elseif ($successRate -lt 50) { "[BAD]" }
                     elseif ($successRate -lt 75) { "[REGULAR]" }
                     else { "[GOOD]" }
            
            Write-Host "   $status $functional/$total agents ($successRate%)" -ForegroundColor White
            
            $ecosystemStats[$ecoName] = @{
                total = $total
                functional = $functional
                broken = $broken
                success_rate = $successRate
            }
            
            # Collect functional agents
            $ecosystemData.agents | Where-Object { $_.functional -eq $true } | ForEach-Object {
                $functionalAgents += [PSCustomObject]@{
                    ecosystem = $ecoName
                    name = $_.name
                    file = $_.file
                    size = $_.size_bytes
                }
            }
            
            # Collect broken agents
            $ecosystemData.agents | Where-Object { $_.functional -eq $false } | ForEach-Object {
                $brokenAgents += [PSCustomObject]@{
                    ecosystem = $ecoName
                    name = $_.name
                    file = $_.file
                    error = $_.error
                    size = $_.size_bytes
                }
                
                if ($_.error) {
                    $allErrors += $_.error
                }
            }
            
            # Show first 3 unique errors per ecosystem
            $ecosystemErrors = $ecosystemData.agents | Where-Object { $_.error } | 
                              Select-Object -ExpandProperty error | Sort-Object | Get-Unique | Select-Object -First 3
            foreach ($error in $ecosystemErrors) {
                $shortError = if ($error.Length -gt 70) { $error.Substring(0, 70) + "..." } else { $error }
                Write-Host "      ERROR: $shortError" -ForegroundColor Red
            }
        } else {
            Write-Host "   [NO DATA] No agent data found" -ForegroundColor Red
        }
    } else {
        Write-Host "`n$($ecoName.ToUpper()): [NOT FOUND] Not found in report" -ForegroundColor Red
    }
}

# Also search for properties containing "ecosystem" in the name
Write-Host "`nSearching for other ecosystem properties..." -ForegroundColor Yellow
foreach ($property in $qaData.PSObject.Properties) {
    if ($property.Name -like "*ecosystem*" -and $property.Name -notin $ecosystemNames) {
        Write-Host "Additional property found: $($property.Name)" -ForegroundColor Yellow
        # Process similarly if needed
    }
}

# Top most common errors
Write-Host "`nTOP 10 MOST COMMON ERRORS:" -ForegroundColor Red
Write-Host "===========================" -ForegroundColor Red

if ($allErrors.Count -gt 0) {
    $errorCounts = @{}
    foreach ($error in $allErrors) {
        # Extract main error type
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
        Write-Host "   $rank. $($errorEntry.Name): $($errorEntry.Value) agents ($percentage%)" -ForegroundColor White
        $rank++
    }
} else {
    Write-Host "   No errors found in report" -ForegroundColor Yellow
}

# Functional agents
Write-Host "`nFUNCTIONAL AGENTS (SUCCESS CASES):" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

if ($functionalAgents.Count -gt 0) {
    Write-Host "Total functional agents found: $($functionalAgents.Count)" -ForegroundColor Green
    
    foreach ($agent in $functionalAgents) {
        Write-Host "   [OK] $($agent.ecosystem)/$($agent.name) ($($agent.size) bytes)" -ForegroundColor Green
    }
    
    # Analyze first functional agent as template
    $templateAgent = $functionalAgents[0]
    $templateFile = "agents\$($templateAgent.ecosystem)\$($templateAgent.file)"
    
    Write-Host "`nANALYZING TEMPLATE - FUNCTIONAL AGENT:" -ForegroundColor Green
    Write-Host "   Agent: $($templateAgent.name)" -ForegroundColor White
    Write-Host "   File: $templateFile" -ForegroundColor White
    
    if (Test-Path $templateFile) {
        $templateContent = Get-Content $templateFile -Raw
        
        # Structure analysis
        $hasClass = $templateContent -match "class\s+(\w+)"
        $hasInit = $templateContent -match "def __init__"
        $hasExecute = $templateContent -match "def execute"
        $imports = ([regex]::Matches($templateContent, "^(import|from)\s+[\w.]+", 'Multiline')).Count
        
        Write-Host "   STRUCTURE VALIDATED:" -ForegroundColor White
        Write-Host "      - Main class: $hasClass" -ForegroundColor Gray
        Write-Host "      - __init__ method: $hasInit" -ForegroundColor Gray  
        Write-Host "      - execute method: $hasExecute" -ForegroundColor Gray
        Write-Host "      - Import lines: $imports" -ForegroundColor Gray
        
        Write-Host "`n   FIRST 15 LINES (TEMPLATE):" -ForegroundColor White
        Get-Content $templateFile -Head 15 | ForEach-Object { 
            Write-Host "      $_" -ForegroundColor Gray 
        }
    } else {
        Write-Host "   ERROR: Template file does not exist: $templateFile" -ForegroundColor Red
    }
} else {
    Write-Host "   [CRITICAL] NO FUNCTIONAL AGENTS TO USE AS TEMPLATE" -ForegroundColor Red
}

# Analysis of problematic agents
Write-Host "`nFIRST 5 PROBLEMATIC AGENTS:" -ForegroundColor Red
Write-Host "============================" -ForegroundColor Red

if ($brokenAgents.Count -gt 0) {
    $sampleBrokenAgents = $brokenAgents | Select-Object -First 5
    foreach ($agent in $sampleBrokenAgents) {
        Write-Host "`n   [ERROR] $($agent.ecosystem)/$($agent.name)" -ForegroundColor Red
        Write-Host "      File: $($agent.file)" -ForegroundColor White
        Write-Host "      Error: $($agent.error)" -ForegroundColor Red
        
        $agentFile = "agents\$($agent.ecosystem)\$($agent.file)"
        if (Test-Path $agentFile) {
            Write-Host "      First 5 lines:" -ForegroundColor White
            Get-Content $agentFile -Head 5 | ForEach-Object {
                Write-Host "         $_" -ForegroundColor Gray
            }
        } else {
            Write-Host "      [ERROR] FILE DOES NOT EXIST" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   No problematic agents found in report" -ForegroundColor Yellow
}

# Specific recommendations
Write-Host "`nSPECIFIC RECOMMENDATIONS:" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

Write-Host "`nIMMEDIATE ACTION:" -ForegroundColor Yellow
if ($functionalAgents.Count -gt 0) {
    Write-Host "   1. [OK] Use $($functionalAgents[0].name) as TEMPLATE" -ForegroundColor Green
    Write-Host "   2. [FIX] Regenerate problematic agents with valid structure" -ForegroundColor White
    Write-Host "   3. [TEST] Validate in batches (10 agents at a time)" -ForegroundColor White
} else {
    Write-Host "   1. [CRITICAL] CREATE TEMPLATE from scratch (no functional agents)" -ForegroundColor Red
    Write-Host "   2. [BUILD] Regenerate ALL agents with correct structure" -ForegroundColor White
    Write-Host "   3. [TEST] Implement validation during generation" -ForegroundColor White
}

Write-Host "`nRECOVERY PLAN:" -ForegroundColor Yellow
Write-Host "   PHASE 1: Analyze functional template (if exists)" -ForegroundColor White
Write-Host "   PHASE 2: Fix most common errors (top 3)" -ForegroundColor White
Write-Host "   PHASE 3: Mass regeneration with validation" -ForegroundColor White
Write-Host "   PHASE 4: Incremental testing until >90% success" -ForegroundColor White

# Final statistics
Write-Host "`nFINAL STATISTICS:" -ForegroundColor White
Write-Host "==================" -ForegroundColor White

$totalEcosystems = $ecosystemStats.Keys.Count
$criticalEcosystems = ($ecosystemStats.Values | Where-Object { $_.success_rate -eq 0 }).Count
$avgSuccessRate = if ($ecosystemStats.Values.Count -gt 0) { 
    ($ecosystemStats.Values | Measure-Object -Property success_rate -Average).Average 
} else { 0 }

Write-Host "   Total ecosystems analyzed: $totalEcosystems" -ForegroundColor Cyan
Write-Host "   Critical ecosystems (0% success): $criticalEcosystems" -ForegroundColor Red
Write-Host "   Global average success: $([math]::Round($avgSuccessRate, 1))%" -ForegroundColor Yellow

# Show JSON structure for debugging
Write-Host "`nJSON STRUCTURE (DEBUG):" -ForegroundColor Yellow
Write-Host "=======================" -ForegroundColor Yellow
Write-Host "Main properties found:" -ForegroundColor White
foreach ($prop in $qaData.PSObject.Properties.Name) {
    Write-Host "   - $prop" -ForegroundColor Gray
}

Write-Host "`nUSEFUL FILES:" -ForegroundColor Green
Write-Host "   qa_summary.json (complete analysis)" -ForegroundColor White

Write-Host "`nNEXT STEP:" -ForegroundColor Cyan
if ($functionalAgents.Count -gt 0) {
    $nextAgent = $functionalAgents[0]
    Write-Host "   Analyze functional agent: $($nextAgent.ecosystem)/$($nextAgent.name)" -ForegroundColor White
    Write-Host "   Command: notepad agents\$($nextAgent.ecosystem)\$($nextAgent.file)" -ForegroundColor Gray
} else {
    Write-Host "   Create agent template from scratch and regenerate entire system" -ForegroundColor White
}

Write-Host "`nQA ANALYSIS COMPLETE" -ForegroundColor Cyan