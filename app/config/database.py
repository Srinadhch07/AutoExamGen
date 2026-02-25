from dotenv import load_dotenv
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL")

async_client = AsyncIOMotorClient( MONGO_URL, tlsCAFile=certifi.where())
sync_client = MongoClient( MONGO_URL, tlsCAFile=certifi.where())

async_db = async_client["test"]
sync_db = sync_client["test"]

# Async collections
admins_collection = async_db["admins"]
users_collection = async_db["users"]
exams_collection = async_db["exams"]
exam_results_collection = async_db["results"]
resume_evaluations_collection = async_db["resume_evaluations"]

# Sync collections
sync_resume_evaluations_collection = sync_db["resume_evaluations"]

async def check_connection():
    try:
        await async_db.command("ping")
        sync_client.admin.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print("MongoDB connection failed:", e)




