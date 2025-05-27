from typing import List, Optional, Type
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from app.domains.auth.schemas.role import RoleSchema
from app.domains.auth.models.role import Role
from app.domains.auth.schemas.permission import PermissionCreate, PermissionUpdate, PermissionSchema
from app.domains.auth.models.permission import Permission
from app.domains.auth.models.role_permission import RolePermission
from app.domains.auth.models.user_permissions import UserPermission
from app.domains.auth.models.user_role import UserRole

class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_permission(self, permission_data: PermissionCreate) -> PermissionSchema:
        permission_data_dict = permission_data.model_dump()
        new_permission = Permission(**permission_data_dict)
        self.session.add(new_permission)
        await self.session.commit()
        await self.session.refresh(new_permission)
        return PermissionSchema(**new_permission.__dict__)

    async def get_all_permissions(self) -> List[PermissionSchema]:
        statement = select(Permission)
        result = await self.session.execute(statement)
        permissions = result.scalars().all()
        return [PermissionSchema(**permission.__dict__) for permission in permissions]

    async def get_permission_by_id(self, permission_id: UUID) -> Optional[Permission]:
        statement = select(Permission).where(Permission.id == permission_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        statement = select(Permission).where(Permission.name == name)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def update_permission(self, permission: Type[Permission], permission_data: PermissionUpdate) -> PermissionSchema:
        try:
            for key, value in permission_data.model_dump(exclude_unset=True).items():
                setattr(permission, key, value)

            await self.session.commit()
            await self.session.refresh(permission)
            return PermissionSchema(**permission.__dict__)
        except NoResultFound:
            return None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_permission(self, permission: Type[Permission]) -> bool:
        try:
            await self.session.delete(permission)
            await self.session.commit()
            return True
        except NoResultFound:
            return None
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_permissions_by_role(self, role_id: UUID) -> List[PermissionSchema]:
        statement = select(Permission).join(RolePermission).where(RolePermission.role_id == role_id)
        result = await self.session.execute(statement)
        permissions = result.scalars().all()
        return [PermissionSchema(**permission.__dict__) for permission in permissions]

    # async def get_permissions_by_user(self, user_id: UUID) -> List[PermissionSchema]:
    #     # statement = select(Permission).join(RolePermission).join(UserRole).where(UserRole.user_id == user_id)
    #     statement = (select(Permission).join(RolePermission, RolePermission.permission_id == Permission.id).join(UserRole, UserRole.role_id == RolePermission.role_id).where(UserRole.user_id == user_id))
    #     result = await self.session.execute(statement)
    #     permissions = result.scalars().all()
    #     return [PermissionSchema(**permission.__dict__) for permission in permissions]
    
    async def get_permissions_by_user(self, user_id: UUID) -> List[PermissionSchema]:
        # statement = select(Permission).join(RolePermission).join(UserRole).where(UserRole.user_id == user_id)
        statement = (select(Permission).join(UserPermission, UserPermission.permission_id == Permission.id).where(UserPermission.user_id == user_id))
        result = await self.session.execute(statement)
        permissions = result.scalars().all()
        return [PermissionSchema(**permission.__dict__) for permission in permissions]

    async def get_roles_by_user(self, user_id: UUID) -> List[RoleSchema]:
        statement = select(Role).join(UserRole).where(UserRole.user_id == user_id)
        result = await self.session.execute(statement)
        roles = result.scalars().all()
        return [RoleSchema(**role.__dict__) for role in roles]

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> bool:
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(role_permission)
        await self.session.commit()
        return True
    
    async def assign_permission_to_role_by_name(self, role_name: str, permission_name: str) -> bool:
    
        role = await self.session.execute(select(Role).where(Role.name == role_name))
        role = role.scalar_one_or_none()
    
        permission = await self.session.execute(select(Permission).where(Permission.name == permission_name))
        permission = permission.scalar_one_or_none()

        if not role or not permission:
            return False  

        
        role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
        self.session.add(role_permission)
        await self.session.commit()
        
        return True


    # async def assign_permission_to_user(self, user_id: UUID, permission_id: UUID) -> bool:
    #     user_role = await self.get_roles_by_user(user_id)
    #     if not user_role:
    #         raise NoResultFound("User has no assigned roles")
    #     role_permissions = [await self.get_permissions_by_role(role.id) for role in user_role]
    #     if any(permission_id in [p.id for p in permissions] for permissions in role_permissions):
    #         return False
    #     user_permission = UserPermission(role_id=user_role[0].id, permission_id=permission_id)
    #     self.session.add(user_permission)
    #     await self.session.commit()
    #     return True
    
    async def assign_permission_to_user(self, user_id: UUID, permission_id: UUID) -> bool:
        user_permissions = await self.get_permissions_by_user(user_id)  # Get user's current permissions

        # If permission already exists, prevent duplicate assignment
        if any(p.id == permission_id for p in user_permissions):
            raise HTTPException(status_code=400, detail="Permission already assigned to user")

        # Assign the new permission
        new_user_permission = UserPermission(user_id=user_id, permission_id=permission_id)
        self.session.add(new_user_permission)
        await self.session.commit()
        return True


    async def remove_permission_from_role(self, role_id: UUID, permission_id: UUID) -> bool:
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id, RolePermission.permission_id == permission_id
        )
        result = await self.session.execute(statement)
        role_permission = result.scalars().first()
        if role_permission:
            await self.session.delete(role_permission)
            await self.session.commit()
            return True
        return False

    async def remove_permission_from_user(self, user_id: UUID, permission_id: UUID) -> bool:
        """Remove a specific permission directly assigned to a user."""
        statement = select(UserPermission).where(
            UserPermission.user_id == user_id, UserPermission.permission_id == permission_id
        )
        result = await self.session.execute(statement)
        user_permission = result.scalars().first()

        if not user_permission:
            raise HTTPException(status_code=404, detail="Permission not found for user")

        await self.session.delete(user_permission)
        await self.session.commit()
        return True

