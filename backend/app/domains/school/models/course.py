from app.domains.school.models.teacher_course import TeacherCourseLink
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional
from app.db.base_class import APIBase


class Course(APIBase, table=True):
    __tablename__ = "courses"

    name: str
    description: Optional[str] = None
    programme_id: UUID = Field(foreign_key="programmes.id")

    programme: Optional["Programme"] = Relationship(back_populates="courses")
    teachers: List["Teacher"] = Relationship(
        back_populates="courses", link_model=TeacherCourseLink
    )