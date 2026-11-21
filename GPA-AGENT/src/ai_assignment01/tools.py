"""Backward-compatible imports for tools hosted by the MCP server."""

from server.tools import (
    COURSES,
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

__all__ = [
    "COURSES",
    "marks_to_grade_points",
    "calculate_semester_gpa",
    "calculate_new_cgpa",
    "required_gpa_for_target",
    "get_semester_courses",
    "get_credit_hours_for_range",
    "get_credit_hours",
    "get_remaining_credit_hours",
    "save_report",
]
