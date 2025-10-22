# NADAKKI AI SUITE - ANALYZE BEST TEMPLATES
Write-Host "NADAKKI AI SUITE - TEMPLATE ANALYSIS" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$templates = @(
    @{Name="Base Components"; Path="agents\originacion\base_components_v2.py"; Size="24.3KB"},
    @{Name="Regulatory Radar"; Path="agents\compliance\regulatory_radar.py"; Size="22.7KB"},
    @{Name="Behavior Miner"; Path="agents\originacion\behavior_miner_v2.py"; Size="9.4KB"},
    @{Name="Quantum Decision"; Path="agents\decision\quantumdecision.py"; Size="9.3KB"},
    @{Name="Sentinel Bot"; Path="agents\originacion\sentinelbot.py"; Size="8KB"}
)

foreach ($template in $templates) {
    Write-Host "`n=== $($template.Name.ToUpper()) ($($template.Size)) ===" -ForegroundColor Yellow
    Write-Host "File: $($template.Path)" -ForegroundColor Gray
    
    if (Test-Path $template.Path) {
        Write-Host "Status: FOUND" -ForegroundColor Green
        
        # Show first 30 lines
        $content = Get-Content $template.Path -Raw
        $lines = Get-Content $template.Path | Select-Object -First 30
        
        # Basic analysis
        $totalLines = ($content -split "`n").Count
        $classes = ($content | Select-String -Pattern "class " -AllMatches).Matches.Count
        $functions = ($content | Select-String -Pattern "def " -AllMatches).Matches.Count
        $imports = ($content | Select-String -Pattern "import " -AllMatches).Matches.Count
        
        Write-Host "Stats: $totalLines lines, $classes classes, $functions functions, $imports imports" -ForegroundColor White
        Write-Host ""
        Write-Host "--- PREVIEW ---" -ForegroundColor Cyan
        $lines | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
        Write-Host "..." -ForegroundColor DarkGray
        
    } else {
        Write-Host "Status: NOT FOUND" -ForegroundColor Red
    }
    
    Write-Host ("-" * 80) -ForegroundColor DarkGray
}

Write-Host "`nTEMPLATE ANALYSIS COMPLETE" -ForegroundColor Green
Write-Host "Recommendation: Use 'Base Components' as framework + 'Regulatory Radar' as agent template" -ForegroundColor Cyan