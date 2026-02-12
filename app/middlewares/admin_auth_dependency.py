from fastapi import  RE, HTTPException
from app.database.admin_auth_crud import get_admin_by_id

from app.auth.jwt_handler import verify_token, admin_verify_token


async def get_current_admin(request: Request):
    auth_header = request.headers.get("Authorization")
    print(f'[Get Current Admin]: {auth_header}')
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth_header.split(" ")[1]
    token = token.strip().replace('"', '')
    try:
        payload = await admin_verify_token(token)
        admin_id = payload.get("sub")
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        admin = await get_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=401, detail="admin not found")
        # if not admin.get("is_active", False):
        #     raise HTTPException(status_code=401, detail="admin is blocked")
        if not admin.get("is_auth", False):
            raise HTTPException(status_code=401, detail="admin is not logged in")
        request.state.admin = admin
        return admin
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")