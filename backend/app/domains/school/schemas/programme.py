from typing import Optional

from pydantic import BaseModel

from app.db.base_class import SchoolRelatedAPIBase, UpdateBase


class ProgrammeBase(SchoolRelatedAPIBase):
    """Programmes Base Schema"""
    name: Optional[str] = None
    description: Optional[str] = None


class ProgrammeCreate(BaseModel):
    """Programmes Create Schema"""
    name: str
    description: Optional[str] = None


class ProgrammeUpdate(UpdateBase):
    """Programmes Update Schema"""
    name: Optional[str] = None
    description: Optional[str] = None


class ProgrammeOut(ProgrammeBase):
    """Programmes Out Schema"""
