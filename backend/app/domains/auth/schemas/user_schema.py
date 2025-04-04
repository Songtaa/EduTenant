import uuid
from pydantic import UUID4, EmailStr, Field
from sqlmodel import SQLModel

# from db.base_class import BaseModel


# class UserCreateModel(BaseModel):
#     username: str = Field(max_length=8)
#     email: EmailStr = Field(max_length=40)
#     password: str = Field(min_length=8)


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    user_role: str = Field(default="user", max_length=255)
    # password: str = Field(min_length=8)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserUpdate(UserBase):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class UserInDBBase(UserBase):
    id: UUID4

    class Config:
        orm_mode = True


class UserSchema(UserInDBBase):
    pass
