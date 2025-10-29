import os
from typing import Any, List

from dotenv import load_dotenv

load_dotenv()


def _get_canvas():
    # Lazy import to keep canvasapi optional until actually used
    try:
        from canvasapi import Canvas  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Canvas API client is not available. Install 'canvasapi' to use Canvas features."
        ) from exc
    api_url = os.getenv("CANVAS_API_URL")
    api_key = os.getenv("CANVAS_API_KEY")
    if not api_url or not api_key:
        raise RuntimeError("Canvas API not configured. Set CANVAS_API_URL and CANVAS_API_KEY.")
    return Canvas(api_url, api_key)


def _serialize_course(course: Any) -> dict[str, Any]:
    term_obj = getattr(course, "term", None)
    term_name = getattr(term_obj, "name", None) if term_obj is not None else None
    return {
        "id": course.id,
        "name": getattr(course, "name", None),
        "term": term_name or "N/A",
        "account_id": getattr(course, "account_id", None),
    }


def get_user_courses() -> List[dict[str, Any]]:
    """Fetch current user's courses filtered to active + starred.

    - Active: enrollment_state="active"
    - Starred: cross-reference with get_favorite_courses()

    Returns empty list if Canvas is not configured.
    """
    try:
        canvas = _get_canvas()
    except Exception as e:
        print(f"[WARN] Canvas not configured: {e}")
        return []

    user = canvas.get_current_user()
    # Include term to populate display name when available
    try:
        active_courses = list(
            user.get_courses(enrollment_state=["active"], include=["term"])  # type: ignore[arg-type]
        )
    except Exception as e:
        print(f"[WARN] Failed to fetch active courses: {e}")
        active_courses = []

    try:
        favorites = {c.id for c in user.get_favorite_courses()}
    except Exception as e:
        print(f"[WARN] Failed to fetch favorite courses: {e}")
        favorites = set()

    filtered = [c for c in active_courses if c.id in favorites]
    return [_serialize_course(c) for c in filtered]


def get_all_user_courses() -> List[dict[str, Any]]:
    """Fetch all courses for the current user (unfiltered, for debugging).

    Attempts to include term when available.
    """
    try:
        canvas = _get_canvas()
    except Exception as e:
        print(f"[WARN] Canvas not configured: {e}")
        return []

    user = canvas.get_current_user()
    try:
        courses = list(user.get_courses(include=["term"]))  # type: ignore[arg-type]
    except Exception as e:
        print(f"[WARN] Failed to fetch all courses: {e}")
        courses = []
    return [_serialize_course(c) for c in courses]


def get_all_assignments() -> List[dict[str, Any]]:
    """Fetch assignments from all active, available courses for the current user."""
    try:
        canvas = _get_canvas()
    except Exception as e:
        print(f"[WARN] Canvas not configured: {e}")
        return []

    user = canvas.get_current_user()
    courses = user.get_courses(enrollment_state=["active"], state=["available"])
    all_assignments: List[dict[str, Any]] = []

    for course in courses:
        course_id = course.id
        try:
            course_obj = canvas.get_course(course_id)
            assignments = course_obj.get_assignments()
            for a in assignments:
                assignment_data = {
                    "course_id": course_id,
                    "assignment_id": a.id,
                    "name": getattr(a, "name", None),
                    "due_at": getattr(a, "due_at", None),
                    "html_url": getattr(a, "html_url", None),
                }
                all_assignments.append(assignment_data)
        except Exception as e:
            print(f"[WARN] Failed to fetch assignments for course {course_id}: {e}")

    print(f"[DEBUG] Total assignments fetched: {len(all_assignments)}")
    return all_assignments
