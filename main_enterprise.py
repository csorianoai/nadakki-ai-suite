"""
Nadakki Enterprise FastAPI Application - Refactored
Auto-generated modular architecture
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime

# Import all our generated modules
from core.authentication.jwt_auth import jwt_auth
from adapters.wordpress.wp_adapter import create_wordpress_adapter
from core.cors_config import cors_config
from api.missing_endpoints import router as missing_endpoints_router

# Import existing modules (adapt as needed)
try:
    from app import app as legacy_app
    LEGACY_MODE = True
except ImportError:
    LEGACY_MODE = False

class NadakkiEnterpriseApp:
    def __init__(self):
        self.app = FastAPI(
            title="Nadakki AI Enterprise Suite",
            description="Advanced AI-powered credit evaluation platform with 36+ specialized agents",
            version="3.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self.setup_middleware()
        self.setup_authentication()
        self.setup_routes()
        self.setup_wordpress_adapter()
        self.setup_error_handlers()
    
    def setup_middleware(self):
        """Setup all middleware layers"""
        # CORS Configuration
        cors_config.add_cors_middleware(self.app)
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = datetime.utcnow()
            response = await call_next(request)
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Add response time header
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        # Tenant isolation middleware
        @self.app.middleware("http") 
        async def tenant_isolation(request: Request, call_next):
            tenant_id = request.headers.get("X-Tenant-ID", "default")
            request.state.tenant_id = tenant_id
            response = await call_next(request)
            return response
    
    def setup_authentication(self):
        """Setup JWT authentication system"""
        # Health check endpoint (no auth required)
        @self.app.get("/api/v1/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "3.0.0",
                "authentication": "enabled",
                "wordpress_adapter": "enabled"
            }
        
        # Authentication endpoints
        @self.app.post("/api/v1/auth/login")
        async def login(credentials: dict):
            # Implement actual authentication logic
            username = credentials.get("username")
            password = credentials.get("password")
            tenant_id = credentials.get("tenant_id", "default")
            
            # Validate credentials (replace with actual validation)
            if username and password:
                access_token = jwt_auth.create_access_token(
                    data={"sub": username},
                    tenant_id=tenant_id,
                    roles=["user", "admin"]  # Replace with actual roles
                )
                
                refresh_token = jwt_auth.create_refresh_token(username, tenant_id)
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": jwt_auth.access_token_expire_minutes * 60
                }
            
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        @self.app.post("/api/v1/auth/refresh")
        async def refresh_token(refresh_data: dict):
            refresh_token = refresh_data.get("refresh_token")
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Refresh token required")
            
            try:
                payload = jwt_auth.verify_token(refresh_token)
                if payload.get("type") != "refresh":
                    raise HTTPException(status_code=401, detail="Invalid token type")
                
                # Generate new access token
                access_token = jwt_auth.create_access_token(
                    data={"sub": payload.get("sub")},
                    tenant_id=payload.get("tenant_id"),
                    roles=["user", "admin"]  # Replace with actual roles
                )
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": jwt_auth.access_token_expire_minutes * 60
                }
                
            except Exception as e:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    def setup_routes(self):
        """Setup all application routes"""
        # Include missing endpoints router
        self.app.include_router(missing_endpoints_router, prefix="", tags=["enterprise"])
        
        # Legacy endpoints compatibility
        if LEGACY_MODE:
            # Mount existing routes if they exist
            pass
        
        # New enterprise endpoints
        @self.app.get("/api/v1/info")
        async def system_info():
            return {
                "name": "Nadakki AI Enterprise Suite",
                "version": "3.0.0",
                "features": [
                    "JWT Authentication",
                    "WordPress Integration", 
                    "Multi-tenant Architecture",
                    "36+ AI Agents",
                    "Power BI Integration",
                    "Enterprise Security"
                ],
                "endpoints": {
                    "authentication": "/api/v1/auth/*",
                    "wordpress": "/api/v1/wp/*",
                    "institutions": "/api/v1/institutions/*",
                    "powerbi": "/api/v1/powerbi/*",
                    "reports": "/api/v1/reports/*",
                    "tenants": "/api/v1/tenants/*"
                }
            }
    
    def setup_wordpress_adapter(self):
        """Setup WordPress integration adapter"""
        self.wordpress_adapter = create_wordpress_adapter(self.app)
    
    def setup_error_handlers(self):
        """Setup global error handlers"""
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error_code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error_code": "INTERNAL_ERROR",
                    "message": "Internal server error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    def get_app(self):
        """Get the FastAPI application instance"""
        return self.app

# Create application instance
nadakki_enterprise = NadakkiEnterpriseApp()
app = nadakki_enterprise.get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main_enterprise:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
