# ============================================================
# NADAKKI CLEANUP SCRIPT — Ejecutar en la raíz de nadakki-ai-suite
# ============================================================
# INSTRUCCIONES: Abrir PowerShell, navegar a la carpeta del repo y ejecutar:
#   .\cleanup_nadakki.ps1
# ============================================================

Write-Host "=== PASO 1: Verificar branch ===" -ForegroundColor Cyan
git rev-parse --abbrev-ref HEAD
git status

Write-Host "`n=== PASO 2: Crear carpeta archive ===" -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveDir = "_archive_local\root_cleanup_$timestamp"
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
Write-Host "Carpeta creada: $archiveDir"

Write-Host "`n=== PASO 3: Mover carpetas de backup ===" -ForegroundColor Cyan
$folders = @("agents_backup_*", "backup_pre_cleanup_*", "backup_skeletons_*")
foreach ($pattern in $folders) {
    Get-ChildItem -Directory -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  Moviendo carpeta: $($_.Name)"
        Move-Item $_.FullName "$archiveDir\"
    }
}

Write-Host "`n=== PASO 4: Mover archivos main backup ===" -ForegroundColor Cyan
$backupPatterns = @("main.py.backup_*", "main_backup_*.py")
foreach ($pattern in $backupPatterns) {
    Get-ChildItem -File -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  Moviendo: $($_.Name)"
        Move-Item $_.FullName "$archiveDir\"
    }
}

Write-Host "`n=== PASO 5: Mover test_*.py de la raíz ===" -ForegroundColor Cyan
$testCount = 0
Get-ChildItem -File -Filter "test_*.py" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "$archiveDir\"
    $testCount++
}
Write-Host "  $testCount archivos test movidos"

Write-Host "`n=== PASO 6: Actualizar .gitignore ===" -ForegroundColor Cyan
$gitignoreContent = @"
# ==========================
# Python
# ==========================
.venv/
__pycache__/
*.pyc
.env

# ==========================
# Node
# ==========================
.next/
**/node_modules/
**/.next/
**/.turbo/
**/.cache/

# ==========================
# Builds / Dist
# ==========================
**/build/
**/dist/

# ==========================
# Logs / Reports / Archives
# ==========================
**/*.log
**/*.bak
**/*.zip
audit_reports/
_archive_local/

# ==========================
# Backups (root cleanup)
# ==========================
agents_backup_*/
backup_pre_cleanup_*/
backup_skeletons_*/
*.backup_*
main.py.backup_*
main_backup_*.py
test_*.py

# ==========================
# Secrets / Credentials
# ==========================
API_REFERENCE.md
nadakki-lambda-deployment.zip
"@
Set-Content -Path ".gitignore" -Value $gitignoreContent -Encoding UTF8
Write-Host "  .gitignore actualizado"

Write-Host "`n=== PASO 7: Commit ===" -ForegroundColor Cyan
git add -A
git commit -m "chore: archive root backups/tests and add ignore rules"

Write-Host "`n=== PASO 8: Push ===" -ForegroundColor Cyan
git push origin main

Write-Host "`n=== PASO 9: Verificación final ===" -ForegroundColor Cyan
git status
git log --oneline -n 3

Write-Host "`n=== COMPLETADO ===" -ForegroundColor Green
