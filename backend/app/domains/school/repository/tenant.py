# app/repositories/tenant.py
from uuid import UUID
from app.utils.errors import TenantCreationException
from app.utils.schema_utils import SchemaFactory
from fastapi import HTTPException
from sqlalchemy import select, text
from app.domains.school.models.school import School
from sqlmodel import Session
from app.domains.school.models.tenant import Tenant
from app.crud.base import BaseRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, List, Optional, Dict
from app.domains.school.schemas.tenant import TenantCreate, TenantUpdate, TenantSchema


class TenantRepository(BaseRepository[Tenant, TenantCreate, TenantUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)
    
    async def get_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.subdomain == subdomain)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_schema_name(self, schema_name: str) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.schema_name == schema_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    
    async def get_all(self) -> List[Optional[TenantSchema]]:
        statement = select(Tenant)
        result = await self.session.execute(statement)
        users = result.scalars().all()
        return [TenantSchema(**user.__dict__) for user in users]

    
    async def list_all(
        self,
        search_term: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tenant]:
        query = select(Tenant)

        if active_only:
            query = query.where(Tenant.is_active.is_(True))

        if search_term:
            query = query.where(
                (Tenant.name.ilike(f"%{search_term}%")) |
                (Tenant.domain.ilike(f"%{search_term}%"))
            )

        result = await self.session.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
