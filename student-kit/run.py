"""Chat with your finished agent. Given: run it with  python run.py

How a session goes:
  1. Ask for a team. The agent may ask you a question or two first.
  2. It shows you a DRAFT. Ask for any changes you like ("drop Haris Rauf").
  3. When you are happy, approve it ("lock it in"). Only now is it sent to the checker.
  4. If the checker rejects it, the agent fixes only what the rules need, and this
     program tells you exactly which players it changed. You can still ask for more.

Try these:
  1. Pick me a balanced team, captain should be a bowler.
  2. Load it with Qalandars, I want 8 of them.
  3. Put every player worth 10 or more credits in my team.
"""

from langchain.messages import AIMessage, HumanMessage

from data import find_player, table
from team_graph import MAX_ATTEMPTS, SUBMIT_TOOL, app


def this_turn(messages) -> list:
    """The messages since your last message (the agent's work and the checker's replies)."""
    for i in range(len(messages) - 1, -1, -1):
        m = messages[i]
        if isinstance(m, HumanMessage) and not m.text.startswith("[team checker]"):
            return messages[i + 1:]
    return messages


def submissions(turn) -> list[dict]:
    """Every team the agent submitted in this turn, oldest first."""
    return [call["args"] for m in turn if isinstance(m, AIMessage)
            for call in m.tool_calls if call["name"] == SUBMIT_TOOL]


def problems_in(checker_message) -> list[str]:
    return [line for line in checker_message.text.splitlines() if line.startswith("- ")]


def team_table(team: dict) -> str:
    """A submitted team as a table, valid or not (unknown names are marked)."""
    captain = team.get("captain", "")
    rows = []
    for name in team.get("players", []):
        p = find_player(name)
        mark = " (C)" if name == captain else ""
        if p is None:
            rows.append(["??", name + mark, "not in either squad", ""])
        else:
            rows.append([p["role"], p["name"] + mark, p["team"], f"{p['credits']:g}"])
    order = ["WK", "BAT", "AR", "BOWL", "??"]
    rows.sort(key=lambda row: order.index(row[0]))
    return table(["Role", "Player", "Team", "Credits"], rows)


def changes(approved: dict, final: dict) -> list[str]:
    """What the agent changed between the team you approved and the one that passed."""
    before, after = approved.get("players", []), final.get("players", [])
    went_out = [name for name in before if name not in after]
    came_in = [name for name in after if name not in before]
    lines = []
    if went_out or came_in:
        size = max(len(went_out), len(came_in))
        pairs = [[went_out[i] if i < len(went_out) else "", came_in[i] if i < len(came_in) else ""]
                 for i in range(size)]
        lines = table(["Out", "In"], pairs).splitlines()
    if approved.get("captain") != final.get("captain"):
        lines.append(f"Captain: {approved.get('captain')} -> {final.get('captain')}")
    return lines


def chat() -> None:
    messages = []
    print("Fantasy XI Builder. Type 'exit' to stop.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() == "exit":
            break
        messages = messages + [HumanMessage(user_input)]
        result = app.invoke({"messages": messages, "attempts": 0, "status": ""})
        messages = result["messages"]
        turn = this_turn(messages)
        submitted = submissions(turn)
        rejections = [m for m in turn if isinstance(m, HumanMessage)]  # only the checker's

        if result["status"] == "bad":
            last = submitted[-1]
            print(f"\nAgent: I couldn't build a valid team in {MAX_ATTEMPTS} tries. The last team I tried:\n")
            print(team_table(last))
            print("\nProblems:")
            print("\n".join(problems_in(rejections[-1])))
            print("Tell me what to change, and I'll try again.\n")
        elif result["status"] == "ok":
            print(f"\nAgent: {messages[-1].text}")
            changed = changes(submitted[0], submitted[-1]) if len(submitted) > 1 else []
            if changed:
                print("\nThe checker rejected the team you approved:")
                print("\n".join(problems_in(rejections[0])))
                print("So the agent changed it to fit the rules:")
                print("\n".join(changed))
                print("Ask for a different swap if you don't like it.")
            print()
        else:
            print(f"\nAgent: {messages[-1].text}\n")


if __name__ == "__main__":
    chat()
