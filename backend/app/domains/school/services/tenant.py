# app/services/tenant.py
from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException
from app.domains.auth.services.user_service import UserService
from app.utils.seeder import seed_admin_user
from sqlmodel import Session
from app.domains.school.schemas.tenant import TenantCreate, TenantUpdate, TenantRead
from app.domains.school.repository.tenant import TenantRepository
from app.domains.school.models.tenant import Tenant
from app.db.session import get_master_session
from app.utils.tenant import create_schema, create_schema_tables
from app.domains.auth.schemas.user_schema import UserCreate
from app.db.session import get_tenant_session


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text



class TenantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = TenantRepository(session)

    async def create_tenant(self, tenant_data: TenantCreate) -> TenantRead:
        """Create a new tenant with schema and tables"""

        if await self.repository.get_by_domain(tenant_data.domain):
            raise HTTPException(status_code=400, detail="Domain already in use")

        try:
            # Use master session to create schema and tables
            async with get_master_session() as master_session:
                await create_schema(tenant_data.domain)
                await create_schema_tables(tenant_data.domain, master_session)

                # Register tenant in the master DB
                tenant = await self.repository.create(tenant_data)
                await master_session.commit()

            return TenantRead.from_orm(tenant)

        except Exception as e:
            await master_session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

    async def create_tenant_with_admin(self, tenant_data: TenantCreate, admin_data: UserCreate):
        """Create a tenant and seed a default admin user"""
        tenant_out = await self.create_tenant(tenant_data)

        # Use tenant-specific session to seed admin
        async with get_tenant_session(tenant_data.domain) as tenant_session:
            await seed_admin_user(tenant_session, admin_data)

        return tenant_out

    async def get_tenant(self, tenant_id: UUID) -> TenantRead:
        """Retrieve a tenant by ID"""
        tenant = await self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")
        return TenantRead.from_orm(tenant)

    async def update_tenant(self, tenant_id: UUID, update_data: TenantUpdate) -> TenantRead:
        """Update tenant details"""
        tenant = await self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        if update_data.domain and update_data.domain != tenant.domain:
            if await self.repository.get_by_domain(update_data.domain):
                raise HTTPException(400, "New domain already in use")

        updated_tenant = await self.repository.update(tenant, update_data)
        await self.session.commit()

        return TenantRead.from_orm(updated_tenant)

    async def deactivate_tenant(self, tenant_id: UUID) -> bool:
        """Soft-deactivate a tenant"""
        tenant = await self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        await self.repository.update(tenant, {"is_active": False})
        await self.session.commit()
        return True

    async def search_tenants(
        self,
        search_term: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[TenantRead]:
        tenants = await self.repository.search_tenants(
            search_term=search_term,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        return [TenantRead.from_orm(t) for t in tenants]

    async def _create_schema(self, schema_name: str):
        """Creates the schema in the shared database"""
        await self.session.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
        )

# FastAPI Dependency Injection
def get_tenant_service(session: AsyncSession = Depends(get_master_session)) -> TenantService:
    return TenantService(session)
