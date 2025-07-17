from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4

from app.db.base_class import SchoolRelatedAPIBase, UpdateBase


class TeacherBase(SchoolRelatedAPIBase):
    """Teachers Base Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    user_id: Optional[UUID4] = None


class TeacherCreate(BaseModel):
    """Teachers Create Schema"""
    full_name: str
    email: str
    phone: Optional[str] = None
    user_id: UUID4


class TeacherUpdate(UpdateBase):
    """Teachers Update Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    student_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    parent_id: Optional[UUID4] = None


class TeacherOut(TeacherBase):
    """Teachers Out Schema"""
