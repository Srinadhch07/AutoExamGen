import random
from bson import ObjectId
import json
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import json, ast
import random
import logging
import re
from uuid import uuid4

logger = logging.getLogger(__name__)

def generate_random_text():
    chars = "abcdefghijklmnopqrstyouvxyz1234567890"
    return ''.join(random.choice(chars) for _ in range(10))

def generate_otp(length=6):
    if length <= 0:
        raise ValueError("OTP length must be greater than 0")
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

def convert_objectids(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, list):
        return [convert_objectids(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    else:
        return obj

def safe_json_loads(s: str) -> dict:

    if isinstance(s, dict):
        return s
    if not isinstance(s, str):
        raise ValueError("AI response must be string or dict")
    
    cleaned = s.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON from AI: %s", e)
        logger.error("RAW RESPONSE:\n%s", s)
        raise ValueError("AI returned invalid JSON")

def safe_json(data):
    def default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, ObjectId):
            return str(o)
        return str(o)
    return json.dumps(data, ensure_ascii=False, default=default)

def serialize_doc(doc):
    if not doc:
        return doc

    serialized = {}

    for key, value in doc.items():

        # Convert ObjectId
        if isinstance(value, ObjectId):
            serialized[key] = str(value)

        # Convert datetime
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()

        # Convert nested dict
        elif isinstance(value, dict):
            serialized[key] = serialize_doc(value)

        # Convert list of objects
        elif isinstance(value, list):
            serialized[key] = [serialize_doc(item) if isinstance(item, dict) else (
                str(item) if isinstance(item, ObjectId) else item
            ) for item in value]

        else:
            serialized[key] = value

    return serialized

def serialize_docs(docs):
    return [serialize_doc(doc) for doc in docs]

def is_valid_objectid(id_str: str) -> bool:
    try:
        ObjectId(id_str)
        pass
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

def count_words(text: str) -> int:
    return len(text.split())

def utc_to_ist(utc_str: str):
    dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%MZ")
    return dt + timedelta(hours=5, minutes=30)

def to_ist(dt):
    return dt + timedelta(hours=5, minutes=30)

def is_private_email(email: str) -> bool:
    return email.endswith("privaterelay.appleid.com")

def package_day_stats(activated_at: datetime, expires_at: datetime, total_days: int):
    if not activated_at or not expires_at:
        return {
            "days_completed": None,
            "days_remaining": None,
            "days_after_expiry": None
        }
    
    if activated_at.tzinfo is None:
        activated_at = activated_at.replace(tzinfo=timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    

    today_utc = datetime.now(timezone.utc).date()
    activated_date = activated_at.astimezone(timezone.utc).date()
    expires_date = expires_at.astimezone(timezone.utc).date()

    days_completed = (today_utc - activated_date).days
    if days_completed < 0:
        days_completed = 0

    days_remaining = total_days - days_completed
    if days_remaining < 0:
        days_remaining = 0

    days_after_expiry = (today_utc - expires_date).days if today_utc > expires_date else 0

    return {
        "days_completed": days_completed,
        "total_days": total_days,
        "days_remaining": days_remaining,
        "days_after_expiry": days_after_expiry
    }

def get_subscription_status(activated_at, expires_at):
    if not activated_at or not expires_at:
        return {
            "is_active": False,
            "is_expired": False,
        }
    if isinstance(activated_at, str):
        activated_at = datetime.fromisoformat(activated_at)
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    
    if activated_at.tzinfo is None:
        activated_at = activated_at.replace(tzinfo=timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    is_active = expires_at > now
    is_expired = not is_active
    
    return {
        "is_active": is_active,
        "is_expired": is_expired,
    }

def generate_safe_filename(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    cleaned = cleaned.strip().replace(" ", "_")
    if not cleaned:
        cleaned = "Resume"
    unique_id = uuid4().hex[:6]
    return f"{cleaned}_{unique_id}"