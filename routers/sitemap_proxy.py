from fastapi import APIRouter, Response
import httpx
from datetime import date
from typing import Dict, Any

router = APIRouter()

@router.get("/sitemap-proxy/{tenant}")
async def serve_sitemap(tenant: str = "nadakki") -> Response:
    """
    Proxy para servir sitemap XML desde Supabase Edge Function.
    
    tenant: Identificador del cliente (nadakki, credicefi, etc.)
    """
    
    # Mapeo de tenants a sus edge functions
    tenant_map: Dict[str, str] = {
        "nadakki": "https://cegfydakaticlbjuaoxj.supabase.co/functions/v1/sitemap",
    }
    
    supabase_url = tenant_map.get(tenant)
    
    if not supabase_url:
        return Response(
            content=f'Error: Tenant {tenant} no configurado',
            status_code=404,
            media_type="text/plain"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(supabase_url, timeout=10.0)
            
            if response.status_code == 200:
                xml_content = response.text
                
                # Validar que sea XML
                if '<?xml' not in xml_content or '<urlset' not in xml_content:
                    raise ValueError("Respuesta no es XML válido")
                
                return Response(
                    content=xml_content,
                    media_type="application/xml; charset=utf-8",
                    headers={
                        "Cache-Control": "public, max-age=3600, s-maxage=7200",
                        "X-Sitemap-Tenant": tenant,
                        "X-Sitemap-Source": "supabase-edge-function",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            else:
                raise Exception(f"Supabase respondió con {response.status_code}")
                
        except Exception as e:
            print(f"Error obteniendo sitemap para {tenant}: {e}")
            
            # Fallback: sitemap mínimo
            today = date.today().isoformat()
            domain = "nadakki.com"
            
            fallback = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://{domain}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
            
            return Response(
                content=fallback,
                media_type="application/xml; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Sitemap-Tenant": tenant,
                    "X-Sitemap-Status": "fallback",
                    "Access-Control-Allow-Origin": "*"
                }
            )

@router.get("/sitemap-proxy")
async def serve_nadakki_sitemap() -> Response:
    """Ruta por defecto para nadakki.com"""
    return await serve_sitemap("nadakki")
