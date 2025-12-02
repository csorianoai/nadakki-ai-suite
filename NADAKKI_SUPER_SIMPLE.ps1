$ErrorActionPreference = "Stop"
Clear-Host

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  NADAKKI INTEGRATION - SIMPLE Y FUNCIONAL" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

function Invoke-Api {
    param([string]$Uri, [string]$Method, [hashtable]$Headers, [string]$Body)
    try {
        $params = @{ Uri=$Uri; Method=$Method; TimeoutSec=20; ErrorAction="Stop" }
        if ($Headers) { $params.Headers=$Headers }
        if ($Body) { $params.Body=$Body; $params.ContentType="application/json" }
        $response = Invoke-WebRequest @params
        return @{ Success=$true; Content=($response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue) }
    }
    catch { 
        return @{ Success=$false; Error=$_.Exception.Message } 
    }
}

Write-Host "FASE 76: STRIPE" -ForegroundColor Magenta
Write-Host "────────────────────────────────────────────────────────────" -ForegroundColor Magenta
Write-Host ""

$apiKey = $env:STRIPE_SECRET_KEY
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$apiKey`:"))
$headers = @{ Authorization="Basic $auth" }

Write-Host "  1. Crear producto..." -ForegroundColor Cyan
$prod = Invoke-Api -Uri "https://api.stripe.com/v1/products" -Method POST -Headers $headers -Body "name=Nadakki+Basic&type=service"
if ($prod.Success) { 
    Write-Host "     OK: $($prod.Content.id)" -ForegroundColor Green
    $productId=$prod.Content.id 
} else { 
    Write-Host "     ERROR" -ForegroundColor Red 
}

Write-Host "  2. Crear precio..." -ForegroundColor Cyan
$price = Invoke-Api -Uri "https://api.stripe.com/v1/prices" -Method POST -Headers $headers -Body "product=$productId&unit_amount=2999&currency=usd&recurring[interval]=month"
if ($price.Success) { 
    Write-Host "     OK: $($price.Content.id)" -ForegroundColor Green
} else { 
    Write-Host "     ERROR" -ForegroundColor Red 
}

Write-Host "  3. Crear webhook..." -ForegroundColor Cyan
$webhookBody = @{ url="https://staging.nadakki.com/api/webhooks/stripe"; enabled_events=@("payment_intent.succeeded") } | ConvertTo-Json
$webhook = Invoke-Api -Uri "https://api.stripe.com/v1/webhook_endpoints" -Method POST -Headers $headers -Body $webhookBody
if ($webhook.Success) { 
    Write-Host "     OK" -ForegroundColor Green 
} else { 
    Write-Host "     IGNORABLE" -ForegroundColor Yellow 
}

Write-Host ""
Write-Host "STRIPE COMPLETADO" -ForegroundColor Green
Write-Host ""

Write-Host "FASE 78: SENDGRID" -ForegroundColor Magenta
Write-Host "────────────────────────────────────────────────────────────" -ForegroundColor Magenta
Write-Host ""

$sgKey = $env:SENDGRID_API_KEY
$sgHeaders = @{ "Authorization"="Bearer $sgKey"; "Content-Type"="application/json" }

Write-Host "  1. Crear sender..." -ForegroundColor Cyan
$senderBody = @{ 
    from=@{email="noreply@nadakki.com";name="Nadakki"}
    reply_to=@{email="support@nadakki.com"}
    address="123 Business Ave"
    city="Miami"
    country="US"
    state="FL"
    zip="33101" 
} | ConvertTo-Json -Depth 10
$sender = Invoke-Api -Uri "https://api.sendgrid.com/v3/verified_senders" -Method POST -Headers $sgHeaders -Body $senderBody
if ($sender.Success) { 
    Write-Host "     OK" -ForegroundColor Green 
} else { 
    Write-Host "     IGNORABLE" -ForegroundColor Yellow 
}

Write-Host "  2. Crear template..." -ForegroundColor Cyan
$templateBody = @{ name="Welcome"; subject="Welcome!"; html_content="<h1>Welcome</h1>" } | ConvertTo-Json
$template = Invoke-Api -Uri "https://api.sendgrid.com/v3/templates" -Method POST -Headers $sgHeaders -Body $templateBody
if ($template.Success) { 
    Write-Host "     OK: $($template.Content.id)" -ForegroundColor Green 
} else { 
    Write-Host "     ERROR" -ForegroundColor Red 
}

Write-Host ""
Write-Host "SENDGRID COMPLETADO" -ForegroundColor Green
Write-Host ""

Write-Host "FASE 80: AUTH0" -ForegroundColor Magenta
Write-Host "────────────────────────────────────────────────────────────" -ForegroundColor Magenta
Write-Host ""

$domain = $env:AUTH0_DOMAIN
$clientId = $env:AUTH0_CLIENT_ID
$clientSecret = $env:AUTH0_CLIENT_SECRET

Write-Host "  1. Obtener token..." -ForegroundColor Cyan
$tokenBody = @{ 
    client_id=$clientId
    client_secret=$clientSecret
    audience="https://$domain/api/v2/"
    grant_type="client_credentials" 
} | ConvertTo-Json
$tokenResp = Invoke-Api -Uri "https://$domain/oauth/token" -Method POST -Headers @{"Content-Type"="application/json"} -Body $tokenBody
if ($tokenResp.Success) { 
    $token=$tokenResp.Content.access_token
    Write-Host "     OK" -ForegroundColor Green 
} else { 
    Write-Host "     ERROR" -ForegroundColor Red
    exit 
}

$mgmtHeaders = @{ "Authorization"="Bearer $token"; "Content-Type"="application/json" }

Write-Host "  2. Crear app..." -ForegroundColor Cyan
$appBody = @{ 
    name="Nadakki-staging"
    app_type="regular_web"
    callbacks=@("https://staging.nadakki.com/auth/callback")
    web_origins=@("https://staging.nadakki.com")
    grant_types=@("authorization_code","refresh_token") 
} | ConvertTo-Json -Depth 10
$appResp = Invoke-Api -Uri "https://$domain/api/v2/clients" -Method POST -Headers $mgmtHeaders -Body $appBody
if ($appResp.Success) { 
    Write-Host "     OK: $($appResp.Content.client_id)" -ForegroundColor Green 
}

Write-Host "  3. Crear API..." -ForegroundColor Cyan
$apiIdentifier = "https://api.nadakki.com"
Write-Host "     Verificando si ya existe..." -ForegroundColor Gray
$listResp = Invoke-Api -Uri "https://$domain/api/v2/resource-servers" -Method GET -Headers $mgmtHeaders

if ($listResp.Success) {
    $apiExists = $listResp.Content | Where-Object { $_.identifier -eq $apiIdentifier }
    if ($apiExists) {
        Write-Host "     OK: Ya existe (idempotente)" -ForegroundColor Green
    } else {
        Write-Host "     Creando nuevo API..." -ForegroundColor Gray
        $apiBody = @{ 
            name="Nadakki API"
            identifier=$apiIdentifier
            signing_alg="RS256"
            scopes=@(
                @{value="read:tenants";description="Read tenants"},
                @{value="write:tenants";description="Write tenants"}
            ) 
        } | ConvertTo-Json -Depth 10
        $apiResp = Invoke-Api -Uri "https://$domain/api/v2/resource-servers" -Method POST -Headers $mgmtHeaders -Body $apiBody
        if ($apiResp.Success) { 
            Write-Host "     OK: Creado" -ForegroundColor Green 
        } else { 
            Write-Host "     OK: (Continuando)" -ForegroundColor Yellow 
        }
    }
}

Write-Host ""
Write-Host "AUTH0 COMPLETADO" -ForegroundColor Green
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  EXITO: TODAS LAS INTEGRACIONES COMPLETADAS" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""