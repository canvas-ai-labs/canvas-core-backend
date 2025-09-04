from canvasapi import Canvas
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")

canvas = Canvas(API_URL, API_KEY)

def get_user_courses():
    user = canvas.get_current_user()
    # Only include active enrollments and available courses
    courses = user.get_courses(enrollment_state=["active"], state=["available"])
    return [{"id": course.id, "name": getattr(course, 'name', None)} for course in courses]

def get_all_assignments():
    user = canvas.get_current_user()
    # Only include active enrollments and available courses
    courses = user.get_courses(enrollment_state=["active"], state=["available"])
    all_assignments = []

    for course in courses:
        course_id = course.id
        try:
            course_obj = canvas.get_course(course_id)
            assignments = course_obj.get_assignments()
            for a in assignments:
                assignment_data = {
                    "course_id": course_id,
                    "assignment_id": a.id,
                    "name": a.name,
                    "due_at": a.due_at,
                    "html_url": getattr(a, 'html_url', None)
                }
                all_assignments.append(assignment_data)
        except Exception as e:
            print(f"[WARN] Failed to fetch assignments for course {course_id}: {e}")

    print(f"[DEBUG] Total assignments fetched: {len(all_assignments)}")
    return all_assignments
