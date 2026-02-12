import razorpay
from fastapi import HTTPException
from app.config.database import settings_collection


async def get_payment_keys():
    data = await settings_collection.find_one({}, {
        "razorpay_key_id": 1,
        "razorpay_secret_key": 1
    })
    if not data:
        raise HTTPException(status_code=404, detail="Payment settings not found")
    return data.get("razorpay_key_id"), data.get("razorpay_secret_key")


async def razorpay_client():
    key_id, key_secret = await get_payment_keys()

    if not key_id or not key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys missing")

    return razorpay.Client(auth=(key_id, key_secret))
