import json
import uuid
from fastapi import APIRouter, HTTPException
from fastapi import BackgroundTasks
from uuid import uuid4
from datetime import datetime
from bson import ObjectId
import logging

from app.agents.v2.langgraph.exam_generator_graph import graph as exam_generation_graph
from app.agents.v1.langgraph.exam_generation_graph import generate_long_questions_graph
from app.tasks.evaluation_tasks import evaluate_long_exam
from app.config.database import exams_collection, exam_results_collection
from app.schemas.v2.exam_schema import ExamCreate, EvaluateExamRequest, GradeOutput
from app.utils.generate_ai_response import generate_ai_suggestions
from app.helpers.helpers import serialize_doc
from app.transformers.v1.embeddings import get_embedding, cosine_similarity
from app.agents.v2.langchain.exam_grading_chain import  grader_llm
from app.llm_models.v2.groq_client import evaluate_answer

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

@router.post("/evalaute-exam", summary="Exam Evaluation API")
async def evaluate_exam(payload:EvaluateExamRequest,  background_tasks: BackgroundTasks):
    examId = payload.examId
    student_answers = {item.qId : item.answer for item in payload.responses}
    exam = await exams_collection.find_one({"_id": ObjectId(examId)})
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    all_questions = {}
    for section in exam["sections"]:
        for question in section["questions"]:
            all_questions[question["qid"]] = {
                "type": section["type"],
                "question": question.get("question"),
                "correct_answer": question.get("correct_answer"),
                "model_answer": question.get("answer"),
                "theme": section["theme"]
            }
    # Metrics
    score = 0
    exam_evaluation = []
    total_questions = len(all_questions)
    attempted = sum(1 for ans in student_answers.values() if str(ans).strip()  not in (None, "N/A", "", "-"))
    unattempted = total_questions - attempted
    suggestion_needed = {}
    HIGH_THRESHOLD = 0.85
    LOW_THRESHOLD = 0.40
    
    # Evalution
    for qid, student_answer in student_answers.items():
        question = all_questions.get(qid)
        if not question:
            continue
        if question["type"] == "mcq":
            is_correct =  student_answer == question["correct_answer"]
            if is_correct:
                message = "correct"
                score +=1
            else:
                message = "incorrect"
                suggestion_needed[qid] = {
                    "question": question.get("question"),
                    "student_answer": student_answer,
                    "correct_answer": question["correct_answer"]
                }
            exam_evaluation.append({
                    "qid": qid,
                    "message": message,
                    "student_answer": student_answer,
                    "correct_answer": question["correct_answer"],
                    "theme": question["theme"],
                    "type":  question["type"]
            })
        
        elif question["type"] == "long":
            feedback = None
            llm_score = None
            student_vectors = get_embedding(student_answer)
            model_vector = get_embedding(question["model_answer"])
            similarity = cosine_similarity(student_vectors, model_vector)
            if similarity >= HIGH_THRESHOLD:
                score +=1
                method = "semantic-auto-pass"
                message = "correct"
            elif similarity <= LOW_THRESHOLD:
                method = "semantic-auto-fail"
                message = "incorrect"
            else:
                logging.debug("AI evaluation started")
                method = "ai-evaluted"
                try:
                    # result = await  grader_llm.ainvoke({
                    #     "model_answer": question["model_answer"],
                    #     "student_answer": student_answer 
                    # })
                    result = await evaluate_answer(question["model_answer"], student_answer)
                    logging.debug(f"Result: {result} ")
                except Exception as e:
                    logging.error(f"Grading failed: {e}")
                    result = GradeOutput(
                        score = 0,
                        feedback="Evaluation failed due to system error"
                    )
                llm_score = result["score"]
                feedback = result["feedback"]
                if llm_score >= 0.8:
                    message = "correct"
                elif llm_score >= 0.5:
                    message = "partially correct"
                else:
                    message = "incorrect"
            data = {
                  "qid": qid,
                    "message": message,
                    "student_answer": student_answer,
                    "correct_answer": question["model_answer"],
                    "theme": question["theme"],
                    "type":  question["type"],
                    "method": method,
                    "similarity": float(similarity),
                }
            if feedback:
                data["feedback"] = feedback
            if llm_score is not None:
                data["ai_score"] = llm_score
            
            exam_evaluation.append(data)

        # Post Metrics
        accuracy = score/total_questions
        # Background tasks 
        background_tasks.add_task( generate_ai_suggestions, examId, suggestion_needed)   
        
        result = {
        "examId": examId,
        "total_question": total_questions, 
        "attempted": attempted, 
        "unattempted": unattempted,
        "accuracy": accuracy,
        "score": score,
        "evaluation": exam_evaluation
        }   
    # await exam_results_collection.insert_one(result)
    return { "status": True, "message": "Exam Evaluation successful", "data": serialize_doc(result)}


