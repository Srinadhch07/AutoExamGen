from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from app.agents.v1.langchain.question_generator_chain import question_chain, long_question_chain


class ExamState(TypedDict):
    subject: str
    difficulty: str
    num_questions: int
    questions: List[Dict]
    tokens_count: int

class LongExamState(TypedDict):
    subject: str
    difficulty: str
    num_questions: str
    data: List[Dict]
    tokens_count: int

async def generate_questions(state: ExamState):
    result, tokens_count = await question_chain.ainvoke({
        "subject": state["subject"],
        "difficulty": state["difficulty"],
        "num_questions": state["num_questions"]
    })
    state["questions"] = result
    state["tokens_count"] = tokens_count
    return state

async  def generate_long_questions(state: LongExamState):
    result, tokens_count = await long_question_chain.ainvoke({
        "subject": state["subject"],
        "difficulty": state["difficulty"],
        "num_questions": state["num_questions"]
    })
    state["data"] = result
    state["tokens_count"] = tokens_count
    return state

builder = StateGraph(ExamState)
builder.add_node("generate_questions", generate_questions)
builder.set_entry_point("generate_questions")
builder.add_edge("generate_questions", END)

long_question_builder = StateGraph(LongExamState)
long_question_builder.add_node("generate_long_questions", generate_long_questions)
long_question_builder.set_entry_point("generate_long_questions")
long_question_builder.add_edge("generate_long_questions", END)

exam_generation_graph = builder.compile()
generate_long_questions_graph = long_question_builder.compile()