from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from app.agents.v1.langchain.question_generator_chain import question_chain


class ExamState(TypedDict):
    subject: str
    difficulty: str
    num_questions: int
    questions: List[Dict]


async def generate_questions(state: ExamState):
    result = await question_chain.ainvoke({
        "subject": state["subject"],
        "difficulty": state["difficulty"],
        "num_questions": state["num_questions"]
    })
    state["questions"] = result
    return state


builder = StateGraph(ExamState)
builder.add_node("generate_questions", generate_questions)
builder.set_entry_point("generate_questions")
builder.add_edge("generate_questions", END)

exam_generation_graph = builder.compile()