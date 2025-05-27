from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    description: str
    price: Optional[float]


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float]


class ServiceRead(ServiceBase):
    id: UUID

    class Config:
        orm_mode = True


class ServiceSchema(ServiceRead):
    pass
