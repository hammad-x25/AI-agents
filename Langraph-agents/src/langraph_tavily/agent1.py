import os
import requests

from dotenv import load_dotenv

load_dotenv()

from llm import llm

from langchain.agents import create_agent

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
)

from langchain_core.tools import tool

from langchain_tavily import TavilySearch


# ============================================================
# EXPORT TOOL
# ============================================================

@tool
def export_and_notify(
    markdown_content: str,
    ntfy_topic: str = "elevenorbits",
) -> str:

    """
    Export a Markdown study plan to a permanent web page
    and send a push notification containing the URL.
    """

    try:

        response = requests.post(
            "https://rentry.co/api/new",
            data={
                "text": markdown_content
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        url = data["url"]

        requests.post(
            f"https://ntfy.sh/{ntfy_topic}",
            data=f"Your plan is ready: {url}".encode(),
            timeout=5,
        )

        return (
            f"Published successfully at {url}. "
            f"Notification sent."
        )

    except requests.RequestException as e:

        return f"Network request failed: {e}"

    except Exception as e:

        return f"Export failed: {e}"


# ============================================================
# TAVILY
# ============================================================

web_search_tool = TavilySearch(
    max_results=3,
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
)


@tool
def tavily_web_search(
    query: str,
) -> str:

    """
    Search the web for current information using Tavily.

    Use this when up-to-date or external information
    is needed.
    """

    results = web_search_tool.invoke(query)

    return str(results)


# ============================================================
# TOOLS
# ============================================================

tools = [
    tavily_web_search,
    export_and_notify,
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an intelligent study and research assistant.

Your responsibilities:

1. Understand what the user wants.

2. Use tavily_web_search whenever current or external
   information is required.

3. Use previous conversation messages and previous tool
   results when they are relevant.

4. Create clear and useful study plans when requested.

5. Use export_and_notify only when the user asks to
   publish, export, or notify them about a plan.

6. Never call tools unnecessarily.

7. If enough information already exists in the conversation,
   use it instead of searching again.
"""


# ============================================================
# CREATE AGENT
# ============================================================

app = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


# ============================================================
# HISTORY
# ============================================================

history: list[AnyMessage] = []


# ============================================================
# CLI
# ============================================================

print("======================================")
print("     STUDY / RESEARCH AGENT")
print("======================================")
print("Type 'quit' to exit.\n")


while True:

    user_input = input("You: ").strip()

    if user_input.lower() == "quit":

        print("\nAssistant: Goodbye!")

        break

    if not user_input:
        continue

    history.append(
        HumanMessage(
            content=user_input
        )
    )

    # create_agent receives the current messages
    # and internally performs:
    #
    # model
    #   ↓
    # tool call?
    #   ↓
    # tools
    #   ↓
    # model
    #   ↓
    # ...
    # until final answer

    result = app.invoke(
        {
            "messages": history
        }
    )

    # create_agent returns the full message state
    history = result["messages"]

    last_message = history[-1]

    print(
        f"\nAssistant: {last_message.content}\n"
    )