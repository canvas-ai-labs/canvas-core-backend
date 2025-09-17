"""
Mock LLM service for testing without OpenAI API key.
Provides simulated intelligent responses for demonstration.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models import Assignment, Course


class MockCanvasLLMService:
    """Mock LLM service for testing without API keys."""

    def __init__(self, db: Session):
        self.db = db

    def summarize_syllabus(self, course_id: int) -> dict[str, Any]:
        """Mock syllabus analysis."""
        course = self.db.query(Course).filter(Course.canvas_course_id == course_id).first()

        if not course:
            return {"course_id": course_id, "error": "Course not found"}

        # Generate mock analysis based on course name
        mock_analysis = {
            "summary": f"This course, {course.name}, appears to be a comprehensive academic program designed to provide students with foundational knowledge and practical skills. The course emphasizes both theoretical understanding and hands-on application.",
            "key_points": [
                "Regular assignments and assessments throughout the semester",
                "Emphasis on critical thinking and analytical skills",
                "Group projects and collaborative learning opportunities",
                "Integration of technology and modern methodologies",
            ],
            "grading_policy": {
                "breakdown": {
                    "assignments": 40,
                    "exams": 35,
                    "participation": 15,
                    "final_project": 10,
                },
                "late_policy": "Late submissions accepted with 10% penalty per day",
            },
            "important_dates": [
                {"date": "2025-09-10", "event": "Midterm Exam"},
                {"date": "2025-11-15", "event": "Final Project Due"},
                {"date": "2025-12-10", "event": "Final Exam"},
            ],
            "requirements": [
                "Regular attendance and participation",
                "Completion of all assignments on time",
                "Active engagement in group discussions",
                "Adherence to academic integrity policies",
            ],
            "resources": [
                "Course textbook and supplementary readings",
                "Online learning management system",
                "Library resources and databases",
                "Office hours for additional support",
            ],
        }

        return {
            "course_id": course_id,
            "course_name": course.name,
            "analysis": mock_analysis,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    def analyze_assignment(self, assignment_id: int) -> dict[str, Any]:
        """Mock assignment analysis."""
        assignment = (
            self.db.query(Assignment)
            .join(Course)
            .filter(Assignment.canvas_assignment_id == assignment_id)
            .first()
        )

        if not assignment:
            return {"assignment_id": assignment_id, "error": "Assignment not found"}

        # Determine assignment type based on name
        name_lower = assignment.name.lower()
        if "quiz" in name_lower:
            assignment_type = "quiz"
            complexity = "low"
            estimated_hours = 1
        elif "exam" in name_lower:
            assignment_type = "exam"
            complexity = "high"
            estimated_hours = 3
        elif "homework" in name_lower or "hw" in name_lower:
            assignment_type = "homework"
            complexity = "medium"
            estimated_hours = 4
        elif "project" in name_lower:
            assignment_type = "project"
            complexity = "high"
            estimated_hours = 8
        else:
            assignment_type = "other"
            complexity = "medium"
            estimated_hours = 2

        mock_analysis = {
            "assignment_type": assignment_type,
            "complexity": complexity,
            "estimated_hours": estimated_hours,
            "key_concepts": [
                "Critical analysis and evaluation",
                "Application of course theories",
                "Research and information synthesis",
                "Clear communication and presentation",
            ],
            "suggested_approach": f"Start by reviewing the {assignment.name} requirements carefully. Break the work into smaller, manageable tasks. Begin with research and outlining, then proceed with the main work. Allow time for review and revision before submission.",
            "potential_challenges": [
                "Time management and deadline pressure",
                "Understanding complex requirements",
                "Balancing depth with breadth of coverage",
                "Integrating multiple sources or concepts",
            ],
            "preparation_tips": [
                "Start early to avoid last-minute stress",
                "Create a detailed timeline with milestones",
                "Seek clarification on unclear requirements",
                "Use office hours for additional guidance",
                "Form study groups for collaborative learning",
            ],
        }

        return {
            "assignment_id": assignment_id,
            "assignment_name": assignment.name,
            "course_name": assignment.course.name,
            "analysis": mock_analysis,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

    def generate_study_plan(self, user_id: int, days_ahead: int = 14) -> dict[str, Any]:
        """Mock study plan generation."""
        # Get upcoming assignments
        upcoming_assignments = (
            self.db.query(Assignment)
            .join(Course)
            .filter(
                Assignment.due_at.isnot(None),
                Assignment.due_at >= datetime.now(UTC),
                Assignment.due_at <= datetime.now(UTC) + timedelta(days=days_ahead),
            )
            .order_by(Assignment.due_at)
            .limit(10)
            .all()
        )

        if not upcoming_assignments:
            return {
                "message": "No upcoming assignments in the specified timeframe",
                "study_plan": [],
            }

        # Generate mock study plan
        daily_plan = []
        current_date = datetime.now().date()

        for day in range(min(7, days_ahead)):  # Generate plan for up to 7 days
            plan_date = current_date + timedelta(days=day)

            # Assign 1-2 tasks per day
            tasks = []
            for _i, assignment in enumerate(upcoming_assignments[:2]):
                task_name = f"Work on {assignment.name}"
                if "quiz" in assignment.name.lower():
                    task_name = f"Study for {assignment.name}"
                elif "exam" in assignment.name.lower():
                    task_name = f"Review materials for {assignment.name}"

                priority = (
                    "high"
                    if (assignment.due_at - datetime.now(UTC)).days <= 2
                    else "medium"
                )

                tasks.append(
                    {
                        "assignment": assignment.name,
                        "course": assignment.course.name,
                        "task": task_name,
                        "estimated_hours": 2 + day,  # Vary hours
                        "priority": priority,
                    }
                )

            daily_plan.append(
                {
                    "day": day + 1,
                    "date": plan_date.strftime("%Y-%m-%d"),
                    "tasks": tasks,
                    "total_hours": sum(task["estimated_hours"] for task in tasks),
                }
            )

        mock_study_plan = {
            "study_strategy": "balanced",
            "total_estimated_hours": sum(day["total_hours"] for day in daily_plan),
            "daily_plan": daily_plan,
            "tips": [
                "Start each study session with a clear goal",
                "Take regular breaks to maintain focus",
                "Review previous material before starting new topics",
                "Use active learning techniques like summarizing and teaching",
                "Maintain a consistent study schedule",
                "Create a distraction-free study environment",
            ],
        }

        return {
            "user_id": user_id,
            "timeframe_days": days_ahead,
            "assignments_count": len(upcoming_assignments),
            "study_plan": mock_study_plan,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def ask_question(
        self, user_id: int, question: str, context_course_id: int | None = None
    ) -> dict[str, Any]:
        """Mock Q&A responses."""
        # Generate contextual responses based on question keywords
        question_lower = question.lower()

        if "deadline" in question_lower or "due" in question_lower:
            answer = "Based on your current assignments, I recommend checking your upcoming deadlines regularly. You have several assignments due soon, including some high-priority items. Use the deadline tracking features to stay on top of your work and set reminders for important dates."

        elif "study" in question_lower or "prepare" in question_lower:
            answer = "For effective studying, I suggest creating a structured study plan that breaks down your work into manageable chunks. Focus on high-priority assignments first, especially those due within the next few days. Use active learning techniques like summarizing, practice problems, and teaching concepts to others."

        elif "time" in question_lower or "manage" in question_lower:
            answer = "Time management is crucial for academic success. I recommend using a calendar to track all your assignments and deadlines. Allocate specific time blocks for studying each subject, and don't forget to include breaks. Start working on assignments as soon as they're assigned to avoid last-minute stress."

        elif "grade" in question_lower or "score" in question_lower:
            answer = "To improve your grades, focus on understanding the grading criteria for each assignment. Make sure you're meeting all requirements and submitting work on time. Don't hesitate to ask for clarification on assignments you find confusing. Regular review of course material can also help reinforce learning."

        else:
            answer = f"That's a great question about '{question}'. Based on your current course load and upcoming assignments, I'd recommend staying organized with your coursework and maintaining regular study habits. If you need specific help with any assignment or course material, feel free to ask more detailed questions."

        return {
            "question": question,
            "answer": answer,
            "context_course_id": context_course_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }


def get_mock_llm_service(db: Session = Depends(get_db)) -> MockCanvasLLMService:
    """Dependency to get mock LLM service."""
    return MockCanvasLLMService(db)
