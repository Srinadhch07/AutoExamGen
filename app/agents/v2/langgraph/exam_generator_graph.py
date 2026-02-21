from typing import TypedDict
from datetime import datetime, UTC
import logging
from langgraph.graph import StateGraph, END
import asyncio
from app.config.database import exams_collection
from app.agents.v2.langchain.exam_generator_chain import chain
import uuid

logger = logging.getLogger(__name__)

class ExamState(TypedDict):
    exam_name: str
    subject: str
    themes: list
    sections_block: str
    generated_exam: dict
    result: None 

def build_sections_block(themes):
    block = ""
    for i, t in enumerate(themes, 1):
        block += f"""
Section {i}:
Theme: {t['theme']}
Type: {t['type']}
Difficulty: {t['difficulty']}
Number of Questions: {t['count']}
"""
    return block

# Nodes
async def build_prompt_node(state: ExamState):
    state["sections_block"] = build_sections_block(state["themes"])
    logger.debug(f"Node-1: Section-block: {state["sections_block"]}")
    return state

async def generate_exam_node(state: ExamState):
    logger.debug(f"Node-2: Invoking Generator chain.")
    result = chain.invoke({
        "exam_name": state["exam_name"],
        "subject": state["subject"],
        "sections_block": state["sections_block"],
    })
    result = result.model_dump()
    for section in result.get("sections"):
        for question in section.get("questions", []):
            question["qid"] = str(uuid.uuid4())
    state["generated_exam"] = result
    logger.debug(f'Node-2: Generation successful. Generated exam : {state["generated_exam"]}')
    return state

async def store_exam_node(state: ExamState):
    logger.debug('Node-3: Initialized')

    state["generated_exam"]["created_at"] = datetime.now(UTC)

    insert_result = await exams_collection.insert_one(
        state["generated_exam"]
    )
    state["generated_exam"]["_id"] = str(insert_result.inserted_id)

    state["result"] = state["generated_exam"]

    logger.debug('Node-3: Database updated')

    return state

builder = StateGraph(ExamState)

# Langgraph
builder.add_node("build_prompt", build_prompt_node)
builder.add_node("generate_exam", generate_exam_node)
builder.add_node("store_exam", store_exam_node)

builder.set_entry_point("build_prompt")

builder.add_edge("build_prompt", "generate_exam")
builder.add_edge("generate_exam", "store_exam")
builder.add_edge("store_exam", END)

graph = builder.compile()

async def main():
    input_data = {
        "exam_name": "Placement Test 1",
        "subject": "Computer Science",
        "themes": [
            {"theme": "HR", "type": "mcq", "difficulty": "easy", "count": 1},
            {"theme": "Aptitude", "type": "mcq", "difficulty": "easy", "count": 1},
            {"theme": "Coding", "type": "long", "difficulty": "easy", "count": 1},
        ],
    }
    initial_state = {
        "exam_name": input_data["exam_name"],
        "subject": input_data["subject"],
        "themes": input_data["themes"],
    }

    final_state = await graph.ainvoke(initial_state)
    logging.debug("Exam generated and stored successfully.")

# if __name__ == "__main__":
#     asyncio.run(main())