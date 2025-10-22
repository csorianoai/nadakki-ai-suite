# NADAKKI AI SUITE - QA ANALYSIS (ARRAY-COMPATIBLE VERSION)
Write-Host "NADAKKI AI SUITE - QA REPORT ANALYSIS" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if report exists
if (!(Test-Path "qa_summary.json")) {
    Write-Host "ERROR: qa_summary.json not found!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item "qa_summary.json").Length
Write-Host "Report file found: qa_summary.json ($fileSize bytes)" -ForegroundColor Green

try {
    # Read JSON content
    Write-Host "Reading JSON report..." -ForegroundColor Yellow
    $rawContent = Get-Content "qa_summary.json" -Raw
    $qaData = $rawContent | ConvertFrom-Json
    Write-Host "JSON parsed successfully" -ForegroundColor Green

    # Handle both array and object formats
    if ($qaData -is [Array]) {
        Write-Host "`n[INFO] JSON is an ARRAY with $($qaData.Count) elements" -ForegroundColor Yellow
        
        if ($qaData.Count -gt 0) {
            # Use first element if it contains summary data
            $summary = $qaData[0]
            Write-Host "Using first array element for analysis" -ForegroundColor Yellow
        } else {
            Write-Host "ERROR: Empty array found" -ForegroundColor Red
            exit 1
        }
    } else {
        # It's an object
        $summary = $qaData
        Write-Host "`n[INFO] JSON is an OBJECT" -ForegroundColor Green
    }

    # GENERAL SUMMARY
    Write-Host "`nGENERAL SUMMARY:" -ForegroundColor Cyan
    Write-Host "================" -ForegroundColor Cyan
    
    # Try different property names for totals
    $totalAgents = $null
    $functionalAgents = $null
    
    foreach ($prop in @('total_agents', 'totalAgents', 'agents_total', 'count', 'total')) {
        if ($summary.PSObject.Properties[$prop]) {
            $totalAgents = $summary.$prop
            Write-Host "Total agents: $totalAgents" -ForegroundColor White
            break
        }
    }
    
    foreach ($prop in @('functional_agents', 'functionalAgents', 'working', 'success')) {
        if ($summary.PSObject.Properties[$prop]) {
            $functionalAgents = $summary.$prop
            Write-Host "Functional: $functionalAgents" -ForegroundColor White
            break
        }
    }

    if ($totalAgents -and $functionalAgents) {
        $successRate = [math]::Round(($functionalAgents / $totalAgents) * 100, 1)
        $problemAgents = $totalAgents - $functionalAgents
        Write-Host "Success rate: $successRate%" -ForegroundColor Green
        Write-Host "With problems: $problemAgents" -ForegroundColor Red
    }

    # ECOSYSTEM ANALYSIS
    Write-Host "`nECOSYSTEM ANALYSIS:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    $ecosystems = @('originacion', 'decision', 'vigilancia', 'recuperacion', 'compliance', 'operacional', 'experiencia', 'inteligencia', 'fortaleza')
    
    foreach ($ecosystem in $ecosystems) {
        $ecoData = $null
        # Try different property formats
        foreach ($prop in @($ecosystem, "ecosystem_$ecosystem", $ecosystem.ToUpper())) {
            if ($summary.PSObject.Properties[$prop]) {
                $ecoData = $summary.$prop
                break
            }
        }
        
        if ($ecoData) {
            Write-Host "$($ecosystem.ToUpper()): [FOUND] $ecoData" -ForegroundColor Green
        } else {
            Write-Host "$($ecosystem.ToUpper()): [NOT FOUND] Not found in report" -ForegroundColor Red
        }
    }

    # Show all available properties for debugging
    Write-Host "`nAVAILABLE PROPERTIES IN JSON:" -ForegroundColor Yellow
    Write-Host "==============================" -ForegroundColor Yellow
    $summary.PSObject.Properties.Name | Sort-Object | ForEach-Object {
        $value = $summary.$_
        if ($value -is [string] -or $value -is [int] -or $value -is [double]) {
            Write-Host "  - $_ : $value" -ForegroundColor White
        } else {
            Write-Host "  - $_ : [Object/Array]" -ForegroundColor Gray
        }
    }

} catch {
    Write-Host "ERROR parsing JSON: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Raw content preview:" -ForegroundColor Yellow
    (Get-Content "qa_summary.json" -Raw).Substring(0, [Math]::Min(200, (Get-Content "qa_summary.json" -Raw).Length))
    exit 1
}

Write-Host "`nQA ANALYSIS COMPLETE" -ForegroundColor Cyan