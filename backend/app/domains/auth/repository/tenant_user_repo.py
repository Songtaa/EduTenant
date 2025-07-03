from typing import List, Optional

from app.crud.base import BaseRepository, ModelType
from app.domains.auth.models.users import User
from app.domains.auth.models.user_role import UserRole
from app.domains.auth.models.tenant_user import TenantUser
from app.domains.auth.schemas.tenant_user import TenantUserCreate, TenantUserSchema, TenantUserUpdate
from app.domains.school.models.tenant_user_role import TenantUserRole
from pydantic import UUID4
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.utils.security import Security
from uuid import UUID
from typing import List, Type

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TenantUserRepository(BaseRepository[ModelType, TenantUserCreate, TenantUserUpdate]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        super().__init__(model, session)


    async def get_all(self) -> List[Optional[TenantUserSchema]]:
        statement = select(TenantUser)
        result = await self.session.execute(statement)
        users = result.scalars().all()
        return [TenantUserSchema(**user.__dict__) for user in users]


    async def get_user_by_email(self, email: str):
        statement = select(TenantUser).where(TenantUser.email == email)

        result = await self.session.execute(statement)

        user = result.scalar()

        return user

    async def get_user_by_id(self, user_id: UUID):
        statement = select(TenantUser).where(TenantUser.id == user_id)
        result = await self.session.execute(statement) 
        user = result.scalars().first()
        return user

    

    async def create_user(self, user_data: TenantUserCreate):
        user_data_dict = user_data.model_dump()

        logger.info(f"Creating tenant user in model: {self.model.__tablename__}")
        new_user = TenantUser(**user_data_dict)

        new_user.password = Security.generate_password_hash(user_data_dict["password"])
        # new_user.role = "user"


        self.session.add(new_user)

        await self.session.commit()
        logger.info(f"Tenant user created with email: {new_user.email} and id: {new_user.id}")

        return new_user

    async def update(self, user: Type[TenantUser], user_data: TenantUserUpdate)-> TenantUserSchema:
        try:
            
            for key, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, key, value)

            
            await self.session.commit()
            await self.session.refresh(user)  
            return TenantUserSchema(**user.__dict__)
        except NoResultFound:
            return None  
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_user(self, user:Type[TenantUser]):
        try:

            await self.session.delete(user)
            await self.session.commit()
            return True
        except NoResultFound:
            return None
        except Exception as e:
            await self.session.rollback()
            raise e


    def assign_role(self, user_id: UUID, role_id: UUID):
        user_role = TenantUserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        self.session.commit()
        return {"message": "Role assigned successfully"}
    
    
# user_repository = UserRepository()