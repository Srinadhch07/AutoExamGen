from dotenv import load_dotenv
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL")
client = AsyncIOMotorClient(
    MONGO_URL,
    tlsCAFile=certifi.where()
)
db = client["test"]

# Admin collection
admins_collection = db["admins"]

# User collection
users_collection = db["users"]
exams_collection = db["exams"]
exam_results_collection = db["results"]

async def check_connection():
    try:
        await db.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print("MongoDB connection failed:", e)




