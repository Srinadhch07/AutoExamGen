from groq import Groq
import json
import os
from dotenv import load_dotenv
import logging
 
from app.agents.v2.prompts.ats_analyzer_prompts import SYSTEM_PROMPT
from app.agents.v2.prompts.resume_prompts import SYSTEM_PROMPT as RESUME_SYSTEM_PROMPT
from app.schemas.v2.resume_schema import ResumeSchema
from app.helpers.helpers import safe_json_loads

load_dotenv()
logger = logging.getLogger(__name__)

client = Groq()

def build_prompt(model_answer, student_answer):
    return f"""
You are a strict automated grading system.

Compare the student answer with the model answer carefully.

Scoring rules:
- 1 = logically correct and matches model answer
- 0 = incorrect or missing key concepts

Return ONLY valid JSON in this exact format:
{{"score": 0, "feedback": "short explanation"}}

Model Answer:
{model_answer}

Student Answer:
{student_answer}
"""

async def evaluate_answer(model_answer, student_answer):
    prompt = build_prompt(model_answer, student_answer)

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a strict exam evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_completion_tokens=500,
        top_p=1
    )
    response_text = completion.choices[0].message.content.strip()
    try:
        result = json.loads(response_text)
        return result
    except Exception:
        return {
            "score": 0,
            "feedback": "Invalid response format from model"
        }

async def ats_evaluator(USER_PROMPT):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ],
        temperature=0.2,
        max_completion_tokens=2000,
    )
    response = completion.choices[0].message.content.strip()
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError as e:
        logger.error("ATS evaluation JSON error: %s", e)
        logger.error("RAW RESPONSE:\n%s", response)

        return {
            "status": "error",
            "error_type": "INVALID_JSON",
            "message": "Model returned malformed JSON",
            "error": str(e),
            "raw_preview": response[:500]
        }

async def resume_generator(USER_PROMPT, original_data=None):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages = [
           {"role": "system", "content": RESUME_SYSTEM_PROMPT},
           {"role": "user", "content": USER_PROMPT}
        ],
        temperature = 0.2,
        max_completion_tokens=2000,
    )
    response = None
    try:
        response = completion.choices[0].message.content.strip()
        if not response:
            raise ValueError("AI response is empty")
        result = safe_json_loads(response)
        validated = ResumeSchema(**result)
        return validated, True
    except Exception as e:
        logger.error("Resume Generation is failed: %s",e)
        logger.error("RAW RESPONSE:\n%s", response)
        if original_data:
            logger.warning("Using Original data as fallback")
            return ResumeSchema(**original_data), False
        else:
            raise ValueError("AI Generation failed and No fallback is availabale")

