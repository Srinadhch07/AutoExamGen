from app.utils.push_andriod_notification import send_push_notification_single
from app.utils.push_ios_notification import send_ios_push

# async def send_dynamic_notification(
#     user: dict,
#     title: str,
#     message: str,
#     screen: str = ""
# ):
#     print(f'[CHECK POINT]: Entered into dynimca function')
#     if not user:
#         return

#     token = user.get("fcm_token")
#     platform = (user.get("platform") or "").lower()

#     if not token or not platform:
#         print(f'[CHECK POINT]: No tokens found')
#         return

#     # Android
#     if platform == "android":
#         await send_push_notification_single( title=title, message=message, token = token, screen=screen)

#     # iOS
#     elif platform == "ios":
#         await send_ios_push( token=token, title=title, body=message, screen=screen)

async def send_dynamic_notification(user: dict, notification: dict):
    print("[CHECK POINT]: sending notification.")

    if not user or not notification:
        return

    token = user.get("fcm_token")
    platform = (user.get("platform") or "").lower()

    if not token or not platform:
        print("[CHECK POINT]: No tokens found")
        return

    title = notification.get("title", "")
    message = notification.get("message", "")
    screen = notification.get("screen", "")

    # Android
    if platform == "android":
        await send_push_notification_single(
            token=token,
            notification=notification
        )

    # iOS
    elif platform == "ios":
        await send_ios_push(
            token=token,
            notification=notification
        )
