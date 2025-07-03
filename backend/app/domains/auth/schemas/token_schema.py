# app/domains/auth/schemas/token_schema.py

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class TokenBlocklistBase(BaseModel):
    jti: str
    expires_at: datetime
    tenant: Optional[str] = None


class TokenBlocklistCreate(TokenBlocklistBase):
    global_user_id: Optional[UUID] = None
    tenant_user_id: Optional[UUID] = None


class TokenBlocklistRead(TokenBlocklistBase):
    id: int
    global_user_id: Optional[UUID] = None
    tenant_user_id: Optional[UUID] = None

    class Config:
        orm_mode = True
