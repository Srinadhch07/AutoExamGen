from pydantic import BaseModel, EmailStr, Field, constr, validator
from typing import Optional, List, Literal

class ThemeConfig(BaseModel):
    theme: str = Field(..., example="HR")
    type: Literal["mcq", "long", "short"] = Field(..., example="mcq")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., example="easy")
    count: int = Field(..., ge=1, example=1)


class ExamCreate(BaseModel):
    exam_name: str = Field(..., example="Placement Test 1")
    subject: str = Field(..., example="Computer Science")
    themes: List[ThemeConfig]

class EvaluateExamItem(BaseModel):
    qId:str
    answer:str
class EvaluateExamRequest(BaseModel):
    examId: str
    responses : List[EvaluateExamItem]

