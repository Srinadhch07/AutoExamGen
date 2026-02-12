#v2
from fastapi import APIRouter, HTTPException,Request
from app.schemas import schemas
from app.database import crud
from app.auth.jwt_handler import create_access_token
from passlib.hash import bcrypt
from app.validators import basic_validators
from app.auth.jwt_handler import create_access_token
from fastapi.responses import RedirectResponse
import httpx
from dotenv import load_dotenv
import os
from app.helpers import helpers
from datetime import datetime, timedelta
from app.services import send_mail
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt
import httpx
from app.models import auth_models
from app.helpers.helpers import serialize_doc, serialize_docs
from app.database.subscription_crud import get_package_by_name
from app.helpers.timezone_utils import now_utc
from app.config.config import countries_collection
router = APIRouter()
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

APPLE_KEYS_URL =  os.getenv("APPLE_KEYS_URL")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")

@router.post("/register")
async def register(payload: schemas.UserCreate, request: Request):
    try:
        payload.email = payload.email.strip().lower()
        payload.name = payload.name.strip()
        
        if payload.email and not basic_validators.is_valid_name(payload.name):
            raise HTTPException(status_code=400, detail="Invalid name format.")
        
        if payload.email and not basic_validators.is_valid_email(payload.email):
            raise HTTPException(status_code=400, detail="Invalid email format.")

        existing_user = await crud.get_user_by_email((payload.email.lower()))
        
        if existing_user:
            if existing_user['is_verified']:
                raise HTTPException(status_code=400, detail="Email already registered.")
            else:
                otp = helpers.generate_otp()
                otp_expiry = datetime.utcnow() + timedelta(minutes=5)
                existing_user = await crud.update_user(existing_user["_id"], {"otp": otp, "otp_expiry": otp_expiry})
                mail_sent = await send_mail.send_otp_email(existing_user, existing_user["otp"])
                if mail_sent:
                    return {
                        "message": "OTP sent successfully",
                        "user_id": str(existing_user["_id"]),
                        "email": existing_user["email"]
                    }

        if not basic_validators.is_strong_password(payload.password):
            raise HTTPException(
                status_code=400,
                detail="Invalid password format. Must be 8-128 chars, include uppercase, lowercase, number, and a special character."
            )

        otp = helpers.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        
        payload_dict = payload.dict()
        package = await get_package_by_name("Default")
        payload_dict.update({
            "otp": otp,
            "otp_expiry": otp_expiry,
            "is_verified": False,
            "full_name": None,
            "nick_name": None,
            "country_code": None,
            "mobile_code": None,
            "phone_number": None,
            "location": None,
            "DOB": None,
            "bio": None,
            "profile_photo": None,
            "schedule_call_time": "21:00",
            "schedule_dairy_time": "21:00",
            "num_journals": 0,
            "num_books": 0,
            "is_active": True,
            "is_blocked": False,
            "is_auth": False,
            "fcm_token":None,
            "platform": None,
            "category": None,
            "remaining_books": package["book_count"],
            "subscription_type": package["package_name"],
            "subscription": {
                "package_id": package["_id"],
                "package_name": package["package_name"],
                "price":package["price"],
                "activated_at": now_utc(),
                "expires_at": None,
                "status": "Active",
                "is_active": package["is_active"]
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })

        user = await crud.create_user(payload_dict)
        mail_sent = await send_mail.send_otp_email(user, user["otp"]) 

        if mail_sent:
            return {
                "message": "OTP sent successfully",
                "user_id": str(user["_id"]),
                "email": user["email"]
            }
        else:
            await crud.delete_user(user["_id"])
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal error in register(): {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/verifyotp")
async def verify_otp(payload: schemas.VERIFYOTP, request: Request):
    try:
        email = payload.email
        otp = payload.otp

        if not email:
            raise HTTPException(status_code=404, detail="Email not found.")

        if not otp:
            raise HTTPException(status_code=404, detail="OTP not found.")

        if not basic_validators.is_valid_email(email):
            raise HTTPException(status_code=400, detail="Invalid email format.")

        user = await crud.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="No user found.")

        # OTP expiry check
        if datetime.utcnow() > user["otp_expiry"]:
            raise HTTPException(status_code=423, detail="OTP Expired")

        # Compare stored OTP with input
        if otp == user["otp"]:
            await crud.update_user(user["_id"], {"is_verified": True})

            token = await create_access_token({"sub": str(user["_id"])})

            # Update auth details
            user = await crud.update_user(
                str(user["_id"]),
                {   "full_name": user["name"],
                    "is_auth": True,
                    "fcm_token": payload.fcm_token,
                    "platform": payload.platform,
                },
            )

            request.session["user_id"] = str(user["_id"])

            return {
                "message": "Verification successful.",
                "user_name": user.get("name"),
                "access_token": token,
                "is_active": True,
                "is_auth": True,
                "email": user["email"],
                "signup_method": user["signup_method"]
            }

        else:
            raise HTTPException(status_code=403, detail="Invalid OTP.")

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/resendotp")
async def resendotp(payload: dict, request: Request):
    try:
        if payload["email"] and not basic_validators.is_valid_email(payload["email"]):
            raise HTTPException(status_code=400, detail="Invalid email format.")
            
        existing_user = await crud.get_user_by_email(payload["email"])        
        if not existing_user:
            raise HTTPException(status_code=404, detail="No user found.")
            
        otp = helpers.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        existing_user = await  crud.update_user(existing_user["_id"],{"otp":otp,"otp_expiry":otp_expiry})
        mail_sent = await send_mail.send_forgot_otp(serialize_doc(existing_user), existing_user["otp"])

        if mail_sent:
            return {
                "message": "OTP sent successfully",
                "existing_user_id": str(existing_user["_id"]),
                "email": existing_user["email"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
async def login(payload: schemas.LoginRequest, request: Request):
    try:
        
        user = await crud.get_user_by_email(payload.email)
        is_profile_updated = False

        if not user:
            raise HTTPException(status_code=401, detail="Please enter a registered email")
        if user:
            if user.get("is_blocked",{}):
                raise HTTPException(status_code=401, detail="User is blocked")
            if user.get("phone_number"):
                is_profile_updated = True

        if  user["signup_method"] == "oauth":
            raise HTTPException(status_code=401, detail="Invalid Login method")
        if not user["is_verified"]:
            raise HTTPException(status_code=403, detail="Please verify your account by signing up again.")
                    
        if not await crud.verify_user(payload.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        token = await create_access_token({"sub": str(user["_id"])})

        user = await crud.update_user(str(user["_id"]),{"is_auth": True, "fcm_token": payload.fcm_token, "platform": payload.platform})
        request.session["user_id"] = str(user["_id"])

        return {
                "user_id": str(user["_id"]),
                "user_name": user.get("name"),
                "access_token": token,
                "is_active": True,
                "is_auth": True,
                "signup_method": user["signup_method"], 
                "is_profile_updated": is_profile_updated
            }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error at login(): {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/countries")
async def countries(request: Request):
    try:
            all_countries = await countries_collection.find({"status": "Active"}) \
                .sort("countryName", 1) \
                .collation({"locale": "en", "strength": 2}) \
                .to_list(length=None)

            return {
                "countries": serialize_docs(all_countries)
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error at countries(): {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@router.post("/forgot-password/sendotp")
async def sendotp(payload: dict, request: Request):
    try:

        if payload["email"] and not basic_validators.is_valid_email(payload["email"]):
            raise HTTPException(status_code=400, detail="Invalid email format.")
            
        existing_user = await crud.get_user_by_email(payload["email"])    
        if not existing_user:
            raise HTTPException(status_code=404, detail="No user found.")
        if existing_user.get("signup_method",{}).lower() == "oauth":
            raise HTTPException(status_code=400, detail="Can't send OTP, use another login method.")        
        otp = helpers.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        existing_user = await  crud.update_user(existing_user["_id"],{"otp":otp,"otp_expiry":otp_expiry})
        mail_sent = await send_mail.send_forgot_otp(serialize_doc(existing_user), existing_user["otp"])

        if mail_sent:
            return {
                "message": "OTP sent successfully",
                "existing_user_id": str(existing_user["_id"]),
                "email": existing_user["email"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again.")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/forgot-password/verifyotp")
async def verfiy_otp(payload: dict, request: Request):
    try:
        email = payload.get("email")
        user = await crud.get_user_by_email(email)   
        if not user: 
            raise HTTPException(status_code = 404, detail="No user found")
        otp = payload.get("otp")

        if not otp:
            raise HTTPException(status_code=404, detail="OTP not found.")
        
        if datetime.utcnow() > user["otp_expiry"]:
            return {"message": "OTP expired"}
        if otp == user["otp"]:
            request.session['email_for_password'] = user['email']
            return {
                "message": "Verification successful. Please change your password now."
            }
        else:
            raise HTTPException(status_code=403, detail="Invalid OTP.")
            
    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/updatepassword")
async def sendotp(payload: dict, request: Request):
    try:
        email = payload.get("email")

        if not email:
            raise HTTPException(status_code=404, detail="No email found.")

        existing_user = await crud.get_user_by_email(email)

        if not existing_user:
            raise HTTPException(status_code=404, detail="No user found.")

        if not basic_validators.is_strong_password(payload["password"]):
            raise HTTPException(status_code=400,detail="Invalid password format. Must be 8-128 chars, include uppercase, lowercase, number, and a special character."
            )
        hashed_pass = await crud.hash_password(payload["password"])
        updated_user = await crud.update_user(existing_user["_id"],{"password": hashed_pass})

        if updated_user:
            return {
                "message": "Password updated successfully.",
                "existing_user_id": str(updated_user["_id"]),
                "email": updated_user["email"]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update the passoword. Please try again.")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/logout")
async def logout(request: Request):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="user not logged in")
        
        updated_user = await crud.update_user(user_id, {"is_auth": False, "fcm_token": None })
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update user status")

        request.session.clear()

        return {"message": "user logged out successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error at user_logout(): {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/google/signin")
async def google_signin(payload: auth_models.GoogleLoginRequest, request: Request):
    try:
        try:
            idinfo = id_token.verify_oauth2_token(
                payload.token,
                google_requests.Request()
            )

            if idinfo["aud"] != GOOGLE_CLIENT_ID:
                raise HTTPException(status_code=401, detail="Invalid audience")

        except ValueError as e:
            print("Google token verification error:", str(e))
            raise HTTPException(status_code=401, detail="Invalid Google token")

        email = idinfo.get("email")
        name = idinfo.get("name")

        if not email:
            raise HTTPException(status_code=400, detail="Google token does not contain email")

        user = await crud.get_user_by_email(email)
        is_exist = False
        is_profile_updated = False
        if user:
            if user.get("is_blocked",{}):
                raise HTTPException(status_code=401, detail="User is blocked")
            

            if user.get("signup_method") != "oauth":
                raise HTTPException(status_code=400, detail="Email registered with password login")
            is_exist = True

            if user.get("phone_number"):
                is_profile_updated = True

            token = await create_access_token({"sub": str(user["_id"])})

            await crud.update_user(
                str(user["_id"]),
                { 
                    "is_auth": True,
                    "fcm_token": payload.fcm_token,
                    "platform": payload.platform,
                    "updated_at": datetime.utcnow()
                }
            )

        else:
            package= await get_package_by_name("Default")
            user_data = {
                "email": email,
                "password":"s211120039346070083d",
                "name": name,
                "signup_method": "oauth",
                "country_code": None,
                "mobile_code": None,
                "phone_number": None,
                "is_verified": True,
                "is_active": True,
                "is_blocked": False,
                "is_auth": True,
                "fcm_token": payload.fcm_token,
                "platform": payload.platform,
                "category": None,
                "remaining_books": package["book_count"],
                "subscription_type": package["package_name"],
                "subscription": {
                    "package_id": package["_id"],
                    "package_name": package["package_name"],
                    "price":package["price"],
                    "activated_at": now_utc(),
                    "expires_at": None,
                    "status": None,
                    "is_active": package["is_active"]
                },
                "schedule_call_time": "21:00",
                "schedule_dairy_time": "21:00",
                "num_journals": 0,
                "num_books": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            print(f"[CHECK POINT]:About to creaet user ")
            user = await crud.create_user(user_data)
            print(f"[CHECK POINT]:After to creaet user ")
            token = await create_access_token({"sub": str(user["_id"])})

        # 3. Save session
        request.session["user_id"] = str(user["_id"])

        return {

            "user_id": str(user["_id"]),
            "user_name": name,
            "access_token": token,
            "email": email,
            "is_auth": True,
            "is_active": True,
            "is_exist": is_exist,
            "is_profile_updated": is_profile_updated
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Google Signin Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

from fastapi import APIRouter, HTTPException, Request
import httpx, json
import jwt
from jwt.algorithms import RSAAlgorithm
from datetime import datetime

@router.post("/apple/signin")
async def apple_signin(payload: auth_models.AppleLoginRequest, request: Request):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(APPLE_KEYS_URL)
            apple_keys = res.json()["keys"]

        token = payload.token

        try:
            header = jwt.get_unverified_header(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid Apple token header")

        kid = header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Invalid Apple token")


        key = next((k for k in apple_keys if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid Apple token key")

        try:
            public_key = RSAAlgorithm.from_jwk(json.dumps(key))
            print("PUBLIC KEY:", public_key)
        except Exception as e:
            print("JWK Conversion Error:", e)
            raise HTTPException(status_code=500, detail="Failed to process Apple JWK")

        if not APPLE_CLIENT_ID:
            print("ERROR: APPLE_CLIENT_ID is MISSING")
            raise HTTPException(status_code=500, detail="Apple client ID not configured")

        try:
            claims = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=APPLE_CLIENT_ID,
            )
        except Exception as e:
            print("Apple Decode Error:", e)
            raise HTTPException(status_code=401, detail="Invalid Apple identity token")

        apple_id = claims.get("sub")
        email = claims.get("email")
        name = payload.name or "Apple User"

        if not apple_id:
            raise HTTPException(status_code=401, detail="Invalid Apple token data")

        real_email = None
        private_email = None
        is_private = False

        if email:
            if helpers.is_private_email(email):
                private_email = email
                is_private = True
            else:
                real_email = email

        user = await crud.get_user_by_apple_id(apple_id)
        print(f'real_email: {real_email}, private email: {private_email}')

        is_exist = False
        is_profile_updated = False

        if user:
            if user.get("phone_number"):
                is_profile_updated = True
            
            is_exist = True

            if user.get("is_blocked"):
                raise HTTPException(status_code=403, detail="User is blocked")
        else:

            if real_email:
                user = await crud.get_user_by_email(real_email)
            if not user and private_email:
                user = await crud.get_user_by_private_email(private_email)

  

        if not user:

            package = await get_package_by_name("Default")

            user_data = {
                "apple_id": apple_id,
                "email": real_email or private_email,
                "private_email": private_email,
                "is_private_email": is_private,

                "password":"s211120039346070083d",
                "name": name,
                "signup_method": "oauth",
                "country_code": None,
                "mobile_code": None,
                "phone_number": None,

                "is_verified": True,
                "is_active": True,
                "is_blocked": False,
                "is_auth": True,

                "fcm_token": payload.fcm_token,
                "platform": payload.platform,
                "category": None,
                "remaining_books": package["book_count"],
                "subscription_type": package["package_name"],
                "subscription": {
                    "package_id": package["_id"],
                    "package_name": package["package_name"],
                    "price": package["price"],
                    "activated_at": now_utc(),
                    "expires_at": None,
                    "status": None,
                    "is_active": package["is_active"]
                },

                "schedule_call_time": "21:00",
                "schedule_dairy_time": "21:00",
                "num_journals": 0,
                "num_books": 0,

                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            user = await crud.create_user(user_data)



        if user.get("is_blocked"):
            raise HTTPException(status_code=403, detail="User is blocked")
        


        access_token = await create_access_token({"sub": str(user["_id"])})
        await crud.update_user(
                str(user["_id"]),
                { 
                    "is_auth": True,
                    "fcm_token": payload.fcm_token,
                    "platform": payload.platform,
                    "updated_at": datetime.utcnow()
                }
            )


        request.session["user_id"] = str(user["_id"])

        display_email = real_email or private_email

        return {
            "user_id": str(user["_id"]),
            "user_name": user.get("name"),
            "email": display_email,
            "access_token": access_token,
            "is_auth": True,
            "is_active": True,
            "is_private_email": user.get("is_private_email", False),
            "is_exist": is_exist,
            "is_profile_updated": is_profile_updated
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Apple Sign-in Error:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
