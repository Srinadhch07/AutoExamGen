from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm_models.v1 import ollama_client

prompt = PromptTemplate.from_template("""
Compare responses with answer key.

Responses:
{responses}

Answer Key:
{answer_key}

Return JSON:
{{
  "score": number,
  "wrong_questions": []
}}
""")

evaluation_chain = prompt | ollama_client | StrOutputParser()