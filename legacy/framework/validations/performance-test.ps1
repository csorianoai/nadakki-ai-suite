param([int]$Iterations = 10)
$results = @()
for ($i = 0; $i -lt $Iterations; $i++) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/api/test" -TimeoutSec 5 | Out-Null
        $sw.Stop()
        $results += $sw.ElapsedMilliseconds
    }
    catch {
        Write-Host "Iteration $i failed"
    }
}
if ($results.Count -gt 0) {
    $avg = ($results | Measure-Object -Average).Average
    Write-Host "Performance Test Results:" -ForegroundColor Cyan
    Write-Host "  Average: ${avg}ms" -ForegroundColor Green
}
