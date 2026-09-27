import streamlit as st

from langchain.messages import HumanMessage
from agent import agent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PUCIT GPA Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.html("""
<style>

/* ---------------------------------------------------------
   GLOBAL
--------------------------------------------------------- */

.stApp {
    background-color: #f7f7f8;
}

.block-container {
    max-width: 900px;
    padding-top: 1.5rem;
    padding-bottom: 7rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ---------------------------------------------------------
   MAIN TITLE
--------------------------------------------------------- */

h1 {
    text-align: center;
    color: #202123;
    font-weight: 750;
    margin-bottom: 0.25rem;
}


/* ---------------------------------------------------------
   CHAT
--------------------------------------------------------- */

[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.025);
}

[data-testid="stChatInput"] {
    border-radius: 14px;
}


/* ---------------------------------------------------------
   BUTTONS
--------------------------------------------------------- */

.stButton > button {
    width: 100%;
    min-height: 44px;
    border-radius: 11px;
    border: 1px solid #d1d5db;
    background-color: white;
    color: #202123;
    font-weight: 500;
    transition: 0.15s ease;
}

.stButton > button:hover {
    background-color: #f3f4f6;
    border-color: #9ca3af;
}


/* ---------------------------------------------------------
   SIDEBAR
--------------------------------------------------------- */

[data-testid="stSidebar"] {
    background-color: #202123;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p {
    color: white;
}

[data-testid="stSidebar"] hr {
    border-color: #343541;
}

[data-testid="stSidebar"] button {
    background-color: #343541 !important;
    color: white !important;
    border: 1px solid #565869 !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] button:hover {
    background-color: #40414f !important;
    border-color: #6b6c7b !important;
}


/* ---------------------------------------------------------
   RESPONSIVE
--------------------------------------------------------- */

@media (max-width: 700px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

}

</style>
""")


# ============================================================
# SESSION STATE
# ============================================================

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []


# ============================================================
# HELPERS
# ============================================================

def reset_chat():
    st.session_state.ui_messages = []
    st.session_state.agent_messages = []


def extract_text(message) -> str:
    """
    Safely extracts the final text from a LangChain message.
    """

    text = getattr(message, "text", None)

    if isinstance(text, str) and text.strip():
        return text.strip()

    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip()

    return ""


def send_to_agent(prompt: str) -> str:
    """
    Send a message to the agent while preserving the complete
    LangChain conversation and tool history.
    """

    st.session_state.agent_messages.append(
        HumanMessage(content=prompt)
    )

    result = agent.invoke(
        {
            "messages": st.session_state.agent_messages
        }
    )

    # Keep full history including tool calls/tool results
    st.session_state.agent_messages = result["messages"]

    final_message = result["messages"][-1]

    response = extract_text(final_message)

    if not response:
        return (
            "I couldn't complete the request properly. "
            "Please provide the missing academic information "
            "or try again."
        )

    return response


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎓 GPA Assistant")

    st.caption("PUCIT BS Computer Science")

    st.divider()

    if st.button(
        "＋ New Chat",
        use_container_width=True,
    ):
        reset_chat()
        st.rerun()

    st.markdown("### I can help with")

    st.markdown(
        """
- 📊 Semester GPA
- 🎯 Target CGPA
- 📈 CGPA projection
- 📚 Course credit hours
- 🔢 Grade points
- 💾 Saving reports
        """
    )

    st.divider()

    st.caption(
        "GPA and CGPA calculations are performed using "
        "academic tools instead of being estimated by the model."
    )


# ============================================================
# HEADER
# ============================================================

st.title("🎓 PUCIT GPA Assistant")

st.markdown(
    "<p style='text-align:center; color:#6b7280;'>"
    "GPA & CGPA planning for BS Computer Science students"
    "</p>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center;'>"
    "<span style='"
    "background:#dcfce7;"
    "color:#166534;"
    "padding:5px 12px;"
    "border-radius:20px;"
    "font-size:12px;"
    "font-weight:600;'>"
    "● Online"
    "</span>"
    "</p>",
    unsafe_allow_html=True,
)


# ============================================================
# WELCOME SCREEN
# ============================================================

selected_prompt = None

if not st.session_state.ui_messages:

    st.write("")

    with st.container(border=True):

        st.markdown(
            "<h3 style='text-align:center;'>"
            "How can I help with your GPA?"
            "</h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align:center; color:#6b7280;'>"
            "Calculate your GPA, project your CGPA, check course "
            "credit hours, or plan toward a target CGPA."
            "</p>",
            unsafe_allow_html=True,
        )

    st.write("")

    st.caption("Try an example")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📊 Calculate GPA",
            use_container_width=True,
        ):
            selected_prompt = (
                "I got 78 in Analysis of Algorithms, "
                "85 in Artificial Intelligence, and "
                "64 in Human Computer Interaction. "
                "These are Semester 5 courses. "
                "What is my GPA?"
            )

        if st.button(
            "📚 Semester 5 courses",
            use_container_width=True,
        ):
            selected_prompt = (
                "Show me the courses and credit hours "
                "for Semester 5."
            )

    with col2:

        if st.button(
            "🎯 Plan target CGPA",
            use_container_width=True,
        ):
            selected_prompt = (
                "My current CGPA is 3.0. "
                "I am entering Semester 5 and "
                "I want to reach a 3.4 CGPA."
            )

        if st.button(
            "📈 Project my CGPA",
            use_container_width=True,
        ):
            selected_prompt = (
                "I want to calculate what my CGPA "
                "will become after this semester."
            )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.ui_messages:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):
            st.markdown(message["content"])

    else:

        with st.chat_message(
            "assistant",
            avatar="🎓",
        ):
            st.markdown(message["content"])


# ============================================================
# INPUT
# ============================================================

typed_prompt = st.chat_input(
    "Ask about GPA, CGPA, courses, marks or your target..."
)

prompt = typed_prompt or selected_prompt


# ============================================================
# PROCESS MESSAGE
# ============================================================

if prompt:

    # Store visible user message
    st.session_state.ui_messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # Display current user message
    with st.chat_message(
        "user",
        avatar="👤",
    ):
        st.markdown(prompt)


    # Generate assistant response
    with st.chat_message(
        "assistant",
        avatar="🎓",
    ):

        with st.spinner(
            "Checking your academic information..."
        ):

            try:

                response = send_to_agent(prompt)

            except Exception as error:

                print("AGENT ERROR:", error)

                response = (
                    "Something went wrong while processing "
                    "your request. Please try again."
                )

        st.markdown(response)


    # Store visible assistant reply
    st.session_state.ui_messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )


    # If an example button was used, rerun so the welcome
    # screen disappears and only the chat remains.
    if selected_prompt:
        st.rerun()