from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime

# Try to import JWT, fall back if not available
try:
    from core.authentication.jwt_auth import jwt_auth
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print('Warning: JWT authentication not available')

app = FastAPI(
    title="Nadakki AI Enterprise Suite",
    description="Advanced AI-powered credit evaluation platform",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nadakki.com",
        "https://www.nadakki.com", 
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "jwt_available": JWT_AVAILABLE,
        "features": ["CORS", "Health Check", "Process Time"]
    }

@app.get("/api/v1/info")
async def system_info():
    return {
        "name": "Nadakki AI Enterprise Suite",
        "version": "3.0.0",
        "description": "Advanced AI-powered credit evaluation platform",
        "jwt_authentication": JWT_AVAILABLE,
        "endpoints": {
            "health": "/api/v1/health",
            "info": "/api/v1/info",
            "docs": "/docs",
            "wordpress": "/api/v1/wp/*"
        }
    }

@app.post("/api/v1/wp/evaluate")
async def wp_evaluate_credit(request: Request):
    try:
        wp_site = request.headers.get('X-WordPress-Site', 'unknown')
        tenant_id = request.headers.get('X-Tenant-ID', 'default')
        body = await request.json()
        
        result = {
            "evaluation_id": f"eval_{int(datetime.utcnow().timestamp())}",
            "risk_level": "medium",
            "score": 0.72,
            "recommendations": ["Standard approval process recommended"],
            "tenant_id": tenant_id,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": result,
            "message": "Credit evaluation completed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error: {str(e)}",
                "error_code": "EVALUATION_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/api/v1/wp/agents")
async def wp_get_agents(request: Request):
    agents = [
        {"name": "SentinelBot", "status": "active", "category": "monitoring"},
        {"name": "DNAProfiler", "status": "active", "category": "analysis"},
        {"name": "RiskOracle", "status": "active", "category": "evaluation"}
    ]
    
    return {
        "success": True,
        "data": {"agents": agents},
        "message": f"Retrieved {len(agents)} agents",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_enterprise_working:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
