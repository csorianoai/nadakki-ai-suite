# SUPER AGENT QUALITY EVALUATOR v1.0
param(
    [string]$AgentsPath = "agents/marketing",
    [switch]$Verbose,
    [switch]$GenerateReport
)

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "           SUPER AGENT QUALITY EVALUATOR v1.0" -ForegroundColor White
Write-Host "           Target: 101/100" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$agentFiles = Get-ChildItem $AgentsPath -Filter "*.py" | Where-Object { $_.Name -notmatch "layers|__init__|__pycache__" }

if ($agentFiles.Count -eq 0) {
    Write-Host "No agent files found in: $AgentsPath" -ForegroundColor Red
    exit 1
}

Write-Host "Evaluating $($agentFiles.Count) agents in: $AgentsPath" -ForegroundColor Yellow
Write-Host ""

$totalAgents = 0
$passedAgents = 0
$allResults = @()

foreach ($file in $agentFiles) {
    $totalAgents++
    $content = Get-Content $file.FullName -Raw
    $score = 0
    $bonus = 0
    $failed = @()
    
    # Core Structure (30 pts)
    if ($content -match 'VERSION\s*=\s*[''"]3\.2\.0[''"]') { $score += 5 } else { $failed += "Missing VERSION 3.2.0" }
    if ($content -match 'SUPER_AGENT\s*=\s*True') { $score += 5 } else { $failed += "Missing SUPER_AGENT = True" }
    if ($content -match 'def execute\s*\(') { $score += 5 } else { $failed += "Missing execute()" }
    if ($content -match 'from\s+\.layers\.|from\s+agents\.marketing\.layers\.|LAYERS_AVAILABLE') { $score += 5 } else { $failed += "Missing layers import" }
    if ($content -match 'tenant_id') { $score += 5 } else { $failed += "Missing tenant_id" }
    if ($content -match '[''"]actionable[''"]') { $score += 5 } else { $failed += "Missing actionable" }
    
    # Decision Layer (20 pts)
    if ($content -match 'decision_layer|_decision_layer_applied') { $score += 10 } else { $failed += "Missing decision layer" }
    if ($content -match 'confidence_score') { $score += 5 } else { $failed += "Missing confidence_score" }
    if ($content -match 'datetime\.utcnow\(\)|timestamp') { $score += 5 } else { $failed += "Missing timestamps" }
    
    # Compliance (10 pts)
    if ($content -match 'compliance_layer|compliance_status') { $score += 10 } else { $failed += "Missing compliance" }
    
    # Business Impact (10 pts)
    if ($content -match 'business_impact|business_impact_score') { $score += 10 } else { $failed += "Missing business impact" }
    
    # Error Handling (10 pts)
    if ($content -match '_error_handling') { $score += 5 } else { $failed += "Missing error handling" }
    if ($content -match 'circuit_breaker|CircuitBreaker') { $score += 5 } else { $failed += "Missing circuit breaker" }
    
    # Audit Trail (10 pts)
    if ($content -match 'audit_trail|_input_hash|_output_hash') { $score += 10 } else { $failed += "Missing audit trail" }
    
    # Data Quality (5 pts)
    if ($content -match '_data_quality') { $score += 5 } else { $failed += "Missing _data_quality" }
    
    # Reason Codes (5 pts)
    if ($content -match 'reason_codes') { $score += 5 } else { $failed += "Missing reason_codes" }
    
    # BONUS (+6 pts)
    if ($content -match 'def health_check\s*\(') { $bonus += 2 }
    if ($content -match 'def _self_test_examples\s*\(') { $bonus += 2 }
    if ($content -match 'validation_errors') { $bonus += 2 }
    
    $totalScore = $score + $bonus
    
    # Display result
    $icon = if ($totalScore -ge 101) { "[PERFECT]" } elseif ($totalScore -ge 100) { "[PASS]" } elseif ($totalScore -ge 90) { "[ALMOST]" } else { "[FAIL]" }
    $color = if ($totalScore -ge 100) { "Green" } elseif ($totalScore -ge 90) { "Yellow" } else { "Red" }
    
    Write-Host "$icon $($file.Name.PadRight(35)) Score: $totalScore/100" -ForegroundColor $color
    
    if ($Verbose -and $failed.Count -gt 0) {
        foreach ($f in $failed) {
            Write-Host "      - $f" -ForegroundColor Red
        }
    }
    
    if ($totalScore -ge 100) { $passedAgents++ }
    
    $allResults += @{
        Agent = $file.Name
        Score = $score
        Bonus = $bonus
        Total = $totalScore
        Failed = $failed
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "                         RESUMEN" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total Agentes:     $totalAgents" -ForegroundColor White
Write-Host "  Aprobados (>=100): $passedAgents / $totalAgents" -ForegroundColor $(if ($passedAgents -eq $totalAgents) { "Green" } else { "Yellow" })
Write-Host ""

if ($passedAgents -eq $totalAgents) {
    Write-Host "  TODOS LOS AGENTES APROBADOS!" -ForegroundColor Green
} else {
    Write-Host "  Algunos agentes necesitan mejoras" -ForegroundColor Yellow
}
Write-Host ""
