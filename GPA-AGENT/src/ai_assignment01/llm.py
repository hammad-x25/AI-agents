from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os
load_dotenv()

Groq_api_key=os.getenv("GROQ_API_KEY")

llm=init_chat_model("groq:openai/gpt-oss-120b",api_key=Groq_api_key)

