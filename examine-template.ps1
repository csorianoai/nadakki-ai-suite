# NADAKKI AI SUITE - EXAMINE FUNCTIONAL TEMPLATE
Write-Host "🔍 SEARCHING FOR THE FUNCTIONAL AGENT TEMPLATE" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Read the QA data to find the completed agent
$rawContent = Get-Content "qa_summary.json" -Raw
$agentsData = $rawContent | ConvertFrom-Json

# Find the completed agent
$completedAgent = $agentsData | Where-Object { $_.Estado -eq "Completo" }

if ($completedAgent) {
    Write-Host "✅ FOUND FUNCTIONAL AGENT:" -ForegroundColor Green
    Write-Host "  Ecosystem: $($completedAgent.Ecosistema)" -ForegroundColor Yellow
    Write-Host "  File: $($completedAgent.Archivo)" -ForegroundColor Yellow
    Write-Host "  Size: $($completedAgent.TamanoKb) KB" -ForegroundColor Yellow
    Write-Host ""
    
    # Try to find and examine the actual file
    $agentPath = "agents/$($completedAgent.Ecosistema)/$($completedAgent.Archivo)"
    
    if (Test-Path $agentPath) {
        Write-Host "📁 FILE FOUND: $agentPath" -ForegroundColor Green
        Write-Host ""
        
        # Show file content
        Write-Host "📄 FILE CONTENT (TEMPLATE):" -ForegroundColor Cyan
        Write-Host "============================" -ForegroundColor Cyan
        Get-Content $agentPath | Select-Object -First 50
        
        Write-Host ""
        Write-Host "..." -ForegroundColor Gray
        Write-Host ""
        Write-Host "📊 FILE STATISTICS:" -ForegroundColor Yellow
        $content = Get-Content $agentPath -Raw
        $lines = ($content -split "`n").Count
        $classes = ($content | Select-String -Pattern "class " -AllMatches).Matches.Count
        $functions = ($content | Select-String -Pattern "def " -AllMatches).Matches.Count
        
        Write-Host "  Lines: $lines" -ForegroundColor White
        Write-Host "  Classes: $classes" -ForegroundColor White  
        Write-Host "  Functions: $functions" -ForegroundColor White
        
    } else {
        Write-Host "❌ FILE NOT FOUND: $agentPath" -ForegroundColor Red
        Write-Host "Searching in all agent folders..." -ForegroundColor Yellow
        
        # Search for any completed files in agents folder
        Get-ChildItem -Path "agents" -Recurse -Filter "*.py" | ForEach-Object {
            $size = [math]::Round($_.Length / 1KB, 1)
            if ($size -gt 6) {
                Write-Host "  Found: $($_.FullName.Replace((Get-Location).Path, '').TrimStart('\')) ($size KB)" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "❌ NO COMPLETED AGENTS FOUND" -ForegroundColor Red
    Write-Host "Will search for largest files as potential templates..." -ForegroundColor Yellow
    
    # Find largest Python files
    Write-Host ""
    Write-Host "🔍 LARGEST AGENT FILES (POTENTIAL TEMPLATES):" -ForegroundColor Cyan
    Get-ChildItem -Path "agents" -Recurse -Filter "*.py" | 
        Sort-Object Length -Descending | 
        Select-Object -First 10 | 
        ForEach-Object {
            $size = [math]::Round($_.Length / 1KB, 1)
            $relativePath = $_.FullName.Replace((Get-Location).Path, "").TrimStart('\')
            Write-Host "  $relativePath ($size KB)" -ForegroundColor $(if ($size -gt 6) { "Green" } else { "Yellow" })
        }
}

Write-Host ""
Write-Host "🎯 TEMPLATE ANALYSIS COMPLETE" -ForegroundColor Green