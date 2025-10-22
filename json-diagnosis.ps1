# NADAKKI AI SUITE - JSON DIAGNOSIS SCRIPT
Write-Host "=== JSON STRUCTURE DIAGNOSIS ===" -ForegroundColor Cyan

# Leer contenido crudo
$rawContent = Get-Content "qa_summary.json" -Raw
Write-Host "File size: $($rawContent.Length) characters" -ForegroundColor Yellow

# Mostrar primeros 500 caracteres
Write-Host "First 500 characters:" -ForegroundColor Green
$rawContent.Substring(0, [Math]::Min(500, $rawContent.Length))

Write-Host "`n=== JSON TYPE DETECTION ===" -ForegroundColor Cyan
if ($rawContent.TrimStart().StartsWith('[')) {
    Write-Host "DETECTED: JSON ARRAY []" -ForegroundColor Red
} elseif ($rawContent.TrimStart().StartsWith('{')) {
    Write-Host "DETECTED: JSON OBJECT {}" -ForegroundColor Green
} else {
    Write-Host "DETECTED: UNKNOWN FORMAT" -ForegroundColor Red
}

# Intentar parsear como array
try {
    $jsonArray = $rawContent | ConvertFrom-Json
    Write-Host "`nArray Length: $($jsonArray.Count)" -ForegroundColor Yellow
    
    if ($jsonArray.Count -gt 0) {
        Write-Host "First element type: $($jsonArray[0].GetType().Name)" -ForegroundColor Yellow
        Write-Host "First element properties:" -ForegroundColor Yellow
        $jsonArray[0].PSObject.Properties.Name | ForEach-Object { 
            Write-Host "  - $_ : $($jsonArray[0].$_)" 
        }
    }
} catch {
    Write-Host "Failed to parse as JSON: $($_.Exception.Message)" -ForegroundColor Red
}