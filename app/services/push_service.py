import firebase_admin
from firebase_admin import messaging

async def send_fcm_notification(token: str, title: str, body: str):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        messaging.send(message)
    except Exception as e:
        print(f"[FCM ERROR]: {e}")
