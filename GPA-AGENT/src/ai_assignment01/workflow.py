from langgraph.graph import StateGraph,MessagesState,START,END
from llm import llm 
from tools import (
    marks_to_grade_points,
    calculate_semester_gpa,
    calculate_new_cgpa,
    required_gpa_for_target,
    get_semester_courses,
    get_remaining_credit_hours,
    save_report,
    get_credit_hours_for_range
)
from agent import SYSTEM_PROMPT
from langchain.messages import HumanMessage,SystemMessage,AnyMessage
from typing import TypedDict,Annotated
import operator

class GradeState(TypedDict):
    marks:list[int]
    credit_hours:list[float]
    gpa:float
    gradepoint:list[float]

class MessagesState(TypedDict):
    messages:Annotated[AnyMessage,operator.add]

def model(state:MessagesState)->dict:
    reply=llm.invoke([SystemMessage(SYSTEM_PROMPT)]+state["messages"])
    return {"messages":[reply]}


builder=StateGraph(MessagesState)

builder.add_node("model",model)
builder.add_edge(START,"model")
builder.add_edge("model",END)
app=builder.compile()

Question=input()
ans=app.invoke({"messages":[HumanMessage(Question)]})


print(ans["messages"].content)

