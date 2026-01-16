import os
import httpx
import asyncio

async def verify_token():
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    
    if not token or not page_id:
        print("Falta token o page_id en .env")
        return
    
    print("🔍 Verificando token de Facebook...")
    print(f"Token (primeros 20 chars): {token[:20]}...")
    print(f"Page ID: {page_id}")
    
    # 1. Verificar token básico
    url = "https://graph.facebook.com/v18.0/me"
    params = {"access_token": token, "fields": "id,name"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        print("\n1. Verificación de token básico:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    
    # 2. Verificar permisos del token
    url = "https://graph.facebook.com/v18.0/me/permissions"
    params = {"access_token": token}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        print("\n2. Permisos del token:")
        for perm in data.get("data", []):
            if perm.get("status") == "granted":
                print(f"   ✅ {perm['permission']}")
            else:
                print(f"   ❌ {perm['permission']} ({perm.get('status', 'unknown')})")
    
    # 3. Verificar conexión con la página
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {"access_token": token, "fields": "id,name,access_token"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        print("\n3. Conexión con página:")
        if response.status_code == 200:
            page_data = response.json()
            print(f"   ✅ Página: {page_data.get('name')} ({page_data.get('id')})")
            if page_data.get('access_token'):
                print(f"   🔑 Token de página disponible")
                print(f"   Token de página: {page_data['access_token'][:20]}...")
        else:
            print(f"   ❌ Error: {response.json()}")

if __name__ == "__main__":
    asyncio.run(verify_token())
