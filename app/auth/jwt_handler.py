from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
import asyncio
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from app.config.config import users_collection, admin_collection
from bson import ObjectId

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) 
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    )

# User token verification
async def verify_token(token: str):
    try:
        loop = asyncio.get_event_loop()
        payload = await loop.run_in_executor(
            None, lambda: jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        )
        
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="No user ID found.")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
       
        if not user:
            raise HTTPException(status_code=401, detail="No user found.")
        return {"sub": user_id}

    except JWTError as e:
        print(f"JWTError in verify_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# admin token verification
async def admin_verify_token(token: str):
    try:
        loop = asyncio.get_event_loop()
        payload = await loop.run_in_executor(
            None, lambda: jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        )
        
        admin_id: str = payload.get("sub")
        if not admin_id:
            raise HTTPException(status_code=401, detail="No admin Id found.")
        admin = await admin_collection.find_one({"_id": ObjectId(admin_id)})
       
        if not admin:
            raise HTTPException(status_code=401, detail="No admin found.")
        return {"sub": admin_id}

    except JWTError as e:
        print(f"JWTError in verify_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    
