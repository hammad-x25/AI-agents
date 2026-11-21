"""main.py, but as a chat: talk to the agent back to back.

Same servers as main.py, plus our own calculator server. Memory works exactly
like Lab 6: a checkpointer plus a thread_id, and we send only the new message
each turn. Type 'exit' to stop.

All the noise (server logs, warnings) goes to mcp.log next to this file,
so the terminal shows only the chat. If something breaks, look in mcp.log.
"""

import os
import sys
from pathlib import Path

# Send everything written to stderr (our warnings + every server's logs) to a file.
# Done first, at the file-descriptor level, so the server processes inherit it too.
LOG = Path(__file__).parent / "mcp.log"
_log = open(LOG, "w")
os.dup2(_log.fileno(), 2)

import asyncio

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from llm import llm

# Our own calculator server, started locally over stdio with the same Python running this file.
CALC = Path(__file__).parent / "cal_mcp_server" / "src" / "main.py"

# The only folder the filesystem server may touch. Anything outside it is refused.
FILES = Path(__file__).parent / "mcp_files"
FILES.mkdir(exist_ok=True)

config = {
    "mcpServers": {
        "classroom": {"command": "uvx", "args": ["--managed-python", "classroom-mcp"]},
        "langchain": {"url": "https://docs.langchain.com/mcp", "transport": "http"},
        "calc": {"command": sys.executable, "args": [str(CALC)]},
        "files": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(FILES)],
        },
    },
}

console = Console()


def show_servers(tools):
    """One line per server: how many tools it gave us."""
    lines = []
    for name in config["mcpServers"]:
        count = sum(t.name.startswith(name + "_") for t in tools)
        lines.append(f"[green]●[/] [bold]{name}[/]  [dim]{count} tools[/]")
    lines.append("\n[dim]Type 'exit' to quit. Logs go to mcp.log[/]")
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]MCP chat[/]",
            border_style="blue",
            expand=False,
        )
    )


def show_turn(new_messages):
    """Show which tools the agent called this turn, then its answer."""
    for m in new_messages:
        if isinstance(m, AIMessage):
            for call in m.tool_calls:
                args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items())
                console.print(
                    f"  [dim]🔧 {call['name']}({args})[/]", markup=True, highlight=False
                )
        elif isinstance(m, ToolMessage) and m.status == "error":
            console.print(
                f"  [red]✗ {m.name} failed: {m.text[:120]}[/]", highlight=False
            )

    answer = new_messages[-1].text
    console.print(
        Panel(
            Markdown(answer),
            title="[bold magenta]Agent[/]",
            title_align="left",
            border_style="magenta",
        )
    )


async def main():
    console.print("[dim]Connecting to MCP servers...[/]")

    # Connect once, before the loop: the servers stay up for the whole chat.
    async with MCPAdapter(config) as adapter:
        tools = await adapter.list_tools()
        show_servers(tools)

        agent = create_agent(model=llm, tools=tools, checkpointer=InMemorySaver())
        chat = {"configurable": {"thread_id": "lab7"}}
        seen = 0  # how many messages of the conversation we have already shown

        while True:
            try:
                text = console.input("\n[bold cyan]You ›[/] ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if text.lower() in ("exit", "quit"):
                break
            if not text:
                continue

            with console.status("Thinking..."):
                res = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": text}]}, chat
                )

            # res holds the whole conversation: skip what we showed before, and our own message.
            show_turn(res["messages"][seen + 1 :])
            seen = len(res["messages"])

    console.print("[dim]Bye![/]")


asyncio.run(main())
