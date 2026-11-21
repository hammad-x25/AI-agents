# PUCIT GPA/CGPA Assistant — Assignment 3

This version uses an async LangGraph workflow, a standalone FastMCP server,
SQLite checkpoint memory, named chat threads, and streaming model/tool events.
The agent discovers all calculation tools from MCP; it does not import the
calculation implementation into the graph.

## Setup

```powershell
uv sync
Copy-Item .env.example .env
# Put your GROQ_API_KEY in .env
```

The local default is `MCP_URL=http://127.0.0.1:8000/mcp`.

## Run the MCP server

In terminal 1:

```powershell
uv run python server/server.py
```

Check it independently, without an LLM:

```powershell
uv run fastmcp list server/server.py
uv run fastmcp call server/server.py get_credit_hours semesters='[5,6]'
```

The server exposes the GPA calculations, curriculum lookup, credit-hour,
remaining-hours, and report-saving tools over Streamable HTTP.

## Run the LangGraph client

In terminal 2:

```powershell
uv run ai-assignment01
```

The CLI prints existing thread names before asking who is chatting. During a
chat, use `/switch`, `/history`, `/forget`, or `/quit`. New messages are sent
with only the new `HumanMessage`; LangGraph loads the rest from
`gpa_memory.sqlite` using the selected thread ID.

## Run the UI

```powershell
uv run python -m streamlit run .\src\ai_assignment01\app.py
```

The Streamlit chat uses the same SQLite memory and streams response tokens.

## Assignment 3 implementation map

- `server/tools.py` contains the framework-independent GPA tool functions.
- `server/server.py` publishes every tool through FastMCP.
- `src/ai_assignment01/agent.py` discovers MCP tools, builds the LangGraph
  model → tools loop, uses `AsyncSqliteSaver`, and streams `messages` and
  `updates` events.
- `repair_pending_tool_calls` repairs an interrupted tool call saved by a
  server outage so the next Groq request receives a valid message history.
- If MCP is unavailable before a turn starts, the graph runs with an explicit
  offline notice and does not fabricate a numeric answer.

## Deployment

The agent only needs a reachable Streamable HTTP MCP endpoint. For a hosted
deployment, set `MCP_URL` to the provider's `/mcp` URL and set `FASTMCP_KEY`
when the provider requires a bearer key. `render.yaml` and
`requirements-server.txt` are ready for a Render web service; Render supplies
the `PORT` environment variable and the server binds to `0.0.0.0` automatically.
This repository does not claim a public hosted URL because deployment requires
the owner's hosting account. After deployment, put the generated URL ending in
`/mcp` and any key details in `.env` and in this README before submitting the
zip.
