from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase


class Student(APIBase, table=True):
    __tablename__ = "students"

    full_name: str = Field(max_length=255, index=True)
    email: str = Field(max_length=255, unique=True)
    student_number: Optional[str]
    date_of_birth: Optional[datetime] = None

    user_id: UUID = Field(foreign_key="public.users.id")
    tenant_id: UUID = Field(foreign_key="public.tenants.id")

    class_id: Optional[UUID] = Field(foreign_key="classes.id")
    parent_id: Optional[UUID] = Field(foreign_key="parents.id")
    school_id: UUID = Field(foreign_key="schools.id")

    class_: Optional["Class"] = Relationship(back_populates="students")
    school: Optional["School"] = Relationship(back_populates="students")
