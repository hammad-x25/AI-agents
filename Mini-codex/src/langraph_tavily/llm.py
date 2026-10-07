# src/coding_companion/llm.py

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load environment variables from .env
load_dotenv()


# ---------------------------------------------------------
# ENVIRONMENT VALIDATION
# ---------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY was not found.\n"
        "Add it to your .env file:\n"
        "GROQ_API_KEY=your_key_here"
    )


# ---------------------------------------------------------
# MODEL CONFIGURATION
# ---------------------------------------------------------

MODEL_NAME = "openai/gpt-oss-120b"


llm = ChatGroq(
    model=MODEL_NAME,

    # Low temperature is better for a coding agent:
    # fewer random variations and more deterministic behavior.
    temperature=0.0,

    # GPT-OSS supports reasoning effort.
    reasoning_effort="medium",

    # Do not expose raw reasoning/thinking in normal responses.
    reasoning_format="hidden",

    # Retry temporary API failures.
    max_retries=2,

    # Request timeout.
    timeout=60,
)


def get_llm() -> ChatGroq:
    """
    Return the configured language model instance.
    """
    return llm