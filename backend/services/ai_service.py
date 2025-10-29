"""
AI-powered analysis service for Canvas data.
Provides intelligent insights, deadline tracking, and content summarization.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models import Assignment, Course, NotificationLog


class CanvasAIService:
    """AI service for Canvas data analysis and insights."""

    def __init__(self, db: Session):
        self.db = db

    def get_upcoming_deadlines(self, user_id: int, days_ahead: int = 7) -> List[dict[str, Any]]:
        """Get assignments due in the next N days."""
        cutoff_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        current_time = datetime.now(timezone.utc)

        upcoming_assignments = (
            self.db.query(Assignment)
            .join(Course)
            .filter(
                and_(
                    Assignment.due_at.isnot(None),
                    Assignment.due_at >= current_time,
                    Assignment.due_at <= cutoff_date,
                    Assignment.workflow_state != "deleted",
                )
            )
            .order_by(Assignment.due_at)
            .all()
        )

        deadlines: List[dict[str, Any]] = []
        for assignment in upcoming_assignments:
            days_until_due = (assignment.due_at - current_time).days
            if days_until_due <= 1:
                urgency = "high"
            elif days_until_due <= 3:
                urgency = "medium"
            else:
                urgency = "low"

            deadlines.append(
                {
                    "assignment_id": assignment.canvas_assignment_id,
                    "name": assignment.name,
                    "course_name": assignment.course.name,
                    "due_at": assignment.due_at.isoformat(),
                    "days_until_due": days_until_due,
                    "urgency": urgency,
                    "points_possible": assignment.points_possible,
                    "html_url": assignment.html_url,
                    "submission_types": (
                        assignment.submission_types.split(",")
                        if assignment.submission_types
                        else []
                    ),
                }
            )

        return deadlines

    def get_overdue_assignments(self, user_id: int) -> List[dict[str, Any]]:
        """Get assignments that are past due."""
        current_time = datetime.now(timezone.utc)

        overdue_assignments = (
            self.db.query(Assignment)
            .join(Course)
            .filter(
                and_(
                    Assignment.due_at.isnot(None),
                    Assignment.due_at < current_time,
                    Assignment.workflow_state != "deleted",
                )
            )
            .order_by(Assignment.due_at.desc())
            .all()
        )

        overdue: List[dict[str, Any]] = []
        for assignment in overdue_assignments:
            days_overdue = (current_time - assignment.due_at).days
            overdue.append(
                {
                    "assignment_id": assignment.canvas_assignment_id,
                    "name": assignment.name,
                    "course_name": assignment.course.name,
                    "due_at": assignment.due_at.isoformat(),
                    "days_overdue": days_overdue,
                    "points_possible": assignment.points_possible,
                    "html_url": assignment.html_url,
                }
            )

        return overdue

    def get_course_workload_analysis(self, user_id: int) -> List[dict[str, Any]]:
        """Analyze workload distribution across courses."""
        current_time = datetime.now(timezone.utc)
        next_month = current_time + timedelta(days=30)

        # Get assignments due in the next month grouped by course
        courses_data: List[dict[str, Any]] = []
        courses = self.db.query(Course).all()

        for course in courses:
            assignments = (
                self.db.query(Assignment)
                .filter(
                    and_(
                        Assignment.course_id == course.id,
                        Assignment.due_at.isnot(None),
                        Assignment.due_at >= current_time,
                        Assignment.due_at <= next_month,
                        Assignment.workflow_state != "deleted",
                    )
                )
                .all()
            )

            total_points = sum(a.points_possible or 0 for a in assignments)
            assignment_count = len(assignments)

            if assignment_count > 0:
                avg_days_until_due = (
                    sum((a.due_at - current_time).days for a in assignments) / assignment_count
                )

                # Calculate workload intensity
                if assignment_count >= 5 or total_points >= 500:
                    intensity = "high"
                elif assignment_count >= 3 or total_points >= 200:
                    intensity = "medium"
                else:
                    intensity = "low"

                courses_data.append(
                    {
                        "course_id": course.canvas_course_id,
                        "course_name": course.name,
                        "assignment_count": assignment_count,
                        "total_points": total_points,
                        "avg_days_until_due": round(avg_days_until_due, 1),
                        "intensity": intensity,
                        "upcoming_assignments": [
                            {
                                "name": a.name,
                                "due_at": a.due_at.isoformat(),
                                "points": a.points_possible,
                            }
                            for a in assignments[:3]
                        ],
                    }
                )

        return sorted(courses_data, key=lambda x: x["assignment_count"], reverse=True)

    def generate_study_recommendations(self, user_id: int) -> dict[str, Any]:
        """Generate AI-powered study recommendations."""
        upcoming = self.get_upcoming_deadlines(user_id, days_ahead=14)
        overdue = self.get_overdue_assignments(user_id)
        workload = self.get_course_workload_analysis(user_id)

        recommendations = {
            "priority_actions": [],
            "time_management": {},
            "study_focus": [],
            "alerts": [],
        }

        # Priority actions based on deadlines
        high_priority = [a for a in upcoming if a["urgency"] == "high"]
        if high_priority:
            recommendations["priority_actions"].append(
                {
                    "type": "urgent_deadline",
                    "message": f"You have {len(high_priority)} assignment(s) due within 24 hours!",
                    "assignments": high_priority,
                }
            )

        if overdue:
            recommendations["priority_actions"].append(
                {
                    "type": "overdue_work",
                    "message": f"You have {len(overdue)} overdue assignment(s) that need attention.",
                    "assignments": overdue[:3],  # Show top 3 most recent
                }
            )

        # Time management suggestions
        total_upcoming = len(upcoming)
        if total_upcoming > 0:
            avg_days_ahead = sum(a["days_until_due"] for a in upcoming) / total_upcoming

            if avg_days_ahead < 3:
                recommendations["time_management"]["strategy"] = "sprint"
                recommendations["time_management"][
                    "message"
                ] = "Focus on immediate deadlines with intensive daily sessions."
            elif avg_days_ahead < 7:
                recommendations["time_management"]["strategy"] = "balanced"
                recommendations["time_management"][
                    "message"
                ] = "Maintain steady progress across all assignments."
            else:
                recommendations["time_management"]["strategy"] = "planning"
                recommendations["time_management"][
                    "message"
                ] = "Great! You have time to plan and work systematically."

        # Study focus recommendations
        high_intensity_courses = [c for c in workload if c["intensity"] == "high"]
        if high_intensity_courses:
            recommendations["study_focus"] = high_intensity_courses[:2]  # Top 2 demanding courses

        # Alerts
        if len(upcoming) > 10:
            recommendations["alerts"].append(
                {
                    "type": "heavy_workload",
                    "message": f"You have {len(upcoming)} assignments due soon. Consider prioritizing.",
                }
            )

        return recommendations

    def create_deadline_notification(
        self, user_id: int, assignment_id: int, notification_type: str = "deadline_reminder"
    ) -> NotificationLog:
        """Create a deadline notification for a user."""
        assignment = (
            self.db.query(Assignment)
            .filter(Assignment.canvas_assignment_id == assignment_id)
            .first()
        )

        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        # Calculate urgency message
        if assignment.due_at:
            time_until_due = assignment.due_at - datetime.now(timezone.utc)
            days_until = time_until_due.days
            hours_until = time_until_due.seconds // 3600

            if days_until == 0:
                urgency_msg = f"due in {hours_until} hours"
            elif days_until == 1:
                urgency_msg = "due tomorrow"
            else:
                urgency_msg = f"due in {days_until} days"
        else:
            urgency_msg = "due date not specified"

        notification = NotificationLog(
            user_id=user_id,
            notification_type=notification_type,
            title=f"📚 {assignment.name}",
            message=f"Assignment '{assignment.name}' in {assignment.course.name} is {urgency_msg}.",
            extra_data=f'{{"assignment_id": {assignment.canvas_assignment_id}, "course_id": {assignment.course.canvas_course_id}, "points": {assignment.points_possible}}}',
        )

        self.db.add(notification)
        self.db.commit()
        return notification


def get_ai_service(db: Session = Depends(get_db)) -> CanvasAIService:
    """Dependency to get AI service."""
    return CanvasAIService(db)
