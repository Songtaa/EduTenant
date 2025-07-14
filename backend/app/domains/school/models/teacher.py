from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase
from app.domains.school.models.teacher_course import TeacherCourseLink


class Teacher(APIBase, table=True):
    __tablename__ = "teachers"

    full_name: str
    email: str = Field(index=True, unique=True)
    phone: Optional[str] = None

    user_id: UUID = Field(foreign_key="public.users.id")
    school_id: UUID = Field(foreign_key="schools.id")
    tenant_id: UUID = Field(foreign_key="public.tenants.id")

    courses: List["Course"] = Relationship(
        back_populates="teachers", link_model=TeacherCourseLink
    )
    school: Optional["School"] = Relationship(back_populates="teachers")
