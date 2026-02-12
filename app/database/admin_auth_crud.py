
from app.config.config import admin_collection, dairy_entries_collection, book_collection, ist_time
from bson import ObjectId
from passlib.hash import bcrypt
from typing import Any
from bson import ObjectId
from datetime import datetime
import bcrypt
async def hash_password(password: str):
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_pw

async def create_admin(admin_data: dict):
    
    admin_defaults = {
        "full_name": None,
        "email": None,
        "phone_number": None,
        "role": "admin",
        "admin_name": None,
        "location": None,
        "bio": None,
        "image_path": None,
        "created_at": ist_time(),
        "updated_at": ist_time(),
        "is_active": True,
        "is_auth": False
    }


    for key, value in admin_defaults.items():
        admin_data.setdefault(key, value)

    if "password" in admin_data and admin_data["password"]:
        hashed_pw = bcrypt.hashpw(admin_data["password"].encode("utf-8"), bcrypt.gensalt())
        admin_data["password"] = hashed_pw.decode("utf-8")
    else:
        raise ValueError("Password is required for admin account creation")

    result = await admin_collection.insert_one(admin_data)
    admin_data["_id"] = str(result.inserted_id)

    return admin_data

async def get_or_create_oauth_admin(email: str, name: str, provider: str):
    admin = await admin_collection.find_one({"email": email})
    print(f"get_or_create_oauth_admin: {email}, {name}, {provider}")
    if not admin:
        admin_data = {
            "email": email,
            "name": name,
            "signup_method": "oauth",
            "provider": provider,
            "is_verified":True
        }
        result = await admin_collection.insert_one(admin_data)
        admin = await admin_collection.find_one({"_id": result.inserted_id})
    return admin

async def verify_admin(password: str, hashed) -> bool:
    password = password.encode("utf-8")
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password, hashed)

async def get_admin_by_email(email: str):
    
    admin = await admin_collection.find_one({"email": email})
    
    if admin:
        admin["_id"] = str(admin["_id"])
    return admin

async def get_admin_by_id(admin_id: str):
    admin = await admin_collection.find_one({"_id": ObjectId(admin_id)})
    if admin:
        admin["_id"] = str(admin["_id"])
    return admin

async def update_admin(admin_id: str, update_data: dict):
    await admin_collection.update_one({"_id": ObjectId(admin_id)}, {"$set": update_data})
    return await get_admin_by_id(admin_id)

async def upsert_admin_preferences(db, admin_id, pref_data) -> Any:
    admin_preference_collection = db["admin_preferences"]

    await admin_preference_collection.update_one(
        {"admin_id": admin_id},
        {"$set": pref_data.dict()},
        upsert=True
    )

    updated_pref = await admin_preference_collection.find_one({"admin_id": admin_id})
    return updated_pref

async def update_admin_profile(admin_id: str, update_data: dict):
    result = await admin_collection.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": update_data}
    )
    updated_admin = await admin_collection.find_one({"_id": ObjectId(admin_id)})
    return updated_admin

async def count_dairy_entries(admin_id: str):
    total_dairy_entries = await dairy_entries_collection.count_documents({"admin_id": admin_id, "book_generated": False})
    return total_dairy_entries or 0

async def count_dairy_entries_in_library(admin_id: str):
    total_dairy_entries = await dairy_entries_collection.count_documents({"admin_id": admin_id})
    return total_dairy_entries or 0

async def count_books(admin_id: str):
    total_books = await book_collection.count_documents({"admin_id": admin_id})
    return total_books or 0