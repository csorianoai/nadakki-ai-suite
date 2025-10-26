"""
NADAKKI AI SUITE v3.8.0 – CREDICEFI BILLING & SaaS SUBDOMAIN MANAGER
---------------------------------------------------------------------
Quantum Sentinel Cloud + Financial Billing System + Multi-Tenant Subdomain Control
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging, os, json
from datetime import datetime
from typing import Dict, Any

# Base Setup
os.makedirs("logs", exist_ok=True)
os.makedirs("exports", exist_ok=True)
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
  handlers=[logging.FileHandler("logs/credicefi_billing.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger("CrediCefiBilling")

app = FastAPI(
  title="CrediCefi Billing Manager",
  description="AI-powered financial billing and tenant control",
  version="3.8.0",
  docs_url="/docs",
  redoc_url="/redoc"
)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"]
)

# Routers
from billing_routes_v7 import router as billing_router
from governance_routes_v6 import router as governance_router
app.include_router(billing_router)
app.include_router(governance_router)

# Simulación tenants
TENANTS = {
  "credicefi": {"plan": "enterprise", "subdomain": "credicefi.nadakki.com", "balance": 0.0, "usage": 0},
  "banco_ahorro": {"plan": "professional", "subdomain": "ahorro.nadakki.com", "balance": 0.0, "usage": 0},
}

@app.get("/")
async def root():
  return {
    "service": "CrediCefi Billing API",
    "version": "3.8.0",
    "phase": "7 – Billing & Subdomains",
    "modules": ["/billing/summary", "/billing/payments", "/governance/summary"]
  }

@app.get("/health")
async def health():
  return {"status": "healthy", "tenants": len(TENANTS), "timestamp": datetime.now().isoformat()}

@app.on_event("startup")
async def on_start():
  logger.info("🚀 CREDICEFI BILLING SYSTEM v3.8.0 INICIADO")
  logger.info("✓ Billing API en / billing  |  Governance en / governance")
  logger.info("✓ Multi-tenant subdomains operativos")
  logger.info("✓ Panel Streamlit activo en http://127.0.0.1:8501")
