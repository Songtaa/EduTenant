from app.domains.school.models.teacher_course import TeacherCourseLink
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional
from app.db.base_class import APIBase

class Teacher(APIBase, table=True):
    __tablename__ = "teachers"
    
    full_name: str
    email: str = Field(index=True, unique=True)
    phone: Optional[str] = None

    courses: List["Course"] = Relationship(
        back_populates="teachers", link_model=TeacherCourseLink
    )
