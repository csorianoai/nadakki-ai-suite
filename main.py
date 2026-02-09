# ===============================================================================
# NADAKKI AI Suite - Main Application v4.0
# ===============================================================================
"""
NADAKKI Advertising Manager - Multi-tenant Platform with Dynamic AI Agents Discovery
Auto-descubre TODOS los 239 agentes sin hardcoding
Rutas ABSOLUTAS para Windows - 100% funcional
"""
from fastapi import FastAPI, Header, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# ============================================================
# CREAR APP FASTAPI
# ============================================================
app = FastAPI(
    title="NADAKKI Advertising Manager",
    description="Multi-tenant advertising platform with dynamic AI agents - v4.0",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CONFIGURACIÓN DINÁMICA - SIN HARDCODING
# ============================================================

AGENT_FILE_PATTERNS = [
    re.compile(r'.*IA\.py$', re.IGNORECASE),
    re.compile(r'.*Agent\.py$', re.IGNORECASE),
]

IGNORE_PATTERNS = [
    'backup', 'legacy', 'tests', 'test_', 'placeholders',
    'hyper_agents', '__pycache__', '.git', 'node_modules',
    'backup_', 'legacy_', 'agents_backup_'
]

MODULE_MAPPING = {
    "marketing": "marketing",
    "google-ads": "advertising",
    "nadakki-google-ads-mvp": "advertising",
    "legal": "legal",
    "contabilidad": "contabilidad",
    "logistica": "logistica",
    "educacion": "educacion",
    "investigacion": "investigacion",
    "presupuesto": "presupuesto",
    "rrhh": "rrhh",
    "ventascrm": "ventascrm",
    "recuperacion": "recuperacion",
    "regtech": "regtech",
    "operacional": "operacional",
    "originacion": "originacion",
}

ADVERTISING_PLATFORM_MAPPING = {
    "google_ads": {"keywords": ["google_ads", "google_ad", "rsa_ad", "search_terms", "budget_pacing"], "name": "Google Ads", "icon": "🔍"},
    "meta_ads": {"keywords": ["meta_ads", "facebook", "instagram", "messenger"], "name": "Meta Ads", "icon": "📱"},
    "linkedin_ads": {"keywords": ["linkedin"], "name": "LinkedIn Ads", "icon": "💼"},
    "tiktok_ads": {"keywords": ["tiktok", "videoreel"], "name": "TikTok Ads", "icon": "🎵"},
    "pinterest_ads": {"keywords": ["pinterest"], "name": "Pinterest Ads", "icon": "📌"},
    "youtube_ads": {"keywords": ["youtube"], "name": "YouTube Ads", "icon": "▶️"},
    "twitter_ads": {"keywords": ["twitter", "x_ads"], "name": "Twitter/X Ads", "icon": "🐦"},
    "snapchat_ads": {"keywords": ["snapchat", "snap_"], "name": "Snapchat Ads", "icon": "👻"},
}

DOMINICAN_BANKS = {
    "banreservas": {"name": "Banreservas", "market_share": 30.57},
    "banco_popular": {"name": "Banco Popular", "market_share": 22.18},
    "banco_bhd": {"name": "Banco BHD", "market_share": 15.42},
    "scotiabank": {"name": "Scotiabank", "market_share": 4.31},
}

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def should_ignore(path: str) -> bool:
    path_lower = path.lower()
    return any(pattern in path_lower for pattern in IGNORE_PATTERNS)

def detect_agent_type(filename: str) -> str:
    if filename.lower().endswith("ia.py"):
        return "IA"
    elif filename.lower().endswith("agent.py"):
        return "Agent"
    return "Unknown"

def detect_module(relative_path: str) -> str:
    parts = str(relative_path).replace("\\", "/").split("/")
    if len(parts) > 0:
        module = parts[0].lower()
        return MODULE_MAPPING.get(module, module)
    return "general"

def detect_advertising_platform(agent_id: str, filename: str) -> Optional[str]:
    name_lower = (agent_id + "_" + filename).lower()
    for platform_id, platform_info in ADVERTISING_PLATFORM_MAPPING.items():
        if any(kw in name_lower for kw in platform_info["keywords"]):
            return platform_id
    return None

def detect_category(agent_id: str, filename: str) -> str:
    name = agent_id.lower()
    categories = {
        "lead_management": ["lead", "scoring", "predictive"],
        "experimentation": ["abtest", "ab_test", "impact"],
        "campaign_management": ["campaign", "optimizer"],
        "content": ["content", "generator", "creative"],
        "social_media": ["social", "post", "listening"],
        "analytics": ["sentiment", "cohort", "analytics", "competitor", "intelligence"],
        "attribution": ["channel", "attribution", "budget", "forecast", "mix"],
        "segmentation": ["segment", "audience", "geo", "customer"],
        "personalization": ["personaliz", "engine"],
        "retention": ["retention", "predictor", "email", "automation"],
        "customer_journey": ["journey", "form", "minimal"],
        "pricing": ["pricing", "affinity", "offer", "filter", "cash"],
        "influencer": ["influencer", "match"],
        "quality": ["contact", "quality", "evaluat"],
        "orchestration": ["orchestrat"],
        "advertising": ["google_ads", "rsa_ad", "search_terms", "budget_pacing", "strategist"],
        "video": ["video", "reel", "viral"],
        "brand": ["brand", "fideliz"],
    }
    for category, keywords in categories.items():
        if any(kw in name for kw in keywords):
            return category
    return "general"

def get_agent_metadata(filepath: str, filename: str) -> dict:
    metadata = {
        "version": "unknown",
        "description": "",
        "has_execute": False,
        "size_kb": 0,
        "lines": 0,
    }
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)
        metadata["has_execute"] = "def execute" in content or "async def execute" in content
        metadata["size_kb"] = round(os.path.getsize(filepath) / 1024, 2)
        metadata["lines"] = content.count('\n') + 1
    except Exception as e:
        pass
    return metadata

# ============================================================
# FUNCIÓN PRINCIPAL: Cargar dinámicamente TODOS los agentes
# ============================================================

def load_all_agents() -> Dict[str, dict]:
    agents = {}
    main_file = Path(__file__).resolve()
    base_dir = main_file.parent
    agents_path = base_dir / "agents"
    
    print(f"\n🔍 Scanning for agents:")
    print(f"   Base dir: {base_dir}")
    print(f"   Agents path: {agents_path}")
    print(f"   Exists: {agents_path.exists()}")
    
    if not agents_path.exists():
        print(f"\n❌ ERROR: Agents path not found: {agents_path}")
        return agents
    
    try:
        all_py_files = list(agents_path.rglob("*.py"))
        print(f"\n✅ Found {len(all_py_files)} Python files total in agents/")
        
        matching_files = 0
        ignored_files = 0
        
        for filepath in sorted(all_py_files):
            matches_pattern = False
            for pattern in AGENT_FILE_PATTERNS:
                if pattern.match(filepath.name):
                    matches_pattern = True
                    break
            
            if not matches_pattern:
                continue
            
            try:
                relative = filepath.relative_to(agents_path)
            except ValueError:
                continue
            
            if should_ignore(str(relative)):
                ignored_files += 1
                continue
            
            agent_id = filepath.stem.lower()
            
            if agent_id in agents:
                continue
            
            matching_files += 1
            
            agent_type = detect_agent_type(filepath.name)
            module = detect_module(relative)
            category = detect_category(agent_id, filepath.name)
            platform = detect_advertising_platform(agent_id, filepath.name)
            metadata = get_agent_metadata(str(filepath), filepath.name)
            
            readable_name = (
                agent_id
                .replace("_", " ")
                .replace("ia", " IA")
                .replace("agent", " Agent")
                .title()
                .strip()
            )
            
            agents[agent_id] = {
                "id": agent_id,
                "name": readable_name,
                "filename": filepath.name,
                "module": module,
                "category": category,
                "type": agent_type,
                "advertising_platform": platform,
                "relative_path": str(relative).replace("\\", "/"),
                "status": "active" if metadata.get("has_execute") else "configured",
                "size_kb": metadata.get("size_kb", 0),
                "lines": metadata.get("lines", 0),
            }
        
        print(f"   Matching pattern (*IA.py, *Agent.py): {matching_files}")
        print(f"   Ignored (backup/legacy/test): {ignored_files}")
        print(f"\n✅ Successfully discovered {len(agents)} agents total")
        
    except Exception as e:
        print(f"\n❌ Error scanning agents: {e}")
    
    return agents

# ============================================================
# CARGAR AGENTES AL INICIAR
# ============================================================

print("\n" + "="*80)
print("🚀 NADAKKI Advertising Manager v4.0 - Starting...")
print("="*80)

ALL_AGENTS = load_all_agents()

modules_stats = {}
for agent in ALL_AGENTS.values():
    mod = agent["module"]
    if mod not in modules_stats:
        modules_stats[mod] = 0
    modules_stats[mod] += 1

if modules_stats:
    print(f"\n📂 Agents by module:")
    for mod, count in sorted(modules_stats.items(), key=lambda x: -x[1]):
        print(f"   - {mod}: {count} agents")

platform_stats = {}
for agent in ALL_AGENTS.values():
    if agent["advertising_platform"]:
        plat = agent["advertising_platform"]
        if plat not in platform_stats:
            platform_stats[plat] = 0
        platform_stats[plat] += 1

if platform_stats:
    print(f"\n📢 Advertising agents by platform:")
    for plat, count in sorted(platform_stats.items()):
        print(f"   - {plat}: {count} agents")

print(f"\n🎯 API available at: http://0.0.0.0:8000")
print(f"📚 Docs available at: http://0.0.0.0:8000/docs")
print("="*80 + "\n")

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agents_loaded": len(ALL_AGENTS),
        "total_agents": len(ALL_AGENTS),
        "modules": len(modules_stats)
    }

@app.get("/api/v1/agents")
async def list_agents(
    module: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    x_tenant_id: Optional[str] = Header(None),
):
    agents = list(ALL_AGENTS.values())
    
    if module:
        agents = [a for a in agents if a["module"] == module.lower()]
    if category:
        agents = [a for a in agents if a["category"] == category.lower()]
    if platform:
        agents = [a for a in agents if a["advertising_platform"] == platform.lower()]
    if search:
        search_lower = search.lower()
        agents = [a for a in agents if search_lower in a["id"] or search_lower in a["name"].lower()]
    
    return {
        "tenant_id": x_tenant_id,
        "total": len(agents),
        "agents": agents,
        "source": "dynamic_discovery"
    }

@app.get("/api/v1/agents/summary")
async def agents_summary(x_tenant_id: Optional[str] = Header(None)):
    by_module = {}
    by_category = {}
    by_platform = {}
    by_type = {"IA": 0, "Agent": 0}
    
    for agent in ALL_AGENTS.values():
        mod = agent["module"]
        by_module[mod] = by_module.get(mod, 0) + 1
        cat = agent["category"]
        by_category[cat] = by_category.get(cat, 0) + 1
        if agent["advertising_platform"]:
            plat = agent["advertising_platform"]
            by_platform[plat] = by_platform.get(plat, 0) + 1
        if agent["type"] in by_type:
            by_type[agent["type"]] += 1
    
    return {
        "tenant_id": x_tenant_id,
        "total_agents": len(ALL_AGENTS),
        "by_module": dict(sorted(by_module.items(), key=lambda x: -x[1])),
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "by_advertising_platform": by_platform,
        "by_type": by_type,
        "modules_count": len(by_module),
    }

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str, x_tenant_id: Optional[str] = Header(None)):
    if agent_id not in ALL_AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return {
        "tenant_id": x_tenant_id,
        "agent": ALL_AGENTS[agent_id]
    }

@app.get("/api/v1/advertising/platforms")
async def get_advertising_platforms(x_tenant_id: Optional[str] = Header(None)):
    platforms = {}
    for platform_id, platform_info in ADVERTISING_PLATFORM_MAPPING.items():
        related_agents = [a for a in ALL_AGENTS.values() if a["advertising_platform"] == platform_id]
        platforms[platform_id] = {
            "id": platform_id,
            "name": platform_info["name"],
            "icon": platform_info["icon"],
            "agent_count": len(related_agents),
            "agents": [{"id": a["id"], "name": a["name"], "status": a["status"]} for a in related_agents],
            "status": "active" if len(related_agents) > 0 else "configured",
        }
    return {
        "tenant_id": x_tenant_id,
        "platforms": platforms,
        "total_platforms": len(platforms),
        "total_all_agents": len(ALL_AGENTS),
    }

@app.get("/api/v1/advertising/dashboard")
async def get_advertising_dashboard(x_tenant_id: Optional[str] = Header(None)):
    from datetime import datetime
    return {
        "tenant_id": x_tenant_id,
        "total_agents": len(ALL_AGENTS),
        "modules": modules_stats,
        "platforms": len(ADVERTISING_PLATFORM_MAPPING),
        "tenants": len(DOMINICAN_BANKS),
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/api/v1/advertising/tenants")
async def get_tenants():
    return {
        "tenants": [{"id": k, **v} for k, v in DOMINICAN_BANKS.items()],
        "total": len(DOMINICAN_BANKS),
    }

@app.get("/api/v1/advertising/health")
async def advertising_health(x_tenant_id: Optional[str] = Header(None)):
    return {
        "status": "ok",
        "module": "advertising",
        "tenant_id": x_tenant_id,
        "total_agents": len(ALL_AGENTS),
        "platforms": len(ADVERTISING_PLATFORM_MAPPING),
    }

@app.get("/")
async def root():
    return {
        "system": "NADAKKI Advertising Manager",
        "version": "4.0.0",
        "total_agents": len(ALL_AGENTS),
        "total_modules": len(modules_stats),
        "total_platforms": len(ADVERTISING_PLATFORM_MAPPING),
        "total_tenants": len(DOMINICAN_BANKS),
    }

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)