from typing import TypedDict, Dict
from langgraph.graph import StateGraph, END

from app.agents.v1.langchain.evaluation_chain import evaluation_chain
from app.config.database import exam_results_collection

class LongEvalState(TypedDict):
    examId: str
    qid:str
    question: str
    actual_answer: str
    student_answer: str
    result = Dict

async def evaluate_long_exam(state: LongEvalState):
    result = await evaluation_chain.ainvoke({
        "question": state["question"],
        "actual_answer": state["actual_answer"],
        "student_answer": state["student_answer"]
    })
    state["result"] = result # evaluation details will appear here 
    return state
async def update_db(state: LongEvalState):
    result = state["result"]
    await exam_results_collection.update_one(
        {
            "examId": state["examId"]
        },
        {
           "$push": {
                "evaluation": {
                    "qid": state["qid"],
                    "question": state["question"],
                    "isCorrect": result["isCorrect"],
                    "student_answer": state["student_answer"],
                    "actual_answer": state["actual_answer"],
                    "accuracy": result["accuracy"],
                    "message": result["message"]
                }
            }
        }
    )

    return state


builder = StateGraph(LongEvalState)

builder.add_node("evaluate_long_exam", evaluate_long_exam)
builder.add_node("update_db", update_db)

builder.set_entry_point("evaluate_long_exam")

builder.add_edge("evaluate_long_exam", "update_db")
builder.add_edge("update_db", END)

graph = builder.compile()