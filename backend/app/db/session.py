# app/db/session.py
from fastapi import Request
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict
import logging
from sqlalchemy import event, text

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO if settings.DEBUG else logging.WARNING)


# Master engine for public schema (tenant management)
master_async_engine = create_async_engine(
    str(settings.MASTER_DB_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    poolclass=NullPool
)

# Tenant engines cached in memory
tenant_engines: Dict[str, AsyncSession] = {}

# Session factories for master
MasterAsyncSessionLocal = sessionmaker(
    bind=master_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Session factories for tenant
@asynccontextmanager
async def get_master_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for public schema sessions"""
    async with MasterAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_tenant_engine(tenant_id: str):
    """Get or create an async engine for a specific tenant schema"""
    if tenant_id not in tenant_engines:
        engine = create_async_engine(
            str(settings.SHARED_DB_URL),
            echo=settings.DEBUG,
            pool_pre_ping=True,
            poolclass=NullPool
        )

        # Listen for the connection event and set the search path
        # @event.listens_for(engine.sync_engine, "connect")
        # def set_search_path(dbapi_connection, connection_record):
        #     # Set search path in a non-blocking way (asynchronous)
        #     async def set_schema():
        #         async with dbapi_connection.begin():  # Use async transaction context
        #             await dbapi_connection.execute(text(f"SET search_path TO {tenant_id}, public"))

        #     # Run the async schema setup in the event handler
        #     set_schema()
        
        @event.listens_for(engine.sync_engine, "connect")
        def set_search_path(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET search_path TO {tenant_id}, public")
            cursor.close()


        tenant_engines[tenant_id] = engine

    return tenant_engines[tenant_id]


@asynccontextmanager
async def get_tenant_session(tenant_id: str) -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for tenant-specific schema sessions"""
    engine = get_tenant_engine(tenant_id)
    TenantAsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with TenantAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# async def db_session_dependency(request: Request) -> AsyncSession:
#     """Session dependency that supports both global and tenant-specific routes"""
#     tenant_id = request.headers.get("X-Tenant-ID") or request.url.hostname.split(".")[0]

#     if tenant_id and tenant_id != "api":  # Assuming 'api' is for global access
#         async with get_tenant_session(tenant_id) as session:
#             return session
#     else:
#         async with get_master_session() as session:
#             return session

async def db_session_dependency(request: Request) -> AsyncSession:
    tenant_id = request.headers.get("X-Tenant-ID") or request.url.hostname.split(".")[0]

    if tenant_id and tenant_id != "api":
        session_factory = sessionmaker(
            bind=get_tenant_engine(tenant_id),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    else:
        session_factory = MasterAsyncSessionLocal

    session = session_factory()

    try:
        yield session
    finally:
        await session.close()


async def clear_engine_cache():
    """Clear all cached engines and their connection pools"""
    for engine in tenant_engines.values():
        await engine.dispose()  # Properly close all connections
    tenant_engines.clear()