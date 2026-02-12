from datetime import datetime,timedelta
from bson import ObjectId
from app.config.config import notification_collection, ist_time
from app.helpers.timezone_utils import parse_datetime, ist_to_utc, now_utc

async def create_notification(data: dict):

    schedule_time = data.get("schedule_time")

    if schedule_time:
        dt_ist = parse_datetime(schedule_time)
        data["schedule_time"] = ist_to_utc(dt_ist)

    data.update({
        "screen": "",
        "status": "pending",
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "sent_at": None
    })

    notification = await notification_collection.insert_one(data)
    return await get_notification_by_id(notification.inserted_id)


async def get_notification_by_id(notification_id: str):
    notification = await notification_collection.find_one({"_id": ObjectId(notification_id)})
    if notification:
        notification["_id"] = str(notification["_id"])
    return notification

async def get_all_notifications(filters: dict = None):
    query = filters or {}
    notifications = await notification_collection.find(query).sort("created_at", -1).to_list(None)
    for n in notifications:
        n["_id"] = str(n["_id"])
    return notifications

async def get_pending_notifications():
    # print(f'[CHECK POINT]: get pending notification hitted')
    time_now = ist_time()  
    cursor = notification_collection.find(
        {
            "status": "pending",
            "schedule_time": {"$lte": time_now}
        }
    ).sort("schedule_time", 1) 

    notifications = await cursor.to_list(length=None)

    for n in notifications:
        n["_id"] = str(n["_id"])

    return notifications

async def delete_notification(notification_id: str):
    result = await notification_collection.delete_one({"_id": ObjectId(notification_id)})
    return result.deleted_count > 0

async def update_notification(notification_id: str, data: dict):
    print(f'[CHECK POINT]: Update notificaiton hitted')
    data["updated_at"] = now_utc()
    await notification_collection.update_one({"_id": ObjectId(notification_id)}, {"$set": data})
    return await get_notification_by_id(notification_id)

# dynamic notificaitons

async def create_dynamic_notification(data: dict):
    data.update({
        "created_at": now_utc(),
        "updated_at": now_utc(),
        "sent_at": now_utc()
    })

    result = await notification_collection.insert_one(data)
    data = await get_notification_by_id(str(result.inserted_id))
    return data