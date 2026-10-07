from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from .llm import llm
from .system_prompt import SYSTEM_PROMPT
from .tools import TOOLS


# ============================================================
# MEMORY / CHECKPOINTER
# ============================================================

# Stores conversation state while the Python process is running.
#
# Every thread_id gets its own conversation history.
checkpointer = InMemorySaver()


# ============================================================
# CREATE AGENT
# ============================================================

agent = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)


# ============================================================
# TOKEN USAGE STORAGE
# ============================================================

# We keep token totals separately for each conversation/thread.
#
# Example:
#
# {
#     "default": {
#         "input_tokens": 1200,
#         "output_tokens": 350,
#         "total_tokens": 1550
#     }
# }
#
TOKEN_USAGE: dict[str, dict[str, int]] = {}


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _get_config(thread_id: str) -> dict:
    """
    Create LangGraph config for a conversation.

    thread_id identifies one independent conversation.
    """

    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def _empty_usage() -> dict[str, int]:
    """
    Return an empty token-usage object.
    """

    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }


def _extract_usage(message: AIMessage) -> dict[str, int]:
    """
    Extract token usage from an AIMessage.

    LangChain/Groq may expose token usage through usage_metadata.
    A fallback for response_metadata is also included.
    """

    usage = _empty_usage()

    # --------------------------------------------------------
    # Preferred LangChain usage metadata
    # --------------------------------------------------------

    usage_metadata = getattr(
        message,
        "usage_metadata",
        None,
    )

    if usage_metadata:
        input_tokens = int(
            usage_metadata.get(
                "input_tokens",
                0,
            )
            or 0
        )

        output_tokens = int(
            usage_metadata.get(
                "output_tokens",
                0,
            )
            or 0
        )

        total_tokens = int(
            usage_metadata.get(
                "total_tokens",
                input_tokens + output_tokens,
            )
            or 0
        )

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

    # --------------------------------------------------------
    # Groq / provider metadata fallback
    # --------------------------------------------------------

    response_metadata = getattr(
        message,
        "response_metadata",
        {},
    ) or {}

    token_usage = response_metadata.get(
        "token_usage",
        {},
    ) or {}

    input_tokens = int(
        token_usage.get(
            "prompt_tokens",
            0,
        )
        or 0
    )

    output_tokens = int(
        token_usage.get(
            "completion_tokens",
            0,
        )
        or 0
    )

    total_tokens = int(
        token_usage.get(
            "total_tokens",
            input_tokens + output_tokens,
        )
        or 0
    )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _add_usage(
    thread_id: str,
    usage: dict[str, int],
) -> None:
    """
    Add token usage to the accumulated usage for a thread.
    """

    if thread_id not in TOKEN_USAGE:
        TOKEN_USAGE[thread_id] = _empty_usage()

    TOKEN_USAGE[thread_id]["input_tokens"] += usage[
        "input_tokens"
    ]

    TOKEN_USAGE[thread_id]["output_tokens"] += usage[
        "output_tokens"
    ]

    TOKEN_USAGE[thread_id]["total_tokens"] += usage[
        "total_tokens"
    ]


def _usage_from_messages(
    messages: list,
) -> dict[str, int]:
    """
    Calculate token usage from newly generated AI messages.

    This is important because one agent turn may contain:

        AI tool call
        Tool result
        AI tool call
        Tool result
        Final AI answer

    We want to count ALL AI generations from the current turn.
    """

    usage = _empty_usage()

    for message in messages:

        if not isinstance(message, AIMessage):
            continue

        message_usage = _extract_usage(
            message
        )

        usage["input_tokens"] += message_usage[
            "input_tokens"
        ]

        usage["output_tokens"] += message_usage[
            "output_tokens"
        ]

        usage["total_tokens"] += message_usage[
            "total_tokens"
        ]

    return usage


def _find_final_ai_message(
    messages: list,
) -> AIMessage | None:
    """
    Find the final AI response from a group of messages.
    """

    for message in reversed(messages):

        if isinstance(message, AIMessage):
            return message

    return None


# ============================================================
# MAIN AGENT FUNCTION
# ============================================================

def run_agent(
    user_input: str,
    thread_id: str = "default",
) -> dict[str, Any]:
    """
    Send one user message to the coding agent.

    Conversation history is automatically preserved through
    LangGraph's checkpointer.

    Returns:
        response:
            Final text generated by the agent.

        usage:
            Token usage for THIS turn.

        total_usage:
            Accumulated token usage for this thread.

        messages:
            Complete conversation history returned by the graph.
    """

    user_input = user_input.strip()

    if not user_input:
        return {
            "response": "Please provide a message.",
            "usage": _empty_usage(),
            "total_usage": get_token_usage(thread_id),
            "messages": [],
        }

    config = _get_config(
        thread_id
    )

    # --------------------------------------------------------
    # BEFORE INVOCATION
    #
    # Find how many messages already exist.
    #
    # This lets us distinguish:
    #
    # OLD HISTORY
    #
    # from:
    #
    # NEW MESSAGES CREATED DURING THIS TURN
    # --------------------------------------------------------

    try:
        previous_state = agent.get_state(
            config
        )

        previous_messages = (
            previous_state.values.get(
                "messages",
                [],
            )
            if previous_state.values
            else []
        )

        old_message_count = len(
            previous_messages
        )

    except Exception:
        old_message_count = 0

    # --------------------------------------------------------
    # INVOKE AGENT
    #
    # IMPORTANT:
    #
    # We only send the NEW user message here.
    #
    # LangGraph retrieves previous messages from the
    # checkpointer automatically using thread_id.
    # --------------------------------------------------------

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        },
        config=config,
    )

    all_messages = result.get(
        "messages",
        [],
    )

    # --------------------------------------------------------
    # GET ONLY NEW MESSAGES
    #
    # create_agent returns the complete state/history.
    #
    # Example:
    #
    # old:
    #
    #   Human 1
    #   AI 1
    #
    # after next invocation:
    #
    #   Human 1
    #   AI 1
    #   Human 2
    #   AI tool call
    #   Tool result
    #   AI 2
    #
    # We only want:
    #
    #   Human 2
    #   AI tool call
    #   Tool result
    #   AI 2
    #
    # for this turn's token calculation.
    # --------------------------------------------------------

    new_messages = all_messages[
        old_message_count:
    ]

    turn_usage = _usage_from_messages(
        new_messages
    )

    _add_usage(
        thread_id,
        turn_usage,
    )

    final_message = _find_final_ai_message(
        new_messages
    )

    # Fallback in case message slicing produces no AI message.
    if final_message is None:
        final_message = _find_final_ai_message(
            all_messages
        )

    if final_message is None:
        response = (
            "The agent completed without returning "
            "a final AI message."
        )

    else:
        response = final_message.content

    return {
        "response": response,
        "usage": turn_usage,
        "total_usage": get_token_usage(
            thread_id
        ),
        "messages": all_messages,
    }


# ============================================================
# CONVERSATION HISTORY
# ============================================================

def get_history(
    thread_id: str = "default",
) -> list:
    """
    Return the complete stored message history for a thread.
    """

    config = _get_config(
        thread_id
    )

    try:
        state = agent.get_state(
            config
        )

        if not state.values:
            return []

        return list(
            state.values.get(
                "messages",
                [],
            )
        )

    except Exception:
        return []


# ============================================================
# TOKEN USAGE
# ============================================================

def get_token_usage(
    thread_id: str = "default",
) -> dict[str, int]:
    """
    Return accumulated token usage for a conversation.
    """

    return TOKEN_USAGE.get(
        thread_id,
        _empty_usage(),
    ).copy()


# ============================================================
# CLEAR CONVERSATION
# ============================================================

def clear_conversation(
    thread_id: str = "default",
) -> None:
    """
    Delete conversation memory and token statistics
    for the specified thread.
    """

    try:
        checkpointer.delete_thread(
            thread_id
        )

    finally:
        TOKEN_USAGE.pop(
            thread_id,
            None,
        )