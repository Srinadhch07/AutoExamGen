import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
llm = ChatAnthropic( model="claude-3-5-sonnet-20241022", temperature=0.3, api_key=ANTHROPIC_API_KEY)

