import httpx
import asyncio

async def test_login():
    async with httpx.AsyncClient() as client:
        # Test seeded user login
        print("Testing seeded user login...")
        resp = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "client@docmet.com", "password": "password123"}
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print("✅ Login successful!")
            
            # Test fetching sites
            headers = {"Authorization": f"Bearer {token}"}
            sites_resp = await client.get("http://localhost:8000/api/v1/sites/", headers=headers)
            print(f"Sites status: {sites_resp.status_code}")
            if sites_resp.status_code == 200:
                print(f"Sites: {sites_resp.json()}")
            else:
                print(f"Failed to fetch sites: {sites_resp.text}")
        else:
            print(f"❌ Login failed: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_login())
