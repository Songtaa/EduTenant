from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field

from app.db.base_class import APIBase


class Service(APIBase, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(max_length=255)
    price: Optional[float]
