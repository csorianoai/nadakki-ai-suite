from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        
        excluded_paths = ["/docs", "/openapi.json", "/health", "/api/v1/auth/register", "/api/v1/auth/login"]
        
        is_excluded = any(request.url.path.startswith(path) for path in excluded_paths)
        
        if not is_excluded and request.url.path.startswith("/api/") and not tenant_id:
            raise HTTPException(status_code=400, detail="X-Tenant-ID header required")
        
        request.state.tenant_id = tenant_id
        response = await call_next(request)
        return response
