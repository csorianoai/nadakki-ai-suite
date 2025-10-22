# Simple Nadakki Project Audit Script
Write-Host "NADAKKI PROJECT AUDIT - STARTING..." -ForegroundColor Cyan
Write-Host "Location: $PWD" -ForegroundColor White
Write-Host "Time: $(Get-Date)" -ForegroundColor White

# Count files by type
Write-Host "`n=== FILE ANALYSIS ===" -ForegroundColor Yellow
$htmlCount = (Get-ChildItem -Filter "*.html" -Recurse -ErrorAction SilentlyContinue).Count
$pyCount = (Get-ChildItem -Filter "*.py" -Recurse -ErrorAction SilentlyContinue).Count
$phpCount = (Get-ChildItem -Filter "*.php" -Recurse -ErrorAction SilentlyContinue).Count
$jsCount = (Get-ChildItem -Filter "*.js" -Recurse -ErrorAction SilentlyContinue).Count

Write-Host "HTML files: $htmlCount" -ForegroundColor Green
Write-Host "Python files: $pyCount" -ForegroundColor Green
Write-Host "PHP files: $phpCount" -ForegroundColor Green
Write-Host "JavaScript files: $jsCount" -ForegroundColor Green

# Check for main files
Write-Host "`n=== KEY FILES ===" -ForegroundColor Yellow
if (Test-Path "app.py") { Write-Host "✓ app.py found (Flask app)" -ForegroundColor Green }
if (Test-Path "main.py") { Write-Host "✓ main.py found (Python main)" -ForegroundColor Green }
if (Test-Path "requirements.txt") { Write-Host "✓ requirements.txt found" -ForegroundColor Green }

# Find Nadakki files
Write-Host "`n=== NADAKKI FILES ===" -ForegroundColor Yellow
$nadakkiFiles = Get-ChildItem -Filter "*nadakki*" -Recurse -ErrorAction SilentlyContinue
foreach ($file in $nadakkiFiles) {
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    Write-Host "✓ $($file.Name) - $sizeKB KB" -ForegroundColor Green
}

# Find Enterprise files  
Write-Host "`n=== ENTERPRISE FILES ===" -ForegroundColor Yellow
$enterpriseFiles = Get-ChildItem -Filter "*enterprise*" -Recurse -ErrorAction SilentlyContinue
foreach ($file in $enterpriseFiles) {
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    Write-Host "✓ $($file.Name) - $sizeKB KB" -ForegroundColor Green
}

# Find Agent files
Write-Host "`n=== AGENT FILES ===" -ForegroundColor Yellow
$agentFiles = Get-ChildItem -Filter "*agent*" -Recurse -ErrorAction SilentlyContinue
Write-Host "Agent files found: $($agentFiles.Count)" -ForegroundColor Cyan
foreach ($file in $agentFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor White
}

# Directory structure
Write-Host "`n=== DIRECTORY STRUCTURE ===" -ForegroundColor Yellow
$dirs = Get-ChildItem -Directory -ErrorAction SilentlyContinue
foreach ($dir in $dirs) {
    $fileCount = (Get-ChildItem -Path $dir.FullName -File -Recurse -ErrorAction SilentlyContinue).Count
    Write-Host "$($dir.Name)/ - $fileCount files" -ForegroundColor White
}

Write-Host "`nAUDIT COMPLETED!" -ForegroundColor Cyan