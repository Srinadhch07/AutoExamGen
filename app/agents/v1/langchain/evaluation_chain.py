from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.agents.v1.prompts.prompts import ANSWER_EVALUATOR_PROMPT, ANSWER_EVALUATOR_SYSTEM_PROMPT
from app.llm_models.v1.ollama_client import ollama_runnable
json_parser = JsonOutputParser()

evaluation_prompt = ChatPromptTemplate.from_messages([ ("system", ANSWER_EVALUATOR_SYSTEM_PROMPT), ("user", ANSWER_EVALUATOR_PROMPT)])
evaluation_chain = ( evaluation_prompt | ollama_runnable | json_parser)
