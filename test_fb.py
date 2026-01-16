from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv("FACEBOOK_ACCESS_TOKEN")
page_id = os.getenv("FACEBOOK_PAGE_ID")

print(f"Token OK: {bool(token)}")
print(f"Token (primeros 30): {token[:30] if token else 'None'}...")
print(f"Page ID: {page_id}")

# Test publicacion
import asyncio
from agents.shared_layers.executors.social import get_social

async def test():
    social = get_social()
    print(f"Plataformas: {social.get_platforms()}")
    result = await social.post("Test Nadakki AI v3.3.0 activo!", ["facebook"])
    for p, r in result.items():
        print(f"{p}: success={r.success}, post_id={r.post_id}, error={r.error}")

asyncio.run(test())
