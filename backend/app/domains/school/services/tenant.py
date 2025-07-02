# app/services/tenant.py
from typing import List, Optional
from uuid import UUID
from app.utils.tenant_bootstrapper import TenantBootstrapper
from fastapi import Depends, HTTPException
from app.domains.auth.services.user_service import UserService
from app.utils.seeder import seed_global_admin_user, seed_tenant_admin_user
from sqlmodel import Session
from app.domains.school.schemas.tenant import TenantCreate, TenantUpdate, TenantRead, TenantSchema
from app.domains.school.repository.tenant import TenantRepository
from app.domains.school.models.tenant import Tenant
from app.db.session import get_master_session
from app.utils.tenant import create_schema, create_schema_tables
from app.domains.auth.schemas.user_schema import UserCreate
from app.db.session import get_tenant_session
from app.utils.dependencies import get_master_engine
from app.domains.auth.models.tenant_user import TenantUser

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text



# class TenantService:
#     def __init__(self, session: AsyncSession):
#         self.session = session
#         self.repository = TenantRepository(session)
class TenantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
        self.repository = TenantRepository(session)

    async def get_all(self) -> List[Optional[TenantSchema]]:
        return await self.repository.get_all()

    async def create_tenant(self, tenant_data: TenantCreate) -> TenantRead:
        # Step 0: Check for domain/subdomain conflicts
        if await self.repository.get_by_subdomain(tenant_data.subdomain):
            raise HTTPException(status_code=400, detail="Domain already in use")

        try:
            schema_name = tenant_data.schema_name  # must now be passed explicitly

            # Step 1: Bootstrap schema if needed
            bootstrapper = TenantBootstrapper(get_master_engine())
            await bootstrapper.bootstrap_if_needed(schema_name)

            # Step 2: Create tenant
            tenant = await self.repository.create(tenant_data)
            await self.session.commit()

            return TenantRead.from_orm(tenant)

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")


    async def create_tenant_with_admin(self, tenant_data: TenantCreate, admin_data: UserCreate):
        """Create a tenant and seed a default admin user"""
        tenant_out = await self.create_tenant(tenant_data)

        # Use tenant-specific session to seed admin
        async with get_tenant_session(tenant_data.subdomain) as tenant_session:
            await seed_tenant_admin_user(session=tenant_session, user_data=admin_data, user_model=TenantUser)

        return tenant_out

    async def get_tenant(self, tenant_id: UUID) -> TenantSchema:
        """Retrieve a tenant by ID"""
        tenant = await self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")
        return TenantRead.from_orm(tenant)

    async def update_tenant(self, tenant_id: UUID, update_data: TenantUpdate) -> TenantSchema:
        """Update tenant details"""
        tenant = await self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        if update_data.subdomain and update_data.subdomain != tenant.subdomain:
            if await self.repository.get_by_subdomain(update_data.subdomain):
                raise HTTPException(400, "New subdomain already in use")

        updated_tenant = await self.repository.update(db_obj=tenant, obj_in=update_data)

        await self.session.commit()

        return TenantRead.from_orm(updated_tenant)

    async def deactivate_tenant(self, tenant_id: UUID) -> bool:
        """Soft-deactivate a tenant"""
        tenant = await self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        await self.repository.update(db_obj=tenant, obj_in={"is_active": False})
        return True

    async def list_tenants(
        self,
        search_term: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[TenantRead]:
        tenants = await self.repository.list_all(
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