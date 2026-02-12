from pydantic import BaseModel, EmailStr, Field, constr, validator
from datetime import datetime, time
from typing import Optional, List
import re

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    signup_method: str = "credentials"
    
class OAuthRequest(BaseModel):
    access_token: str = Field(..., min_length=1, description="OAuth access token from Google")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    fcm_token: Optional[str] = None
    platform: str = "android"
    
    class Config:
        extra = "forbid"
class VERIFYOTP(BaseModel):
    email: EmailStr
    otp: str
    fcm_token: Optional[str] = None
    platform: str = "android"
    
    class Config:
        extra = "forbid"


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

    
    class Config:
        extra = "forbid"

class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    age: Optional[int]
    signup_method: str
    created_at: datetime
    class Config:
        validate_by_name = True
        
class UserPreferences(BaseModel):
    genre: str = "Memoir"
    tone: str = "neutral"
    target_audience: str = "self"
    writing_style: str = "narrative"
    language: str = "en"
    dairy_entry_time: Optional[str] = None  
    next_dairy_entry_check: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserPreferencesCreate(UserPreferences):
    pass

class UpdateUserProfileRequest(BaseModel):
    name: Optional[str] = None
    DOB: Optional[str] = None
    location: Optional[str] = None
    dairy_entry_time: Optional[str] = None

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class Conversation(BaseModel):

    date: str
    history: List[Message]

class dairy_entry(BaseModel):
    dairy_entry_title: str
    dairy_entry_summary: str
    emotion: str

class dairy_entryRequest(BaseModel):
    start_date: str
    end_date: str

class Updatedairy_entry(BaseModel):
    dairy_entry_id: str
    dairy_entry_date: Optional[str] = None
    dairy_entry_title: Optional[str] = None
    dairy_entry_summary: Optional[str] = None
    dairy_entry_body: Optional[str] = None
    emotion: Optional[str] = None

class CallScheduleRequest(BaseModel):
    schedule_call_time: str
    
class DiaryScheduleRequest(BaseModel):
    schedule_dairy_time: str

