"""
Canvas data synchronization service.
Handles syncing courses, assignments, and user data from Canvas API to local database.
"""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import Depends
from canvasapi import Canvas

from backend.config import get_settings
from backend.db.session import get_db
from backend.models import User, Course, Assignment, SyncRun


class CanvasSyncService:
    """Service for syncing Canvas data to local database."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.canvas = Canvas(self.settings.canvas_api_url, self.settings.canvas_api_key)
    
    def sync_user_data(self, user_id: Optional[int] = None) -> SyncRun:
        """Sync user data from Canvas."""
        sync_run = SyncRun(
            user_id=user_id or 1,  # Default user for now
            sync_type="user",
            status="running"
        )
        self.db.add(sync_run)
        self.db.commit()
        
        try:
            canvas_user = self.canvas.get_current_user()
            
            # Create or update user
            user = self.db.query(User).filter(
                User.canvas_user_id == canvas_user.id
            ).first()
            
            if not user:
                user = User(
                    canvas_user_id=canvas_user.id,
                    name=getattr(canvas_user, 'name', None),
                    email=getattr(canvas_user, 'email', None)
                )
                self.db.add(user)
                sync_run.items_created += 1
            else:
                user.name = getattr(canvas_user, 'name', user.name)
                user.email = getattr(canvas_user, 'email', user.email)
                sync_run.items_updated += 1
            
            sync_run.items_processed = 1
            sync_run.status = "completed"
            sync_run.completed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            sync_run.status = "failed"
            sync_run.error_message = str(e)
            sync_run.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        return sync_run
    
    def sync_courses(self, user_id: Optional[int] = None) -> SyncRun:
        """Sync courses from Canvas."""
        sync_run = SyncRun(
            user_id=user_id or 1,
            sync_type="courses", 
            status="running"
        )
        self.db.add(sync_run)
        self.db.commit()
        
        try:
            # Fetch only courses the current user is actively enrolled in and are available
            user = self.canvas.get_current_user()
            canvas_courses = user.get_courses(
                enrollment_state=["active"],
                state=["available"]
            )
            
            for canvas_course in canvas_courses:
                # Create or update course
                course = self.db.query(Course).filter(
                    Course.canvas_course_id == canvas_course.id
                ).first()
                
                if not course:
                    course = Course(
                        canvas_course_id=canvas_course.id,
                        name=getattr(canvas_course, 'name', None),
                        course_code=getattr(canvas_course, 'course_code', None),
                        workflow_state=getattr(canvas_course, 'workflow_state', None),
                        syllabus_body=getattr(canvas_course, 'syllabus_body', None)
                    )
                    self.db.add(course)
                    sync_run.items_created += 1
                else:
                    course.name = getattr(canvas_course, 'name', course.name)
                    course.course_code = getattr(canvas_course, 'course_code', course.course_code)
                    course.workflow_state = getattr(canvas_course, 'workflow_state', course.workflow_state)
                    course.syllabus_body = getattr(canvas_course, 'syllabus_body', course.syllabus_body)
                    sync_run.items_updated += 1
                
                sync_run.items_processed += 1
            
            sync_run.status = "completed"
            sync_run.completed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            sync_run.status = "failed"
            sync_run.error_message = str(e)
            sync_run.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        return sync_run
    
    def sync_assignments(self, course_ids: Optional[List[int]] = None, user_id: Optional[int] = None) -> SyncRun:
        """Sync assignments from Canvas."""
        sync_run = SyncRun(
            user_id=user_id or 1,
            sync_type="assignments",
            status="running"
        )
        self.db.add(sync_run)
        self.db.commit()
        
        try:
            if course_ids:
                canvas_courses = [self.canvas.get_course(cid) for cid in course_ids]
            else:
                # Use current user's active, available courses to avoid stale data
                user = self.canvas.get_current_user()
                canvas_courses = user.get_courses(
                    enrollment_state=["active"],
                    state=["available"]
                )
            
            for canvas_course in canvas_courses:
                try:
                    # Ensure course exists in our database
                    course = self.db.query(Course).filter(
                        Course.canvas_course_id == canvas_course.id
                    ).first()
                    
                    if not course:
                        continue  # Skip if course not in our DB
                    
                    assignments = canvas_course.get_assignments()
                    
                    for canvas_assignment in assignments:
                        # Create or update assignment
                        assignment = self.db.query(Assignment).filter(
                            Assignment.canvas_assignment_id == canvas_assignment.id
                        ).first()
                        
                        # Parse due_at safely
                        due_at = None
                        if hasattr(canvas_assignment, 'due_at') and canvas_assignment.due_at:
                            try:
                                due_at = datetime.fromisoformat(canvas_assignment.due_at.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        if not assignment:
                            assignment = Assignment(
                                canvas_assignment_id=canvas_assignment.id,
                                course_id=course.id,
                                name=getattr(canvas_assignment, 'name', None),
                                description=getattr(canvas_assignment, 'description', None),
                                due_at=due_at,
                                html_url=getattr(canvas_assignment, 'html_url', None),
                                submission_types=','.join(getattr(canvas_assignment, 'submission_types', [])),
                                points_possible=getattr(canvas_assignment, 'points_possible', None),
                                workflow_state=getattr(canvas_assignment, 'workflow_state', None)
                            )
                            self.db.add(assignment)
                            sync_run.items_created += 1
                        else:
                            assignment.name = getattr(canvas_assignment, 'name', assignment.name)
                            assignment.description = getattr(canvas_assignment, 'description', assignment.description)
                            assignment.due_at = due_at or assignment.due_at
                            assignment.html_url = getattr(canvas_assignment, 'html_url', assignment.html_url)
                            assignment.submission_types = ','.join(getattr(canvas_assignment, 'submission_types', []))
                            assignment.points_possible = getattr(canvas_assignment, 'points_possible', assignment.points_possible)
                            assignment.workflow_state = getattr(canvas_assignment, 'workflow_state', assignment.workflow_state)
                            sync_run.items_updated += 1
                        
                        sync_run.items_processed += 1
                        
                except Exception as course_error:
                    # Skip courses we don't have access to
                    continue
            
            sync_run.status = "completed"
            sync_run.completed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            sync_run.status = "failed"
            sync_run.error_message = str(e)
            sync_run.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        return sync_run
    
    def full_sync(self, user_id: Optional[int] = None) -> SyncRun:
        """Perform a full sync of user, courses, and assignments."""
        sync_run = SyncRun(
            user_id=user_id or 1,
            sync_type="full",
            status="running"
        )
        self.db.add(sync_run)
        self.db.commit()
        
        try:
            # Sync user first
            user_sync = self.sync_user_data(user_id)
            
            # Sync courses
            courses_sync = self.sync_courses(user_id)
            
            # Sync assignments
            assignments_sync = self.sync_assignments(user_id=user_id)
            
            # Aggregate results
            sync_run.items_processed = (user_sync.items_processed + 
                                      courses_sync.items_processed + 
                                      assignments_sync.items_processed)
            sync_run.items_created = (user_sync.items_created + 
                                    courses_sync.items_created + 
                                    assignments_sync.items_created)
            sync_run.items_updated = (user_sync.items_updated + 
                                    courses_sync.items_updated + 
                                    assignments_sync.items_updated)
            
            if all(s.status == "completed" for s in [user_sync, courses_sync, assignments_sync]):
                sync_run.status = "completed"
            else:
                sync_run.status = "failed"
                errors = [s.error_message for s in [user_sync, courses_sync, assignments_sync] if s.error_message]
                sync_run.error_message = "; ".join(errors)
            
            sync_run.completed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            sync_run.status = "failed"
            sync_run.error_message = str(e)
            sync_run.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        return sync_run


def get_sync_service(db: Session = Depends(get_db)) -> CanvasSyncService:
    """Dependency to get sync service."""
    return CanvasSyncService(db)
