# PUCIT GPA/CGPA Assistant

This project is a conversational AI agent for PUCIT BS Computer Science students. It helps students calculate GPA, project CGPA, check semester course credit hours, and plan for a target CGPA.

## How the Agent Works

The agent uses LangChain with the Groq `openai/gpt-oss-20b` model.

The LLM does not perform calculations itself. Instead, it decides which tool to call and passes the required values to that tool.

Examples of tools include:

- `marks_to_grade_points`
- `calculate_semester_gpa`
- `calculate_new_cgpa`
- `required_gpa_for_target`
- `get_semester_courses`
- `get_credit_hours_for_range`
- `save_report`

Conversation history is preserved during the current program run so the agent can remember previous user messages and tool results.

## Files

- `llm.py` — creates the Groq language model
- `tools.py` — contains GPA/CGPA calculation and curriculum tools
- `agent.py` — creates the conversational agent and system prompt
- `app.py` — Streamlit chat interface
- `.env.example` — example environment variable file

## Run

Install dependencies and start the Streamlit application:

```bash
uv run streamlit run app.py