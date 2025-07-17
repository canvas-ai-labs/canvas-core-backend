from fastapi import APIRouter
from backend.services.canvas_client import get_user_courses, get_all_assignments

router = APIRouter()

@router.get("/courses")
def get_courses():
    courses = get_user_courses()
    return {"courses": courses}

@router.get("/assignments")
def get_assignments():
    assignments = get_all_assignments()
    return {"assignments": assignments}
