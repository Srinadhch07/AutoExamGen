from langchain_core.output_parsers import PydanticOutputParser
from app.schemas.v2.exam_schema import GradeOutput
from app.llm_models.v2.llama_client import llm
from app.agents.v2.prompts.grading_prompt import prompt

parser = PydanticOutputParser(pydantic_object=GradeOutput)

grader_llm = prompt | llm | parser