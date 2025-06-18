from db.base_class import APIBase
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class RefreshToken(APIBase):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'schema': 'public'}

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("public.users.id"), unique=True, nullable=True
    )
    refresh_token = Column(String, unique=True)
    expiration_time = Column(DateTime, nullable=True)

    users = relationship("User", backref="users", uselist=True)
