from celery import states
from app.config.celery_app import celery
from app.services.pdf_service import optimize_resume, analyse_pdf, generate_pdf
import logging

logger = logging.getLogger(__name__)

@celery.task(bind=True, autoretry_for = (Exception,), retry_backoff=10, retry_kwargs= {"max_retries":3}, name="app.tasks.pdf_tasks.analyse_pdf_task")
def analyse_pdf_task(self,payload:dict):
    self.update_state(state =states.STARTED)
    logger.debug("Analyser started")
    analyzed_text = analyse_pdf(payload)
    logger.debug("Analyser stopped")
    return analyzed_text


@celery.task( bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3}, name="app.tasks.pdf_tasks.generate_pdf_task")
def generate_pdf_task(self, payload: dict):
    self.update_state(state=states.STARTED)
    logger.debug("AI generation is started.")
    optimized_resume = optimize_resume(payload)
    logger.debug("PDF generation is started.")
    pdf_path = generate_pdf(optimized_resume)
    logger.debug("PDF generation is successful.")
    return {"pdf_url": pdf_path}