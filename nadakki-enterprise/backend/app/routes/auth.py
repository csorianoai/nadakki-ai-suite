from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import SecurityService
from app.models import Tenant, User
import uuid
import secrets

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    country: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_id: str

@router.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    api_key = f"ndk_{secrets.token_urlsafe(32)}"
    
    tenant = Tenant(
        name=req.company_name,
        email=req.email,
        country=req.country,
        api_key=api_key,
        is_active=False
    )
    db.add(tenant)
    db.flush()
    
    user = User(
        tenant_id=tenant.id,
        email=req.email,
        hashed_password=SecurityService.hash_password(req.password),
        is_admin=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    return {
        "tenant_id": str(tenant.id),
        "user_id": str(user.id),
        "api_key": api_key,
        "status": "pending_approval"
    }

@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == req.email,
        User.tenant_id == req.tenant_id,
        User.is_active == True
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not SecurityService.verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = SecurityService.create_access_token({
        "sub": str(user.id),
        "tenant_id": str(req.tenant_id),
        "email": user.email
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "tenant_id": str(req.tenant_id)
    }
