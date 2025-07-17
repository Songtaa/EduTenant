from typing import Optional

from pydantic import UUID4, BaseModel

from app.db.base_class import APIBase, UpdateBase


class ParentBase(APIBase):
    """Parents Base Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    user_id: Optional[UUID4] = None
    school_id: Optional[UUID4] = None


class ParentCreate(BaseModel):
    """Parents Create Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    user_id: Optional[UUID4] = None


class ParentUpdate(UpdateBase):
    """Parents Update Schema"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None


class ParentOut(ParentBase):
    """Parents Out Schema"""
