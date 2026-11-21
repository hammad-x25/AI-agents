"""Streamlit UI for the persistent, streaming LangGraph client."""

import asyncio

import streamlit as st

from ai_assignment01.agent import stream_turn


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
    [data-testid="stSidebar"] * { color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)


if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "student"


def reset_chat() -> None:
    st.session_state.ui_messages = []


def ask_agent(prompt: str, placeholder) -> str:
    streamed: list[str] = []

    def on_event(event: dict[str, str]) -> None:
        if event["type"] == "token":
            streamed.append(event["text"])
            placeholder.markdown("".join(streamed))
        elif event["type"] == "status" and not streamed:
            placeholder.caption(event["text"])

    response = asyncio.run(
        stream_turn(prompt, st.session_state.thread_id, on_event)
    )
    return response or "I couldn't produce a response. Please try again."


with st.sidebar:
    st.markdown("## 🎓 GPA Assistant")
    st.caption("PUCIT BS Computer Science")
    st.divider()
    st.text_input("Chat name", key="thread_id")
    if st.button("＋ New chat", use_container_width=True):
        reset_chat()
        st.rerun()
    st.markdown("### I can help with")
    st.markdown("GPA · CGPA projection · target planning · courses · credit hours · reports")
    st.divider()
    st.caption("Calculations come from tools on the GPA MCP server.")


st.title("🎓 PUCIT GPA Assistant")
st.markdown(
    "<p style='text-align:center;color:#6b7280'>GPA and CGPA planning for BS Computer Science students</p>",
    unsafe_allow_html=True,
)

for message in st.session_state.ui_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

selected_prompt = None
if not st.session_state.ui_messages:
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
    st.session_state.ui_messages.append({"role": "user", "content": prompt})
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
    st.session_state.ui_messages.append({"role": "assistant", "content": response})
    if selected_prompt:
        st.rerun()
