"""The tools exposed by the GPA MCP server.

These functions deliberately contain no LangChain or agent code.  Any MCP
client can discover and call them through ``server.py``.
"""

from pathlib import Path


COURSES: dict[int, list[tuple[str, str, float]]] = {
    1: [
        ("MS-251", "Probability & Statistics", 3.0),
        ("GE-160", "Applications of ICT", 3.0),
        ("GE-169", "Applied Physics", 3.0),
        ("GE-167", "Discrete Structures", 3.0),
        ("HQ-001", "Quran Translation - I", 0.5),
        ("GE-190", "Functional English", 3.0),
    ],
    2: [
        ("CC-112", "Programming Fundamentals", 3.0),
        ("CC-112-L", "Programming Fundamentals Lab", 1.0),
        ("CC-110", "Digital Logic Design", 2.0),
        ("CC-110-L", "Digital Logic Design Lab", 1.0),
        ("MS-252", "Linear Algebra", 3.0),
        ("GE-191", "Expository Writing", 3.0),
        ("GE-163", "Islamic Studies", 2.0),
        ("HQ-002", "Quran Translation - II", 0.5),
    ],
    3: [
        ("CC-211", "Object Oriented Programming", 3.0),
        ("CC-211-L", "Object Oriented Programming Lab", 1.0),
        ("CC-215", "Database Systems", 3.0),
        ("CC-215-L", "Database Systems Lab", 1.0),
        ("CC-210", "Computer Organization & Assembly Language", 3.0),
        ("GE-162", "Calculus & Analytical Geometry", 3.0),
        ("GE-192", "Introduction to Management", 2.0),
        ("HQ-003", "Quran Translation - III", 0.5),
    ],
    4: [
        ("CC-213", "Data Structures", 3.0),
        ("CC-213-L", "Data Structures Lab", 1.0),
        ("CC-312", "Information Security", 3.0),
        ("CC-214", "Computer Networks", 3.0),
        ("CC-212", "Software Engineering", 3.0),
        ("DC-220", "Advanced Database Management Systems", 3.0),
        ("HQ-004", "Quran Translation - IV", 0.5),
    ],
    5: [
        ("CC-313", "Analysis of Algorithms", 3.0),
        ("CC-310", "Artificial Intelligence", 3.0),
        ("DC-320", "Theory of Automata and Formal Languages", 3.0),
        ("DC-321", "Human Computer Interaction", 3.0),
        ("DC-322", "Computer Architecture", 3.0),
        ("EC-330", "Web Technologies / Elective", 3.0),
        ("HQ-005", "Quran Translation - V", 0.5),
    ],
    6: [
        ("CC-311", "Operating Systems", 3.0),
        ("EC-333", "Mobile Application Development / Elective", 3.0),
        ("EC-324", "Software Construction & Development / Elective", 3.0),
        ("EC-335", "Machine Learning / Elective", 3.0),
        ("EC-334", "Game Design and Development / Elective", 3.0),
        ("MS-253", "Multivariable Calculus", 3.0),
        ("HQ-006", "Quran Translation - VI", 0.5),
    ],
    7: [
        ("CC-411", "Final Year Project - I", 2.0),
        ("DC-328", "Parallel & Distributed Computing", 3.0),
        ("EC-345", "Computer Vision / Elective", 3.0),
        ("EC-425", "Software Quality Engineering / Elective", 3.0),
        ("MS-254", "Technical and Business Writing", 3.0),
        ("GE-263", "Entrepreneurship", 2.0),
        ("GE-262", "Professional Practices", 2.0),
        ("HQ-007", "Quran Translation - VII", 0.5),
    ],
    8: [
        ("CC-412", "Final Year Project - II", 4.0),
        ("DC-421", "Compiler Construction", 3.0),
        ("UE-272", "Introduction to Marketing", 3.0),
        ("GE-168", "Ideology and Constitution of Pakistan", 2.0),
        ("GE-363", "Civics and Community Engagement", 2.0),
        ("HQ-008", "Quran Translation - VIII", 0.5),
    ],
}


def marks_to_grade_points(marks: int) -> float | str:
    """Convert marks from 0-100 to the official PUCIT grade points."""
    if marks < 0 or marks > 100:
        return "Error: marks must be between 0 and 100"
    if marks >= 85:
        return 4.0
    if marks >= 80:
        return 3.7
    if marks >= 75:
        return 3.3
    if marks >= 70:
        return 3.0
    if marks >= 65:
        return 2.7
    if marks >= 61:
        return 2.3
    if marks >= 58:
        return 2.0
    if marks >= 55:
        return 1.7
    if marks >= 50:
        return 1.0
    return 0.0


def calculate_semester_gpa(
    grade_points: list[float], credit_hours: list[float]
) -> float | str:
    """Calculate a credit-weighted GPA from matching grade and credit lists."""
    if not grade_points:
        return "Error: grade points cannot be empty"
    if not credit_hours:
        return "Error: credit hours cannot be empty"
    if len(grade_points) != len(credit_hours):
        return "Error: grade_points and credit_hours must have the same length"
    if any(gp < 0 or gp > 4 for gp in grade_points):
        return "Error: grade points must be between 0 and 4"
    if any(ch <= 0 for ch in credit_hours):
        return "Error: credit hours must be greater than 0"
    total_credit_hours = sum(credit_hours)
    if total_credit_hours <= 0:
        return "Error: total credit hours must be greater than 0"
    return round(
        sum(gp * ch for gp, ch in zip(grade_points, credit_hours))
        / total_credit_hours,
        2,
    )


def calculate_new_cgpa(
    current_cgpa: float,
    completed_credit_hours: float,
    semester_gpa: float,
    semester_credit_hours: float,
) -> float | str:
    """Project CGPA after adding one semester."""
    if current_cgpa < 0 or current_cgpa > 4:
        return "Error: current CGPA must be between 0 and 4"
    if semester_gpa < 0 or semester_gpa > 4:
        return "Error: semester GPA must be between 0 and 4"
    if completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative"
    if semester_credit_hours <= 0:
        return "Error: semester credit hours must be greater than 0"
    total_points = current_cgpa * completed_credit_hours + semester_gpa * semester_credit_hours
    return round(total_points / (completed_credit_hours + semester_credit_hours), 2)


def required_gpa_for_target(
    target_cgpa: float,
    current_cgpa: float,
    completed_credit_hours: float,
    remaining_credit_hours: float,
) -> float | str:
    """Find the average future GPA needed to reach a target CGPA."""
    if target_cgpa < 0 or target_cgpa > 4:
        return "Error: target CGPA must be between 0 and 4"
    if current_cgpa < 0 or current_cgpa > 4:
        return "Error: current CGPA must be between 0 and 4"
    if completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative"
    if remaining_credit_hours <= 0:
        return "Error: remaining credit hours must be greater than 0"
    total_hours = completed_credit_hours + remaining_credit_hours
    return round(
        (target_cgpa * total_hours - current_cgpa * completed_credit_hours)
        / remaining_credit_hours,
        2,
    )


def get_semester_courses(semester: int) -> str:
    """List the authoritative courses and graded hours for a semester."""
    if semester < 1 or semester > 8:
        return "Error: semester must be between 1 and 8"
    lines = [f"Semester {semester} courses:"]
    total = 0.0
    for code, name, hours in COURSES[semester]:
        lines.append(f"{code} - {name} - {hours} credit hours")
        total += hours
    lines.append(f"Total graded credit hours: {total}")
    return "\n".join(lines)


def get_credit_hours_for_range(start_semester: int, end_semester: int) -> float | str:
    """Sum graded credit hours from start semester through end semester."""
    if start_semester < 1 or start_semester > 8:
        return "Error: start semester must be between 1 and 8"
    if end_semester < 1 or end_semester > 8:
        return "Error: end semester must be between 1 and 8"
    if start_semester > end_semester:
        return "Error: start semester cannot be after end semester"
    return round(
        sum(
            hours
            for semester in range(start_semester, end_semester + 1)
            for _, _, hours in COURSES[semester]
        ),
        2,
    )


def get_remaining_credit_hours(current_semester: int) -> float | str:
    """Sum graded hours from the current semester through semester 8."""
    return get_credit_hours_for_range(current_semester, 8)


def get_credit_hours(semesters: list[int]) -> float | str:
    """Compatibility helper: sum the graded hours for an explicit semester list."""
    if not semesters:
        return "Error: semesters cannot be empty"
    if any(semester < 1 or semester > 8 for semester in semesters):
        return "Error: semesters must be between 1 and 8"
    return round(sum(get_credit_hours_for_range(semester, semester) for semester in semesters), 2)


def save_report(filename: str, content: str) -> str:
    """Save a report only after the student explicitly requests it."""
    if not filename.strip():
        return "Error: filename cannot be empty"
    if not content.strip():
        return "Error: report content cannot be empty"
    try:
        Path(filename).write_text(content, encoding="utf-8")
    except OSError as error:
        return f"Error: could not save report: {error}"
    return f"Report saved successfully to {filename}"
