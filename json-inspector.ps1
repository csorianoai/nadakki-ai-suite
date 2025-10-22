# SIMPLE JSON CONTENT INSPECTOR
# Just shows what's actually in the qa_summary.json file

Write-Host "JSON CONTENT INSPECTOR" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

$qaFile = "qa_summary.json"

if (-not (Test-Path $qaFile)) {
    Write-Host "[ERROR] File not found: $qaFile" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $qaFile).Length
Write-Host "File: $qaFile ($fileSize bytes)" -ForegroundColor Green
Write-Host ""

# Read raw content
try {
    $content = Get-Content $qaFile -Raw -Encoding UTF8
    
    # Show file structure
    $trimmed = $content.Trim()
    Write-Host "STRUCTURE DETECTION:" -ForegroundColor Yellow
    Write-Host "First character: '$($trimmed[0])'" -ForegroundColor White
    Write-Host "Last character:  '$($trimmed[-1])'" -ForegroundColor White
    
    if ($trimmed.StartsWith('[') -and $trimmed.EndsWith(']')) {
        Write-Host "Format: JSON ARRAY []" -ForegroundColor Green
    } elseif ($trimmed.StartsWith('{') -and $trimmed.EndsWith('}')) {
        Write-Host "Format: JSON OBJECT {}" -ForegroundColor Green  
    } else {
        Write-Host "Format: UNKNOWN or INVALID" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "FULL CONTENT:" -ForegroundColor Yellow
    Write-Host "=============" -ForegroundColor Yellow
    Write-Host $content -ForegroundColor Gray
    
} catch {
    Write-Host "[ERROR] Cannot read file: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "INSPECTION COMPLETE" -ForegroundColor Green