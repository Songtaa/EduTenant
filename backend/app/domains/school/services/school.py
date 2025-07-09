# app/services/school.py
from typing import List, Optional
from uuid import UUID
import logging
from app.domains.school.repository.tenant import TenantRepository
from fastapi import HTTPException, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.domains.school.schemas.school import SchoolCreate, SchoolUpdate, SchoolOut
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.services.tenant import TenantService
from app.db.session import get_tenant_session
from app.config.tenant_dependencies import get_tenant_id
from app.utils.dependencies import get_tenant_session_dep
from fastapi import Request

logger = logging.getLogger(__name__)

class SchoolService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)
        self.tenant_repo = TenantRepository(session)

    async def _validate_tenant(self) -> None:
        tenant = await self.tenant_repo.get(self.tenant_id)
        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or inactive tenant"
            )

    async def create_school(self, school_data: SchoolCreate) -> SchoolOut:
        await self._validate_tenant()

        existing = await self.school_repo.get_by_name_and_tenant(
            school_data.name, self.tenant_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="School name already exists for this tenant"
            )

        try:
            school_data_with_tenant = school_data.copy(update={"tenant_id": self.tenant_id})
            created_school = await self.school_repo.create(school_data_with_tenant)
            return created_school
        except Exception as e:
            logger.exception("Failed to create school")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create school: {str(e)}"
            )

    async def get_school(self, school_id: UUID) -> SchoolOut:
        await self._validate_tenant()

        school = await self.school_repo.get(school_id)
        if not school or school.tenant_id != self.tenant_id:
            raise HTTPException(404, "School not found")
        return SchoolOut.from_orm(school)

    async def update_school(self, school_id: UUID, update_data: SchoolUpdate) -> SchoolOut:
        await self._validate_tenant()

        school = await self.school_repo.get(school_id)
        if not school or school.tenant_id != self.tenant_id:
            raise HTTPException(404, "School not found")

        try:
            if update_data.name and update_data.name != school.name:
                existing = await self.school_repo.get_by_name_and_tenant(
                    update_data.name, self.tenant_id
                )
                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail="Another school with this name already exists for this tenant"
                    )

            updated_school = await self.school_repo.update(school_id, update_data.dict(exclude_unset=True))
            return updated_school
        except Exception as e:
            await self.session.rollback()
            logger.exception("Failed to update school")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update school: {str(e)}"
            )

    async def get_main_school(self) -> SchoolOut:
        await self._validate_tenant()

        school = await self.school_repo.get_main_school(self.tenant_id)
        if not school:
            raise HTTPException(404, "Main school not configured")
        return SchoolOut.from_orm(school)

    async def list_schools(
        self,
        search_term: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[SchoolOut]:
        await self._validate_tenant()

        schools = await self.school_repo.get_all(
            tenant_id=self.tenant_id,
            search_term=search_term,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        return schools

    async def deactivate_school(self, school_id: UUID) -> bool:
        await self._validate_tenant()

        school = await self.school_repo.get(school_id)
        if not school or school.tenant_id != self.tenant_id:
            raise HTTPException(404, "School not found")

        try:
            await self.school_repo.update(
                school_id, {"is_active": False}
            )
            return True
        except Exception as e:
            await self.session.rollback()
            logger.exception("Failed to deactivate school")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to deactivate school: {str(e)}"
            )


    async def delete_school(self, school_id: UUID) -> bool:
        await self._validate_tenant()

        school = await self.school_repo.get_by_id(school_id)
        if not school or school.tenant_id != self.tenant_id:
            raise HTTPException(status_code=404, detail="School not found")

        try:
            await self.school_repo.delete(school_id)
            return True
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete school: {str(e)}"
            )


async def get_school_service(
    request: Request,
    session: AsyncSession = Depends(get_tenant_session_dep),
    tenant_id: UUID = Depends(get_tenant_id)
) -> SchoolService:
    return SchoolService(session=session, tenant_id=tenant_id)
