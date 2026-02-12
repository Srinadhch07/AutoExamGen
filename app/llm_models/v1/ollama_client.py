import ollama as om
import asyncio
import json

from app.agents.v1.prompts.prompts import QUESTION_PROMPT, GENERATOR_SYSTEM_PROMPT

context = []
async def generate(inputs):
    collected = []
    total = inputs["num_questions"]
    while len(collected) < total:
        need = total - len(collected)

        response = await om.AsyncClient().chat(
            model="qwen2.5:3b-instruct",
            messages=[
                {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": QUESTION_PROMPT.format(
                    num_questions=need,
                    subject=inputs["subject"],
                    difficulty=inputs["difficulty"]
                )}
            ],
            format="json",
            stream=False,
            options={
                "temperature": 0.3,
                "num_predict": 2048
            }
        )

        data = json.loads(response["message"]["content"])
        if isinstance(data, dict):
            data = [data]

        collected.extend(data[:need])
    return collected