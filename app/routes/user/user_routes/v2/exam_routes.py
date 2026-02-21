import json
import uuid
from fastapi import APIRouter
from fastapi import BackgroundTasks
from uuid import uuid4
from datetime import datetime
from bson import ObjectId
import logging

from app.agents.v2.langgraph.exam_generator_graph import graph as exam_generation_graph
from app.agents.v1.langgraph.exam_generation_graph import generate_long_questions_graph
from app.tasks.evaluation_tasks import evaluate_long_exam
from app.config.database import exams_collection, exam_results_collection
from app.schemas.exam_schema import ExamCreate, EvaluateExamRequest
from app.utils.generate_ai_response import generate_ai_suggestions
from app.helpers.helpers import serialize_doc

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/exam")

@router.post("/generate", summary="Exam generation API",   description="Queues exam generation and returns Celery task ID",operation_id="generate_exam_api")
async def generate_exam(payload: ExamCreate):
    input_data = {
        "exam_name": "Placement Test 1",
        "subject": "Computer Science",
        "themes": [
            {"theme": "HR", "type": "mcq", "difficulty": "easy", "count": 1},
            {"theme": "Aptitude", "type": "mcq", "difficulty": "easy", "count": 1},
            {"theme": "Coding", "type": "long", "difficulty": "easy", "count": 1},
        ],
    }
    payload = {
        "exam_name": input_data["exam_name"],
        "subject": input_data["subject"],
        "themes": input_data["themes"],
    }
    result = await exam_generation_graph.ainvoke(payload)
    exam_doc = result["result"]

    if isinstance(exam_doc, str):
        exam_doc = json.loads(exam_doc)
    return { "status": True, "message": "Exam questions are ready.", "data": { "examId":exam_doc["_id"], "Exam infromation": exam_doc} }

@router.post("/generate_long", summary="Exam generation API",   description="Queues exam generation and returns Celery task ID",operation_id="generate_long_exam_api")
async def generate_long_exam(payload: ExamCreate):
    questions = []
    answer_key = {}
    result = await generate_long_questions_graph.ainvoke(payload)
    data = result["data"]
    tokens_count = result["tokens_count"]
    if isinstance(data, str):
        data = json.loads(data)
    for set in data:
        qid = str(uuid.uuid4())
        set["qid"] = qid
        answer_key[qid] = set["answer"]
        questions.append({
            "qid": qid,
            "question": set["question"]
        })
    exam_doc = {
        "subject": payload.subject,
        "difficulty": payload.difficulty,
        "questions": questions,
        "answer_key": answer_key,
        "token_count": tokens_count,
        "questions_type": "long", 
        "created_at": datetime.utcnow()
    }
    exam_docs = await exams_collection.insert_one(exam_doc)
    return { "status": True, "message": "Exam questions are ready.", "data": { "examId": str(exam_docs.inserted_id), "questions": questions}, "tokens_count": tokens_count}

@router.post("/evaluate", summary="Exam evaluation API")
async def evaluate_exam(payload:EvaluateExamRequest, background_tasks: BackgroundTasks):
    examId = payload.examId
    student_answers = {item.qId : item.answer for item in payload.responses}
    exam_doc = await exams_collection.find_one( {"_id": ObjectId(examId)}, {"questions":1, "answer_key": 1})
    answer_sheet_key = exam_doc.get("answer_key") if exam_doc else None
    questions = exam_doc.get("questions") if exam_doc else None
    exam_evaluation = []
    total_questions = len(answer_sheet_key)
    attempted = sum(1 for ans in student_answers.values() if str(ans).strip()  not in (None, "N/A", "", "-"))
    correct_answer_count = 0
    unattempted = total_questions - attempted
    suggestion_needed = []

    for index, (qid, correct_answer) in enumerate(answer_sheet_key.items(), start = 0):
        student_answer = student_answers.get(qid)
        if student_answer is None:
            message  = "Not answered"
            meta_data = questions[index]
            question = meta_data.get("question")
            suggestion_needed.append([qid, question, correct_answer])
        elif student_answer == correct_answer:
            correct_answer_count += 1
            message  = "Correct"
        else:
            message = "Incorrect"
            meta_data = questions[index]
            question = meta_data.get("question")
            suggestion_needed.append([qid, question, correct_answer])
        exam_evaluation.append({
            "question":qid,
            "isCorrect": str(student_answer) == str(correct_answer),
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "message": message
        })
    accuracy = correct_answer_count/total_questions
    background_tasks.add_task( generate_ai_suggestions, examId, suggestion_needed)   
    result = {
        "examId": examId,
        "total_question": total_questions, 
        "attempted": attempted, 
        "unattempted": unattempted,
        "accuracy": accuracy,
        "score": correct_answer_count,
        "evaluation": exam_evaluation
    }
    await exam_results_collection.insert_one(result)
    return { "status": True, "message": "Exam Evaluation successful", "data": serialize_doc(result)}

@router.post("/evaluate-long", summary="Exam evaluation API")
async def evaluate_exam(payload:EvaluateExamRequest):
    examId = payload.examId
    student_answers = {item.qId : item.answer for item in payload.responses}
    exam_doc = await exams_collection.find_one( {"_id": ObjectId(examId), "questions_type": "long"}, {"questions":1, "answer_key": 1})
    answer_sheet_key = exam_doc.get("answer_key") if exam_doc else None
    questions = exam_doc.get("questions") if exam_doc else None

    
    total_questions = len(answer_sheet_key)
    attempted = sum(1 for ans in student_answers.values() if str(ans).strip()  not in (None, "N/A", "", "-"))
    unattempted = total_questions - attempted

    result = {
        "examId": examId,
        "total_questions": total_questions, 
        "attempted": attempted, 
        "unattempted": unattempted,
        "accuracy": None,
        "score": None,
        "status": "processing"
    }
    await exam_results_collection.insert_one(result)

    payload = {
        "examId": examId,
        "questions": questions,
        "answer_sheet_key": answer_sheet_key,
        "student_answers": student_answers
    }
    evaluation_task = evaluate_long_exam.apply_async(args=[payload], countdown=60)
    data = {
        "result": result,
        "evaluation_task_id": evaluation_task.id
    }
    return { "status": True, "message": "Exam Evaluation successful", "data": data }

   
