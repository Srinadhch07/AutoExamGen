from typing import List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from datetime import date

class DateNormalizedModel(BaseModel):

    @field_validator(
        "start_date",
        "end_date",
        "issue_date",
        "expiry_date",
        "date",
        mode="before",
        check_fields=False,
    )
    def normalize_year_month(cls, value):
        if isinstance(value, str):
            if value == "":
                return None
            if len(value) == 7:  # YYYY-MM
                return value + "-01"
        return value
    
class PersonalInfo(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    headline: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    

class WorkExperience(DateNormalizedModel):
    job_title: str
    organization: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    description: List[str] = Field(default_factory=list)
    
class Education(BaseModel):
    qualification: str
    field_of_study: Optional[str] = None
    institution: str
    location: Optional[str] = None
    start_year: int
    end_year: Optional[int] = None
    grade: Optional[str] = None
    

class Project(DateNormalizedModel):
    title: str
    organization: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: List[str] = Field(default_factory=list)
    link: Optional[HttpUrl] = None
    

class Certification(BaseModel):
    title: str
    issuing_organization: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None
    

class Award(DateNormalizedModel):
    title: str
    issuer: str
    date: Optional[date] = None
    

class VolunteerExperience(DateNormalizedModel):
    role: str
    organization: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: List[str] = Field(default_factory=list)
    

class Language(BaseModel):
    language: str
    proficiency: str  # Beginner | Intermediate | Fluent | Native
    

class Skills(BaseModel):
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)
    

class AdditionalInformation(BaseModel):
    interests: List[str] = Field(default_factory=list)
    references: Optional[str] = "Available upon request"
    

class ResumeSchema(BaseModel):
    personal_info: PersonalInfo
    professional_summary: Optional[str] = None
    core_competencies: List[str] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    awards: List[Award] = Field(default_factory=list)
    volunteer_experience: List[VolunteerExperience] = Field(default_factory=list)
    skills: Optional[Skills] = None
    additional_information: Optional[AdditionalInformation] = None