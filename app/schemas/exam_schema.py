from pydantic import BaseModel, EmailStr, Field, constr, validator
from typing import Optional, List

class ExamCreate(BaseModel):
    subject: Optional[str] = "python programming language"
    difficulty: Optional[str] = "easy"
    num_questions: Optional[int] = 2

class EvaluateExamItem(BaseModel):
    qId:str
    answer:str
class EvaluateExamRequest(BaseModel):
    examId: str
    responses : List[EvaluateExamItem]

