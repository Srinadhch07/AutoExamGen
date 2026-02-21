from pydantic import BaseModel, field_validator
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