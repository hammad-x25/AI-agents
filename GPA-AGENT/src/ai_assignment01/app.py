"""Streamlit UI for the persistent, streaming LangGraph client."""

import asyncio
import re

import streamlit as st

from ai_assignment01.agent import (
    forget_thread,
    load_thread_messages,
    saved_threads,
    stream_turn,
)


st.set_page_config(
    page_title="PUCIT GPA Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #f7f7f8; }
    .block-container { max-width: 920px; padding-top: 1.5rem; padding-bottom: 7rem; }
    [data-testid="stChatMessage"] { background: white; border: 1px solid #e5e7eb;
        border-radius: 16px; padding: 1rem; margin-bottom: .75rem; }
    [data-testid="stSidebar"] { background: #202123; }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] input {
        background: #ffffff !important;
        color: #111827 !important;
        caret-color: #111827 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #343541 !important;
        color: #ffffff !important;
        border-color: #565869 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #ffffff !important; }
    .current-chat {
        background: #343541; border: 1px solid #565869; border-radius: 10px;
        color: #ffffff; padding: .65rem .8rem; margin: .5rem 0 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _clean_chat_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 _.-]", "", value).strip()
    return value[:40]


if "chat_ids" not in st.session_state:
    try:
        persisted = asyncio.run(saved_threads())
    except Exception:
        persisted = []
    st.session_state.chat_ids = persisted or ["student"]
if "active_chat" not in st.session_state:
    st.session_state.active_chat = st.session_state.chat_ids[0]
if "messages_by_chat" not in st.session_state:
    st.session_state.messages_by_chat = {}
if "loaded_chats" not in st.session_state:
    st.session_state.loaded_chats = set()


def set_active_chat(chat_id: str) -> None:
    if chat_id == st.session_state.active_chat:
        return
    st.session_state.active_chat = chat_id
    st.rerun()


active_chat = st.session_state.active_chat
if active_chat not in st.session_state.loaded_chats:
    try:
        st.session_state.messages_by_chat[active_chat] = asyncio.run(
            load_thread_messages(active_chat)
        )
    except Exception:
        st.session_state.messages_by_chat[active_chat] = []
    st.session_state.loaded_chats.add(active_chat)


def ask_agent(prompt: str, placeholder) -> str:
    streamed: list[str] = []

    def on_event(event: dict[str, str]) -> None:
        if event["type"] == "token":
            streamed.append(event["text"])
            placeholder.markdown("".join(streamed))
        elif event["type"] == "status" and not streamed:
            placeholder.caption(event["text"])

    response = asyncio.run(stream_turn(prompt, st.session_state.active_chat, on_event))
    return response or "I couldn't produce a response. Please try again."


with st.sidebar:
    st.markdown("## 🎓 GPA Assistant")
    st.caption("PUCIT BS Computer Science")
    st.divider()

    selected_chat = st.selectbox(
        "Your chats",
        options=st.session_state.chat_ids,
        index=st.session_state.chat_ids.index(active_chat),
        key="chat_selector",
    )
    if selected_chat != st.session_state.active_chat:
        set_active_chat(selected_chat)

    st.markdown(
        f"<div class='current-chat'>Current chat<br><strong>{active_chat}</strong></div>",
        unsafe_allow_html=True,
    )

    new_name = st.text_input(
        "New chat name",
        placeholder="e.g. Ali semester 5",
        key="new_chat_name",
    )
    if st.button("＋ Create new chat", use_container_width=True):
        chat_id = _clean_chat_name(new_name) or f"chat-{len(st.session_state.chat_ids) + 1}"
        if chat_id not in st.session_state.chat_ids:
            st.session_state.chat_ids.append(chat_id)
            st.session_state.messages_by_chat[chat_id] = []
            st.session_state.loaded_chats.add(chat_id)
        st.session_state.active_chat = chat_id
        st.rerun()

    if st.button("Delete current chat", use_container_width=True):
        asyncio.run(forget_thread(active_chat))
        st.session_state.chat_ids.remove(active_chat)
        st.session_state.messages_by_chat.pop(active_chat, None)
        st.session_state.loaded_chats.discard(active_chat)
        if not st.session_state.chat_ids:
            st.session_state.chat_ids.append("student")
        st.session_state.active_chat = st.session_state.chat_ids[0]
        st.rerun()

    st.divider()
    st.markdown("### I can help with")
    st.markdown("GPA · CGPA projection · target planning · courses · credit hours · reports")
    st.divider()
    st.caption("Calculations come from tools on the GPA MCP server.")


st.title("🎓 PUCIT GPA Assistant")
st.markdown(
    "<p style='text-align:center;color:#6b7280'>GPA and CGPA planning for BS Computer Science students</p>",
    unsafe_allow_html=True,
)

messages = st.session_state.messages_by_chat.setdefault(active_chat, [])
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

selected_prompt = None
if not messages:
    with st.container(border=True):
        st.markdown("### How can I help with your GPA?")
        st.write("Calculate a GPA, project your CGPA, inspect course credit hours, or plan a target.")
    left, right = st.columns(2)
    with left:
        if st.button("📊 Calculate GPA", use_container_width=True):
            selected_prompt = (
                "I got 78 in Analysis of Algorithms, 85 in Artificial Intelligence, "
                "and 64 in Human Computer Interaction. These are Semester 5 courses. What is my GPA?"
            )
        if st.button("📚 Semester 5 courses", use_container_width=True):
            selected_prompt = "Show me the courses and credit hours for Semester 5."
    with right:
        if st.button("🎯 Plan target CGPA", use_container_width=True):
            selected_prompt = "My current CGPA is 3.0. I am entering Semester 5 and want to reach 3.4."
        if st.button("📈 Project my CGPA", use_container_width=True):
            selected_prompt = "I want to calculate what my CGPA will become after this semester."

typed_prompt = st.chat_input("Ask about GPA, CGPA, courses, marks or your target...")
prompt = typed_prompt or selected_prompt

if prompt:
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("Connecting to the GPA tools..."):
            try:
                response = ask_agent(prompt, placeholder)
            except Exception as error:
                response = f"Something went wrong while processing the request: {error}"
        placeholder.markdown(response)
    messages.append({"role": "assistant", "content": response})
    st.session_state.messages_by_chat[active_chat] = messages
    if selected_prompt:
        st.rerun()
