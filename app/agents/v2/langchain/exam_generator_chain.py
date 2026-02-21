from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import  RunnableSequence, RunnableParallel

from app.schemas.v2.exam_schema import Exam
from app.llm_models.v2.llama_client import llm
from app.agents.v2.prompts.generators_prompts import prompt as generator_prompt

parser = PydanticOutputParser(pydantic_object=Exam)

chain = generator_prompt | llm | parser
