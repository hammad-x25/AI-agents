from __future__ import annotations

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)

from .agent import (
    clear_conversation,
    get_history,
    get_token_usage,
    run_agent,
)


# ============================================================
# CONFIGURATION
# ============================================================

THREAD_ID = "terminal-session"


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_banner() -> None:
    print(
        """
============================================================
                    CODING COMPANION
============================================================

AI coding agent powered by GPT-OSS 120B + LangGraph.

Commands:

  /help       Show available commands
  /plan       Enable Plan Mode
  /normal     Disable Plan Mode
  /tokens     Show token usage
  /history    Show conversation history
  /clear      Clear conversation memory
  /mode       Show current mode
  /exit       Exit the application

============================================================
"""
    )


def print_help() -> None:
    print(
        """
Available Commands
------------------

/plan
    Enable Plan Mode.
    The agent should analyze and plan without modifying the project.

/normal
    Return to normal execution mode.

/mode
    Show the currently active mode.

/tokens
    Display token usage for the current conversation.

/history
    Display conversation history.

/clear
    Clear the current conversation.

/help
    Show this help message.

/exit
    Close the coding companion.
"""
    )


def print_tokens() -> None:
    usage = get_token_usage(
        THREAD_ID
    )

    print("\nToken Usage")
    print("-----------")

    print(
        f"Input tokens : "
        f"{usage['input_tokens']:,}"
    )

    print(
        f"Output tokens: "
        f"{usage['output_tokens']:,}"
    )

    print(
        f"Total tokens : "
        f"{usage['total_tokens']:,}"
    )

    print()


def print_history() -> None:
    history = get_history(
        THREAD_ID
    )

    if not history:
        print(
            "\nNo conversation history.\n"
        )
        return

    print(
        "\nConversation History"
    )

    print(
        "--------------------"
    )

    for message in history:

        if isinstance(
            message,
            HumanMessage,
        ):
            role = "USER"

        elif isinstance(
            message,
            AIMessage,
        ):
            role = "AI"

        elif isinstance(
            message,
            ToolMessage,
        ):
            role = "TOOL"

        else:
            role = type(
                message
            ).__name__.upper()

        content = message.content

        if not content:
            # AI tool-call messages often have
            # empty visible content.
            continue

        print(
            f"\n[{role}]"
        )

        print(
            content
        )

    print()


# ============================================================
# PLAN MODE
# ============================================================

def prepare_input(
    user_input: str,
    plan_mode: bool,
) -> str:
    """
    Add a mode instruction to the current user message.

    Later we can also enforce Plan Mode at the tool layer,
    preventing write/run/delete tools from being available.
    """

    if not plan_mode:
        return user_input

    return f"""
[PLAN MODE ACTIVE]

The user has enabled Plan Mode.

For this request:
- analyze the task
- inspect information only when necessary
- explain what should be done
- do not write or modify files
- do not delete files
- do not install packages
- do not execute code
- do not stage or commit changes
- do not push to GitHub
- do not create repositories

Produce a clear implementation plan only.

USER REQUEST:
{user_input}
""".strip()


# ============================================================
# MAIN CHAT LOOP
# ============================================================

def main() -> None:

    plan_mode = False

    print_banner()

    while True:

        try:
            mode_name = (
                "PLAN"
                if plan_mode
                else "NORMAL"
            )

            user_input = input(
                f"[{mode_name}] You > "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):
            print(
                "\nGoodbye!"
            )
            break

        if not user_input:
            continue

        # ----------------------------------------------------
        # COMMANDS
        # ----------------------------------------------------

        command = user_input.lower()

        if command in {
            "/exit",
            "/quit",
        }:
            print(
                "Goodbye!"
            )

            break

        if command == "/help":
            print_help()
            continue

        if command == "/plan":

            if plan_mode:
                print(
                    "\nPlan Mode is already active.\n"
                )

            else:
                plan_mode = True

                print(
                    "\nPlan Mode enabled."
                )

                print(
                    "The agent will analyze and plan "
                    "without intentionally making changes.\n"
                )

            continue

        if command == "/normal":

            if not plan_mode:
                print(
                    "\nNormal Mode is already active.\n"
                )

            else:
                plan_mode = False

                print(
                    "\nNormal Mode enabled."
                )

                print(
                    "The agent can now perform "
                    "authorized project operations.\n"
                )

            continue

        if command == "/mode":

            print(
                "\nCurrent mode:",
                (
                    "PLAN"
                    if plan_mode
                    else "NORMAL"
                ),
                "\n",
            )

            continue

        if command == "/tokens":
            print_tokens()
            continue

        if command == "/history":
            print_history()
            continue

        if command == "/clear":

            clear_conversation(
                THREAD_ID
            )

            print(
                "\nConversation memory cleared.\n"
            )

            continue

        # ----------------------------------------------------
        # SEND USER REQUEST TO AGENT
        # ----------------------------------------------------

        actual_input = prepare_input(
            user_input=user_input,
            plan_mode=plan_mode,
        )

        print(
            "\nAI > ",
            end="",
            flush=True,
        )

        try:

            result = run_agent(
                actual_input,
                thread_id=THREAD_ID,
            )

            response = result[
                "response"
            ]

            print(
                response
            )

            # -----------------------------------------------
            # SHOW THIS TURN'S TOKEN USAGE
            # -----------------------------------------------

            usage = result[
                "usage"
            ]

            if usage[
                "total_tokens"
            ] > 0:

                print(
                    "\n"
                    f"[Tokens: "
                    f"{usage['input_tokens']:,} input | "
                    f"{usage['output_tokens']:,} output | "
                    f"{usage['total_tokens']:,} total]"
                )

            print()

        except Exception as exc:

            print(
                "\nAgent error:"
            )

            print(
                str(exc)
            )

            print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()