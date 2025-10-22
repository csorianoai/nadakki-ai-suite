param (
  [string]$NombreTenant,
  [ValidateSet("starter", "professional", "enterprise")]
  [string]$Plan
)

# CONFIGURACIÓN SMTP - Microsoft 365 via GoDaddy
$EmailFrom = "ramon@nadaki.com"
$EmailTo = "ops@nadaki.com"
$SmtpServer = "smtp.office365.com"
$SmtpUser = "ramon@nadaki.com"
$SmtpPass = "Richard20152015$#@"
$Puerto = 587

if (-not $NombreTenant) {
  $NombreTenant = Read-Host "Ingresa el nombre del nuevo tenant"
}
if (-not $Plan) {
  $Plan = Read-Host "Ingresa el plan (starter, professional, enterprise)"
}

$Ruta = "public/config/tenants/$NombreTenant.json"
$IndexFile = "public/config/tenants/tenants_index.json"
$LogFile = "logs/tenants.log"

if (-not (Test-Path "logs")) {
  New-Item -ItemType Directory -Path "logs" | Out-Null
}

if (Test-Path $Ruta) {
  Write-Host "⚠️ Ya existe un tenant con ese nombre." -ForegroundColor Yellow
  exit
}

$json = "{`n  `"plan`": `"$Plan`"`n}"
Set-Content -Path $Ruta -Value $json -Encoding UTF8

$tenants = @()
if (Test-Path $IndexFile) {
  $tenants = Get-Content $IndexFile | ConvertFrom-Json
}
$tenants += [pscustomobject]@{ tenant = $NombreTenant; plan = $Plan; created = (Get-Date).ToString("s") }
$tenants | ConvertTo-Json -Depth 3 | Set-Content -Encoding UTF8 $IndexFile

$logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Tenant: $NombreTenant | Plan: $Plan"
Add-Content -Path $LogFile -Value $logEntry

# Enviar correo
try {
  $Subject = "✅ Nuevo Tenant creado: $NombreTenant"
  $Body = @"
Se ha creado un nuevo tenant en Nadakki AI Suite.

Nombre: $NombreTenant
Plan: $Plan
Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

-- Nadakki System
"@

  Send-MailMessage -From $EmailFrom -To $EmailTo -Subject $Subject -Body $Body `
    -SmtpServer $SmtpServer -Port $Puerto -UseSsl `
    -Credential (New-Object PSCredential $SmtpUser, (ConvertTo-SecureString $SmtpPass -AsPlainText -Force))

  Write-Host "📧 Correo enviado desde $EmailFrom a $EmailTo" -ForegroundColor Cyan
} catch {
  Write-Host "❌ Error al enviar correo: $_" -ForegroundColor Red
}

Write-Host "✅ Tenant '$NombreTenant' creado, registrado y notificado." -ForegroundColor Green
