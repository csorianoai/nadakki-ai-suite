[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$json = Get-Content -Path "qa_summary.json" | ConvertFrom-Json

$ecosistemas = @{}

foreach ($item in $json) {
    $ecosistemaKey = $item.Ecosistema.Trim().ToUpper()

    if (-not $ecosistemas.ContainsKey($ecosistemaKey)) {
        $ecosistemas[$ecosistemaKey] = @{
            Total = 0
            Incompletos = 0
            Completos = 0
            TamanoTotal = 0.0
            ArchivosInvalidos = @()
        }
    }

    $ecosistemas[$ecosistemaKey].Total++

    if ($item.Estado -eq "Incompleto") {
        $ecosistemas[$ecosistemaKey].Incompletos++
    } else {
        $ecosistemas[$ecosistemaKey].Completos++
    }

    try {
        $tamano = [double]$item.TamanoKb
        $ecosistemas[$ecosistemaKey].TamanoTotal += $tamano

        if ($tamano -eq 0) {
            $ecosistemas[$ecosistemaKey].ArchivosInvalidos += $item.Archivo
        }
    } catch {
        $ecosistemas[$ecosistemaKey].ArchivosInvalidos += $item.Archivo
    }
}

# Mostrar resumen en consola
foreach ($eco in $ecosistemas.Keys) {
    $data = $ecosistemas[$eco]
    $promedio = if ($data.Total -gt 0) { $data.TamanoTotal / $data.Total } else { 0 }
    Write-Host "=== $eco ==="
    Write-Host "Total agentes: $($data.Total)"
    Write-Host "Completos: $($data.Completos)"
    Write-Host "Incompletos: $($data.Incompletos)"
    Write-Host "Tamaño promedio: $([math]::Round($promedio, 2)) KB"
    Write-Host "Archivos inválidos: $($data.ArchivosInvalidos.Count)"
    Write-Host ""
}

# Exportar resumen a archivo UTF-8
$output = @()

foreach ($eco in $ecosistemas.Keys) {
    $data = $ecosistemas[$eco]
    $promedio = if ($data.Total -gt 0) { $data.TamanoTotal / $data.Total } else { 0 }

    $output += "=== $eco ==="
    $output += "Total agentes: $($data.Total)"
    $output += "Completos: $($data.Completos)"
    $output += "Incompletos: $($data.Incompletos)"
    $output += "Tamaño promedio: $([math]::Round($promedio, 2)) KB"
    $output += "Archivos inválidos: $($data.ArchivosInvalidos.Count)"
    $output += ""
}

$output | Out-File -Encoding UTF8 "qa_audit_result.txt"
notepad "qa_audit_result.txt"
