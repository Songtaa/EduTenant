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


# app/repositories/tenant.py
from typing import Any, List, Optional, Dict
from app.domains.school.schemas.tenant import TenantCreate, TenantUpdate, TenantSchema


class TenantRepository(BaseRepository[Tenant, TenantCreate, TenantUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)
    
    async def get_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        stmt = select(Tenant.schema_name).where(Tenant.subdomain == subdomain)
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

    # async def create(self, tenant_data: TenantCreate) -> Tenant:
    #     try:
    #         # 1. Create the schema
    #         schema_name = tenant_data.subdomain
    #         await self.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    #         # 2. Clone tables using SchemaFactory
    #         schema_factory = SchemaFactory(schema_name)
    #         metatenant_data, _ = schema_factory.clone()

    #         # 3. Create tables for this schema
    #         await self._create_schema_tables(metatenant_data)

    #         # 4. Save tenant in public schema
    #         tenant = Tenant(**tenant_data.dict())
    #         self.session.add(tenant)
    #         await self.session.flush()  # generate ID
    #         await self.session.refresh(tenant)

    #         return tenant

    #     except Exception as e:
    #         await self.session.rollback()
    #         raise TenantCreationException(f"Error creating tenant: {str(e)}")

    # async def _create_schema_tables(self, metatenant_data):
    #     # You need to run the schema creation in a separate sync block
    #     # since SQLAlchemy ORM table creation is synchronous
    #     from app.db.session import engine  # or pass engine into repo constructor if preferred
    #     async with engine.begin() as conn:
    #         await conn.run_sync(metatenant_data.create_all)
    
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
