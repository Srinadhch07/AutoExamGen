from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.jwt_handler import verify_token
from app.database.crud import get_user_by_id


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api"):
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Authorization header missing"}, status_code=401)

        token = auth_header.split(" ")[1]
        try:
            payload = await verify_token(token)
            user_id = payload.get("sub")    
            
            if not user_id:
                return JSONResponse({"detail": "Invalid token payload"}, status_code=401)

            user = await get_user_by_id(user_id)
            if not user:
                return JSONResponse({"detail": "User not found"}, status_code=401)
            
            request.state.user = user

        except Exception as e:
            print(e)
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        return await call_next(request)