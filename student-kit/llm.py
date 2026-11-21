
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load environment variables from .env
load_dotenv()


from langchain.chat_models import init_chat_model

# llm = init_chat_model(
#     "openai:auto",
#     base_url="http://own.omniroute.pucitconnect.me/v1",  # Use your localhost path or the path to your own server or use groq if you haven't set up omniroute
#     api_key="dummy",
# )

Groq_api_key=os.getenv("GROQ_API_KEY")

llm=init_chat_model("groq:openai/gpt-oss-120b",api_key=Groq_api_key)
