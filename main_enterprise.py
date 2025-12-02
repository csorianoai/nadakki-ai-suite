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

# ===============================================================
# ✅ CORE IMPORTS
# ===============================================================
from core.authentication.jwt_auth import jwt_auth
from adapters.wordpress.wp_adapter import create_wordpress_adapter
from core.cors_config import cors_config
from api.missing_endpoints import router as missing_endpoints_router

# ✅ NUEVO: IMPORTAR ROUTER DE MARKETING
from routes.marketing_routes import router as marketing_router

# ===============================================================
# ✅ LEGACY COMPATIBILITY (SAFE FALLBACK)
# ===============================================================
try:
    from app import app as legacy_app
    LEGACY_MODE = True
except ImportError:
    LEGACY_MODE = False


class NadakkiEnterpriseApp:
    def __init__(self):
        """Inicializa la aplicación principal Nadakki Enterprise"""
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

    # ===============================================================
    # ✅ MIDDLEWARE CONFIGURATION
    # ===============================================================
    def setup_middleware(self):
        """Setup all middleware layers"""
        cors_config.add_cors_middleware(self.app)

        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = datetime.utcnow()
            response = await call_next(request)
            process_time = (datetime.utcnow() - start_time).total_seconds()
            response.headers["X-Process-Time"] = str(process_time)
            return response

        # Tenant isolation middleware
        @self.app.middleware("http")
        async def tenant_isolation(request: Request, call_next):
            tenant_id = request.headers.get("X-Tenant-ID", "default")
            request.state.tenant_id = tenant_id
            response = await call_next(request)
            return response

    # ===============================================================
    # ✅ AUTHENTICATION SETUP
    # ===============================================================
    def setup_authentication(self):
        """Setup JWT authentication system"""

        @self.app.get("/api/v1/health")
        async def health_check():
            """Simple health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "3.0.0",
                "authentication": "enabled",
                "wordpress_adapter": "enabled"
            }

        # Login endpoint
        @self.app.post("/api/v1/auth/login")
        async def login(credentials: dict):
            username = credentials.get("username")
            password = credentials.get("password")
            tenant_id = credentials.get("tenant_id", "default")

            if username and password:
                access_token = jwt_auth.create_access_token(
                    data={"sub": username},
                    tenant_id=tenant_id,
                    roles=["user", "admin"]
                )
                refresh_token = jwt_auth.create_refresh_token(username, tenant_id)
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": jwt_auth.access_token_expire_minutes * 60
                }

            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Refresh endpoint
        @self.app.post("/api/v1/auth/refresh")
        async def refresh_token(refresh_data: dict):
            refresh_token = refresh_data.get("refresh_token")
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Refresh token required")

            try:
                payload = jwt_auth.verify_token(refresh_token)
                if payload.get("type") != "refresh":
                    raise HTTPException(status_code=401, detail="Invalid token type")

                access_token = jwt_auth.create_access_token(
                    data={"sub": payload.get("sub")},
                    tenant_id=payload.get("tenant_id"),
                    roles=["user", "admin"]
                )

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": jwt_auth.access_token_expire_minutes * 60
                }
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

    # ===============================================================
    # ✅ ROUTES SETUP (INCLUYE MARKETING CORE)
    # ===============================================================
    def setup_routes(self):
        """Setup all application routes"""
        # Existing router
        self.app.include_router(missing_endpoints_router, prefix="", tags=["Enterprise"])

        # ✅ NUEVO: INCLUIR ROUTER DE MARKETING CORE
        self.app.include_router(marketing_router, prefix="", tags=["Marketing"])

        # Legacy compatibility block
        if LEGACY_MODE:
            pass  # Placeholder for legacy routes if needed

        # System info endpoint
        @self.app.get("/api/v1/info")
        async def system_info():
            """Información general del sistema"""
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
                    "marketing": "/api/v1/marketing/*",
                    "tenants": "/api/v1/tenants/*"
                }
            }

    # ===============================================================
    # ✅ WORDPRESS INTEGRATION
    # ===============================================================
    def setup_wordpress_adapter(self):
        """Setup WordPress integration adapter"""
        self.wordpress_adapter = create_wordpress_adapter(self.app)

    # ===============================================================
    # ✅ ERROR HANDLERS
    # ===============================================================
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
                    "message": str(exc) or "Internal server error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

    # ===============================================================
    # ✅ APP ACCESSOR
    # ===============================================================
    def get_app(self):
        """Return the FastAPI application instance"""
        return self.app


# ===============================================================
# ✅ ENTRYPOINT
# ===============================================================
nadakki_enterprise = NadakkiEnterpriseApp()
app = nadakki_enterprise.get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main_enterprise:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
