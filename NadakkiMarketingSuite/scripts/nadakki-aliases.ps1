<#
================================================================================
 NADAKKI MARKETING SUITE - POWERSHELL ALIASES
 Uso: . .\scripts\nadakki-aliases.ps1
================================================================================
#>

function ndk-install { pip install -r requirements.txt; pip install black flake8 isort pytest-cov }
function ndk-test { python tests/test_all.py }
function ndk-test-cov { pytest tests/ -v --cov=backend --cov-report=html --cov-report=term }
function ndk-lint { 
    Write-Host "--- Black ---" -ForegroundColor Cyan
    black --check . --exclude "venv|__pycache__"
    Write-Host "--- isort ---" -ForegroundColor Cyan
    isort --check-only . --skip venv
    Write-Host "--- Flake8 ---" -ForegroundColor Cyan
    flake8 . --max-line-length=120 --exclude=venv,__pycache__
}
function ndk-format { black . --exclude "venv|__pycache__"; isort . --skip venv }
function ndk-run { uvicorn backend.main:app --reload }
function ndk-docker-up { docker-compose up -d }
function ndk-docker-down { docker-compose down }

Write-Host ""
Write-Host "  NADAKKI ALIASES CARGADOS:" -ForegroundColor Green
Write-Host "    ndk-install   - Instalar dependencias"
Write-Host "    ndk-test      - Ejecutar tests"
Write-Host "    ndk-test-cov  - Tests con cobertura"
Write-Host "    ndk-lint      - Verificar formato"
Write-Host "    ndk-format    - Formatear código"
Write-Host "    ndk-run       - Iniciar servidor"
Write-Host "    ndk-docker-up - Iniciar Docker"
Write-Host ""
