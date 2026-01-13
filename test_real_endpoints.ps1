# NADAKKI - TEST CORREGIDO CON PREFIJOS REALES
$BACKEND = "https://nadakki-ai-suite.onrender.com"

Write-Host "=== TESTING ENDPOINTS REALES ===" -ForegroundColor Cyan

# Health
Write-Host "`nHealth Check..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/health" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# Agents
Write-Host "GET /agents..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/agents" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# Workflows
Write-Host "GET /workflows..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/workflows" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# Workflows Health
Write-Host "GET /workflows/health..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/workflows/health" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# API Campaigns (prefijo real)
Write-Host "GET /api/campaigns..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/api/campaigns" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL: $_" -ForegroundColor Red }

# API Segments
Write-Host "GET /api/segments..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/api/segments" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL: $_" -ForegroundColor Red }

# API Journeys
Write-Host "GET /api/journeys..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/api/journeys" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL: $_" -ForegroundColor Red }

# API Templates
Write-Host "GET /api/templates..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/api/templates" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL: $_" -ForegroundColor Red }

# API Integrations
Write-Host "GET /api/integrations..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/api/integrations" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL: $_" -ForegroundColor Red }

# Cores (este da 500)
Write-Host "GET /cores..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/cores" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL (500)" -ForegroundColor Red }

# Marketing Core específico
Write-Host "GET /cores/marketing..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/cores/marketing" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# Tenants
Write-Host "GET /tenants..." -NoNewline
try { 
    Invoke-RestMethod "$BACKEND/tenants" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# Test Agent Execute - Lead Scoring
Write-Host "POST /agents/marketing/leadscoringia/execute..." -NoNewline
$body = '{"lead_id":"test","score":75}'
try { 
    Invoke-RestMethod "$BACKEND/agents/marketing/leadscoringia/execute" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

# Test Agent - Audience Segmentation (nombre correcto)
Write-Host "POST /agents/marketing/audiencesegmenteria/execute..." -NoNewline
$body = '{"criteria":{"age_min":25}}'
try { 
    Invoke-RestMethod "$BACKEND/agents/marketing/audiencesegmenteria/execute" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30 | Out-Null
    Write-Host " OK" -ForegroundColor Green 
} catch { Write-Host " FAIL" -ForegroundColor Red }

Write-Host "`n=== TEST COMPLETADO ===" -ForegroundColor Cyan
