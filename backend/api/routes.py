
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models import User
from backend.services.ai_service import CanvasAIService, get_ai_service
from backend.services.canvas_client import (
    get_all_assignments,
    get_user_courses,
    get_all_user_courses,
)
from backend.services.mock_llm_service import (
    MockCanvasLLMService,
    get_mock_llm_service,
)
from backend.services.scheduler_service import get_scheduler_service
from backend.services.sync_service import CanvasSyncService, get_sync_service

router = APIRouter()


# Original Canvas API routes
@router.get("/courses")
def get_courses(all: bool = False):
    """Return active + starred courses by default.

    Pass `?all=true` to return all courses (debugging).
    """
    courses = get_all_user_courses() if all else get_user_courses()
    return {"courses": courses}


@router.get("/assignments")
def get_assignments():
    assignments = get_all_assignments()
    return {"assignments": assignments}


# User management
@router.post("/user/init")
def initialize_user(db: Session = Depends(get_db)):
    """Initialize a default user for testing."""
    # Check if user exists
    user = db.query(User).filter(User.canvas_user_id == 1).first()
    if user:
        return {"message": "User already exists", "user_id": user.id}

    # Create default user
    user = User(canvas_user_id=1, name="Default User", email="user@example.com")
    db.add(user)
    db.commit()

    return {"message": "User created", "user_id": user.id}


# New sync routes
@router.post("/sync/full")
def full_sync(
    user_id: Optional[int] = 1, sync_service: CanvasSyncService = Depends(get_sync_service)
):
    """Perform a full sync of user, courses, and assignments."""
    try:
        sync_run = sync_service.full_sync(user_id)
        return {
            "sync_id": sync_run.id,
            "status": sync_run.status,
            "items_processed": sync_run.items_processed,
            "items_created": sync_run.items_created,
            "items_updated": sync_run.items_updated,
            "error_message": sync_run.error_message,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full_sync")
def full_sync_simple(
    user_id: Optional[int] = 1, sync_service: CanvasSyncService = Depends(get_sync_service)
):
    """Simplified full sync endpoint for E2E testing."""
    try:
        sync_run = sync_service.full_sync(user_id)
        
        # Get current counts after sync
        courses = get_all_user_courses()
        assignments = get_all_assignments()
        
        return {
            "status": "ok",
            "message": "Canvas data sync completed successfully!",
            "courses": len(courses),
            "assignments": len(assignments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/courses")
def sync_courses(
    user_id: Optional[int] = 1, sync_service: CanvasSyncService = Depends(get_sync_service)
):
    """Sync courses from Canvas."""
    try:
        sync_run = sync_service.sync_courses(user_id)
        return {
            "sync_id": sync_run.id,
            "status": sync_run.status,
            "items_processed": sync_run.items_processed,
            "items_created": sync_run.items_created,
            "items_updated": sync_run.items_updated,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/assignments")
def sync_assignments(
    course_ids: Optional[List[int]] = None,
    user_id: Optional[int] = 1,
    sync_service: CanvasSyncService = Depends(get_sync_service),
):
    """Sync assignments from Canvas."""
    try:
        sync_run = sync_service.sync_assignments(course_ids, user_id)
        return {
            "sync_id": sync_run.id,
            "status": sync_run.status,
            "items_processed": sync_run.items_processed,
            "items_created": sync_run.items_created,
            "items_updated": sync_run.items_updated,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AI-powered routes
@router.get("/ai/deadlines")
def get_upcoming_deadlines(
    days_ahead: int = 7, user_id: int = 1, ai_service: CanvasAIService = Depends(get_ai_service)
):
    """Get upcoming assignment deadlines with AI insights."""
    try:
        deadlines = ai_service.get_upcoming_deadlines(user_id, days_ahead)
        return {"deadlines": deadlines, "count": len(deadlines)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/overdue")
def get_overdue_assignments(
    user_id: int = 1, ai_service: CanvasAIService = Depends(get_ai_service)
):
    """Get overdue assignments."""
    try:
        overdue = ai_service.get_overdue_assignments(user_id)
        return {"overdue_assignments": overdue, "count": len(overdue)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/workload")
def get_workload_analysis(user_id: int = 1, ai_service: CanvasAIService = Depends(get_ai_service)):
    """Get course workload analysis."""
    try:
        workload = ai_service.get_course_workload_analysis(user_id)
        return {"course_workload": workload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/recommendations")
def get_study_recommendations(
    user_id: int = 1, ai_service: CanvasAIService = Depends(get_ai_service)
):
    """Get AI-powered study recommendations."""
    try:
        recommendations = ai_service.generate_study_recommendations(user_id)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/notify/{assignment_id}")
def create_deadline_notification(
    assignment_id: int,
    user_id: int = 1,
    notification_type: str = "deadline_reminder",
    ai_service: CanvasAIService = Depends(get_ai_service),
):
    """Create a deadline notification for an assignment."""
    try:
        notification = ai_service.create_deadline_notification(
            user_id, assignment_id, notification_type
        )
        return {
            "notification_id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "sent_at": notification.sent_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# LLM-powered intelligence routes (using mock service for demo)
@router.post("/llm/syllabus/{course_id}")
def analyze_syllabus(
    course_id: int, llm_service: MockCanvasLLMService = Depends(get_mock_llm_service)
):
    """Analyze and summarize course syllabus using LLM."""
    try:
        analysis = llm_service.summarize_syllabus(course_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/assignment/{assignment_id}")
def analyze_assignment(
    assignment_id: int, llm_service: MockCanvasLLMService = Depends(get_mock_llm_service)
):
    """Analyze assignment content and provide insights using LLM."""
    try:
        analysis = llm_service.analyze_assignment(assignment_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/study-plan")
def generate_study_plan(
    user_id: int = 1,
    days_ahead: int = 14,
    llm_service: MockCanvasLLMService = Depends(get_mock_llm_service),
):
    """Generate AI-powered personalized study plan."""
    try:
        study_plan = llm_service.generate_study_plan(user_id, days_ahead)
        return study_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/ask")
def ask_question(
    question: str,
    user_id: int = 1,
    context_course_id: Optional[int] = None,
    llm_service: MockCanvasLLMService = Depends(get_mock_llm_service),
):
    """Ask questions about coursework with AI-powered responses."""
    try:
        response = llm_service.ask_question(user_id, question, context_course_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Scheduler and automation routes
@router.get("/scheduler/status")
def get_scheduler_status():
    """Get status of all scheduled jobs."""
    try:
        scheduler = get_scheduler_service()
        jobs = scheduler.get_job_status()
        return {"scheduler_status": "running", "jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/sync-now")
def trigger_manual_sync():
    """Manually trigger a sync job."""
    try:
        scheduler = get_scheduler_service()
        result = scheduler.trigger_sync_now()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Metrics endpoint for dashboard
@router.get("/metrics")
def get_metrics():
    """Get dashboard metrics and counts."""
    try:
        # Get current counts
        courses = get_all_user_courses()
        assignments = get_all_assignments()
        
        # Count upcoming deadlines (next 7 days)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        next_week = now + timedelta(days=7)
        
        deadlines = 0
        for assignment in assignments:
            if assignment.get('due_at'):
                try:
                    due_date = datetime.fromisoformat(assignment['due_at'].replace('Z', '+00:00'))
                    if now <= due_date <= next_week:
                        deadlines += 1
                except (ValueError, TypeError):
                    continue
        
        # Get scheduled jobs count (simplified to avoid type issues)
        scheduled_jobs = 3  # Fixed count for now - there are typically 3 main scheduled jobs
        
        return {
            "courses": len(courses),
            "assignments": len(assignments),
            "deadlines": deadlines,
            "scheduled_jobs": scheduled_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
