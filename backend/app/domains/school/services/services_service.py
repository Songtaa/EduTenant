from typing import List, Optional

from app.domains.school.models.services import Service
from app.domains.school.repository.services_repository import ServiceRepository
from app.domains.school.schemas.services_schemas import (
    ServiceCreate,
    ServiceSchema,
    ServiceUpdate,
)
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession


class Service:
    def __init__(self, session: AsyncSession):
        self.service_repository = ServiceRepository(session)

    async def get_services(self) -> List[Service]:
        return await self.service_repository.get_all_services()

    async def service_exists(self, name: str):
        service = await self.service_repository.get_service_by_name(name)

        return True if service is not None else False

    async def create(self, service_data: ServiceCreate) -> ServiceSchema:
        if await self.service_repository.service_exists_by_name(service_data.name):
            raise HTTPException(
                status_code=400, detail="Service with this name already exists"
            )

        created_service = await self.service_repository.create_service(service_data)

        return ServiceSchema(**created_service.__dict__)

    async def get_all(self) -> List[Optional[ServiceSchema]]:
        return await self.service_repository.get_all()

    async def update(self, service_id: UUID4, data: ServiceUpdate) -> ServiceSchema:
        service = await self.service_repository.get_service_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="service not found")

        updated_service = await self.service_repository.update(service, data)
        return updated_service

    async def delete(self, service_id: UUID4) -> bool:
        if not await self.service_repository.get_service_by_id(service_id):
            raise HTTPException(status_code=404, detail="Service not found")
        user = await self.service_repository.get_service_by_id(service_id)
        await self.service_repository.delete_service(user)
        return True
