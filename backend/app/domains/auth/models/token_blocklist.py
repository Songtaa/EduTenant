from sqlalchemy import Column, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid
from app.db.base_class import APIBase
from uuid import uuid4, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class TokenBlocklist(APIBase, table=True):
    __tablename__ = "token_blocklist"
    __table_args__ = {"schema": "public"}

    jti: str = Field(index=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    
    global_user_id: UUID | None = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=True)
    )

    tenant_user_id: UUID | None = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), nullable=True)  
    )

    tenant: str | None = Field(default=None, index=True)  

    global_user: "User" = Relationship(back_populates="tokens", sa_relationship_kwargs={"viewonly": True})
