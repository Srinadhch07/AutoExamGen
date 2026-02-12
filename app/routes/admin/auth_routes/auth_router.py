from fastapi import APIRouter, HTTPException,Request, Response, Depends
from app.schemas import schemas
from app.database import admin_auth_crud
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
from app.helpers.helpers import serialize_doc
from app.middlewares.admin_auth_dependency import get_current_admin
from app.services.s3_service import upload_file_to_s3
from fastapi import File, UploadFile, Form


router = APIRouter()
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

@router.post("/register")
async def register(payload: dict, request: Request):
    try:

        admin_data = {"email": payload["email"], "password": payload["password"]}
        await admin_auth_crud.create_admin(admin_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal error in register(): {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
async def login(payload: schemas.AdminLoginRequest, request: Request):
    try:
        
        admin = await admin_auth_crud.get_admin_by_email(payload.email)
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid email")
        
        if not await admin_auth_crud.verify_admin(payload.password, admin["password"]):
            raise HTTPException(status_code=401, detail="Invalid password")

        token = await create_access_token({"sub": str(admin["_id"])})

        admin = await admin_auth_crud.update_admin(str(admin["_id"]), {"is_auth":True})
        request.session["admin_id"] = str(admin["_id"])

        return {
        "data": {
        "admin_id": str(admin["_id"]),
        "admin_name": admin.get("name"),
        "email": admin.get("email"),
        "access_token": token,
        "is_auth": admin.get("is_auth")
        }

    }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error at login(): {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/update")
async def update_admin(
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    update_password: str = Form(None),
    image_path: UploadFile = File(None),
    admin = Depends(get_current_admin)
):
    try:
        admin_id = str(admin["_id"])

        payload = {}

        if name:
            payload["full_name"] = name
        if email:
            payload["email"] = email
        if phone:
            payload["phone_number"] = phone

        if update_password:
            if not basic_validators.is_strong_password(update_password):
                raise HTTPException(400, "Invalid password format")

            hashed_pass = await admin_auth_crud.hash_password(update_password)
            payload["password"] = hashed_pass

        if image_path:
            file_bytes = await image_path.read()
            filename = image_path.filename
            content_type = image_path.content_type

            image_url = upload_file_to_s3(
                file_bytes=file_bytes,
                filename=filename,
                folder="profile_images",
                content_type=content_type
            )

            payload["image_path"] = image_url

        updated_admin = await admin_auth_crud.update_admin_profile(admin_id, payload)

        return {
            "status": True,
            "message": "Admin updated successfully",
            "data": serialize_doc(updated_admin),
        }

    except Exception as e:
        print("Internal server error:", e)
        raise HTTPException(500, "Internal Server Error")
    
@router.get("/get-profile")
async def get_admin(request: Request, admin= Depends(get_current_admin)):
    try:
        admin_id = str(admin["_id"])
        if not admin_id:
            raise HTTPException(status_code=401, detail="Admin not logged in")
                
        admin_details = await admin_auth_crud.get_admin_by_id(admin_id)
        
        return {
            "admin_details": admin_details
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/forgot-password/sendotp")
async def sendotp(payload: dict, request: Request):
    try:

        if payload["email"] and not basic_validators.is_valid_email(payload["email"]):
            raise HTTPException(status_code=400, detail="Invalid email format.")
            
        existing_admin = await admin_auth_crud.get_admin_by_email(payload["email"])        
        if not existing_admin:
            raise HTTPException(status_code=404, detail="No adminr found.")
        
        otp = helpers.generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        existing_admin = await  admin_auth_crud.update_admin(existing_admin["_id"],{"otp":otp,"otp_expiry":otp_expiry})
        mail_sent = await send_mail.send_forgot_otp(serialize_doc(existing_admin), existing_admin["otp"])

        if mail_sent:
            return {
                "message": "OTP sent successfully",
                "existing_admin_id": str(existing_admin["_id"]),
                "email": existing_admin["email"]
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
        admin = await admin_auth_crud.get_admin_by_email(email)   
        if not admin: 
            raise HTTPException(status_code = 404, detail="No admin found")
        otp = payload.get("otp")

        if not otp:
            raise HTTPException(status_code=404, detail="OTP not found.")
        
        if datetime.utcnow() > admin["otp_expiry"]:
            return {"message": "OTP expired"}
        if otp == admin["otp"]:
            request.session['email_for_password'] = admin['email']
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

        existing_admin = await admin_auth_crud.get_admin_by_email(email)

        if not existing_admin:
            raise HTTPException(status_code=404, detail="No admin found.")

        if not basic_validators.is_strong_password(payload["password"]):
            raise HTTPException(status_code=400,detail="Invalid password format. Must be 8-128 chars, include uppercase, lowercase, number, and a special character."
            )
        hashed_pass = await admin_auth_crud.hash_password(payload["password"])
        updated_admin = await admin_auth_crud.update_admin(existing_admin["_id"],{"password": hashed_pass})

        if updated_admin:
            return {
                "message": "Password updated successfully.",
                "existing_admin_id": str(updated_admin["_id"]),
                "email": updated_admin["email"]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update the passoword. Please try again.")

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/logout")
async def logout(request: Request, admin=Depends(get_current_admin)):
    try:
        admin_id = str(admin["_id"])

        updated_admin = await admin_auth_crud.update_admin(admin_id, {"is_auth": False})

        request.session.clear()
        return {"message": "Admin logged out successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
