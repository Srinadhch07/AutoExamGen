from pydantic import BaseModel, field_validator, Field
from typing import List, Literal, Optional

class MCQQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class LongQuestion(BaseModel):
    question: str
    answer: str

class CodingQuestion(BaseModel):
    question: str
    constraints: str
    sample_input: str
    sample_output: str
    answer: str

class Section(BaseModel):
    theme: str
    type: Literal["mcq", "long"]
    difficulty: Literal["easy", "medium", "hard"]
    questions: list

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        if isinstance(v, str):
            return v.lower().strip()
        return v

    @field_validator("difficulty", mode="before")
    @classmethod
    def normalize_difficulty(cls, v):
        if isinstance(v, str):
            return v.lower().strip()
        return v

class Exam(BaseModel):
    exam_name: Optional[str] = "AI Exam"
    subject: str
    sections: List[Section]

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
    theme: str
    qId:str
    answer:str
class EvaluateExamRequest(BaseModel):
    examId: str
    responses : List[EvaluateExamItem]

class GradeOutput(BaseModel):
    score: float = Field(..., ge=0, le=1)
    feedback: str