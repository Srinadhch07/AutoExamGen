from app.database.notifications_crud import create_dynamic_notification
from app.config.config import ist_time, user_notification_collection
from app.utils.dynamic_notifications import send_dynamic_notification
from app.helpers.timezone_utils import parse_datetime, ist_to_utc,now_ist


async def push_and_store_notification( user: dict,  user_id: str, title: str,  message: str, screen: str = "",icon: str = "", category: str = None):
    try:

        payload = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "screen": screen,
            "icon": icon
        }
        # Admin notification collection
        notification_data = await create_dynamic_notification(payload)

        if not notification_data:
            print("Failed to create notification")
            return None

        # Prepare user notification entry
        user_entry = {
            "user_id": notification_data["user_id"],
            "notification_id": notification_data["_id"],
            "title": notification_data["title"],
            "message": notification_data["message"],
            "is_read": False,
            "is_deleted": False,
            "screen": notification_data["screen"],
            "icon": notification_data["icon"],
            "category": category,
            "received_at": now_ist()
        }
        # Store notification in user collection

        await user_notification_collection.insert_one(user_entry)

        # 5. Send push notification
        await send_dynamic_notification(user, notification_data)

        return {
            "status": "success",
            "notification_id": str(notification_data["_id"])
        }

    except Exception as e:
        print("Error in push_and_store_notification:", str(e))
        return {
            "status": "failed",
            "error": str(e)
        }
