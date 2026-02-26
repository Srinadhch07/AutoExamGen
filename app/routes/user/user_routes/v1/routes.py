from fastapi import APIRouter, HTTPException, UploadFile, File, Form, HTTPException
from app.tasks.pdf_tasks import generate_pdf_task, analyse_pdf_task
from celery.result import AsyncResult
from app.config.celery_app import celery
from app.schemas.v2.resume_schema import ResumeSchema
import os
import uuid
import shutil
router = APIRouter()
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/resume/analyze",status_code=202)
async def analyse_doc(userId: str = Form(...), file: UploadFile = File(...)):
    if userId is None:
        raise HTTPException(status_code = 400, detail="Missing required details.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code = 400, detail="Only PDFs are allowed")
    
    file_id = f'{uuid.uuid4()}_{file.filename}'
    file_path = os.path.join(UPLOAD_DIR, file_id)
    payload = {"path": file_path}

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.debug("Pdf task started")
    task = analyse_pdf_task.apply_async(args=[payload], countdown=10)
    logger.debug("Pdf Task finished")
    return { "status": True, "message": "PDF Uploaded", "data": { "task_id": task.id, "status":"processing" }}

@router.post("/resume/generate", status_code=202)
async def generate_pdf_api(payload: ResumeSchema):
    task = generate_pdf_task.apply_async(args=[payload.model_dump(mode="json")], countdown=0)   
    return { "status": True, "message": "PDF generation queued", "data": { "task_id": task.id}}

@router.get("/task-status/{task_id}")
def task_status(task_id: str):
    result = AsyncResult(task_id, app=celery)
    return {
        "status": True, "message": "Task details", "data" : { "task_id": task_id, "state": result.state, "result": result.result if result.successful() else None
        }
    }






