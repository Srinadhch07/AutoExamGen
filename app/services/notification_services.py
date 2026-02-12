from datetime import datetime
from fastapi import HTTPException
from app.config.config import users_collection, user_notification_collection, ist_time
from app.utils.push_andriod_notification import send_push_notification, send_push_notification_single
from app.utils.push_ios_notification import send_ios_push
from app.utils.dynamic_notifications import send_dynamic_notification
from app.database.notifications_crud import (
    get_pending_notifications,
    update_notification
)

# handles single city/packages
async def process_scheduled_notifications():
    try:
        pending_notifications = await get_pending_notifications()
        if not pending_notifications:
            return

        for notif in pending_notifications:
            title = notif.get("title")
            message = notif.get("message")
            target = notif.get("target_audience", "").lower()
            value = notif.get("target_value")
            screen = notif.get("screen") or ""

            if not title or not message:
                continue


            await update_notification(notif["_id"], {"status": "processing"})

            query = {"fcm_token": {"$ne": None}}

            if target == "city":
                query["location"] = value
            elif target == "package":
                query["subscription.package_name"] = value
            elif target == "all":
                pass
            else:
                await update_notification(notif["_id"], {"status": "failed"})
                continue

            users = await users_collection.find(query).to_list(None)
            if not users:
                await update_notification(notif["_id"], {"status": "no_users"})
                continue

            now = ist_time()
            entries = [{
                "user_id": str(u["_id"]),
                "notification_id": str(notif["_id"]),
                "title": title,
                "message": message,
                "screen": screen,
                "icon": "user",
                "is_read": False,
                "is_deleted": False,
                "admin_sent": True,
                "received_at": now
            } for u in users]

            
            insert_result = await user_notification_collection.insert_many(entries)
            inserted_ids = insert_result.inserted_ids
            # print(f'[CHECK POINT]: Inserted into user_notifcation_collections')


            # print(f'[CHECK POINT]: Sending Admin Notifications')
            for user, inserted_id in zip(users, inserted_ids):

                # Fetch complete document
                user_notification = await user_notification_collection.find_one({"_id": inserted_id})

                # Send using universal sender
                await send_dynamic_notification(
                    user=user,
                    notification=user_notification
                )


            await update_notification(
                notif["_id"],
                {"status": "sent", "sent_at": ist_time()}
            )

        print("All scheduled notifications processed successfully.")

    except Exception as e:
        print(f"Error in process_scheduled_notifications(): {e}")

