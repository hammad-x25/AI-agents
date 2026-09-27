from pathlib import Path

from langchain_core.tools import tool


COURSES = {
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


@tool
def marks_to_grade_points(marks: int) -> float:
    """
    Use this tool when a student's numerical marks need to be converted
    into PUCIT grade points according to the official grading bands.
    """

    if marks < 0 or marks > 100:
        return "Error: marks must be between 0 and 100"

    if marks >= 85:
        return 4.0
    elif marks >= 80:
        return 3.7
    elif marks >= 75:
        return 3.3
    elif marks >= 70:
        return 3.0
    elif marks >= 65:
        return 2.7
    elif marks >= 61:
        return 2.3
    elif marks >= 58:
        return 2.0
    elif marks >= 55:
        return 1.7
    elif marks >= 50:
        return 1.0
    else:
        return 0.0


@tool
def calculate_semester_gpa(
    grade_points: list[float],
    credit_hours: list[float]
) -> float:
    """
    Use this tool when grade points and credit hours for all graded
    courses in a semester are available and the semester GPA needs
    to be calculated.
    """

    if len(grade_points) == 0:
        return "Error: grade points cannot be empty"

    if len(credit_hours) == 0:
        return "Error: credit hours cannot be empty"

    if len(grade_points) != len(credit_hours):
        return "Error: grade_points and credit_hours must have the same length"

    if any(gp < 0 or gp > 4 for gp in grade_points):
        return "Error: grade points must be between 0 and 4"

    if any(ch <= 0 for ch in credit_hours):
        return "Error: credit hours must be greater than 0"

    weighted_points = sum(
        grade_point * credit_hour
        for grade_point, credit_hour in zip(grade_points, credit_hours)
    )

    total_credit_hours = sum(credit_hours)

    if total_credit_hours <= 0:
        return "Error: total credit hours must be greater than 0"

    semester_gpa = weighted_points / total_credit_hours

    return round(semester_gpa, 2)

@tool
def calculate_new_cgpa(
    current_cgpa: float,
    completed_credit_hours: float,
    semester_gpa: float,
    semester_credit_hours: float
) -> float:
    """
    Use this tool when a student's current CGPA, completed credit hours,
    semester GPA and semester credit hours are known and the projected
    CGPA after that semester is needed.
    """

    if current_cgpa < 0 or current_cgpa > 4:
        return "Error: current CGPA must be between 0 and 4"

    if semester_gpa < 0 or semester_gpa > 4:
        return "Error: semester GPA must be between 0 and 4"

    if completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative"

    if semester_credit_hours <= 0:
        return "Error: semester credit hours must be greater than 0"

    total_points = (
        current_cgpa * completed_credit_hours
        + semester_gpa * semester_credit_hours
    )

    total_credit_hours = (
        completed_credit_hours + semester_credit_hours
    )

    new_cgpa = total_points / total_credit_hours

    return round(new_cgpa, 2)


@tool
def required_gpa_for_target(
    target_cgpa: float,
    current_cgpa: float,
    completed_credit_hours: float,
    remaining_credit_hours: float
) -> float:
    """
    Use this tool when a student wants to know the average GPA required
    over a specified number of future credit hours to reach a target CGPA.

    The returned GPA may be greater than 4.0. The agent must interpret
    values above 4.0 as impossible for that particular credit-hour horizon
    and try a longer horizon when appropriate.
    """

    if target_cgpa < 0 or target_cgpa > 4:
        return "Error: target CGPA must be between 0 and 4"

    if current_cgpa < 0 or current_cgpa > 4:
        return "Error: current CGPA must be between 0 and 4"

    if completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative"

    if remaining_credit_hours <= 0:
        return "Error: remaining credit hours must be greater than 0"

    total_credit_hours = (
        completed_credit_hours + remaining_credit_hours
    )

    target_total_points = (
        target_cgpa * total_credit_hours
    )

    current_total_points = (
        current_cgpa * completed_credit_hours
    )

    required_future_points = (
        target_total_points - current_total_points
    )

    required_gpa = (
        required_future_points / remaining_credit_hours
    )

    return round(required_gpa, 2)

@tool
def get_semester_courses(semester: int) -> str:
    """
    Use this tool when the courses and credit hours for a particular
    PUCIT BS Computer Science semester are needed.
    """

    if semester < 1 or semester > 8:
        return "Error: semester must be between 1 and 8"

    courses = COURSES[semester]

    lines = [f"Semester {semester} courses:"]

    total_credit_hours = 0.0

    for code, course_name, credit_hours in courses:
        lines.append(
            f"{code} - {course_name} - {credit_hours} credit hours"
        )

        total_credit_hours += credit_hours

    lines.append(
        f"Total graded credit hours: {total_credit_hours}"
    )

    return "\n".join(lines)

@tool
def get_remaining_credit_hours(current_semester: int) -> float:
    """
    Use this tool when the total graded credit hours remaining from the
    student's current semester through Semester 8 are needed.

    The current semester is included because a student who says they are
    in Semester 5 has not yet completed Semester 5.
    """

    if current_semester < 1 or current_semester > 8:
        return "Error: semester must be between 1 and 8"

    remaining_credit_hours = 0.0

    for semester in range(current_semester, 9):
        for _, _, credit_hours in COURSES[semester]:
            remaining_credit_hours += credit_hours

    return remaining_credit_hours


@tool
def save_report(filename: str, content: str) -> str:
    """
    Use this tool only when the student explicitly asks to save a useful
    result such as a semester GPA, projected CGPA, or target-CGPA plan.
    Do not use it automatically.
    """

    if not filename.strip():
        return "Error: filename cannot be empty"

    if not content.strip():
        return "Error: report content cannot be empty"

    try:
        path = Path(filename)

        path.write_text(
            content,
            encoding="utf-8"
        )

        return f"Report saved successfully to {filename}"

    except OSError as error:
        return f"Error: could not save report: {error}"


@tool
def get_credit_hours_for_range(
    start_semester: int,
    end_semester: int
) -> float:
    """
    Use this tool to calculate the total graded credit hours
    from start_semester through end_semester, inclusive.

    Use it to determine completed credit hours or the credit hours
    in a target-CGPA planning horizon.
    """

    if start_semester < 1 or start_semester > 8:
        return "Error: start semester must be between 1 and 8"

    if end_semester < 1 or end_semester > 8:
        return "Error: end semester must be between 1 and 8"

    if start_semester > end_semester:
        return "Error: start semester cannot be after end semester"

    total = 0.0

    for semester in range(start_semester, end_semester + 1):
        for _, _, credit_hours in COURSES[semester]:
            total += credit_hours

    return total    