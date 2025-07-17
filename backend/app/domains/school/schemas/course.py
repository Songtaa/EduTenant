from typing import Optional

from pydantic import BaseModel, UUID4

from app.db.base_class import UpdateBase, SchoolRelatedAPIBase


class CourseBase(SchoolRelatedAPIBase):
    """Courses Base Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    programme_id: Optional[UUID4] = None


class CourseCreate(BaseModel):
    """Courses Create Schema"""
    name: str
    description: Optional[str] = None
    code: str
    programme_id: UUID4


class CourseUpdate(UpdateBase):
    """Courses Update Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    programme_id: Optional[UUID4] = None


class CourseOut(CourseBase):
    """Courses Out Schema"""
