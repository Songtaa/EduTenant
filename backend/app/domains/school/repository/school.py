# app/repositories/school.py
from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from app.domains.school.models.school import School
from app.crud.base import BaseRepository
from app.domains.school.schemas.school import SchoolCreate, SchoolUpdate

class SchoolRepository(BaseRepository[School, SchoolUpdate, SchoolCreate]):
    def __init__(self, session: Session):
        super().__init__(School, session)
    
    def get_main_school(self, tenant_id: UUID) -> Optional[School]:
        return self.session.exec(
            select(School)
            .where(School.tenant_id == tenant_id)
            .where(School.name == "Main Campus")
        ).first()