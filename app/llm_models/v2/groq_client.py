from groq import Groq
import json

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
        temperature=0.2,   # IMPORTANT: low but not zero
        max_completion_tokens=500,
        top_p=1
    )

    response_text = completion.choices[0].message.content.strip()

    print("RAW LLM OUTPUT:", response_text)  # Debug

    try:
        result = json.loads(response_text)
        return result
    except Exception:
        return {
            "score": 0,
            "feedback": "Invalid response format from model"
        }