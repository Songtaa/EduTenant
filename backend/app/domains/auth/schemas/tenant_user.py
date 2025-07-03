import uuid
from pydantic import UUID4, ConfigDict, EmailStr, Field
from sqlmodel import SQLModel




class TenantUserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    user_role: str = Field(default="user", max_length=255)
    # password: str = Field(min_length=8)


class TenantUserCreate(TenantUserBase):
    password: str = Field(min_length=8, max_length=40)


class TenantUserUpdate(TenantUserBase):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class TenantUserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class TenantUserPublic(TenantUserBase):
    id: uuid.UUID


class TenantUsersPublic(SQLModel):
    data: list[TenantUserPublic]
    count: int

class TenantUserInDBBase(TenantUserBase):
    id: UUID4

    # class Config:
    #     orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class TenantUserSchema(TenantUserInDBBase):
    pass
