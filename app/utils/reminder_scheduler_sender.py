from datetime import datetime, timedelta
from bson import ObjectId
from app.config.config import users_collection, conversations
from app.utils.dynamic_sender import push_and_store_notification
from app.database.admin_chat_management_crud import get_chat_settings

conversation_collection = conversations

from datetime import datetime, timedelta
import pytz
from bson import ObjectId

IST = pytz.timezone("Asia/Kolkata")

async def send_chat_reminder_notifications():
    users = users_collection.find({"is_active": True})

   
    now_ist = datetime.now(IST)
    today_str = now_ist.date().isoformat()
    # print(f'[Chat reminder]: Started colletcting users')
    configuration = await get_chat_settings()
    min_words = configuration.get("min_words",{})
    async for user in users:
        try:
            
            user_id = str(user["_id"])
            scheduled_time = user.get("schedule_dairy_time")

            if not scheduled_time:
                continue

            last_sent = user.get("chat_reminder_sent_date")
            if last_sent == today_str:
                continue

            naive_ist = datetime.strptime(
                f"{today_str} {scheduled_time}",
                "%Y-%m-%d %H:%M"
            )
            scheduled_ist = IST.localize(naive_ist)

            trigger_time = scheduled_ist - timedelta(hours=1)

            if not (trigger_time <= now_ist <= trigger_time + timedelta(minutes=2)):
                # print(f'[Chat reminder]: User schedule time is not reached: {user["name"]}')
                continue


            # print(f'[Chat reminder]: User schedule time is reached: {user["name"]}')

            conversation = await conversation_collection.find_one({
                "user_id": user_id,
                "date": today_str
            })

            word_count = 0
            if conversation:
                messages = conversation.get("context") or conversation.get("history") or []

                for msg in messages:
                    content = msg.get("content")

                    if isinstance(content, str):
                        word_count += len(content.split())
                    elif isinstance(content, list):
                        for block in content:
                            if block.get("type") == "text":
                                word_count += len(block.get("text", "").split())

            if word_count < min_words:
                # print(f'[Chat reminder]: Sending reminder notifications: {user["name"]}')

                await push_and_store_notification(
                    user=user,
                    user_id=user_id,
                    title="Time to chat with AI ✍️",
                    message=f"1 hour left! Chat with AI and reach {min_words} words.",
                    screen="/screens/ChatScreen",
                    icon="bell"
                )

                await users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"chat_reminder_sent_date": today_str}}
                )
            # else:
                # print(f'[Chat reminder]: Sending reminder notifications: {user["name"]}')

        except Exception as e:
            print(f"[CHAT REMINDER ERROR] {user_id}: {e}")
