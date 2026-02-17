import ollama as om
import asyncio
import json
from langchain_core.runnables import RunnableLambda

from app.agents.v1.prompts.prompts import QUESTION_PROMPT, GENERATOR_SYSTEM_PROMPT, LONG_ANSWER_PROMPT, LONG_ANSWER_SYSTEM_PROMPT
from app.services.token_counter import token_count

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
    tokens_count = {
        "input_tokens": token_count([QUESTION_PROMPT, GENERATOR_SYSTEM_PROMPT] ),
        "output_tokens": token_count(list(str(data))) 
    }
    return collected, tokens_count

async def generate_long(inputs = None):
    collected = []
    total = inputs["num_questions"] 
    while len(collected) < total:
        need = total - len(collected)

        response = await om.AsyncClient().chat(
            model="qwen2.5:3b-instruct",
            messages=[
                {"role": "system", "content": LONG_ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": LONG_ANSWER_PROMPT.format(
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
    tokens_count = {
        "input_tokens": token_count([LONG_ANSWER_SYSTEM_PROMPT, LONG_ANSWER_PROMPT] ),
        "output_tokens": token_count(list(str(data))) 
    }
    return collected, tokens_count

async def ollama(messages):
    response = await om.AsyncClient().chat(
        model="qwen2.5:3b-instruct",
        messages=messages,
        format="json",
        stream=False,
        options={
            "temperature": 0.2,
            "num_predict": 1024
        }
    )
    return response["message"]["content"]

ollama_runnable = RunnableLambda(
    lambda x: ollama(x.to_messages())
)