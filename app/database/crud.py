
from app.config.config import users_collection, user_preferences, dairy_entries_collection, book_collection, conversations, user_notification_collection
from bson import ObjectId
import hashlib
from passlib.hash import bcrypt
from typing import Any
from app.validators import basic_validators
from fastapi import  HTTPException
from bson import ObjectId
from datetime import datetime
from app.helpers.helpers import get_subscription_status


async def hash_password(password: str):
    hashed_pw = bcrypt.hash(password)
    return hashed_pw


async def create_user(user_data: dict):
    password = user_data.get("password")

    if password:
        hashed_pw = bcrypt.hash(password)
        user_data["password"] = hashed_pw
    else:
        user_data["password"] = None  # Apple / Google accounts have no password

    result = await users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data

async def get_or_create_oauth_user(email: str, name: str, provider: str):
    user = await users_collection.find_one({"email": email})
    print(f"get_or_create_oauth_user: {email}, {name}, {provider}")
    if not user:
        user_data = {
            "email": email,
            "name": name,
            "signup_method": "oauth",
            "provider": provider,
            "is_verified":True
        }
        result = await users_collection.insert_one(user_data)
        user = await users_collection.find_one({"_id": result.inserted_id})
    return user

async def verify_user(password: str, hashed: str) -> bool:
    password = password.encode("utf-8")
    return bcrypt.verify(password, hashed)

async def get_user_by_email(email: str):
    user = await users_collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user

async def get_user_by_id(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return None

    subscription = user.get("subscription", {})
    
    activated_at = subscription.get("activated_at")
    expires_at = subscription.get("expires_at")

    # Compute subscription status only if data exists
    subscription_status = get_subscription_status(activated_at, expires_at) if activated_at and expires_at else None

    user["subscription_status"] = subscription_status

    # Convert ID to string
    user["_id"] = str(user["_id"])

    return user


async def update_user(user_id: str, update_data: dict):

    user = await users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    return await get_user_by_id(user_id)

async def delete_user(user_id: str):
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    await dairy_entries_collection.delete_many({"user_id": user_id})
    await user_notification_collection.delete_many({"user_id": user_id})
    await conversations.delete_many({"user_id": user_id})
    await book_collection.delete_many({"user_id": ObjectId(user_id)})
    # Update related data.
    return result.deleted_count > 0 

async def upsert_user_preferences(db, user_id, pref_data) -> Any:
    user_preference_collection = db["user_preferences"]

    await user_preference_collection.update_one(
        {"user_id": user_id},
        {"$set": pref_data.dict()},
        upsert=True
    )

    updated_pref = await user_preference_collection.find_one({"user_id": user_id})
    return updated_pref

async def update_user_profile(db, user_id: str, update_data: dict):
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return updated_user

async def count_dairy_entries(user_id: str):
    # total_dairy_entries = await dairy_entries_collection.count_documents({"user_id": user_id, "book_generated": False})
    total_dairy_entries = await dairy_entries_collection.count_documents({"user_id": user_id})
    return total_dairy_entries or 0

async def count_dairy_entries_in_library(user_id: str):
    total_dairy_entries = await dairy_entries_collection.count_documents({"user_id": user_id})
    return total_dairy_entries or 0

async def count_books(user_id: str):
    total_books = await book_collection.count_documents({"user_id": user_id})
    return total_books or 0

async def get_user_preferences_by_id(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
    return user

async def get_user_by_apple_id(apple_id: str):
    return await users_collection.find_one({"apple_id": apple_id})

async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})

async def get_user_by_private_email(email: str):
    return await users_collection.find_one({"private_email": email})
