
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


from langchain.chat_models import init_chat_model


Groq_api_key=os.getenv("GROQ_API_KEY")

llm=init_chat_model("groq:openai/gpt-oss-120b",api_key=Groq_api_key)
