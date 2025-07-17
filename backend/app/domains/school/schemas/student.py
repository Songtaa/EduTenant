from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4

from app.db.base_class import SchoolRelatedAPIBase, UpdateBase


class StudentBase(SchoolRelatedAPIBase):
    """Students Base Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    student_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    user_id: Optional[UUID4] = None
    class_id: Optional[UUID4] = None
    parent_id: Optional[UUID4] = None


class StudentCreate(BaseModel):
    """Students Create Schema"""
    full_name: str
    email: str
    student_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    user_id: UUID4
    class_id: UUID4
    parent_id: UUID4


class StudentUpdate(UpdateBase):
    """Students Update Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    student_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    parent_id: Optional[UUID4] = None


class StudentOut(StudentBase):
    """Students Out Schema"""
