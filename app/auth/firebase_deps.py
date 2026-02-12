import os, json
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, auth as fb_auth
from fastapi import Header, HTTPException

def _init():
    if firebase_admin._apps:
        return
    cred_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
    elif cred_path:
        cred = credentials.Certificate(cred_path)
    else:
        raise RuntimeError("Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS")
    firebase_admin.initialize_app(cred, {"projectId": project_id})
_init()

def firebase_claims(authorization: str = Header(..., convert_underscores=False)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    id_token = authorization.split(" ", 1)[1].strip()
    try:
        return fb_auth.verify_id_token(id_token, check_revoked=True)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase ID token")
