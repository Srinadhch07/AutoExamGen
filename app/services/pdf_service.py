from fastapi import HTTPException
import fitz
import logging
import asyncio

from app.llm_models.v2.groq_client import ats_evaluator
from app.agents.v2.prompts.ats_analyzer_prompts import USER_PROMPT
from app.config.database import sync_resume_evaluations_collection

logger = logging.getLogger(__name__)

def generate_pdf_logic(payload):
    if not payload and not payload.get("name"):
        raise HTTPException(404,"Missing required details")
    return "https://www.google.com"

def analyse_pdf(payload):
    logger.info("Started analysing the text")
    if not payload and not payload.get("path"):
        raise HTTPException(404,"Missing required details")
    path = payload.get("path")
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    final_prompt = USER_PROMPT.format(resume_text=text)
    result = asyncio.run(ats_evaluator(final_prompt))

    # TODO:  Fetch the user details
    result["userId"] = "0987654321"
    result_details = sync_resume_evaluations_collection.insert_one(result)
    result["_id"] = str(result_details.inserted_id)
    logger.info("Analyzation completed.")
    return result

    