from typing import Optional
from uuid import UUID, uuid4

from app.db.base_class import APIBase
from sqlmodel import Field


class Service(APIBase, table=True):

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: str = Field(max_length=255)
    price: Optional[float]
