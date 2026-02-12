from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import os
import traceback

logger = logging.getLogger("app")

DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"

async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.extract_tb(exc.__traceback__)
    last = tb[-1] if tb else None
    location = f"{last.filename}:{last.lineno}" if last else "unknown"

    logger.error(f"{type(exc).__name__} at {location} : {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(exc) if DEBUG else "Internal server error",
            "error_location": location if DEBUG else None,
            "data": None
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": exc.errors(),
            "data": None
        }
    )