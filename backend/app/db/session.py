# app/db/session.py
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
        @event.listens_for(engine.sync_engine, "connect")
        def set_search_path(dbapi_connection, connection_record):
            # Set search path in a non-blocking way (asynchronous)
            async def set_schema():
                async with dbapi_connection.begin():  # Use async transaction context
                    await dbapi_connection.execute(text(f"SET search_path TO {tenant_id}, public"))

            # Run the async schema setup in the event handler
            set_schema()

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

async def clear_engine_cache():
    """Clear all cached engines and their connection pools"""
    for engine in tenant_engines.values():
        await engine.dispose()  # Properly close all connections
    tenant_engines.clear()