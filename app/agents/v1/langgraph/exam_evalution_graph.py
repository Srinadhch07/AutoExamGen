from typing import TypedDict, Dict
from langgraph.graph import StateGraph, END

from app.agents.v1.langchain.evaluation_chain import evaluation_chain


class EvalState(TypedDict):
    responses: Dict
    answer_key: Dict
    result: Dict


def evaluate_exam(state: EvalState):
    result = evaluation_chain.invoke({
        "responses": state["responses"],
        "answer_key": state["answer_key"]
    })
    state["result"] = result
    return state


builder = StateGraph(EvalState)
builder.add_node("evaluate_exam", evaluate_exam)
builder.set_entry_point("evaluate_exam")
builder.add_edge("evaluate_exam", END)

exam_evaluation_graph = builder.compile()