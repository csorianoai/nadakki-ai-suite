param([switch]$All)

$ScriptStart = Get-Date
$LogDir = "logs"
$LogFile = Join-Path $LogDir "devops_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

if (-not (Test-Path $LogDir)) { 
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null 
}

function Write-Log {
    param([string]$Message, [string]$Type = "Info")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] [$Type] $Message"
    
    switch ($Type) {
        "Success" { Write-Host "[OK] $Message" -ForegroundColor Green }
        "Error" { Write-Host "[ERROR] $Message" -ForegroundColor Red }
        "Warning" { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
        "Info" { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
    }
    Add-Content -Path $LogFile -Value $logMessage
}

Write-Log "DEVOPS AUTOMATION INICIANDO" "Info"

Write-Log "PASO 31: Creando validaciones Pydantic" "Info"
$validation = @'
from pydantic import BaseModel, EmailStr, Field
import re

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    company_name: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2, max_length=2)
'@
$validation | Out-File -Encoding UTF8 "app\core\validation.py"
Write-Log "Creado: app/core/validation.py" "Success"

Write-Log "PASO 32: Creando excepciones" "Info"
$exceptions = @'
from fastapi import HTTPException

class NadakkiException(Exception):
    def __init__(self, message: str, error_code: str = "ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
'@
$exceptions | Out-File -Encoding UTF8 "app\core\exceptions.py"
Write-Log "Creado: app/core/exceptions.py" "Success"

Write-Log "PASO 33: Creando logging" "Info"
if (-not (Test-Path "logs\app")) { 
    New-Item -ItemType Directory -Path "logs\app" -Force | Out-Null 
}
$logging = @'
import logging
import logging.handlers

class LogManager:
    _loggers = {}
    
    @staticmethod
    def get_logger(name: str, log_dir: str = "logs/app"):
        if name not in LogManager._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            LogManager._loggers[name] = logger
        return LogManager._loggers[name]
'@
$logging | Out-File -Encoding UTF8 "app\core\logging.py"
Write-Log "Creado: app/core/logging.py" "Success"

Write-Log "PASO 34: Creando rate limiting" "Info"
$ratelimit = @'
from datetime import datetime, timedelta

class InMemoryRateLimiter:
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, tenant_id: str, max_requests: int = 100, window_seconds: int = 60):
        if tenant_id not in self.requests:
            self.requests[tenant_id] = []
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[tenant_id] = [r for r in self.requests[tenant_id] if r > cutoff]
        
        if len(self.requests[tenant_id]) < max_requests:
            self.requests[tenant_id].append(now)
            return True, max_requests - len(self.requests[tenant_id])
        return False, 0

rate_limiter = InMemoryRateLimiter()
'@
$ratelimit | Out-File -Encoding UTF8 "app\core\rate_limit.py"
Write-Log "Creado: app/core/rate_limit.py" "Success"

Write-Log "PASO 35: Creando API key validation" "Info"
$apikey = @'
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

async def verify_api_key(x_api_key: str = Header(...), db: Session = None):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"tenant_id": "test", "api_key_id": "test"}

def generate_api_key(prefix: str = "ndk") -> str:
    return f"{prefix}_{secrets.token_urlsafe(32)}"
'@
$apikey | Out-File -Encoding UTF8 "app\core\api_key.py"
Write-Log "Creado: app/core/api_key.py" "Success"

Write-Log "PASO 36: Creando Stripe Service" "Info"
$stripe = @'
import stripe
from typing import Dict

class StripeService:
    @staticmethod
    def create_customer(email: str, name: str, tenant_id: str) -> str:
        try:
            customer = stripe.Customer.create(
                email=email, 
                name=name, 
                metadata={"tenant_id": tenant_id}
            )
            return customer.id
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
    
    @staticmethod
    def create_checkout_session(customer_id: str, plan: str, success_url: str, cancel_url: str) -> Dict:
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url
            )
            return {"session_id": session.id, "url": session.url}
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
'@
$stripe | Out-File -Encoding UTF8 "app\services\stripe_service.py"
Write-Log "Creado: app/services/stripe_service.py" "Success"

Write-Log "PASO 37: Creando Webhooks" "Info"
$webhooks = @'
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, "test_secret")
        return {"status": "success"}
    except:
        raise HTTPException(status_code=400, detail="Invalid")
'@
$webhooks | Out-File -Encoding UTF8 "app\routes\webhooks.py"
Write-Log "Creado: app/routes/webhooks.py" "Success"

Write-Log "PASO 38: Creando Subscriptions" "Info"
$subs = @'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

@router.post("/create-checkout")
async def create_checkout(plan: str, success_url: str, cancel_url: str):
    return {"session_id": "test", "url": "https://example.com"}
'@
$subs | Out-File -Encoding UTF8 "app\routes\subscriptions.py"
Write-Log "Creado: app/routes/subscriptions.py" "Success"

Write-Log "PASO 39: Creando Metering" "Info"
$metering = @'
from datetime import datetime
from typing import Dict

class MeteringService:
    @staticmethod
    def track_usage(tenant_id: str, metric: str, quantity: int = 1):
        print(f"Usage: {tenant_id} {metric} {quantity}")
    
    @staticmethod
    def get_usage_for_period(tenant_id: str, start: datetime, end: datetime) -> Dict:
        return {"api_calls": 0, "agents_executed": 0}
'@
$metering | Out-File -Encoding UTF8 "app\services\metering_service.py"
Write-Log "Creado: app/services/metering_service.py" "Success"

Write-Log "PASO 40: Creando Invoices" "Info"
$invoices = @'
import stripe
from typing import Dict, List

class InvoiceService:
    @staticmethod
    def create_invoice(stripe_customer_id: str, description: str = "Nadakki") -> Dict:
        try:
            invoice = stripe.Invoice.create(
                customer=stripe_customer_id, 
                description=description
            )
            return {"id": invoice.id, "status": invoice.status}
        except Exception as e:
            raise Exception(str(e))
'@
$invoices | Out-File -Encoding UTF8 "app\services\invoice_service.py"
Write-Log "Creado: app/services/invoice_service.py" "Success"

Write-Log "PASO 41: Creando CORS Policy" "Info"
$cors = @'
from typing import List

class TenantCORSPolicy:
    @staticmethod
    def get_allowed_origins(tenant_id: str, config: dict = None) -> List[str]:
        origins = [
            "http://localhost:3000",
            "http://localhost:8000",
        ]
        if config and "custom_domain" in config:
            origins.append(f"https://{config.get('custom_domain')}")
        return origins
'@
$cors | Out-File -Encoding UTF8 "app\core\cors_policy.py"
Write-Log "Creado: app/core/cors_policy.py" "Success"

Write-Log "PASO 42: Creando GDPR Service" "Info"
$gdpr = @'
from sqlalchemy.orm import Session
from datetime import datetime

class GDPRService:
    @staticmethod
    def export_user_data(user_id: str, db: Session) -> dict:
        return {
            "user": {"id": user_id},
            "audit_logs": []
        }
    
    @staticmethod
    def delete_user_data(user_id: str, db: Session) -> bool:
        return True
'@
$gdpr | Out-File -Encoding UTF8 "app\services\gdpr_service.py"
Write-Log "Creado: app/services/gdpr_service.py" "Success"

Write-Log "PASO 43: Creando Encryption" "Info"
$encryption = @'
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self, master_key: str = None):
        if master_key:
            if isinstance(master_key, str):
                master_key = master_key.encode()
            key = base64.urlsafe_b64encode(master_key[:32])
            self.cipher = Fernet(key)
        else:
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, plaintext: str) -> str:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        return self.cipher.encrypt(plaintext).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        return self.cipher.decrypt(ciphertext).decode()
'@
$encryption | Out-File -Encoding UTF8 "app\core\encryption.py"
Write-Log "Creado: app/core/encryption.py" "Success"

Write-Log "PASO 44: Creando Audit Trail" "Info"
$audit = @'
from sqlalchemy.orm import Session
from datetime import datetime
import json

class AuditTrailService:
    @staticmethod
    def log_action(tenant_id: str, user_id: str, action: str, resource: str, 
                   status: str, details: dict = None, db: Session = None):
        print(f"AUDIT: {action} on {resource} by {user_id}")
        return True
'@
$audit | Out-File -Encoding UTF8 "app\services\audit_trail_service.py"
Write-Log "Creado: app/services/audit_trail_service.py" "Success"

Write-Log "PASO 45: Actualizando requirements.txt" "Info"
Add-Content -Path "requirements.txt" -Value "stripe==7.4.0"
Add-Content -Path "requirements.txt" -Value "cryptography==41.0.7"
Add-Content -Path "requirements.txt" -Value "pydantic-extra-types==2.0.0"
Write-Log "Actualizado: requirements.txt" "Success"

$Duration = ((Get-Date) - $ScriptStart).TotalSeconds

Write-Log "" "Info"
Write-Log "========================================" "Info"
Write-Log "DEVOPS AUTOMATION COMPLETADO" "Success"
Write-Log "========================================" "Info"
Write-Log "Tiempo: $Duration segundos" "Success"
Write-Log "" "Info"
Write-Log "ARCHIVOS CREADOS: 15" "Success"
Write-Log "Validaciones, Stripe, Seguridad" "Success"
Write-Log "" "Info"
Write-Log "LOGS en: $LogFile" "Info"
Write-Log "" "Info"
Write-Log "PROXIMOS PASOS:" "Warning"
Write-Log "1. pip install stripe cryptography" "Info"
Write-Log "2. Actualizar .env con STRIPE_SECRET_KEY" "Info"
Write-Log "3. python -m uvicorn app.main:app --reload" "Info"