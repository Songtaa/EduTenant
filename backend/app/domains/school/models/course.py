from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional
from app.db.base_class import APIBase


class Course(SQLModel, table=True):
    __tablename__ = "courses"

    name: str
    description: Optional[str] = None
    programme_id: UUID = Field(foreign_key="programme.id")

    programme: Optional["Programme"] = Relationship(back_populates="courses")
    teachers: List["Teacher"] = Relationship(
        back_populates="courses", link_model="TeacherCourseLink"
    )