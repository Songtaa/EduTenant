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
    user_id: UUID = Field(foreign_key="public.users.id")
    school_id: UUID = Field(foreign_key="schools.id")

    courses: List["Course"] = Relationship(
        back_populates="teachers", link_model=TeacherCourseLink
    )
