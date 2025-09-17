"""
LLM-powered content analysis service for Canvas data.
Provides syllabus summarization, assignment analysis, and intelligent insights.
"""

import json
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.db.session import get_db
from backend.models import Assignment, Course


class CanvasLLMService:
    """LLM service for intelligent Canvas content analysis."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

        # Initialize OpenAI client lazily and handle optional dependency
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        try:
            from langchain_openai import ChatOpenAI  # type: ignore

            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                openai_api_key=openai_api_key,
            )
        except Exception as exc:  # ImportError or others
            raise ImportError(
                "langchain-openai is required for LLM endpoints. Install it to enable these routes."
            ) from exc

    def summarize_syllabus(self, course_id: int) -> dict[str, Any]:
        """Analyze and summarize a course syllabus."""
        course = self.db.query(Course).filter(Course.canvas_course_id == course_id).first()

        if not course or not course.syllabus_body:
            return {
                "course_id": course_id,
                "course_name": course.name if course else "Unknown",
                "summary": "No syllabus content available",
                "key_points": [],
                "grading_policy": None,
                "important_dates": [],
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

        # Clean HTML and prepare text
        syllabus_text = self._clean_html(course.syllabus_body)

        # Create analysis prompt
        system_prompt = """You are an expert academic advisor analyzing course syllabi.
        Provide a comprehensive analysis of the syllabus content focusing on:
        1. Course overview and learning objectives
        2. Grading breakdown and policies
        3. Important dates and deadlines
        4. Key requirements and expectations
        5. Resources and materials needed

        Return your analysis in JSON format with the following structure:
        {
            "summary": "Brief 2-3 sentence overview",
            "key_points": ["point1", "point2", ...],
            "grading_policy": {
                "breakdown": {"category": percentage, ...},
                "late_policy": "description"
            },
            "important_dates": [{"date": "YYYY-MM-DD", "event": "description"}, ...],
            "requirements": ["requirement1", "requirement2", ...],
            "resources": ["resource1", "resource2", ...]
        }"""

        human_prompt = f"""Analyze this course syllabus for {course.name}:

        {syllabus_text[:4000]}  # Limit to avoid token limits

        Provide a structured analysis in JSON format."""

        try:
            # Import at call time to avoid hard dependency at import time
            from langchain.schema import HumanMessage, SystemMessage  # type: ignore

            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt),
                ]
            )

            # Parse JSON response
            analysis_text = response.content
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"summary": analysis_text, "key_points": [], "grading_policy": None}

            return {
                "course_id": course_id,
                "course_name": course.name,
                "analysis": analysis,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            return {
                "course_id": course_id,
                "course_name": course.name,
                "summary": f"Analysis failed: {str(e)}",
                "key_points": [],
                "grading_policy": None,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

    def analyze_assignment(self, assignment_id: int) -> dict[str, Any]:
        """Analyze assignment content and provide insights."""
        assignment = (
            self.db.query(Assignment)
            .join(Course)
            .filter(Assignment.canvas_assignment_id == assignment_id)
            .first()
        )

        if not assignment:
            return {"assignment_id": assignment_id, "error": "Assignment not found"}

        # Prepare assignment context
        description = self._clean_html(assignment.description or "")
        context = f"""
        Course: {assignment.course.name}
        Assignment: {assignment.name}
        Due Date: {assignment.due_at.isoformat() if assignment.due_at else 'Not specified'}
        Points: {assignment.points_possible or 'Not specified'}
        Submission Types: {assignment.submission_types or 'Not specified'}

        Description:
        {description[:2000]}
        """

        system_prompt = """You are an expert academic tutor analyzing assignment details.
            Provide helpful insights including:
            1. Assignment type and complexity
            2. Estimated time to complete
            3. Key skills/concepts required
            4. Suggested approach/strategy
            5. Potential challenges

            Return analysis in JSON format:
            {
                "assignment_type": "essay|project|quiz|homework|exam|other",
                "complexity": "low|medium|high",
                "estimated_hours": number,
                "key_concepts": ["concept1", "concept2", ...],
                "suggested_approach": "step-by-step strategy",
                "potential_challenges": ["challenge1", "challenge2", ...],
                "preparation_tips": ["tip1", "tip2", ...]
            }"""

        try:
            from langchain.schema import HumanMessage, SystemMessage  # type: ignore

            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Analyze this assignment:\n\n{context}"),
                ]
            )

            analysis_text = response.content
            json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"assignment_type": "other", "complexity": "medium"}

            return {
                "assignment_id": assignment_id,
                "assignment_name": assignment.name,
                "course_name": assignment.course.name,
                "analysis": analysis,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            return {
                "assignment_id": assignment_id,
                "assignment_name": assignment.name,
                "error": f"Analysis failed: {str(e)}",
            }

    def generate_study_plan(self, user_id: int, days_ahead: int = 14) -> dict[str, Any]:
        """Generate an AI-powered personalized study plan."""
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
            .all()
        )

        if not upcoming_assignments:
            return {
                "message": "No upcoming assignments in the specified timeframe",
                "study_plan": [],
            }

        # Prepare assignment data for LLM
        assignments_data = []
        for assignment in upcoming_assignments[:10]:  # Limit to top 10
            days_until = (assignment.due_at - datetime.now(UTC)).days
            assignments_data.append(
                {
                    "name": assignment.name,
                    "course": assignment.course.name,
                    "due_in_days": days_until,
                    "points": assignment.points_possible or 0,
                    "submission_types": assignment.submission_types or "",
                }
            )

        system_prompt = """You are an expert academic advisor creating personalized study plans.
        Based on the upcoming assignments, create a day-by-day study plan that:
        1. Prioritizes assignments by urgency and importance
        2. Breaks down large tasks into manageable chunks
        3. Balances workload across different courses
        4. Includes buffer time for unexpected issues
        5. Suggests optimal study strategies

        Return a structured study plan in JSON format:
        {
            "study_strategy": "balanced|intensive|sprint",
            "total_estimated_hours": number,
            "daily_plan": [
                {
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "tasks": [
                        {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                            "course": "course name",
                            "task": "specific task to do",
                            "estimated_hours": number,
                            "priority": "high|medium|low"
                        }
                    ],
                    "total_hours": number
                }
            ],
            "tips": ["tip1", "tip2", ...]
        }"""

        human_prompt = f"""Create a {days_ahead}-day study plan for these upcoming assignments:

        {json.dumps(assignments_data, indent=2)}

        Today's date: {datetime.now().strftime('%Y-%m-%d')}

        Consider the student's workload and create a realistic, achievable plan."""

        try:
            from langchain.schema import HumanMessage, SystemMessage  # type: ignore

            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt),
                ]
            )

            analysis_text = response.content
            json_match = re.search(r"\{.*\}", analysis_text, re.DOTALL)
            if json_match:
                study_plan = json.loads(json_match.group())
            else:
                study_plan = {"study_strategy": "balanced", "daily_plan": []}

            return {
                "user_id": user_id,
                "timeframe_days": days_ahead,
                "assignments_count": len(upcoming_assignments),
                "study_plan": study_plan,
                "generated_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            return {"user_id": user_id, "error": f"Study plan generation failed: {str(e)}"}

    def ask_question(
        self, user_id: int, question: str, context_course_id: int | None = None
    ) -> dict[str, Any]:  # Updated typing for Python 3.9
        """Answer student questions using Canvas data as context."""
        context_data = ""

        if context_course_id:
            # Get course context
            course = (
                self.db.query(Course).filter(Course.canvas_course_id == context_course_id).first()
            )

            if course:
                assignments = (
                    self.db.query(Assignment)
                    .filter(Assignment.course_id == course.id)
                    .order_by(Assignment.due_at.desc())
                    .limit(5)
                    .all()
                )

                context_data = f"""
                Course Context: {course.name}
                Recent Assignments:
                """
                for assignment in assignments:
                    due_str = (
                        assignment.due_at.strftime("%Y-%m-%d")
                        if assignment.due_at
                        else "No due date"
                    )
                    context_data += f"- {assignment.name} (Due: {due_str}, Points: {assignment.points_possible or 'N/A'})\n"

        system_prompt = """You are a helpful academic assistant with access to the student's Canvas course data.
        Answer questions about coursework, deadlines, study strategies, and academic planning.
        Be specific and actionable in your responses. If you don't have enough context, ask clarifying questions.

        Keep responses concise but helpful (2-3 paragraphs max)."""

        human_prompt = f"""Student question: {question}

        {context_data}

        Please provide a helpful response based on the available context."""

        try:
            from langchain.schema import HumanMessage, SystemMessage  # type: ignore

            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt),
                ]
            )

            return {
                "question": question,
                "answer": response.content,
                "context_course_id": context_course_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            return {"question": question, "error": f"Failed to generate response: {str(e)}"}

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text."""
        if not html_content:
            return ""

        # Remove HTML tags
        import re

        clean_text = re.sub(r"<[^>]+>", "", html_content)

        # Clean up whitespace
        clean_text = re.sub(r"\s+", " ", clean_text)
        clean_text = clean_text.strip()

        return clean_text


def get_llm_service(db: Session = Depends(get_db)) -> CanvasLLMService:
    """Dependency to get LLM service."""
    return CanvasLLMService(db)
