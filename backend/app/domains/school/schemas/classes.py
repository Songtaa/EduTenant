from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.db.base_class import UpdateBase, SchoolRelatedAPIBase


class ClassesBase(SchoolRelatedAPIBase):
    """Classes Base Schema"""
    name: Optional[str] = None
    academic_year: Optional[int] = None
    programme_id: Optional[UUID] = None


class ClassesCreate(BaseModel):
    """Classes Create Schema"""
    name: str
    academic_year: int
    programme_id: UUID


class ClassesUpdate(UpdateBase):
    """Classes Update Schema"""
    name: Optional[str] = None
    academic_year: Optional[int] = None


class ClassesOut(ClassesBase):
    """Classes Out Schema"""
