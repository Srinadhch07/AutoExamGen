import os
from dotenv import load_dotenv
from datetime import datetime,timedelta,date

load_dotenv()
    
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "qwen2:0.5b"
