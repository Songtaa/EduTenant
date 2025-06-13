from typing import List, Optional, Type
from uuid import UUID

from sqlmodel import select
# from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domains.school.models.services import Service
from app.domains.school.schemas.services_schemas import ServiceBase, ServiceRead,ServiceCreate, ServiceUpdate, ServiceSchema
from sqlalchemy.orm.exc import NoResultFound
from sqlmodel import select
from app.utils.security import Security
from uuid import UUID
from typing import List, Type


class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_services(self) -> List[Service]:
        statement = select(Service)
        result = await self.session.execute(statement)
        return result.scalars().all()
    
    async def get_all(self) -> List[Optional[ServiceSchema]]:
        statement = select(Service)
        result = await self.session.execute(statement)
        services = result.scalars().all()
        return [ServiceSchema(**service.__dict__) for service in services]

    # async def service_exists_by_name(self, name: str) -> bool:
    #     service = self.session.query(Service).filter_by(name=name).first()
    #     return bool(service)

    async def service_exists_by_name(self, name: str) -> bool:
        statement = select(Service).where(Service.name == name) 
        result = await self.session.execute(statement) 
        service = result.scalars().first()
        return bool(service)

    async def get_service_by_name(self, name: str):

        statement = select(Service).where(Service.name == name)

        result = await self.session.exec(statement)

        service = result.scalar()

        return service

    async def get_service_by_id(self, service_id: UUID):
        statement = select(Service).where(Service.id == service_id)
        result = await self.session.execute(statement) 
        service = result.scalars().first()
        return service

    

    async def create_service(self, service_data: ServiceCreate):
        service_data_dict = service_data.model_dump()

        new_service = Service(**service_data_dict)


        self.session.add(new_service)

        await self.session.commit()

        return new_service

    async def update(self, service: Type[Service], service_data: ServiceUpdate)-> ServiceSchema:
        try:
            
            for key, value in service_data.model_dump(exclude_unset=True).items():
                setattr(service, key, value)

            
            await self.session.commit()
            await self.session.refresh(service)  
            return ServiceSchema(**service.__dict__)
        except NoResultFound:
            return None  
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_service(self, service:Type[Service]):
        try:

            await self.session.delete(service)
            await self.session.commit()
            return True
        except NoResultFound:
            return None
        except Exception as e:
            await self.session.rollback()
            raise e