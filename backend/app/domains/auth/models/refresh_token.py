from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase


class RefreshToken(APIBase, table=True):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "public"}

    user_id: UUID = Field(foreign_key="public.users.id", primary_key=True)
    refresh_token: str = Field(unique=True)
    expiration_time: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="refresh_token")
