from celery import states
from app.config.celery_app import celery
import asyncio
from app.agents.v1.langgraph.exam_evalution_graph import graph
from app.config.database import exam_results_collection

@celery.task( bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3}, name="app.tasks.evaluation_tasks.evaluate_long_exam")
def evaluate_long_exam(self, payload: dict):

    self.update_state(state=states.STARTED)
    examId = payload.get("examId")
    questions = payload.get("questions")
    answer_sheet_key = payload.get("answer_sheet_key")
    student_answers = payload.get("student_answers")

    for index, (qid, actual_answer) in enumerate(answer_sheet_key.items(), start = 0):
        student_answer = student_answers.get(qid)
        meta_data = questions[index]
        question = meta_data.get("question")
        payload = { "examId": examId,"question": question,"actual_answer": actual_answer, "student_answer": student_answer}
        asyncio.run(graph.ainvoke(payload))
        asyncio.run( exam_results_collection.update_one( {"examId": examId}, {"$set": {"status": "completed"}})
    ) 
    return {"examId": examId, "status": "completed"}