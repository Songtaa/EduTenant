from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domains.auth.repository.permission import PermissionRepository
from app.domains.auth.schemas.permission import (
    PermissionCreate,
    PermissionUpdate,
    PermissionSchema,
)

import logging

logging.basicConfig(level=logging.DEBUG)


class PermissionService:
    def __init__(self, session: AsyncSession):
        self.permission_repo = PermissionRepository(session)

    async def create(self, permission_data: PermissionCreate) -> PermissionSchema:
        existing_permission = await self.permission_repo.get_permission_by_name(permission_data.name)
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission already exists")
        return await self.permission_repo.create_permission(permission_data)

    async def get_all(self) -> List[PermissionSchema]:
        return await self.permission_repo.get_all_permissions()

    async def get_by_id(self, permission_id: UUID) -> Optional[PermissionSchema]:
        permission = await self.permission_repo.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionSchema(**permission.__dict__)

    async def update(self, permission_id: UUID, data: PermissionUpdate) -> PermissionSchema:
        permission = await self.permission_repo.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return await self.permission_repo.update_permission(permission, data)

    async def delete(self, permission_id: UUID) -> bool:
        permission = await self.permission_repo.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return await self.permission_repo.delete_permission(permission)

    async def get_permissions_by_role(self, role_id: UUID) -> List[PermissionSchema]:
        return await self.permission_repo.get_permissions_by_role(role_id)

    async def get_permissions_by_user(self, user_id: UUID) -> List[PermissionSchema]:
        return await self.permission_repo.get_permissions_by_user(user_id)

    async def get_roles_by_user(self, user_id: UUID):
        return await self.permission_repo.get_roles_by_user(user_id)

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> bool:
        """Assign a single permission to a role using the repository pattern."""
        role_permissions = await self.permission_repo.get_permissions_by_role(role_id)
        if any(p.id == permission_id for p in role_permissions):
            raise HTTPException(status_code=400, detail="Permission already assigned to role")

        return await self.permission_repo.assign_permission_to_role(role_id, permission_id)

    # async def assign_permission_to_user(self, user_id: UUID, permission_id: UUID) -> bool:
    #     """Assign a single permission directly to a user using the repository pattern."""
    #     user_permissions = await self.permission_repo.get_permissions_by_user(user_id)
    #     if any(p.id == permission_id for p in user_permissions):
    #         raise HTTPException(status_code=400, detail="Permission already assigned to user")

    #     return await self.permission_repo.assign_permission_to_user(user_id, permission_id)

    async def assign_permission_to_user(self, user_id: UUID, permission_id: UUID) -> bool:
        user_permissions = await self.permission_repo.get_permissions_by_user(user_id)
        logging.debug(f"Existing permissions for user {user_id}: {user_permissions}")

        if any(p.id == permission_id for p in user_permissions):
            raise HTTPException(status_code=400, detail="Permission already assigned to user")

        result = await self.permission_repo.assign_permission_to_user(user_id, permission_id)
        logging.debug(f"Permission {permission_id} assigned: {result}")

        return result

    async def remove_permission_from_role(self, role_id: UUID, permission_id: UUID) -> bool:
        """Remove a permission from a role using the repository pattern."""
        return await self.permission_repo.remove_permission_from_role(role_id, permission_id)

    async def remove_permission_from_user(self, user_id: UUID, permission_id: UUID) -> bool:
        """Remove a permission directly assigned to a user using the repository pattern."""
        return await self.permission_repo.remove_permission_from_user(user_id, permission_id)
