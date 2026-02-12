import httpx
from fastapi import HTTPException

async def verify_google_token(access_token: str):
    url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    data = response.json()
    return {
        "email": data.get("email"),
        "name": data.get("name")
    }
