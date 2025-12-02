param([int]$Iterations = 100)

$results = @()
$sw = [System.Diagnostics.Stopwatch]::new()

for ($i = 1; $i -le $Iterations; $i++) {
    $sw.Restart()
    $json = @{ test = $i; data = (1..100) } | ConvertTo-Json
    $parsed = $json | ConvertFrom-Json
    $sw.Stop()
    $results += $sw.ElapsedMilliseconds
}

$avg = [math]::Round(($results | Measure-Object -Average).Average, 2)
$min = ($results | Measure-Object -Minimum).Minimum
$max = ($results | Measure-Object -Maximum).Maximum

Write-Host "Performance Results: Avg=${avg}ms, Min=${min}ms, Max=${max}ms" -ForegroundColor Green

@{ average_ms = $avg; min_ms = $min; max_ms = $max; iterations = $Iterations } | ConvertTo-Json | Out-File "reports\phase-72-performance-$((Get-Date).ToString('yyyy-MM-dd_HH-mm-ss')).json"
