import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GOOGLE_API_KEY"),    
)