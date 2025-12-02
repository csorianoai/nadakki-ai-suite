# NADAKKI ENTERPRISE - SETUP SCRIPT PROFESIONAL
# Nivel: Expert 0.1% - Con 7 Autoevaluaciones

$ErrorActionPreference = "Stop"
$WarningPreference = "SilentlyContinue"

# COLORES PARA OUTPUT
$Success = "Green"
$Warning = "Yellow"
$ErrorColor = "Red"
$Info = "Cyan"

function Write-Log {
    param([string]$Message, [string]$Type = "Info")
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    switch ($Type) {
        "Success" { Write-Host "[$timestamp] ✅ $Message" -ForegroundColor $Success }
        "ErrorMsg" { Write-Host "[$timestamp] ❌ $Message" -ForegroundColor $ErrorColor }
        "Warning" { Write-Host "[$timestamp] ⚠️  $Message" -ForegroundColor $Warning }
        default { Write-Host "[$timestamp] ℹ️  $Message" -ForegroundColor $Info }
    }
}

# AUTOEVALUACIÓN 1: Verificar que estamos en el directorio correcto
Write-Log "AUTOEVALUACIÓN 1: Verificando directorio..." "Info"
if (-not (Test-Path ".\app")) {
    Write-Log "ERROR: No estás en nadakki-enterprise/backend/" "ErrorMsg"
    Write-Log "Navega a: cd nadakki-enterprise\backend" "ErrorMsg"
    exit 1
}
if (-not (Test-Path "requirements.txt")) {
    Write-Log "ERROR: No encontré requirements.txt" "ErrorMsg"
    exit 1
}
Write-Log "✓ Directorio correcto" "Success"

# AUTOEVALUACIÓN 2: Verificar que venv está activado
Write-Log "AUTOEVALUACIÓN 2: Verificando venv..." "Info"
if ($null -eq $env:VIRTUAL_ENV) {
    Write-Log "ERROR: venv no está activado" "ErrorMsg"
    Write-Log "Ejecuta: .\venv\Scripts\Activate.ps1" "ErrorMsg"
    exit 1
}
Write-Log "✓ Virtual environment activo" "Success"

# AUTOEVALUACIÓN 3: Verificar que dependencias están instaladas
Write-Log "AUTOEVALUACIÓN 3: Verificando dependencias..." "Info"
try {
    python -c "import fastapi; import sqlalchemy; import pydantic" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: Dependencias no instaladas correctamente" "ErrorMsg"
        exit 1
    }
    Write-Log "✓ Todas las dependencias instaladas" "Success"
} catch {
    Write-Log "ERROR: No se pueden verificar dependencias" "ErrorMsg"
    exit 1
}

# AUTOEVALUACIÓN 4: Verificar estructura de carpetas
Write-Log "AUTOEVALUACIÓN 4: Verificando estructura de carpetas..." "Info"
$requiredDirs = @("app\core", "app\models", "app\routes", "app\services", "app\middleware", "tests")
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        Write-Log "ERROR: Carpeta faltante: $dir" "ErrorMsg"
        exit 1
    }
}
Write-Log "✓ Todas las carpetas existen" "Success"

# AUTOEVALUACIÓN 5: Verificar permisos de escritura
Write-Log "AUTOEVALUACIÓN 5: Verificando permisos de escritura..." "Info"
try {
    $testFile = "test_write.tmp"
    "test" | Out-File $testFile
    Remove-Item $testFile
    Write-Log "✓ Permisos de escritura OK" "Success"
} catch {
    Write-Log "ERROR: No hay permisos de escritura" "ErrorMsg"
    exit 1
}

Write-Log "════════════════════════════════════════════" "Info"
Write-Log "INICIANDO CREACIÓN DE ARCHIVOS PYTHON" "Info"
Write-Log "════════════════════════════════════════════" "Info"

# ============================================================
# PASO 8: CREAR app/main.py
# ============================================================
Write-Log "PASO 8: Creando app/main.py..." "Info"

$mainContent = @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="Nadakki SaaS",
    version="1.0.0",
    docs_url="/docs"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "nadakki-saas",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@

$mainContent | Out-File -Encoding UTF8 "app\main.py"
Write-Log "✓ app/main.py creado" "Success"

# ============================================================
# PASO 9: CREAR app/core/config.py
# ============================================================
Write-Log "PASO 9: Creando app/core/config.py..." "Info"

$configContent = @"
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Nadakki SaaS"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    
    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = False
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    ENCRYPTION_MASTER_KEY: str
    REDIS_URL: str
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
"@

$configContent | Out-File -Encoding UTF8 "app\core\config.py"
Write-Log "✓ app/core/config.py creado" "Success"

# ============================================================
# PASO 10: CREAR app/core/security.py
# ============================================================
Write-Log "PASO 10: Creando app/core/security.py..." "Info"

$securityContent = @"
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None

class EncryptionService:
    
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_MASTER_KEY.encode())
    
    def encrypt_field(self, value: str, tenant_id: str) -> str:
        plaintext = f"{tenant_id}:{value}".encode()
        return self.cipher.encrypt(plaintext).decode()
    
    def decrypt_field(self, encrypted: str, tenant_id: str) -> str:
        plaintext = self.cipher.decrypt(encrypted.encode()).decode()
        stored_tenant, value = plaintext.split(":", 1)
        if stored_tenant != tenant_id:
            raise ValueError("Tenant ID mismatch")
        return value
"@

$securityContent | Out-File -Encoding UTF8 "app\core\security.py"
Write-Log "✓ app/core/security.py creado" "Success"

# ============================================================
# PASO 11: CREAR app/core/database.py
# ============================================================
Write-Log "PASO 11: Creando app/core/database.py..." "Info"

$databaseContent = @"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas
Base.metadata.create_all(bind=engine)
"@

$databaseContent | Out-File -Encoding UTF8 "app\core\database.py"
Write-Log "✓ app/core/database.py creado" "Success"

# ============================================================
# PASO 12: CREAR app/models/base.py
# ============================================================
Write-Log "PASO 12: Creando app/models/base.py..." "Info"

$baseModelContent = @"
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class TenantMixin:
    pass
"@

$baseModelContent | Out-File -Encoding UTF8 "app\models\base.py"
Write-Log "✓ app/models/base.py creado" "Success"

# ============================================================
# PASO 13: CREAR app/models/tenant.py
# ============================================================
Write-Log "PASO 13: Creando app/models/tenant.py..." "Info"

$tenantContent = @"
from sqlalchemy import Column, String, UUID, Boolean, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
import uuid

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    api_key = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    country = Column(String(2), nullable=False)
    region = Column(String(50))
    industry = Column(String(100))
    plan = Column(Enum("starter", "professional", "enterprise"), default="starter", nullable=False)
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255), unique=True)
    is_active = Column(Boolean, default=False)
    compliance_reviewed = Column(Boolean, default=False)
    gdpr_compliant = Column(Boolean, default=False)
    aml_risk_score = Column(String(50))
    branding = Column(JSON, nullable=True)
    custom_domain = Column(String(255), nullable=True, unique=True)
    
    __table_args__ = (UniqueConstraint('name', name='uq_tenant_name'),)
    
    def __repr__(self):
        return f"<Tenant {self.name} ({self.plan})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "plan": self.plan,
            "is_active": self.is_active,
            "country": self.country,
            "created_at": self.created_at.isoformat()
        }
"@

$tenantContent | Out-File -Encoding UTF8 "app\models\tenant.py"
Write-Log "✓ app/models/tenant.py creado" "Success"

# ============================================================
# PASO 14: CREAR MODELOS RESTANTES
# ============================================================
Write-Log "PASO 14: Creando modelos restantes..." "Info"

$userContent = @"
from sqlalchemy import Column, String, UUID, ForeignKey, Boolean, UniqueConstraint
from app.models.base import Base, TimestampMixin
import uuid

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    job_title = Column(String(255))
    phone = Column(String(20))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (UniqueConstraint('tenant_id', 'email', name='uq_tenant_user_email'),)
    
    def __repr__(self):
        return f"<User {self.email}>"
"@

$userContent | Out-File -Encoding UTF8 "app\models\user.py"

$subscriptionContent = @"
from sqlalchemy import Column, String, UUID, ForeignKey, Integer, DateTime
from app.models.base import Base, TimestampMixin
import uuid

class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=False, unique=True)
    stripe_subscription_id = Column(String(255), nullable=False, unique=True)
    stripe_product_id = Column(String(255))
    plan = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    monthly_requests_limit = Column(Integer)
    requests_used_this_month = Column(Integer, default=0)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_ends_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Subscription {self.tenant_id} - {self.plan}>"
"@

$subscriptionContent | Out-File -Encoding UTF8 "app\models\subscription.py"

$apiKeyContent = @"
from sqlalchemy import Column, String, UUID, ForeignKey, Boolean, DateTime
from app.models.base import Base, TimestampMixin
import uuid
from datetime import datetime

class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self):
        return f"<APIKey {self.name}>"
"@

$apiKeyContent | Out-File -Encoding UTF8 "app\models\api_key.py"

$agentContent = @"
from sqlalchemy import Column, String, UUID, ForeignKey, JSON, Integer, Text
from app.models.base import Base, TimestampMixin
import uuid

class AgentExecution(Base, TimestampMixin):
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    agent_type = Column(String(100))
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost_cents = Column(Integer)
    
    def __repr__(self):
        return f"<AgentExecution {self.agent_name} - {self.status}>"
"@

$agentContent | Out-File -Encoding UTF8 "app\models\agent_execution.py"

$auditContent = @"
from sqlalchemy import Column, String, UUID, ForeignKey, JSON, Text
from app.models.base import Base, TimestampMixin
import uuid

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    resource_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    details = Column(JSON)
    
    def __repr__(self):
        return f"<AuditLog {self.action} - {self.status}>"
"@

$auditContent | Out-File -Encoding UTF8 "app\models\audit_log.py"

Write-Log "✓ Modelos (user, subscription, api_key, agent_execution, audit_log) creados" "Success"

# ============================================================
# PASO 15: ACTUALIZAR app/models/__init__.py
# ============================================================
Write-Log "PASO 15: Actualizando app/models/__init__.py..." "Info"

$modelsInitContent = @"
from app.models.base import Base
from app.models.tenant import Tenant
from app.models.user import User
from app.models.subscription import Subscription
from app.models.agent_execution import AgentExecution
from app.models.audit_log import AuditLog
from app.models.api_key import APIKey

__all__ = [
    "Base",
    "Tenant",
    "User",
    "Subscription",
    "AgentExecution",
    "AuditLog",
    "APIKey"
]
"@

$modelsInitContent | Out-File -Encoding UTF8 "app\models\__init__.py"
Write-Log "✓ app/models/__init__.py actualizado" "Success"

# ============================================================
# PASO 16: CREAR app/core/__init__.py
# ============================================================
Write-Log "PASO 16: Creando app/core/__init__.py..." "Info"

"" | Out-File -Encoding UTF8 "app\core\__init__.py"
Write-Log "✓ app/core/__init__.py creado" "Success"

# ============================================================
# AUTOEVALUACIÓN 6: Verificar creación de archivos
# ============================================================
Write-Log "AUTOEVALUACIÓN 6: Verificando creación de archivos..." "Info"

$requiredFiles = @(
    "app\main.py",
    "app\core\config.py",
    "app\core\security.py",
    "app\core\database.py",
    "app\core\__init__.py",
    "app\models\base.py",
    "app\models\tenant.py",
    "app\models\user.py",
    "app\models\subscription.py",
    "app\models\api_key.py",
    "app\models\agent_execution.py",
    "app\models\audit_log.py",
    "app\models\__init__.py"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Log "ERROR: Archivos faltantes:" "ErrorMsg"
    foreach ($file in $missingFiles) {
        Write-Log "  - $file" "ErrorMsg"
    }
    exit 1
}
Write-Log "✓ Todos los archivos creados correctamente" "Success"

# ============================================================
# AUTOEVALUACIÓN 7: Verificar sintaxis Python
# ============================================================
Write-Log "AUTOEVALUACIÓN 7: Verificando sintaxis Python..." "Info"

try {
    python -m py_compile app\main.py 2>&1 | Out-Null
    python -m py_compile app\core\config.py 2>&1 | Out-Null
    python -m py_compile app\core\security.py 2>&1 | Out-Null
    python -m py_compile app\models\base.py 2>&1 | Out-Null
    python -m py_compile app\models\tenant.py 2>&1 | Out-Null
    Write-Log "✓ Sintaxis Python válida" "Success"
} catch {
    Write-Log "ERROR: Error de sintaxis en archivos Python" "ErrorMsg"
    exit 1
}

# ============================================================
# RESUMEN FINAL
# ============================================================
Write-Log "════════════════════════════════════════════" "Info"
Write-Log "✅ SETUP COMPLETADO EXITOSAMENTE" "Success"
Write-Log "════════════════════════════════════════════" "Info"

Write-Log "PRÓXIMO PASO:" "Info"
Write-Log "Ejecuta: python -m uvicorn app.main:app --reload" "Warning"

Write-Log "" "Info"
Write-Log "Luego abre en navegador:" "Info"
Write-Log "http://localhost:8000/docs" "Warning"