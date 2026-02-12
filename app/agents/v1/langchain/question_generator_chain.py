from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
import json
import random

from app.llm_models.v1.ollama_client import generate
question_chain = RunnableLambda(generate)