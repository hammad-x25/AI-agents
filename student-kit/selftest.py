"""Check your work as you go:  python selftest.py

No model calls, it only looks at how your tools, agent and graph are
put together and prints OK or FIX for each. Run it as often as you like.
Use run.py to see the agent actually work.
"""

ORIGINAL_NAMES = {0: "f1", 1: "player", 2: "pick", 3: "compare"}
ORIGINAL_DESCRIPTIONS = {"returns info", "submit the team."}
BAD_ARG_NAMES = {"a", "b", "t", "x", "r", "m", "c", "p", "n"}
PURPOSE = ["squad", "player form", "players by role", "compare two players", "submit team"]


def show(ok, text):
    print(f"  {'OK ' if ok else 'FIX'}  {text}")


print("\nPart A: tools")
TOOLS = None
try:
    from langchain.tools import tool as make_tool
    from langchain_core.tools import BaseTool
    from tools import TOOLS
except Exception as exc:
    show(False, f"tools.py does not import: {exc}")

if TOOLS is not None:
    for i, t in enumerate(TOOLS[:5]):
        label = f"tool {i + 1} ({PURPOSE[i]})"
        try:
            is_tool = isinstance(t, BaseTool)
            st = t if is_tool else make_tool(t)
            props = st.tool_call_schema.model_json_schema().get("properties", {})
            desc = (st.description or "").strip()
            show(is_tool, f"{label}: has @tool")
            show(st.name != ORIGINAL_NAMES.get(i) and len(st.name) >= 6, f"{label}: name '{st.name}'")
            show(all(len(a) >= 3 and a.lower() not in BAD_ARG_NAMES for a in props), f"{label}: argument names {list(props)}")
            show(all(any(k in s for k in ("type", "anyOf", "items")) for s in props.values()), f"{label}: every argument has a type")
            show(len(desc) >= 40 and desc.lower() not in ORIGINAL_DESCRIPTIONS, f"{label}: description says when to use it")
            if i == 3:
                show("Args:" not in desc and all(s.get("description") for s in props.values()),
                     f"{label}: Args block parsed into argument descriptions")
        except Exception as exc:
            show(False, f"{label}: the model could not be given this tool ({exc})")

print("\nPart B: agent")
try:
    import agent as agent_module
    from langgraph.graph.state import CompiledStateGraph
    a = agent_module.agent
    show(isinstance(a, CompiledStateGraph) and "tools" in a.nodes, "agent is built with create_agent and has tools")
    show(len(agent_module.SYSTEM_PROMPT.strip()) > 200, "system prompt has more than the one given line")
except Exception as exc:
    show(False, f"agent.py does not import: {exc}")

print("\nPart C: graph")
try:
    import team_graph
    g = team_graph.app.get_graph()
    edges = {(e.source, e.target) for e in g.edges}
    show({"agent", "check"} <= set(g.nodes), "nodes 'agent' and 'check'")
    for edge in [("__start__", "agent"), ("agent", "check"), ("check", "agent"), ("check", "__end__")]:
        show(edge in edges, f"edge {edge[0]} -> {edge[1]}")
except Exception as exc:
    show(False, f"graph not built yet: {exc}")
print()
