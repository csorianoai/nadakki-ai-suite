import httpx
import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("FACEBOOK_ACCESS_TOKEN")
page_id = os.getenv("FACEBOOK_PAGE_ID")

print(f"Intentando publicar en Page {page_id}...")

# Publicar directamente
url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
data = {
    "message": "Test directo Nadakki AI v3.3.0 🚀",
    "access_token": token
}

r = httpx.post(url, data=data)
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")
