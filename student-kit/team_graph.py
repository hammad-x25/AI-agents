"""Part C: a small LangGraph wrapper around the agent.

    START -> agent -> check --(route)--> END
               ^                 |
               +-----------------+   (team broke a rule, fewer than 3 attempts)

The agent node and the check node are written for you.
You write route() and the graph wiring at the bottom.
"""

from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph

from agent import agent
from checks import RULES, team_sheet, validate_team
from tools import TOOLS

MAX_ATTEMPTS = 3
SUBMIT_TOOL = getattr(TOOLS[4], "name", getattr(TOOLS[4], "__name__", ""))


class State(MessagesState):
    attempts: int  # how many bad teams the checker has rejected this turn
    status: str    # "ok", "bad" or "no_team", set by the check node


# ---------------------------------------------------------------- given nodes

def agent_node(state: State) -> dict:
    """Run the create_agent agent on the conversation so far."""
    result = agent.invoke({"messages": state["messages"]})
    new_messages = result["messages"][len(state["messages"]):]
    return {"messages": new_messages}


def check_node(state: State) -> dict:
    """Plain code: find the team the agent just submitted and check the rules."""
    submitted = None
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            break  # only look at what the agent did in this run
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                if call["name"] == SUBMIT_TOOL:
                    submitted = call["args"]
                    break
        if submitted:
            break

    if submitted is None:
        return {"status": "no_team"}  # the agent asked the user something instead

    players = submitted.get("players", [])
    captain = submitted.get("captain", "")
    problems = validate_team(players, captain)
    if not problems:
        return {"status": "ok", "messages": [AIMessage(team_sheet(players, captain))]}

    feedback = (
        "[team checker] The team was rejected:\n- " + "\n- ".join(problems)
        + f"\nRules: {RULES}.\nFix these problems and submit again."
    )
    return {
        "status": "bad",
        "attempts": state.get("attempts", 0) + 1,
        "messages": [HumanMessage(feedback)],
    }


# ---------------------------------------------------------------- your part

def route(state: State) -> str:
    """Decide what happens after the check node.

     (Part C):
      - status "ok" or "no_team"          -> END
      - status "bad" and attempts >= MAX_ATTEMPTS -> END (give up honestly)
      - status "bad" otherwise            -> back to "agent"
    """
    if(state["status"]=="ok" or state["status"]=="no_team"):
        return "END"
    if(state["status"]=="bad" or state["attempts"]>=MAX_ATTEMPTS):
        return "END"
    if(state["status"]=="bad"):
        return "Agent"    
         
    


# TODO (Part C): build the graph.
#   builder = StateGraph(State)
#   add the two nodes ("agent" and "check"), the edges, and one
#   conditional edge out of "check" that uses route.
#   Then compile it into app.

builder=StateGraph(State)
builder.add_node("Agent",agent_node)
builder.add_node("Check Node",check_node)
builder.add_edge(START,"Agent")
builder.add_edge("Agent","Check Node")

builder.add_conditional_edges(
    "Check Node",
    route
)
app = builder.compile()

