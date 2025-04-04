# app/services/tenant.py
from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlmodel import Session
from app.domains.school.schemas.tenant import TenantCreate, TenantUpdate, TenantOut
from app.domains.school.repository.tenant import TenantRepository
from app.domains.school.models.tenant import Tenant
from app.db.session import get_master_session

class TenantService:
    def __init__(self, session: Session):
        self.repository = TenantRepository(session)

    def create_tenant(self, tenant_data: TenantCreate) -> TenantOut:
        """Create a new tenant with validation"""
        if self.repository.get_by_domain(tenant_data.domain):
            raise HTTPException(
                status_code=400,
                detail="Domain already in use"
            )

        try:
            tenant = self.repository.create(tenant_data)
            return TenantOut.from_orm(tenant)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create tenant: {str(e)}"
            )

    def get_tenant(self, tenant_id: UUID) -> TenantOut:
        """Retrieve a single tenant"""
        tenant = self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )
        return TenantOut.from_orm(tenant)

    def update_tenant(
        self,
        tenant_id: UUID,
        update_data: TenantUpdate
    ) -> TenantOut:
        """Partially update tenant details"""
        tenant = self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        if update_data.domain and update_data.domain != tenant.domain:
            if self.repository.get_by_domain(update_data.domain):
                raise HTTPException(400, "New domain already in use")

        updated_tenant = self.repository.update(
            db_obj=tenant,
            obj_in=update_data
        )
        return TenantOut.from_orm(updated_tenant)

    def deactivate_tenant(self, tenant_id: UUID) -> bool:
        """Soft delete a tenant"""
        tenant = self.repository.get(tenant_id)
        if not tenant:
            raise HTTPException(404, "Tenant not found")

        return self.repository.update(
            db_obj=tenant,
            obj_in={"is_active": False}
        )

    def search_tenants(
        self,
        search_term: str = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[TenantOut]:
        """Search tenants with pagination"""
        tenants = self.repository.search_tenants(
            search_term=search_term,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        return [TenantOut.from_orm(t) for t in tenants]

# Dependency for FastAPI
def get_tenant_service(session: Session = Depends(get_master_session)):
    return TenantService(session)