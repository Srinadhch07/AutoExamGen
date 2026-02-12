
from datetime import datetime
from bson import ObjectId
from app.config.config import subscription_package_collection, ist_time
from app.helpers.timezone_utils import now_utc
from app.helpers.helpers import serialize_doc

async def create_subscription_package(data: dict):
    data["is_active"] = True
    data["created_at"] = ist_time()
    data["updated_at"] = ist_time()
    result = await subscription_package_collection.insert_one(data)
    return str(result.inserted_id)

async def get_all_packages(is_active: bool | None = None):
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    packages = await subscription_package_collection.find(query).to_list(length=None)
    return packages

async def get_package_by_id(package_id: str):
    return await subscription_package_collection.find_one({"_id": ObjectId(package_id)})

async def get_package_by_name(package_name: str):
    return serialize_doc(await subscription_package_collection.find_one({"package_name": package_name}))

async def update_subscription_package(package_id: str, data: dict):
    data["updated_at"] = ist_time()
    result = await subscription_package_collection.update_one(
        {"_id": ObjectId(package_id)},
        {"$set": data}
    )
    return result.modified_count > 0

async def deactivate_package(package_id: str):
    result = await subscription_package_collection.update_one(
        {"_id": ObjectId(package_id)},
        {"$set": {"is_active": False, "updated_at": ist_time()}}
    )
    return result.modified_count > 0
