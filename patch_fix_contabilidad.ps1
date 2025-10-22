Write-Host "Aplicando patch a ContabilidadCoordinator y corrigiendo instancias..."

# Ruta del archivo coordinador
$coordinatorPath = ".\agents\contabilidad\contabilidad_coordinator.py"
$content = Get-Content $coordinatorPath -Raw

# 1) Agregar alias get_module_status si no existe
if ($content -notmatch "def get_module_status") {
    Write-Host "Agregando alias get_module_status()..."
    $aliasCode = @'
    def get_module_status(self):
        """Alias para compatibilidad con versiones anteriores"""
        return self.get_status_all_agents()
'@
    $content += "`n" + $aliasCode
    Set-Content $coordinatorPath -Value $content -Encoding UTF8
} else {
    Write-Host "Alias get_module_status() ya existe — no modificado"
}

# 2) Corregir instancias erróneas en otros archivos
$filesToFix = @(
    ".\agentes_contabilidad_completos.py",
    ".\test_accounting_status.py"
)

foreach ($file in $filesToFix) {
    if (Test-Path $file) {
        $text = Get-Content $file -Raw
        $pattern = 'ContabilidadCoordinator\(\s*\{[^\}]*\}\s*\)'
        if ($text -match $pattern) {
            Write-Host "Corrigiendo instanciación en $file..."
            $text = [regex]::Replace($text, $pattern, 'ContabilidadCoordinator("demo")')
            Set-Content $file -Value $text -Encoding UTF8
        } else {
            Write-Host "$file no necesita cambios"
        }
    }
}

Write-Host "Patch aplicado correctamente."
