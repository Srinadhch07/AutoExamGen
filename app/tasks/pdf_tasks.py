from celery import states
from app.config.celery_app import celery
from app.services.pdf_service import generate_pdf_logic

@celery.task( bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3}, name="app.tasks.pdf_tasks.generate_pdf_task")
def generate_pdf_task(self, payload: dict):
    self.update_state(state=states.STARTED)
    pdf_url = generate_pdf_logic(payload)
    return pdf_url