from fastapi import Request, HTTPException, Depends
from app.auth.jwt_handler import verify_token
from app.database.crud import get_user_by_id
from app.helpers.package_checker import check_and_apply_default_package

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    # print(f"Entered into middleware\nauth header :{auth_header}")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth_header.split(" ")[1]
    token = token.strip().replace('"', '')
    try:
        payload = await verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.get("is_blocked", False):
            raise HTTPException(status_code=403, detail="User is blocked")
        if not user.get("is_auth", False):
            raise HTTPException(status_code=401, detail="User is not logged in")
        await check_and_apply_default_package(user)
        request.state.user = user
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")