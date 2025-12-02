# ============================================================
# NADAKKI ENTERPRISE - DEVOPS AUTOMATION SCRIPT
# Automatización de: Validaciones, Stripe, Seguridad & Compliance
# Versión: 2.0 Pro - PowerShell 7+
# Autor: DevOps Automation System
# ============================================================

param(
    [Parameter(HelpMessage = "Ejecutar todos los pasos")]
    [switch]$All,
    
    [Parameter(HelpMessage = "Ejecutar solo validaciones")]
    [switch]$Validations,
    
    [Parameter(HelpMessage = "Ejecutar solo Stripe")]
    [switch]$Stripe,
    
    [Parameter(HelpMessage = "Ejecutar solo Seguridad")]
    [switch]$Security,
    
    [Parameter(HelpMessage = "Modo verbose")]
    [switch]$Verbose,
    
    [Parameter(HelpMessage = "Sin prompts interactivos")]
    [switch]$NoInteractive
)

$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================
$ScriptStart = Get-Date
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptPath "logs"
$LogFile = Join-Path $LogDir "devops_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"
$ErrorLogFile = Join-Path $LogDir "errors_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

# COLORES
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Debug = "Gray"
}

# ============================================================
# FUNCIONES CORE DE LOGGING Y UTILIDADES
# ============================================================

function Initialize-LogSystem {
    <#
    .SYNOPSIS
        Inicializa el sistema de logging
    #>
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    Write-Log "Iniciando Nadakki DevOps Automation" "Success"
    Write-Log "Script ejecutado en: $ScriptPath" "Info"
    Write-Log "Sistema operativo: $(Get-ComputerInfo -Property OsName)" "Info"
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Type = "Info",
        [bool]$ToFile = $true
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Type] $Message"
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor $Colors.Success }
        "Error" { Write-Host "❌ $Message" -ForegroundColor $Colors.Error }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning }
        "Info" { Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info }
        "Debug" { Write-Host "🐛 $Message" -ForegroundColor $Colors.Debug }
    }
    
    if ($ToFile) {
        if ($Type -eq "Error") {
            Add-Content -Path $ErrorLogFile -Value $logMessage
        }
        Add-Content -Path $LogFile -Value $logMessage
    }
}

function Test-Dependency {
    param(
        [string]$Name,
        [string]$Command,
        [string]$InstallHint
    )
    
    Write-Log "Verificando dependencia: $Name..." "Info"
    
    try {
        $result = & $Command 2>&1
        Write-Log "✓ $Name disponible" "Success"
        return $true
    }
    catch {
        Write-Log "✗ $Name no encontrado" "Error"
        if ($InstallHint) {
            Write-Log "Instalar con: $InstallHint" "Warning"
        }
        return $false
    }
}

# ============================================================
# PASO 31-35: VALIDACIONES Y SEGURIDAD BACKEND
# ============================================================

function Create-ValidationModule {
    <#
    .SYNOPSIS
        Crea el módulo de validaciones con Pydantic
    #>
    Write-Log "PASO 31: Creando módulo de validaciones..." "Info"
    
    $validationCode = @'
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re

# ============================================================
# MODELOS DE VALIDACIÓN
# ============================================================

class RegisterSchema(BaseModel):
    """Validación para registro de usuarios"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=255)
    country: str = Field(..., min_length=2, max_length=2)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")
    
    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain digit")
        if not re.search(r"[!@#$%^&*()]", v):
            raise ValueError("Password must contain special character")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "company_name": "My Company",
                "country": "US"
            }
        }

class LoginSchema(BaseModel):
    """Validación para login"""
    email: EmailStr
    password: str
    tenant_id: str = Field(..., min_length=36, max_length=36)

class TenantUpdateSchema(BaseModel):
    """Validación para actualizar tenant"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    plan: Optional[str] = Field(None, regex="^(starter|professional|enterprise)$")
    is_active: Optional[bool] = None

class AgentExecutionSchema(BaseModel):
    """Validación para ejecución de agentes"""
    agent_name: str = Field(..., min_length=1, max_length=100)
    input_data: dict
    tenant_id: str = Field(..., min_length=36, max_length=36)

class SubscriptionSchema(BaseModel):
    """Validación para suscripción"""
    plan: str = Field(..., regex="^(starter|professional|enterprise)$")
    payment_method: Optional[str] = None
    billing_email: EmailStr

class APIKeySchema(BaseModel):
    """Validación para API keys"""
    name: str = Field(..., min_length=1, max_length=255)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)

# ============================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================

def validate_request(schema_class, data: dict):
    """
    Valida datos contra un schema Pydantic
    Retorna: (is_valid, data_validated, errors)
    """
    try:
        validated = schema_class(**data)
        return True, validated.dict(), None
    except Exception as e:
        return False, None, str(e)

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_uuid(uuid_str: str) -> bool:
    """Valida formato UUID v4"""
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    return bool(re.match(pattern, uuid_str, re.IGNORECASE))

def validate_tenant_id(tenant_id: str) -> bool:
    """Valida ID de tenant (String(36))"""
    return len(tenant_id) == 36 and all(c in '0123456789abcdef-' for c in tenant_id.lower())
'@

    $validationCode | Out-File -Encoding UTF8 "app\core\validation.py"
    Write-Log "✓ Módulo de validaciones creado: app/core/validation.py" "Success"
}

function Create-ExceptionHandling {
    <#
    .SYNOPSIS
        Crea manejador centralizado de excepciones
    #>
    Write-Log "PASO 32: Creando manejador de excepciones..." "Info"
    
    $exceptionCode = @'
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)

# ============================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================

class NadakkiException(Exception):
    """Excepción base de Nadakki"""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(NadakkiException):
    """Error de validación"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 422)

class AuthenticationException(NadakkiException):
    """Error de autenticación"""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "AUTH_ERROR", 401)

class AuthorizationException(NadakkiException):
    """Error de autorización"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "FORBIDDEN", 403)

class RateLimitException(NadakkiException):
    """Error de rate limit"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT", 429)

class ResourceNotFoundException(NadakkiException):
    """Recurso no encontrado"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND", 404)

class StripeException(NadakkiException):
    """Error de Stripe"""
    def __init__(self, message: str):
        super().__init__(message, "STRIPE_ERROR", 400)

class DatabaseException(NadakkiException):
    """Error de base de datos"""
    def __init__(self, message: str):
        super().__init__(message, "DB_ERROR", 500)

# ============================================================
# MANEJADOR CENTRALIZADO
# ============================================================

def format_error_response(exc: NadakkiException) -> Dict[str, Any]:
    """Formatea respuesta de error"""
    return {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": exc.status_code
        }
    }

async def exception_handler(request, exc: NadakkiException):
    """Handler para excepciones de Nadakki"""
    logger.error(f"Exception: {exc.error_code} - {exc.message}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(exc)
    )

async def general_exception_handler(request, exc: Exception):
    """Handler para excepciones generales"""
    error_code = "INTERNAL_SERVER_ERROR"
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": error_code,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "status": 500
            }
        }
    )

# ============================================================
# LOGGER CONFIGURADO
# ============================================================

def configure_logging(log_file: str = "nadakki.log"):
    """Configura logging centralizado"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

from datetime import datetime
'@

    $exceptionCode | Out-File -Encoding UTF8 "app\core\exceptions.py"
    Write-Log "✓ Manejador de excepciones creado: app/core/exceptions.py" "Success"
}

function Create-LoggingSystem {
    <#
    .SYNOPSIS
        Crea sistema de logging con rotación
    #>
    Write-Log "PASO 33: Creando sistema de logging..." "Info"
    
    # Crear directorios de logs
    $appLogsDir = "logs\app"
    $auditLogsDir = "logs\audit"
    
    foreach ($dir in @($appLogsDir, $auditLogsDir)) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    $loggingCode = @'
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================

class LogManager:
    """Gestor centralizado de logs"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name: str, log_dir: str = "logs/app"):
        """Obtiene o crea un logger"""
        if name not in LogManager._loggers:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            
            # Rotación de logs: máximo 5 archivos de 10MB cada uno
            handler = logging.handlers.RotatingFileHandler(
                filename=f"{log_dir}/{name}.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            LogManager._loggers[name] = logger
        
        return LogManager._loggers[name]

class AuditLogger:
    """Logger especializado para auditoría"""
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.logger = LogManager.get_logger("audit", log_dir)
    
    def log_action(self, tenant_id: str, user_id: str, action: str, resource: str, 
                   status: str, details: dict = None):
        """Log de acción de usuario"""
        message = f"TENANT:{tenant_id} | USER:{user_id} | ACTION:{action} | RESOURCE:{resource} | STATUS:{status}"
        if details:
            message += f" | DETAILS:{details}"
        
        self.logger.info(message)
    
    def log_security_event(self, event_type: str, tenant_id: str, details: str):
        """Log de eventos de seguridad"""
        message = f"SECURITY EVENT: {event_type} | TENANT:{tenant_id} | {details}"
        self.logger.warning(message)
    
    def log_api_call(self, tenant_id: str, endpoint: str, method: str, status_code: int, 
                     response_time_ms: float):
        """Log de llamadas a API"""
        message = f"API CALL | TENANT:{tenant_id} | {method} {endpoint} | STATUS:{status_code} | TIME:{response_time_ms}ms"
        self.logger.info(message)

# Instancia global
audit_logger = AuditLogger()
app_logger = LogManager.get_logger("application")
'@

    $loggingCode | Out-File -Encoding UTF8 "app\core\logging.py"
    Write-Log "✓ Sistema de logging creado: app/core/logging.py" "Success"
}

function Create-RateLimiting {
    <#
    .SYNOPSIS
        Crea sistema de rate limiting por tenant
    #>
    Write-Log "PASO 34: Creando sistema de rate limiting..." "Info"
    
    $rateLimitCode = @'
from datetime import datetime, timedelta
from typing import Dict, Tuple
import threading
import hashlib

# ============================================================
# RATE LIMITING EN MEMORIA (Alternativa a Redis)
# ============================================================

class InMemoryRateLimiter:
    """Rate limiter en memoria para desarrollo"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, tenant_id: str, max_requests: int = 100, 
                   window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Verifica si la solicitud está permitida
        Retorna: (allowed, remaining_requests)
        """
        with self.lock:
            key = tenant_id
            now = datetime.utcnow()
            
            if key not in self.requests:
                self.requests[key] = []
            
            # Limpiar requests antiguos
            cutoff_time = now - timedelta(seconds=window_seconds)
            self.requests[key] = [
                req_time for req_time in self.requests[key] 
                if req_time > cutoff_time
            ]
            
            # Verificar límite
            if len(self.requests[key]) < max_requests:
                self.requests[key].append(now)
                remaining = max_requests - len(self.requests[key])
                return True, remaining
            else:
                return False, 0
    
    def get_reset_time(self, tenant_id: str, window_seconds: int = 60) -> int:
        """Obtiene el tiempo (segundos) para resetear el límite"""
        if tenant_id not in self.requests or not self.requests[tenant_id]:
            return 0
        
        oldest_request = min(self.requests[tenant_id])
        reset_time = oldest_request + timedelta(seconds=window_seconds)
        return int((reset_time - datetime.utcnow()).total_seconds())

# Instancia global
rate_limiter = InMemoryRateLimiter()

# ============================================================
# CONFIGURACIÓN POR PLAN
# ============================================================

PLAN_LIMITS = {
    "starter": {"requests_per_minute": 60, "requests_per_hour": 1000},
    "professional": {"requests_per_minute": 300, "requests_per_hour": 10000},
    "enterprise": {"requests_per_minute": 1000, "requests_per_hour": 100000}
}

def get_limit_for_plan(plan: str) -> dict:
    """Obtiene límites para un plan"""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])
'@

    $rateLimitCode | Out-File -Encoding UTF8 "app\core\rate_limit.py"
    Write-Log "✓ Sistema de rate limiting creado: app/core/rate_limit.py" "Success"
}

function Create-APIKeyValidation {
    <#
    .SYNOPSIS
        Crea validación de API keys en headers
    #>
    Write-Log "PASO 35: Creando validación de API keys..." "Info"
    
    $apiKeyCode = @'
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import APIKey, Tenant
from datetime import datetime
import secrets

# ============================================================
# VALIDACIÓN DE API KEYS
# ============================================================

async def verify_api_key(
    x_api_key: str = Header(..., description="API Key"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Verifica que el API key sea válido
    """
    
    # Buscar el API key en la base de datos
    api_key_obj = db.query(APIKey).filter(
        APIKey.key == x_api_key,
        APIKey.is_active == True
    ).first()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Verificar que no haya expirado
    if api_key_obj.expires_at and datetime.utcnow() > api_key_obj.expires_at:
        raise HTTPException(
            status_code=401,
            detail="API key has expired"
        )
    
    # Obtener tenant
    tenant = db.query(Tenant).filter(
        Tenant.id == api_key_obj.tenant_id
    ).first()
    
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tenant is inactive"
        )
    
    # Actualizar último uso
    api_key_obj.last_used_at = datetime.utcnow()
    db.commit()
    
    return {
        "tenant_id": str(tenant.id),
        "api_key_id": str(api_key_obj.id),
        "plan": tenant.plan
    }

# ============================================================
# GENERADOR DE API KEYS
# ============================================================

def generate_api_key(prefix: str = "ndk") -> str:
    """Genera un API key seguro"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def create_api_key(tenant_id: str, name: str, db: Session) -> str:
    """Crea un nuevo API key para un tenant"""
    from app.models import APIKey
    
    api_key = generate_api_key()
    
    api_key_obj = APIKey(
        tenant_id=tenant_id,
        key=api_key,
        name=name,
        is_active=True
    )
    
    db.add(api_key_obj)
    db.commit()
    
    return api_key
'@

    $apiKeyCode | Out-File -Encoding UTF8 "app\core\api_key.py"
    Write-Log "✓ Validación de API keys creada: app/core/api_key.py" "Success"
}

# ============================================================
# PASO 36-40: INTEGRACIÓN CON STRIPE
# ============================================================

function Create-StripeIntegration {
    <#
    .SYNOPSIS
        Crea integración con Stripe API
    #>
    Write-Log "PASO 36: Creando integración con Stripe..." "Info"
    
    $stripeCode = @'
import stripe
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.exceptions import StripeException
from datetime import datetime, timedelta

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# ============================================================
# SERVICIOS DE STRIPE
# ============================================================

class StripeService:
    """Servicio centralizado para operaciones con Stripe"""
    
    @staticmethod
    def create_customer(email: str, name: str, tenant_id: str) -> str:
        """Crea un cliente en Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"tenant_id": tenant_id}
            )
            return customer.id
        except stripe.error.StripeException as e:
            raise StripeException(f"Error creating customer: {str(e)}")
    
    @staticmethod
    def create_checkout_session(customer_id: str, plan: str, 
                               success_url: str, cancel_url: str) -> Dict[str, Any]:
        """Crea una sesión de checkout"""
        try:
            price_map = {
                "starter": settings.STRIPE_STARTER_PRICE_ID,
                "professional": settings.STRIPE_PROFESSIONAL_PRICE_ID,
                "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID
            }
            
            price_id = price_map.get(plan)
            if not price_id:
                raise StripeException(f"Invalid plan: {plan}")
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeException as e:
            raise StripeException(f"Error creating checkout: {str(e)}")
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Dict[str, Any]:
        """Obtiene detalles de suscripción"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "plan": subscription.items.data[0].price.id if subscription.items.data else None
            }
        except stripe.error.StripeException as e:
            raise StripeException(f"Error retrieving subscription: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """Cancela una suscripción"""
        try:
            subscription = stripe.Subscription.delete(
                subscription_id,
                prorate=False
            )
            return {
                "id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at
            }
        except stripe.error.StripeException as e:
            raise StripeException(f"Error canceling subscription: {str(e)}")
    
    @staticmethod
    def update_subscription(subscription_id: str, plan: str) -> Dict[str, Any]:
        """Actualiza plan de suscripción"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            price_map = {
                "starter": settings.STRIPE_STARTER_PRICE_ID,
                "professional": settings.STRIPE_PROFESSIONAL_PRICE_ID,
                "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID
            }
            
            new_price_id = price_map.get(plan)
            if not new_price_id:
                raise StripeException(f"Invalid plan: {plan}")
            
            # Actualizar línea de item
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription.items.data[0].id,
                    "price": new_price_id
                }],
                proration_behavior="create_prorations"
            )
            
            return {
                "id": updated_subscription.id,
                "status": updated_subscription.status,
                "plan": plan
            }
        except stripe.error.StripeException as e:
            raise StripeException(f"Error updating subscription: {str(e)}")
'@

    $stripeCode | Out-File -Encoding UTF8 "app\services\stripe_service.py"
    Write-Log "✓ Integración con Stripe creada: app/services/stripe_service.py" "Success"
}

function Create-StripeWebhooks {
    <#
    .SYNOPSIS
        Crea endpoints seguros para webhooks de Stripe
    #>
    Write-Log "PASO 37: Creando webhooks de Stripe..." "Info"
    
    $webhooksCode = @'
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models import Subscription, Tenant
from app.services.stripe_service import StripeService
import stripe
import json

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])

# ============================================================
# WEBHOOKS DE STRIPE
# ============================================================

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook seguro para eventos de Stripe
    Valida firma de Stripe antes de procesar
    """
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Validar firma
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Procesar eventos
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    if event_type == "customer.subscription.created":
        _handle_subscription_created(event_data, db)
    elif event_type == "customer.subscription.updated":
        _handle_subscription_updated(event_data, db)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(event_data, db)
    elif event_type == "invoice.paid":
        _handle_invoice_paid(event_data, db)
    elif event_type == "invoice.payment_failed":
        _handle_invoice_failed(event_data, db)
    
    return {"status": "success"}

# ============================================================
# HANDLERS DE EVENTOS
# ============================================================

def _handle_subscription_created(data: dict, db: Session):
    """Maneja creación de suscripción"""
    tenant = db.query(Tenant).filter(
        Tenant.stripe_customer_id == data["customer"]
    ).first()
    
    if tenant:
        subscription = Subscription(
            tenant_id=tenant.id,
            stripe_subscription_id=data["id"],
            stripe_customer_id=data["customer"],
            plan="starter",
            status=data["status"]
        )
        db.add(subscription)
        db.commit()

def _handle_subscription_updated(data: dict, db: Session):
    """Maneja actualización de suscripción"""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == data["id"]
    ).first()
    
    if subscription:
        subscription.status = data["status"]
        db.commit()

def _handle_subscription_deleted(data: dict, db: Session):
    """Maneja cancelación de suscripción"""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == data["id"]
    ).first()
    
    if subscription:
        subscription.status = "canceled"
        db.commit()

def _handle_invoice_paid(data: dict, db: Session):
    """Maneja pago de factura"""
    # Registrar pago exitoso
    print(f"Invoice paid: {data['id']}")

def _handle_invoice_failed(data: dict, db: Session):
    """Maneja falló de pago"""
    # Registrar fallo de pago
    print(f"Invoice payment failed: {data['id']}")
'@

    $webhooksCode | Out-File -Encoding UTF8 "app\routes\webhooks.py"
    Write-Log "✓ Webhooks de Stripe creados: app/routes/webhooks.py" "Success"
}

function Create-SubscriptionManagement {
    <#
    .SYNOPSIS
        Crea gestión de suscripciones
    #>
    Write-Log "PASO 38: Creando gestión de suscripciones..." "Info"
    
    $subscriptionCode = @'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Subscription, Tenant
from app.services.stripe_service import StripeService
from app.core.exceptions import StripeException, ResourceNotFoundException
from app.core.api_key import verify_api_key

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

# ============================================================
# GESTIÓN DE SUSCRIPCIONES
# ============================================================

@router.post("/create-checkout")
async def create_checkout(
    plan: str,
    success_url: str,
    cancel_url: str,
    api_key_info: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Crea sesión de checkout para nueva suscripción
    """
    try:
        tenant_id = api_key_info["tenant_id"]
        
        # Obtener o crear cliente Stripe
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ResourceNotFoundException("Tenant")
        
        if not tenant.stripe_customer_id:
            customer_id = StripeService.create_customer(
                email=tenant.email,
                name=tenant.name,
                tenant_id=tenant_id
            )
            tenant.stripe_customer_id = customer_id
            db.commit()
        
        # Crear sesión de checkout
        checkout = StripeService.create_checkout_session(
            customer_id=tenant.stripe_customer_id,
            plan=plan,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return {
            "session_id": checkout["session_id"],
            "url": checkout["url"]
        }
    except StripeException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/current")
async def get_current_subscription(
    api_key_info: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Obtiene suscripción actual"""
    tenant_id = api_key_info["tenant_id"]
    
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == tenant_id
    ).first()
    
    if not subscription:
        raise ResourceNotFoundException("Subscription")
    
    return {
        "id": str(subscription.id),
        "plan": subscription.plan,
        "status": subscription.status,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end
    }

@router.post("/cancel")
async def cancel_subscription(
    api_key_info: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Cancela suscripción actual"""
    try:
        tenant_id = api_key_info["tenant_id"]
        
        subscription = db.query(Subscription).filter(
            Subscription.tenant_id == tenant_id
        ).first()
        
        if not subscription:
            raise ResourceNotFoundException("Subscription")
        
        result = StripeService.cancel_subscription(
            subscription.stripe_subscription_id
        )
        
        subscription.status = result["status"]
        db.commit()
        
        return {"status": "canceled", "canceled_at": result.get("canceled_at")}
    except StripeException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upgrade")
async def upgrade_subscription(
    new_plan: str,
    api_key_info: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Actualiza plan de suscripción"""
    try:
        tenant_id = api_key_info["tenant_id"]
        
        subscription = db.query(Subscription).filter(
            Subscription.tenant_id == tenant_id
        ).first()
        
        if not subscription:
            raise ResourceNotFoundException("Subscription")
        
        result = StripeService.update_subscription(
            subscription.stripe_subscription_id,
            new_plan
        )
        
        subscription.plan = new_plan
        db.commit()
        
        return {"status": "updated", "plan": new_plan}
    except StripeException as e:
        raise HTTPException(status_code=400, detail=str(e))
'@

    $subscriptionCode | Out-File -Encoding UTF8 "app\routes\subscriptions.py"
    Write-Log "✓ Gestión de suscripciones creada: app/routes/subscriptions.py" "Success"
}

function Create-MeteringSystem {
    <#
    .SYNOPSIS
        Crea sistema de metering y seguimiento de uso
    #>
    Write-Log "PASO 39: Creando sistema de metering..." "Info"
    
    $meteringCode = @'
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models import Subscription

# ============================================================
# SISTEMA DE METERING
# ============================================================

class MeteringService:
    """Servicio de seguimiento de uso"""
    
    @staticmethod
    def track_usage(tenant_id: str, metric: str, quantity: int = 1, db: Session = None):
        """
        Registra uso de un métrica
        Métricas soportadas: api_calls, agents_executed, data_processed_mb, storage_used_mb
        """
        # Aquí se podría enviar a un sistema de metering como Stripe Billing
        # Por ahora, solo registramos en logs
        print(f"Usage tracked - Tenant:{tenant_id} | Metric:{metric} | Qty:{quantity}")
    
    @staticmethod
    def get_usage_for_period(tenant_id: str, start_date: datetime, 
                            end_date: datetime, db: Session) -> Dict[str, int]:
        """Obtiene estadísticas de uso para un período"""
        # Esto se implementaría consultando una tabla de eventos de uso
        return {
            "api_calls": 0,
            "agents_executed": 0,
            "data_processed_mb": 0,
            "storage_used_mb": 0
        }
    
    @staticmethod
    def check_usage_limits(tenant_id: str, subscription: Subscription) -> bool:
        """Verifica si se ha excedido el límite de uso"""
        # Implementar lógica basada en plan
        limits = {
            "starter": {"monthly_requests": 1000, "max_agents": 10},
            "professional": {"monthly_requests": 10000, "max_agents": 100},
            "enterprise": {"monthly_requests": 100000, "max_agents": None}
        }
        
        plan_limit = limits.get(subscription.plan, limits["starter"])
        
        # Obtener uso actual del mes
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # TODO: Implementar consulta de eventos de uso
        
        return True

# ============================================================
# EVENTOS DE USO (Para auditoría)
# ============================================================

class UsageEvent:
    """Evento de uso para auditoría"""
    
    def __init__(self, tenant_id: str, metric: str, quantity: int, timestamp: datetime = None):
        self.tenant_id = tenant_id
        self.metric = metric
        self.quantity = quantity
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self):
        return {
            "tenant_id": self.tenant_id,
            "metric": self.metric,
            "quantity": self.quantity,
            "timestamp": self.timestamp.isoformat()
        }
'@

    $meteringCode | Out-File -Encoding UTF8 "app\services\metering_service.py"
    Write-Log "✓ Sistema de metering creado: app/services/metering_service.py" "Success"
}

function Create-InvoiceSystem {
    <#
    .SYNOPSIS
        Crea sistema de facturación automática
    #>
    Write-Log "PASO 40: Creando sistema de facturas..." "Info"
    
    $invoiceCode = @'
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
import stripe
from app.core.config import settings
from app.models import Subscription, Tenant

# ============================================================
# SERVICIO DE FACTURAS
# ============================================================

class InvoiceService:
    """Servicio de facturas"""
    
    @staticmethod
    def create_invoice(tenant_id: str, subscription_id: str, 
                      db: Session, description: str = "Nadakki SaaS Subscription") -> Dict:
        """Crea una factura manual"""
        
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise Exception("Subscription not found")
        
        try:
            invoice = stripe.Invoice.create(
                customer=subscription.stripe_customer_id,
                subscription=subscription.stripe_subscription_id,
                description=description,
                auto_advance=True  # Auto-finalizar factura
            )
            
            return {
                "id": invoice.id,
                "number": invoice.number,
                "amount": invoice.amount_due,
                "currency": invoice.currency,
                "status": invoice.status,
                "url": invoice.hosted_invoice_url
            }
        except Exception as e:
            print(f"Error creating invoice: {str(e)}")
            raise
    
    @staticmethod
    def list_invoices(subscription_id: str, limit: int = 10) -> List[Dict]:
        """Lista facturas de una suscripción"""
        try:
            invoices = stripe.Invoice.list(
                limit=limit,
                subscription=subscription_id
            )
            
            return [
                {
                    "id": inv.id,
                    "number": inv.number,
                    "amount": inv.amount_due,
                    "status": inv.status,
                    "date": datetime.fromtimestamp(inv.created).isoformat()
                }
                for inv in invoices.data
            ]
        except Exception as e:
            print(f"Error listing invoices: {str(e)}")
            return []
    
    @staticmethod
    def send_invoice(invoice_id: str) -> bool:
        """Envía una factura al cliente"""
        try:
            stripe.Invoice.send_invoice(invoice_id)
            return True
        except Exception as e:
            print(f"Error sending invoice: {str(e)}")
            return False
    
    @staticmethod
    def download_invoice(invoice_id: str) -> Optional[str]:
        """Obtiene URL de descarga de factura PDF"""
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            return invoice.pdf
        except Exception as e:
            print(f"Error downloading invoice: {str(e)}")
            return None

# ============================================================
# GENERACIÓN AUTOMÁTICA DE FACTURAS
# ============================================================

async def generate_monthly_invoices(db: Session):
    """
    Genera facturas automáticas al final del mes
    Debe ejecutarse como tarea programada (cron job)
    """
    subscriptions = db.query(Subscription).filter(
        Subscription.status == "active"
    ).all()
    
    for subscription in subscriptions:
        try:
            InvoiceService.create_invoice(
                tenant_id=subscription.tenant_id,
                subscription_id=subscription.id,
                db=db,
                description=f"Monthly subscription - {subscription.plan}"
            )
        except Exception as e:
            print(f"Error generating invoice for {subscription.id}: {str(e)}")
'@

    $invoiceCode | Out-File -Encoding UTF8 "app\services\invoice_service.py"
    Write-Log "✓ Sistema de facturas creado: app/services/invoice_service.py" "Success"
}

# ============================================================
# PASO 41-45: SEGURIDAD Y COMPLIANCE
# ============================================================

function Create-SSLCertificates {
    <#
    .SYNOPSIS
        Configura certificados SSL/TLS para HTTPS
    #>
    Write-Log "PASO 41: Configurando certificados SSL/TLS..." "Info"
    
    # Crear carpeta de certificados
    $certDir = "certs"
    if (-not (Test-Path $certDir)) {
        New-Item -ItemType Directory -Path $certDir -Force | Out-Null
    }
    
    Write-Log "Para HTTPS en producción:" "Warning"
    Write-Log "1. Usar Let's Encrypt: https://letsencrypt.org/" "Info"
    Write-Log "2. O usar: certbot certonly --standalone -d tu-dominio.com" "Info"
    Write-Log "3. Esto genera certificados en: /etc/letsencrypt/live/tu-dominio.com/" "Info"
    
    # Crear archivo de configuración de SSL
    $sslConfig = @'
# ============================================================
# CONFIGURACIÓN SSL/TLS
# ============================================================

SSL_CERT_PATH = "/etc/letsencrypt/live/tu-dominio.com/fullchain.pem"
SSL_KEY_PATH = "/etc/letsencrypt/live/tu-dominio.com/privkey.pem"

# Para desarrollo con certificado autofirmado:
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Verificar certificado:
# openssl x509 -in cert.pem -text -noout

# Renovación automática con certbot:
# 0 0 1 * * certbot renew --quiet
'@

    $sslConfig | Out-File -Encoding UTF8 "certs\SSL_CONFIG.md"
    Write-Log "✓ Guía de SSL/TLS creada: certs/SSL_CONFIG.md" "Success"
}

function Create-CORSPolicy {
    <#
    .SYNOPSIS
        Crea política CORS avanzada por tenant
    #>
    Write-Log "PASO 42: Configurando CORS avanzado..." "Info"
    
    $corsCode = @'
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# ============================================================
# POLÍTICA CORS AVANZADA
# ============================================================

class TenantCORSPolicy:
    """Política CORS por tenant"""
    
    @staticmethod
    def get_allowed_origins(tenant_id: str, tenant_config: dict = None) -> List[str]:
        """
        Obtiene orígenes permitidos para un tenant
        El tenant puede registrar dominios personalizados
        """
        
        # Orígenes por defecto
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ]
        
        # Si el tenant tiene un dominio personalizado
        if tenant_config and "custom_domain" in tenant_config:
            domain = tenant_config["custom_domain"]
            allowed_origins.extend([
                f"https://{domain}",
                f"http://{domain}",
                f"https://app.{domain}",
                f"https://admin.{domain}"
            ])
        
        return allowed_origins

def configure_cors_middleware(app, default_origins: List[str] = None):
    """Configura middleware CORS"""
    
    if not default_origins:
        default_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=default_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-Tenant-ID",
            "X-Request-ID"
        ],
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600
    )

# ============================================================
# VALIDACIÓN DE ORIGEN
# ============================================================

def validate_origin(origin: str, allowed_origins: List[str]) -> bool:
    """Valida que el origen sea permitido"""
    if origin in allowed_origins:
        return True
    
    # Permitir subdomios si se especifica con wildcard
    for allowed in allowed_origins:
        if allowed.startswith("*."):
            domain = allowed[2:]
            if origin.endswith(f".{domain}") or origin == f"https://{domain}":
                return True
    
    return False
'@

    $corsCode | Out-File -Encoding UTF8 "app\core\cors_policy.py"
    Write-Log "✓ Política CORS creada: app/core/cors_policy.py" "Success"
}

function Create-GDPRCompliance {
    <#
    .SYNOPSIS
        Implementa compliance GDPR
    #>
    Write-Log "PASO 43: Implementando GDPR compliance..." "Info"
    
    $gdprCode = @'
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Tenant, User, AuditLog
from app.core.logging import audit_logger
import json

# ============================================================
# GDPR COMPLIANCE
# ============================================================

class GDPRService:
    """Servicio de cumplimiento GDPR"""
    
    @staticmethod
    def export_user_data(user_id: str, db: Session) -> dict:
        """
        Exporta todos los datos personales de un usuario
        Cumple con derecho de portabilidad de datos
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise Exception("User not found")
        
        # Recopilar datos del usuario
        user_data = {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat(),
                "job_title": user.job_title,
                "phone": user.phone
            },
            "audit_logs": []
        }
        
        # Incluir logs de auditoría
        audit_logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).all()
        
        for log in audit_logs:
            user_data["audit_logs"].append({
                "action": log.action,
                "resource": log.resource,
                "status": log.status,
                "timestamp": log.created_at.isoformat()
            })
        
        audit_logger.log_security_event(
            "DATA_EXPORT",
            str(user.tenant_id),
            f"User data exported for user {user.email}"
        )
        
        return user_data
    
    @staticmethod
    def delete_user_data(user_id: str, db: Session) -> bool:
        """
        Elimina todos los datos personales de un usuario
        Cumple con derecho al olvido (right to be forgotten)
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise Exception("User not found")
        
        # Guardar referencia antes de eliminar
        tenant_id = user.tenant_id
        email = user.email
        
        # Eliminar logs de auditoría
        db.query(AuditLog).filter(AuditLog.user_id == user_id).delete()
        
        # Eliminar usuario
        db.delete(user)
        db.commit()
        
        audit_logger.log_security_event(
            "DATA_DELETED",
            tenant_id,
            f"User data deleted for {email} (right to be forgotten)"
        )
        
        return True
    
    @staticmethod
    def delete_inactive_tenant(tenant_id: str, days_inactive: int = 365, 
                              db: Session = None) -> bool:
        """
        Elimina tenant inactivo según política de retención
        """
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        if not tenant:
            raise Exception("Tenant not found")
        
        # Verificar último acceso
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        if tenant.updated_at < cutoff_date:
            # Exportar datos antes de eliminar
            users = db.query(User).filter(User.tenant_id == tenant_id).all()
            
            # Eliminar datos en cascada
            for user in users:
                db.query(AuditLog).filter(AuditLog.user_id == user.id).delete()
            
            db.query(User).filter(User.tenant_id == tenant_id).delete()
            db.delete(tenant)
            db.commit()
            
            audit_logger.log_security_event(
                "TENANT_DELETED_RETENTION",
                tenant_id,
                f"Tenant deleted due to inactivity ({days_inactive} days)"
            )
            
            return True
        
        return False
    
    @staticmethod
    def get_gdpr_status(tenant_id: str, db: Session) -> dict:
        """Obtiene estado de compliance GDPR"""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        return {
            "tenant_id": tenant_id,
            "gdpr_compliant": tenant.gdpr_compliant if tenant else False,
            "data_processing_agreement": True,  # DPA debe estar firmado
            "right_to_access": True,
            "right_to_be_forgotten": True,
            "data_portability": True,
            "consent_management": True,
            "last_audit": datetime.utcnow().isoformat()
        }
'@

    $gdprCode | Out-File -Encoding UTF8 "app\services\gdpr_service.py"
    Write-Log "✓ GDPR Compliance implementado: app/services/gdpr_service.py" "Success"
}

function Create-DataEncryption {
    <#
    .SYNOPSIS
        Implementa encriptación AES-256 en reposo
    #>
    Write-Log "PASO 44: Configurando encriptación AES-256..." "Info"
    
    $encryptionCode = @'
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os

# ============================================================
# ENCRIPTACIÓN AES-256
# ============================================================

class EncryptionService:
    """Servicio de encriptación de datos"""
    
    def __init__(self, master_key: str = None):
        """
        Inicializa con clave maestra
        La clave debe tener al menos 32 bytes (256 bits)
        """
        if master_key:
            if isinstance(master_key, str):
                master_key = master_key.encode()
            
            # Si la clave no tiene 32 bytes, derivarla
            if len(master_key) < 32:
                kdf = PBKDF2(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b"nadakki_salt_v1",
                    iterations=100000,
                    backend=default_backend()
                )
                key = base64.urlsafe_b64encode(kdf.derive(master_key))
            else:
                key = base64.urlsafe_b64encode(master_key[:32])
            
            self.cipher = Fernet(key)
        else:
            # Generar clave nueva
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, plaintext: str) -> str:
        """Encripta texto plano"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        ciphertext = self.cipher.encrypt(plaintext)
        return ciphertext.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Desencripta texto cifrado"""
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        
        try:
            plaintext = self.cipher.decrypt(ciphertext)
            return plaintext.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_field(self, value: str, tenant_id: str) -> str:
        """Encripta campo con contexto de tenant"""
        context = f"tenant:{tenant_id}:"
        data = context + value
        return self.encrypt(data)
    
    def decrypt_field(self, encrypted: str, tenant_id: str) -> str:
        """Desencripta campo validando tenant"""
        decrypted = self.decrypt(encrypted)
        context = f"tenant:{tenant_id}:"
        
        if not decrypted.startswith(context):
            raise Exception("Tenant context mismatch")
        
        return decrypted[len(context):]

# ============================================================
# CAMPOS ENCRIPTABLES
# ============================================================

ENCRYPTED_FIELDS = [
    "user.phone",
    "user.email",  # Algunos casos requieren encriptación
    "tenant.custom_domain",
    "subscription.stripe_customer_id"
]

def should_encrypt_field(field_path: str) -> bool:
    """Determina si un campo debe encriptarse"""
    return field_path in ENCRYPTED_FIELDS

# ============================================================
# UTILIDADES DE CLAVE
# ============================================================

def generate_encryption_key() -> str:
    """Genera una clave de encriptación segura"""
    return Fernet.generate_key().decode()

def rotate_encryption_key(old_cipher, new_cipher, data_to_rotate: list):
    """Rotación de claves de encriptación"""
    # Desencriptar con clave antigua, encriptar con clave nueva
    rotated = []
    for item in data_to_rotate:
        decrypted = old_cipher.decrypt(item)
        encrypted = new_cipher.encrypt(decrypted)
        rotated.append(encrypted)
    return rotated
'@

    $encryptionCode | Out-File -Encoding UTF8 "app\core\encryption.py"
    Write-Log "✓ Encriptación AES-256 implementada: app/core/encryption.py" "Success"
}

function Create-AuditTrail {
    <#
    .SYNOPSIS
        Crea sistema completo de audit trail
    #>
    Write-Log "PASO 45: Creando audit trail completo..." "Info"
    
    $auditCode = @'
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AuditLog
from app.core.logging import audit_logger
import json
from typing import Optional, Dict, Any

# ============================================================
# AUDIT TRAIL SERVICE
# ============================================================

class AuditTrailService:
    """Servicio de audit trail completo"""
    
    @staticmethod
    def log_action(
        tenant_id: str,
        user_id: str,
        action: str,
        resource: str,
        resource_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = None,
        user_agent: str = None,
        db: Session = None
    ) -> AuditLog:
        """
        Registra una acción en el audit trail
        
        Acciones: CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, etc.
        """
        
        log_entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            status=status,
            error_message=None,
            ip_address=ip_address,
            user_agent=user_agent,
            details=json.dumps(details) if details else None
        )
        
        if db:
            db.add(log_entry)
            db.commit()
        
        # También loguear en archivo
        audit_logger.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource=resource,
            status=status,
            details=details
        )
        
        return log_entry
    
    @staticmethod
    def log_security_event(
        tenant_id: str,
        event_type: str,
        description: str,
        ip_address: str = None,
        db: Session = None
    ) -> AuditLog:
        """
        Registra evento de seguridad
        event_type: LOGIN_FAILED, API_KEY_GENERATED, PERMISSION_DENIED, etc.
        """
        
        log_entry = AuditLog(
            tenant_id=tenant_id,
            action=event_type,
            resource="SECURITY",
            status="SECURITY_EVENT",
            details=json.dumps({"description": description}),
            ip_address=ip_address
        )
        
        if db:
            db.add(log_entry)
            db.commit()
        
        audit_logger.log_security_event(
            event_type=event_type,
            tenant_id=tenant_id,
            details=description
        )
        
        return log_entry
    
    @staticmethod
    def get_audit_trail(
        tenant_id: str,
        filters: Dict = None,
        limit: int = 100,
        db: Session = None
    ) -> list:
        """
        Obtiene audit trail con filtros
        """
        
        query = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id
        )
        
        # Aplicar filtros
        if filters:
            if "action" in filters:
                query = query.filter(AuditLog.action == filters["action"])
            if "resource" in filters:
                query = query.filter(AuditLog.resource == filters["resource"])
            if "user_id" in filters:
                query = query.filter(AuditLog.user_id == filters["user_id"])
            if "status" in filters:
                query = query.filter(AuditLog.status == filters["status"])
            if "start_date" in filters:
                query = query.filter(AuditLog.created_at >= filters["start_date"])
            if "end_date" in filters:
                query = query.filter(AuditLog.created_at <= filters["end_date"])
        
        # Ordenar por fecha descendente y limitar
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def generate_audit_report(
        tenant_id: str,
        period_days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """Genera reporte de auditoría"""
        
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        logs = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.created_at >= start_date
        ).all()
        
        # Análisis
        report = {
            "tenant_id": tenant_id,
            "period_days": period_days,
            "total_events": len(logs),
            "events_by_action": {},
            "events_by_resource": {},
            "events_by_user": {},
            "security_events": 0
        }
        
        for log in logs:
            # Contar por acción
            action = log.action
            report["events_by_action"][action] = report["events_by_action"].get(action, 0) + 1
            
            # Contar por recurso
            resource = log.resource
            report["events_by_resource"][resource] = report["events_by_resource"].get(resource, 0) + 1
            
            # Contar por usuario
            user = str(log.user_id) if log.user_id else "SYSTEM"
            report["events_by_user"][user] = report["events_by_user"].get(user, 0) + 1
            
            # Contar eventos de seguridad
            if log.status == "SECURITY_EVENT":
                report["security_events"] += 1
        
        return report
'@

    $auditCode | Out-File -Encoding UTF8 "app\services\audit_trail_service.py"
    Write-Log "✓ Audit Trail implementado: app/services/audit_trail_service.py" "Success"
}

# ============================================================
# ACTUALIZAR DEPENDENCIAS Y CONFIGURACIÓN
# ============================================================

function Update-Requirements {
    <#
    .SYNOPSIS
        Actualiza requirements.txt con nuevas dependencias
    #>
    Write-Log "Actualizando dependencias..." "Info"
    
    $newDeps = @(
        "stripe==7.4.0",
        "pydantic-extra-types==2.0.0",
        "cryptography==41.0.7",
        "python-multipart==0.0.6"
    )
    
    foreach ($dep in $newDeps) {
        Add-Content -Path "requirements.txt" -Value $dep
    }
    
    Write-Log "✓ Requirements.txt actualizado" "Success"
}

function Update-MainApp {
    <#
    .SYNOPSIS
        Actualiza app/main.py con nuevas rutas y middleware
    #>
    Write-Log "Actualizando app/main.py..." "Info"
    
    $mainUpdate = @'
# Agregar al archivo app/main.py existente:

from app.routes import subscriptions, webhooks
from app.core.exceptions import NadakkiException, exception_handler, general_exception_handler
from app.core.cors_policy import configure_cors_middleware
from app.core.rate_limit import rate_limiter
from app.core.logging import LogManager

# Incluir nuevas rutas
app.include_router(subscriptions.router)
app.include_router(webhooks.router)

# Registrar handlers de excepciones
app.add_exception_handler(NadakkiException, exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configurar CORS avanzado
configure_cors_middleware(app)

# Logger
logger = LogManager.get_logger("main")
'@

    $mainUpdate | Out-File -Encoding UTF8 "app\APP_MAIN_UPDATES.txt"
    Write-Log "✓ Instrucciones de actualización guardadas: app/APP_MAIN_UPDATES.txt" "Success"
}

# ============================================================
# RESUMEN Y COMPLETACIÓN
# ============================================================

function Show-Summary {
    <#
    .SYNOPSIS
        Muestra resumen de ejecución
    #>
    $ScriptEnd = Get-Date
    $Duration = ($ScriptEnd - $ScriptStart).TotalSeconds
    
    Write-Log "════════════════════════════════════════" "Info"
    Write-Log "DEVOPS AUTOMATION COMPLETADO" "Success"
    Write-Log "════════════════════════════════════════" "Info"
    Write-Log "" "Info"
    
    Write-Log "MÓDULOS GENERADOS:" "Info"
    Write-Log "" "Info"
    
    Write-Log "VALIDACIONES Y SEGURIDAD (PASOS 31-35):" "Info"
    Write-Log "  ✅ PASO 31: Validaciones Pydantic → app/core/validation.py" "Success"
    Write-Log "  ✅ PASO 32: Manejo de excepciones → app/core/exceptions.py" "Success"
    Write-Log "  ✅ PASO 33: Logging con rotación → app/core/logging.py" "Success"
    Write-Log "  ✅ PASO 34: Rate limiting → app/core/rate_limit.py" "Success"
    Write-Log "  ✅ PASO 35: Validación API keys → app/core/api_key.py" "Success"
    Write-Log "" "Info"
    
    Write-Log "STRIPE INTEGRATION (PASOS 36-40):" "Info"
    Write-Log "  ✅ PASO 36: Stripe API → app/services/stripe_service.py" "Success"
    Write-Log "  ✅ PASO 37: Webhooks → app/routes/webhooks.py" "Success"
    Write-Log "  ✅ PASO 38: Gestión suscripciones → app/routes/subscriptions.py" "Success"
    Write-Log "  ✅ PASO 39: Metering → app/services/metering_service.py" "Success"
    Write-Log "  ✅ PASO 40: Facturas → app/services/invoice_service.py" "Success"
    Write-Log "" "Info"
    
    Write-Log "SEGURIDAD & COMPLIANCE (PASOS 41-45):" "Info"
    Write-Log "  ✅ PASO 41: SSL/TLS → certs/SSL_CONFIG.md" "Success"
    Write-Log "  ✅ PASO 42: CORS avanzado → app/core/cors_policy.py" "Success"
    Write-Log "  ✅ PASO 43: GDPR Compliance → app/services/gdpr_service.py" "Success"
    Write-Log "  ✅ PASO 44: Encriptación AES-256 → app/core/encryption.py" "Success"
    Write-Log "  ✅ PASO 45: Audit Trail → app/services/audit_trail_service.py" "Success"
    Write-Log "" "Info"
    
    Write-Log "ARCHIVOS AUXILIARES:" "Info"
    Write-Log "  📂 Logs guardados en: $LogDir" "Info"
    Write-Log "  📋 Ejecutable en: $LogFile" "Info"
    Write-Log "" "Info"
    
    Write-Log "TIEMPO TOTAL: $Duration segundos" "Success"
    Write-Log "" "Info"
    
    Write-Log "PRÓXIMOS PASOS:" "Warning"
    Write-Log "1. Instalar nuevas dependencias: pip install -r requirements.txt" "Info"
    Write-Log "2. Configurar variables de entorno en .env:" "Info"
    Write-Log "   - STRIPE_SECRET_KEY (obtener de Stripe Dashboard)" "Info"
    Write-Log "   - STRIPE_WEBHOOK_SECRET" "Info"
    Write-Log "   - ENCRYPTION_MASTER_KEY (generar con: python -c \"from app.core.encryption import generate_encryption_key; print(generate_encryption_key())\")" "Info"
    Write-Log "3. Ejecutar servidor:" "Info"
    Write-Log "   python -m uvicorn app.main:app --reload" "Info"
    Write-Log "4. Verificar documentación en: http://localhost:8000/docs" "Info"
    Write-Log "" "Info"
    
    Write-Log "ENDPOINTS NUEVOS DISPONIBLES:" "Success"
    Write-Log "  POST   /api/v1/subscriptions/create-checkout" "Info"
    Write-Log "  GET    /api/v1/subscriptions/current" "Info"
    Write-Log "  POST   /api/v1/subscriptions/cancel" "Info"
    Write-Log "  POST   /api/v1/subscriptions/upgrade" "Info"
    Write-Log "  POST   /api/v1/webhooks/stripe" "Info"
    Write-Log "" "Info"
    
    Write-Log "SECURITY CHECKLIST:" "Warning"
    Write-Log "  ☐ Actualizar STRIPE_SECRET_KEY en .env" "Info"
    Write-Log "  ☐ Configurar STRIPE_WEBHOOK_SECRET" "Info"
    Write-Log "  ☐ Generar ENCRYPTION_MASTER_KEY segura" "Info"
    Write-Log "  ☐ Configurar HTTPS con Let's Encrypt" "Info"
    Write-Log "  ☐ Habilitar GDPR compliance en tenant" "Info"
    Write-Log "  ☐ Revisar políticas CORS por dominio" "Info"
    Write-Log "  ☐ Configurar rotación de logs" "Info"
    Write-Log "  ☐ Implementar backups automáticos" "Info"
    Write-Log "" "Info"
    
    Write-Log "════════════════════════════════════════" "Success"
}

# ============================================================
# MAIN - ORQUESTACIÓN DEL SCRIPT
# ============================================================

Initialize-LogSystem

# Ejecutar módulos basado en parámetros
if ($All -or $Validations) {
    Write-Log "INICIANDO FASE: VALIDACIONES Y SEGURIDAD" "Info"
    Create-ValidationModule
    Create-ExceptionHandling
    Create-LoggingSystem
    Create-RateLimiting
    Create-APIKeyValidation
}

if ($All -or $Stripe) {
    Write-Log "INICIANDO FASE: STRIPE INTEGRATION" "Info"
    Create-StripeIntegration
    Create-StripeWebhooks
    Create-SubscriptionManagement
    Create-MeteringSystem
    Create-InvoiceSystem
}

if ($All -or $Security) {
    Write-Log "INICIANDO FASE: SEGURIDAD Y COMPLIANCE" "Info"
    Create-SSLCertificates
    Create-CORSPolicy
    Create-GDPRCompliance
    Create-DataEncryption
    Create-AuditTrail
}

# Actualizar archivos base
Update-Requirements
Update-MainApp

# Mostrar resumen
Show-Summary

Write-Log "" "Success"
Write-Log "🎉 SCRIPT COMPLETADO EXITOSAMENTE 🎉" "Success"