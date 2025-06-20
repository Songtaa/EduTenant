from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import uuid4, UUID
from typing import Optional
from app.db.base_class import APIBase

class Parent(APIBase, table=True):
    __tablename__ = "parents"
    
    full_name: str
    email: str = Field(index=True, unique=True)
    phone: Optional[str] = None
    occupation: Optional[str] = None

    user_id: UUID = Field(foreign_key="public.users.id")
    school_id: UUID = Field(foreign_key="schools.id")