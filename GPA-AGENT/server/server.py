"""Standalone FastMCP server for the PUCIT GPA assistant."""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

try:
    from .tools import (
        calculate_new_cgpa,
        calculate_semester_gpa,
        get_credit_hours,
        get_credit_hours_for_range,
        get_remaining_credit_hours,
        get_semester_courses,
        marks_to_grade_points,
        required_gpa_for_target,
        save_report,
    )
except ImportError:  # ``python server/server.py`` puts server/ on sys.path.
    from tools import (
        calculate_new_cgpa,
        calculate_semester_gpa,
        get_credit_hours,
        get_credit_hours_for_range,
        get_remaining_credit_hours,
        get_semester_courses,
        marks_to_grade_points,
        required_gpa_for_target,
        save_report,
    )

load_dotenv()

mcp = FastMCP("pucit-gpa")

for function in (
    marks_to_grade_points,
    calculate_semester_gpa,
    calculate_new_cgpa,
    required_gpa_for_target,
    get_semester_courses,
    get_credit_hours_for_range,
    get_credit_hours,
    get_remaining_credit_hours,
    save_report,
):
    mcp.tool(function)


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    host = os.getenv(
        "MCP_HOST",
        "0.0.0.0" if os.getenv("PORT") else "127.0.0.1",
    )
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
    )
