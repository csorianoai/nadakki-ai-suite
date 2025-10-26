# ============================================================
# MONITOR ENTERPRISE v5 – SENTINEL CLOUD BRIDGE
# ============================================================
from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import json, os
from pathlib import Path

router = APIRouter(prefix="/cloud")
EXPORT_DIR = Path(__file__).resolve().parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

@router.get("/powerbi/data", response_class=JSONResponse)
async def powerbi_data():
    files = sorted(EXPORT_DIR.glob("metrics_*.json"), reverse=True)
    if not files:
        return JSONResponse({"error": "No hay datos exportados"}, status_code=404)
    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
    data["synced_at"] = datetime.now().isoformat()
    return JSONResponse(data)

@router.get("/powerbi/latest", response_class=FileResponse)
async def powerbi_latest():
    files = sorted(EXPORT_DIR.glob("metrics_*.json"), reverse=True)
    if not files:
        return JSONResponse({"error": "No export files found"}, status_code=404)
    return FileResponse(files[0], media_type="application/json", filename=files[0].name)

print("✅ Sentinel Cloud Bridge activo /cloud/powerbi/")
