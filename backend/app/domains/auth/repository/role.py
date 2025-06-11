from app.domains.auth.models.user_role import UserRole
from app.domains.auth.models.role_permission import RolePermission
from sqlmodel import Session, select
from app.domains.auth.models.role import Role

from app.domains.auth.schemas.role import RoleCreate, RoleRead, RoleSchema, RoleUpdate
from uuid import UUID
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from typing import List, Type, Optional


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def grant_permission(self, role_id: UUID, permission_id: UUID):
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(role_permission)
        self.session.commit()
        return {"message": "Permission granted"}

    def revoke_permission(self, role_id: UUID, permission_id: UUID):
        role_permission = self.session.exec(select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission_id)).first()
        if not role_permission:
            return {"error": "Permission not found in role"}
        self.session.delete(role_permission)
        self.session.commit()
        return {"message": "Permission revoked"}
    
    async def get_all_roles(self) -> List[Role]:
        statement = select(Role)
        result = await self.session.execute(statement)
        return result.scalars().all()
    
    async def get_all(self) -> List[Optional[RoleSchema]]:
        statement = select(Role)
        result = await self.session.execute(statement)
        roles = result.scalars().all()
        return [RoleSchema(**role.__dict__) for role in roles]

    async def role_exists_by_name(self, name: str) -> bool:
        statement = select(Role).where(Role.name == name) 
        result = await self.session.execute(statement) 
        role = result.scalars().first()
        return bool(role)

    async def get_role_by_name(self, name: str):

        statement = select(Role).where(Role.name == name)

        result = await self.session.execute(statement)

        role = result.scalar()

        return role

    async def get_role_by_id(self, role_id: UUID):
        statement = select(Role).where(Role.id == role_id)
        result = await self.session.execute(statement) 
        role = result.scalars().first()
        return role

    async def get_roles_by_user(self, user_id: UUID) -> List[RoleSchema]:
        statement = select(Role).join(UserRole).where(UserRole.user_id == user_id)
        result = await self.session.execute(statement)
        roles = result.scalars().all()
        return [RoleSchema(**role.__dict__) for role in roles]

    async def create_role(self, role_data: RoleCreate):
        role_data_dict = role_data.model_dump()

        new_role = Role(**role_data_dict)


        self.session.add(new_role)

        await self.session.commit()

        return new_role

    async def update(self, role: Type[Role], role_data: RoleUpdate)-> RoleSchema:
        try:
            
            for key, value in role_data.model_dump(exclude_unset=True).items():
                setattr(role, key, value)

            
            await self.session.commit()
            await self.session.refresh(role)  
            return RoleSchema(**role.__dict__)
        except NoResultFound:
            return None  
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_service(self, role:Type[Role]):
        try:

            await self.session.delete(role)
            await self.session.commit()
            return True
        except NoResultFound:
            return None
        except Exception as e:
            await self.session.rollback()
            raise e


    async def assign_role_to_user(self, user_id: UUID, role_id: UUID):
        # Check if the role already exists for the user
        existing_user_role = await self.session.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        existing_user_role = existing_user_role.scalar()
        if existing_user_role:
            return {"error": "User already has this role"}

        # Assign the role to the user
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.commit()

        return {"message": "Role assigned to user"}

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID):
        # Find the user-role relationship to remove
        user_role = await self.session.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        user_role = user_role.scalar()
        if not user_role:
            return {"error": "Role not assigned to user"}

        # Remove the role from the user
        await self.session.delete(user_role)
        await self.session.commit()

        return {"message": "Role removed from user"}