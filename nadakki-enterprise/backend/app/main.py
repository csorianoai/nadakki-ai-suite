from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.middleware.tenant import TenantMiddleware
from app.routes import auth, tenants, agents, billing

app = FastAPI(
    title="Nadakki SaaS",
    version="1.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)

app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(agents.router)
app.include_router(billing.router)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "nadakki-saas",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Nadakki SaaS iniciado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
