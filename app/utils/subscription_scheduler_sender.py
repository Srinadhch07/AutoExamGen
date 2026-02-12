from datetime import timedelta
from bson import ObjectId

from app.config.config import users_collection
from app.utils.dynamic_sender import push_and_store_notification
from app.utils.timezone_utils import mongo_to_utc, utc_to_ist, now_ist, IST


async def send_subscription_expiry_reminders():
    print("[SUBSCRIPTION JOB]: Triggered")

    users = users_collection.find({
        "is_active": True,
        "subscription.is_active": True
    })

    current_ist = now_ist()
    today_ist = current_ist.date()
    tomorrow_ist = today_ist + timedelta(days=1)
    tomorrow_str = tomorrow_ist.isoformat()

    async for user in users:
        try:
            user_id = str(user["_id"])
            name = user.get("name", "Unknown")

            subscription = user.get("subscription")
            if not subscription:
                continue

            expires_at = subscription.get("expires_at")
            if not expires_at:
                continue

            # STEP 1: Convert Mongo timestamp → Aware UTC
            expires_utc = mongo_to_utc(expires_at)

            # STEP 2: Convert UTC → IST
            expires_ist = utc_to_ist(expires_utc)

            expiry_date_ist = expires_ist.date()

            # Debug log
            print(f"[CHECK] {name}: Expires at IST = {expires_ist}, expiry_date = {expiry_date_ist}")

            # Only send if expiry date is TOMORROW
            if expiry_date_ist != tomorrow_ist:
                print(f"[SKIP] {name}: Not expiring tomorrow")
                continue

            last_sent = user.get("subscription_reminder_sent_date")
            if last_sent == tomorrow_str:
                print(f"[SKIP] {name}: Reminder already sent today")
                continue

            print(f"[SEND] Sending reminder to {name}")

            await push_and_store_notification(
                user=user,
                user_id=user_id,
                title="Subscription Expiring Soon ⚠️",
                message="Your subscription will expire tomorrow. Renew now to keep your benefits.",
                screen="/screens/subscriptionScreen",
                icon="bell"
            )

            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"subscription_reminder_sent_date": tomorrow_str}}
            )

        except Exception as e:
            print(f"[SUBSCRIPTION ERROR] {user_id}: {e}")
