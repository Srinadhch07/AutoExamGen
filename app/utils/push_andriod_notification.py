import os
import httpx
from google.oauth2 import service_account
import google.auth.transport.requests
from app.config.notification_config import PROJECT_ID, SERVICE_ACCOUNT_FILE, SCOPES

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

def get_access_token() -> str:
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

async def send_push_notification(title: str, message: str, tokens: list[str]):
    print("[FCM Notifcation system]: Sending notifications got tokens")

    if not tokens:
        print("No tokens to send notification.")
        return []

    access_token = get_access_token()
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    results = []

    async with httpx.AsyncClient(timeout=10) as client:
        for token in tokens:
            print(f"Sending to token: {token}")

            payload = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": title,
                        "body": message
                    }
                }
            }

            try:
                response = await client.post(url, headers=headers, json=payload)

                try:
                    res_json = response.json()
                except Exception:
                    res_json = {"raw_response": response.text}

                result = {
                    "token": token,
                    "status_code": response.status_code,
                    "response": res_json
                }

                # log failure
                if response.status_code != 200:
                    print(f"FCM failed for {token}: {res_json}")

                results.append(result)

            except Exception as e:
                print("FCM Exception:", str(e))
                results.append({
                    "token": token,
                    "error": str(e)
                })

    return results

# async def send_push_notification_single(title: str, message: str, token: str, screen: str):
#     print("[CHECK POINT]:Sending notification to single user")

#     if not token:
#         print("No token provided.")
#         return None

#     access_token = get_access_token()
#     url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "message": {
#             "token": token,
#             "notification": {
#                 "title": title,
#                 "body": message
#             },
#             "data": {   
#                 "screen": screen
#             }
#         }
#     }

#     try:
#         async with httpx.AsyncClient(timeout=10) as client:
#             response = await client.post(url, headers=headers, json=payload)

#         try:
#             res_json = response.json()
#         except Exception:
#             res_json = {"raw_response": response.text}

#         result = {
#             "token": token,
#             "status_code": response.status_code,
#             "response": res_json
#         }

#         # log failure
#         if response.status_code != 200:
#             print(f"FCM failed for {token}: {res_json}")

#         print(f'Notification sent for {screen}')
#         return result

#     except Exception as e:
#         print("FCM Exception:", str(e))
#         return {
#             "token": token,
#             "error": str(e)
#         }


async def send_push_notification_single(token: str, notification: dict):
    print("[CHECK POINT]: Andriod notification sent")

    if not token:
        print("No token provided.")
        return None

    title = notification.get("title", "")
    message = notification.get("message", "")
    screen = notification.get("screen", "")

    access_token = get_access_token()
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": message
            },
            "data": {
                "screen": screen,
                "notification_id": str(notification.get("_id"))
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, headers=headers, json=payload)

        try:
            res_json = response.json()
        except Exception:
            res_json = {"raw_response": response.text}

        if response.status_code != 200:
            print(f"FCM failed for {token}: {res_json}")

        print(f"Notification sent for {screen}")

        return {
            "token": token,
            "status_code": response.status_code,
            "response": res_json
        }

    except Exception as e:
        print("FCM Exception:", str(e))
        return {"token": token, "error": str(e)}
