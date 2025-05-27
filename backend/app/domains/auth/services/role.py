from sqlalchemy import UUID, select
from app.domains.auth.repository.role import RoleRepository
from app.domains.auth.models.role import Role
from app.domains.auth.models.user_role import UserRole
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from pydantic import UUID4
from typing import List, Optional
from app.domains.auth.schemas.role import RoleCreate, RoleRead, RoleUpdate, RoleSchema


class RoleService:
    def __init__(self, session: AsyncSession):
        self.role_repo = RoleRepository(session)

    async def role_exists(self, name: str) -> bool:
        return await self.role_repo.get_role_by_name(name) is not None

    async def create(self, role_data: RoleCreate) -> RoleSchema:
        if await self.role_repo.get_role_by_name(role_data.name):
            raise HTTPException(status_code=400, detail="Role with this name already exists")

        created_role = await self.role_repo.create_role(role_data)
        return RoleSchema(**created_role.__dict__)

    async def get_all(self) -> List[Optional[RoleSchema]]:
        return await self.role_repo.get_all()

    async def update(self, role_id: UUID4, data: RoleUpdate) -> RoleSchema:
        role = await self.role_repo.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        updated_role = await self.role_repo.update(role, data)
        return updated_role

    async def delete(self, role_id: UUID4) -> bool:
        role = await self.role_repo.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        await self.role_repo.delete_service(role)
        return True

    # async def get_roles_by_user(self, user_id: UUID) -> List[RoleSchema]:
    #     statement = select(Role).join(UserRole).where(UserRole.user_id == user_id)
    #     result = await self.session.execute(statement)
    #     roles = result.scalars().all()
    #     return [RoleSchema(**role.__dict__) for role in roles]

    async def get_roles_by_user(self, user_id: UUID) -> List[Optional[RoleSchema]]:
        roles = await self.role_repo.get_roles_by_user(user_id)
        return roles


    
    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> dict:
        result = await self.role_repo.assign_role_to_user(user_id, role_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

    
    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> dict:
        result = await self.role_repo.remove_role_from_user(user_id, role_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
