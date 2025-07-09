from fastapi import Request
from app.db.session import master_async_engine
from typing import Annotated, AsyncGenerator, List
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.db.session import db_session_dependency, get_master_session, get_tenant_session

def get_master_engine():
    return master_async_engine


async def get_master_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async with get_master_session() as session:
        yield session



async def get_tenant_session_dep(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with db_session_dependency(request) as session:
        yield session