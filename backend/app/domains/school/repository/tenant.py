# app/repositories/tenant.py
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from app.domains.school.models.school import School
from sqlmodel import Session
from app.domains.school.models.tenant import Tenant
from app.crud.base import BaseRepository
from sqlmodel.ext.asyncio.session import AsyncSession


# app/repositories/tenant.py
from typing import Any, List, Optional, Dict
from app.domains.school.schemas.tenant import TenantCreate, TenantUpdate


class TenantRepository(BaseRepository[Tenant, TenantCreate, TenantUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)
    
    async def get_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.subdomain == subdomain)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_with_school(
        self, 
        tenant_data: TenantCreate, 
        school_data: Dict[str, Any]
    ) -> Tenant:
        """
        Creates a new tenant along with a default school.
        
        Args:
            tenant_data: Validated tenant creation data
            school_data: Raw school data (will be validated in service layer)
            
        Returns:
            The created Tenant with associated School
            
        Note:
            In production, the school creation would happen in a separate
            tenant-specific database session
        """
        try:
            # Create tenant
            tenant = await self.create(tenant_data)
            
            # Create default school (in same transaction for demo)
            school = School(**school_data, tenant_id=tenant.id)
            self.session.add(school)
            self.session.commit()
            self.session.refresh(tenant)
            
            return tenant
            
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create tenant: {str(e)}"
            )
    
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
