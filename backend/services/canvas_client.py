from canvasapi import Canvas
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")

canvas = Canvas(API_URL, API_KEY)

def get_user_courses():
    user = canvas.get_current_user()
    courses = user.get_courses()
    return [{"id": course.id} for course in courses]

def get_all_assignments():
    user = canvas.get_current_user()
    courses = user.get_courses()
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
                    "due_at": a.due_at
                }
                all_assignments.append(assignment_data)
        except Exception as e:
            print(f"[WARN] Failed to fetch assignments for course {course_id}: {e}")

    print(f"[DEBUG] Total assignments fetched: {len(all_assignments)}")
    return all_assignments
