from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    canvas_course_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    course_code = Column(String, nullable=True)
    workflow_state = Column(String, nullable=True)
    syllabus_body = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignments = relationship("Assignment", back_populates="course")
