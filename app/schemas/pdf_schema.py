from pydantic import BaseModel, EmailStr, Field, constr, validator
from typing import Optional, List

class PDFGenerate(BaseModel):
    name: str


