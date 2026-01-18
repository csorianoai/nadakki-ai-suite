import httpx
import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("FACEBOOK_ACCESS_TOKEN")
page_id = os.getenv("FACEBOOK_PAGE_ID")

# 1. Ver info del token
print("=== INFO DEL TOKEN ===")
r = httpx.get(f"https://graph.facebook.com/v18.0/me?access_token={token}&fields=id,name")
print(r.json())

# 2. Ver permisos
print("\n=== PERMISOS ===")
r = httpx.get(f"https://graph.facebook.com/v18.0/me/permissions?access_token={token}")
data = r.json()
for p in data.get("data", []):
    status = "✅" if p.get("status") == "granted" else "❌"
    print(f"  {status} {p['permission']}")

# 3. Verificar si tenemos acceso a la pagina
print(f"\n=== PAGINA {page_id} ===")
r = httpx.get(f"https://graph.facebook.com/v18.0/{page_id}?access_token={token}&fields=id,name,access_token")
print(r.json())
