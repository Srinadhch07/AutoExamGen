import time
import jwt
import httpx
from app.config.notification_config import TEAM_ID, KEY_ID, BUNDLE_ID, P8_FILE_PATH, IS_PRODUCTION

APNS_URL = "https://api.push.apple.com" if IS_PRODUCTION else "https://api.sandbox.push.apple.com"

_cached_token = None
_token_expiry = 0

def get_apns_jwt():
    global _cached_token, _token_expiry

    if _cached_token and time.time() < _token_expiry:
        return _cached_token

    with open(P8_FILE_PATH, "r") as f:
        private_key = f.read()

    headers = {"alg": "ES256", "kid": KEY_ID}
    payload = {"iss": TEAM_ID, "iat": int(time.time())}

    _cached_token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    _token_expiry = time.time() + 55 * 60

    return _cached_token

import httpx
import traceback

# async def send_ios_push(token: str, title: str, body: str, screen: str = ""):
#     try:
        
#         jwt_token = get_apns_jwt()

#         if not jwt_token:
#             return {
#                 "status": "failed",
#                 "error": "Failed to generate APNs JWT"
#             }

#         headers = {
#             "authorization": f"bearer {jwt_token}",
#             "apns-topic": BUNDLE_ID,
#             "content-type": "application/json"
#         }

#         payload = {
#             "aps": {
#                 "alert": {"title": title, "body": body},
#                 "sound": "default"
#             },
#             "screen": screen
#         }

#         url = f"{APNS_URL}/3/device/{token}"

#         async with httpx.AsyncClient(http2=True, timeout=10) as client:
#             response = await client.post(url, headers=headers, json=payload)

#         if response.status_code != 200:
#             print(f"APNs Failed ({response.status_code}): {response.text}")

#         return {
#             "token": token,
#             "status_code": response.status_code,
#             "response": response.text
#         }

#     except httpx.RequestError as e:
#         print("APNs Network Error:", str(e))
#         return {
#             "token": token,
#             "error": "Network error",
#             "details": str(e)
#         }

#     except Exception as e:
#         print("APNs Unknown Error:\n", traceback.format_exc())
#         return {
#             "token": token,
#             "error": "Unhandled exception",
#             "details": str(e)
#         }


async def send_ios_push(token: str, notification: dict):
    try:
        print(f'[CHECK POINT]: IOS notification sent')
        jwt_token = get_apns_jwt()
        if not jwt_token:
            return {"status": "failed", "error": "Failed to generate APNs JWT"}

        title = notification.get("title", "")
        body = notification.get("message", "")
        screen = notification.get("screen", "")

        headers = {
            "authorization": f"bearer {jwt_token}",
            "apns-topic": BUNDLE_ID,
            "content-type": "application/json"
        }

        payload = {
            "aps": {
                "alert": {
                    "title": title,
                    "body": body
                },
                "sound": "default"
            },
            "screen": screen,
            "notification_id": str(notification.get("_id"))
        }

        url = f"{APNS_URL}/3/device/{token}"

        async with httpx.AsyncClient(http2=True, timeout=10) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"APNs Failed ({response.status_code}): {response.text}")

        return {
            "token": token,
            "status_code": response.status_code,
            "response": response.text
        }

    except httpx.RequestError as e:
        print("APNs Network Error:", str(e))
        return {"token": token, "error": "Network error", "details": str(e)}

    except Exception as e:
        print("APNs Unknown Error:\n", traceback.format_exc())
        return {"token": token, "error": "Unhandled exception", "details": str(e)}
