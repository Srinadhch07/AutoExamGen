from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import asyncio

from app.utils.response_handler import ( global_exception_handler, http_exception_handler, validation_exception_handler)
from app.routes.user.user_routes.v1.routes import router as pdf_router
# from app.routes.user.user_routes.v2.exam_routes import router as exam_router
from app.config.database import check_connection
from app.config.logging import init_logging_system
# from app.transformers.v1 import embeddings

init_logging_system()

app = FastAPI( title="AI Agent", version="1.0.0", docs_url="/docs", redoc_url="/redoc", Debug=False)

app.add_middleware( CORSMiddleware, allow_origins=["*"],  allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router( pdf_router, prefix="/api", tags=["PDF"])
# app.include_router( exam_router, prefix="/api", tags=["Exam APIs"])

@app.on_event("startup")
async def startup_event():
    await check_connection()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/meta/favicon.ico")

@app.get("/")
async def home():
    return RedirectResponse(url="/docs")
