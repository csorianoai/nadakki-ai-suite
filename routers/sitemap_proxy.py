from fastapi import APIRouter, Response, HTTPException
import httpx
from datetime import date, datetime
from typing import Optional, Dict, List

router = APIRouter(prefix="/sitemap", tags=["SEO"])

DOMAIN_CONFIGS: Dict[str, dict] = {
    "nadakki.com": {
        "name": "NADAKKI AI Suite",
        "supabase_url": "https://cegfydakaticlbjuaoxj.supabase.co/functions/v1/sitemap",
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "daily"},
            {"path": "/soluciones", "priority": 0.9, "changefreq": "weekly"},
            {"path": "/plataformas", "priority": 0.9, "changefreq": "weekly"},
            {"path": "/marketing-ai", "priority": 0.85, "changefreq": "weekly"},
            {"path": "/creditos-ai", "priority": 0.85, "changefreq": "weekly"},
            {"path": "/cobros-ai", "priority": 0.85, "changefreq": "weekly"},
            {"path": "/blog", "priority": 0.9, "changefreq": "daily"},
            {"path": "/nosotros", "priority": 0.7, "changefreq": "monthly"},
            {"path": "/contacto", "priority": 0.7, "changefreq": "monthly"},
            {"path": "/pricing", "priority": 0.8, "changefreq": "monthly"},
        ]
    },
    "nadaki.com": {
        "name": "Nadaki",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "daily"},
            {"path": "/about", "priority": 0.8, "changefreq": "monthly"},
        ]
    },
    "listindiario.ai": {
        "name": "Listin Diario AI",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "daily"},
            {"path": "/noticias", "priority": 0.9, "changefreq": "hourly"},
            {"path": "/deportes", "priority": 0.85, "changefreq": "hourly"},
            {"path": "/economia", "priority": 0.85, "changefreq": "hourly"},
        ]
    },
    "alofoke.ai": {
        "name": "Alofoke AI",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "daily"},
            {"path": "/radio", "priority": 0.9, "changefreq": "daily"},
            {"path": "/noticias", "priority": 0.9, "changefreq": "hourly"},
        ]
    },
    "jump2media.com": {
        "name": "Jump2Media",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "weekly"},
            {"path": "/services", "priority": 0.9, "changefreq": "weekly"},
            {"path": "/portfolio", "priority": 0.85, "changefreq": "weekly"},
        ]
    },
    "ramonalmontesoriano.com": {
        "name": "Ramon Almonte Soriano",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "weekly"},
            {"path": "/about", "priority": 0.9, "changefreq": "monthly"},
            {"path": "/projects", "priority": 0.85, "changefreq": "weekly"},
            {"path": "/blog", "priority": 0.8, "changefreq": "weekly"},
        ]
    },
}
"nadakiexcursions.com": {
        "name": "Nadaki Excursions",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "daily"},
            {"path": "/tours", "priority": 0.9, "changefreq": "weekly"},
            {"path": "/about", "priority": 0.7, "changefreq": "monthly"},
            {"path": "/contact", "priority": 0.7, "changefreq": "monthly"},
        ]
    },
    "ramonalmonte-soriano.lovable.app": {
        "name": "Ramon Almonte Blog",
        "supabase_url": None,
        "pages": [
            {"path": "/", "priority": 1.0, "changefreq": "weekly"},
            {"path": "/blog", "priority": 0.9, "changefreq": "daily"},
            {"path": "/about", "priority": 0.7, "changefreq": "monthly"},
        ]
    },
def generate_xml(domain: str, pages: List[dict]) -> str:
    today = date.today().isoformat()
    urls = ""
    for p in pages:
        urls += f"""  <url>
    <loc>https://{domain}{p['path']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{p.get('changefreq', 'weekly')}</changefreq>
    <priority>{p.get('priority', 0.5)}</priority>
  </url>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>"""

async def fetch_supabase(url: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10.0)
            return r.text if r.status_code == 200 else None
    except:
        return None

@router.get("/{domain}")
async def get_sitemap(domain: str):
    if domain not in DOMAIN_CONFIGS:
        raise HTTPException(404, f"Domain not found: {list(DOMAIN_CONFIGS.keys())}")
    config = DOMAIN_CONFIGS[domain]
    xml = None
    if config.get("supabase_url"):
        xml = await fetch_supabase(config["supabase_url"])
    if not xml:
        xml = generate_xml(domain, config["pages"])
    return Response(content=xml, media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})

@router.get("/")
async def list_domains():
    return {"domains": list(DOMAIN_CONFIGS.keys()), "usage": "GET /sitemap/{domain}"}
