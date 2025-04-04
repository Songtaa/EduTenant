# app/services/school.py
from typing import List
from uuid import UUID
from fastapi import HTTPException, Depends
from sqlmodel import Session
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolOut
from app.repositories.school import SchoolRepository
from app.db.session import get_tenant_session
from app.core.tenant_dependencies import get_tenant_id

class SchoolService:
    def __init__(self, session: Session, tenant_id: UUID):
        self.repository = SchoolRepository(session)
        self.tenant_id = tenant_id

    def create_school(self, school_data: SchoolCreate) -> SchoolOut:
        """Create a new school for the current tenant"""
        try:
            # Add tenant_id to school data
            school_data_dict = school_data.dict()
            school_data_dict["tenant_id"] = self.tenant_id
            
            school = self.repository.create(school_data_dict)
            return SchoolOut.from_orm(school)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create school: {str(e)}"
            )

    def get_school(self, school_id: UUID) -> SchoolOut:
        """Get school details with tenant validation"""
        school = self.repository.get(school_id)
        if not school or school.tenant_id != self.tenant_id:
            raise HTTPException(404, "School not found")
        return SchoolOut.from_orm(school)

    def update_school(
        self,
        school_id: UUID,
        update_data: SchoolUpdate
    ) -> SchoolOut:
        """Update school information"""
        school = self.repository.get(school_id)
        if not school or school.tenant_id != self.tenant_id:
            raise HTTPException(404, "School not found")

        updated_school = self.repository.update(
            db_obj=school,
            obj_in=update_data
        )
        return SchoolOut.from_orm(updated_school)

    def get_main_school(self) -> SchoolOut:
        """Get the primary school for the tenant"""
        school = self.repository.get_main_school(self.tenant_id)
        if not school:
            raise HTTPException(404, "Main school not configured")
        return SchoolOut.from_orm(school)

    def list_schools(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[SchoolOut]:
        """List all schools for the tenant"""
        schools = self.repository.get_all(
            skip=skip,
            limit=limit
        )
        # Filter by tenant in case repository doesn't
        schools = [s for s in schools if s.tenant_id == self.tenant_id]
        return [SchoolOut.from_orm(s) for s in schools]

# Dependency for FastAPI
def get_school_service(
    tenant_id: UUID = Depends(get_tenant_id),
    session: Session = Depends(get_tenant_session)
):
    return SchoolService(session, tenant_id)