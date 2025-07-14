from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship

from app.db.base_class import APIBase


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
