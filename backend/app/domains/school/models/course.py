from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase
from app.domains.school.models.teacher_course import TeacherCourseLink


class Course(APIBase, table=True):
    __tablename__ = "courses"

    name: str
    description: Optional[str] = None
    code: str

    school_id: UUID = Field(foreign_key="schools.id")
    tenant_id: UUID = Field(foreign_key="public.tenants.id")
    programme_id: UUID = Field(foreign_key="programmes.id")

    programme: Optional["Programme"] = Relationship(back_populates="courses")
    teachers: List["Teacher"] = Relationship(
        back_populates="courses", link_model=TeacherCourseLink
    )
    school: Optional["School"] = Relationship(back_populates="courses")
