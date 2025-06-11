from typing import List, Optional

from app.domains.auth.repository.user_repository import UserRepository
from app.domains.auth.schemas.user_schema import (
    UserCreate,
    UserSchema,
    UserUpdate,
)
from fastapi import HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def user_exists(self, email: str):
        user = await self.repository.get_user_by_email(email)
    
        return True if user is not None else False

    async def create(self, user_data: UserCreate) -> UserSchema:
        if await self.repository.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

        created_user = await self.repository.create_user(user_data)

        # return UserSchema(**created_user.__dict__)
        return UserSchema.from_orm(created_user)

    async def get_all(self) -> List[Optional[UserSchema]]:
        return await self.repository.get_all()

    async def update(self, user_id: UUID4, data: UserUpdate) -> UserSchema:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="user not found")

        updated_user = await self.repository.update(user, data)
        return updated_user

    async def delete(self, user_id: UUID4) -> bool:
        if not await self.repository.get_user_by_id(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        user = await self.repository.get_user_by_id(user_id)
        await self.repository.delete_user(user)
        return True
