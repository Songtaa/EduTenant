from typing import Annotated

from app.db.session import get_master_session
from app.domains.school.services.school import (
    SchoolService,
    SchoolCreate,
    SchoolUpdate,
)
from app.utils.auth_dep import access_token_bearer
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

school_router = APIRouter(prefix="/schools", tags=["Schools"])

sessionDep = Annotated[AsyncSession, Depends(get_master_session)]


@school_router.post("/", response_model=SchoolCreate)
async def create_school(school_data: SchoolCreate, session: sessionDep):
    _school = SchoolService(session)
    school = await _school.create(school_data)
    return school


@school_router.patch("/{school_id}", response_model=SchoolUpdate)
async def update_school(
    school_id: str, school_data: SchoolUpdate, session: sessionDep
):
    _school = SchoolService(session)
    school = await _school.update(school_id, school_data)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@school_router.get("/", response_model=list[SchoolCreate])
async def get_all_schools(
    session: sessionDep, user_details=Depends(access_token_bearer)
):
    _school = SchoolService(session)
    return await _school.get_all()


@school_router.delete("/{_id}", status_code=204)
async def delete_school(
    _id: UUID4,
    session: sessionDep,
):
    _school = SchoolService(session)
    return await _school.delete(_id)
