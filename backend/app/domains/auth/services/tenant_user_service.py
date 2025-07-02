from typing import List, Optional

from app.domains.auth.repository.tenant_user_repo import TenantUserRepository
from app.domains.auth.models.tenant_user import TenantUser
from app.domains.auth.schemas.tenant_user import (
    TenantUserCreate, 
    TenantUserSchema, 
    TenantUserUpdate)
from fastapi import HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession


class TenantUserService:
    def __init__(self, session: AsyncSession, model: type[TenantUser]):
        self.session = session
        self.repository = TenantUserRepository(model, session)

    async def user_exists(self, email: str):
        user = await self.repository.get_user_by_email(email)
    
        return True if user is not None else False

    async def create(self, user_data: TenantUserCreate) -> TenantUserSchema:
        if await self.repository.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

        created_user = await self.repository.create_user(user_data)

        # return UserSchema(**created_user.__dict__)
        return TenantUserSchema.from_orm(created_user)

    async def get_all(self) -> List[Optional[TenantUserSchema]]:
        return await self.repository.get_all()

    async def update(self, user_id: UUID4, data: TenantUserUpdate) -> TenantUserSchema:
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
