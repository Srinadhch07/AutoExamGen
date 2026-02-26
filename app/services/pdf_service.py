from fastapi import HTTPException
import fitz
import logging
import asyncio
import os
from uuid import uuid4
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.llm_models.v2.groq_client import ats_evaluator, resume_generator
from app.agents.v2.prompts.ats_analyzer_prompts import USER_PROMPT
from app.agents.v2.prompts.resume_prompts import USER_PROMPT as RESUME_USER_PROMPT
from app.config.database import sync_resume_evaluations_collection
from app.helpers.helpers import generate_safe_filename

logger = logging.getLogger(__name__)
env = Environment(loader=FileSystemLoader("app/templates"))

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

    # TODO: c10 - Fetch the user details
    result["userId"] = "0987654321"
    result_details = sync_resume_evaluations_collection.insert_one(result)
    result["_id"] = str(result_details.inserted_id)
    logger.info("Analyzation completed.")
    return result

def optimize_resume(payload: dict):
    final_prompt = RESUME_USER_PROMPT.format(resume_json=payload)
    response, credit_deduct = asyncio.run(resume_generator(final_prompt,payload))
    if credit_deduct:
        # TODO: c10 - update the credits in subscription
        pass
    return response

def generate_pdf(details: dict):
    template = env.get_template("maang_resume.html")
    html_content = template.render(resume = details)
    os.makedirs("generated", exist_ok=True)
    # Todo: c30 - update to cloud upload
    pdf_file_path = f"generated/{generate_safe_filename(details.personal_info.full_name)}.pdf"
    HTML(string=html_content).write_pdf(pdf_file_path)
    return pdf_file_path 

    