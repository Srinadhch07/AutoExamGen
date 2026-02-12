from fastapi import APIRouter, HTTPException
from app.tasks.pdf_tasks import generate_pdf_task
from celery.result import AsyncResult
from app.config.celery_app import celery
from app.schemas.pdf_schema import PDFGenerate
router = APIRouter()

@router.post("/generate-pdf", status_code=202)
async def generate_pdf_api(payload: PDFGenerate):
    print("TASK FILE CELERY:", celery.conf.broker_url)
    if not payload or not payload.name:
        raise HTTPException(400, "Missing required details")
    task = generate_pdf_task.apply_async(args=[payload.dict()], countdown=60)
    return { "status": True, "message": "PDF generation queued", "data": { "task_id": task.id}}

@router.get("/task-status/{task_id}")
def task_status(task_id: str):
    result = AsyncResult(task_id, app=celery)
    return {
        "task_id": task_id,
        "state": result.state,
        "result": result.result if result.successful() else None
    }