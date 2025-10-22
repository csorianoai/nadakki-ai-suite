param([switch]$AutoFix)

Write-Host "=== AUDITORÍA RÁPIDA NADAKKI ===" -ForegroundColor Green
Write-Host "Directorio: $(Get-Location)" -ForegroundColor Cyan

$existing = @(); $missing = @()

# Verificar archivos principales
@("main_enterprise.py", "app.py", "requirements_enterprise.txt", ".env") | ForEach-Object {
    if (Test-Path $_) { 
        Write-Host "[OK] $_" -ForegroundColor Green; $existing += $_ 
    } else { 
        Write-Host "[FALTA] $_" -ForegroundColor Red; $missing += $_ 
    }
}

# Verificar directorios
@("agents", "config", "api", "core") | ForEach-Object {
    if (Test-Path $_) { 
        Write-Host "[OK] $_/" -ForegroundColor Green; $existing += $_ 
    } else { 
        Write-Host "[FALTA] $_/" -ForegroundColor Red; $missing += $_ 
    }
}

# Verificar Python y venv
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no encontrado" -ForegroundColor Red
    $missing += "python"
}

@("nadakki_env", "nadakki_env_clean", ".venv") | ForEach-Object {
    if (Test-Path $_) { 
        Write-Host "[OK] Entorno virtual: $_" -ForegroundColor Green; $existing += "venv"; return 
    }
}
if ($existing -notcontains "venv") { 
    Write-Host "[FALTA] Entorno virtual" -ForegroundColor Red; $missing += "venv" 
}

Write-Host "`n=== RESULTADO ===" -ForegroundColor Magenta
Write-Host "Componentes OK: $($existing.Count)" -ForegroundColor Green
Write-Host "Faltantes: $($missing.Count)" -ForegroundColor Red

if ($missing.Count -eq 0) {
    Write-Host "✅ SISTEMA COMPLETO - LISTO PARA USAR" -ForegroundColor Green
} else {
    Write-Host "Faltantes: $($missing -join ', ')" -ForegroundColor Yellow
    if ($AutoFix) {
        Write-Host "Creando script de corrección..." -ForegroundColor Yellow
        'python -m venv nadakki_env; Write-Host "Entorno creado"' | Out-File "fix_nadakki.ps1"
        Write-Host "Ejecuta: ./fix_nadakki.ps1" -ForegroundColor Cyan
    }
}
