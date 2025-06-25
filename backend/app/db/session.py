from fastapi import Request
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict
from app.config.settings import settings
import logging

# Configure logging
logging.basicConfig()
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)

# Master DB Engine
master_async_engine = create_async_engine(
    str(settings.MASTER_DB_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    poolclass=NullPool
)

# Tenant Engine Cache
tenant_engines: Dict[str, AsyncEngine] = {}

# Master Session Factory
MasterAsyncSessionLocal = sessionmaker(
    bind=master_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


# Master Schema Session

@asynccontextmanager
async def get_master_session() -> AsyncGenerator[AsyncSession, None]:
    async with MasterAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()



# Tenant Engine and Session Management

def get_tenant_engine(tenant_id: str) -> AsyncEngine:
    """Get or create tenant-specific engine with search_path set."""
    if tenant_id not in tenant_engines:
        engine = create_async_engine(
            str(settings.SHARED_DB_URL),
            echo=settings.DEBUG,
            pool_pre_ping=True,
            poolclass=NullPool
        )

        @event.listens_for(engine.sync_engine, "connect")
        def set_search_path(dbapi_connection, connection_record):
            try:
                cursor = dbapi_connection.cursor()
                cursor.execute("SET search_path TO %s, public", (tenant_id,))
            finally:
                cursor.close()

        tenant_engines[tenant_id] = engine

        if settings.DEBUG:
            logger.info(f"Created tenant engine for schema: {tenant_id}")

    return tenant_engines[tenant_id]


@asynccontextmanager
async def get_tenant_session(tenant_id: str) -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for tenant-specific sessions."""
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



# Dynamic Session Dependency for Global + Tenant

@asynccontextmanager
async def db_session_dependency(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield appropriate session based on X-Tenant-ID or subdomain."""
    tenant_id = request.headers.get("X-Tenant-ID") or request.url.hostname.split(".")[0]

    if tenant_id and tenant_id != "api":
        async with get_tenant_session(tenant_id) as session:
            yield session
    else:
        async with get_master_session() as session:
            yield session



# Utility: Clear Cached Engines

async def clear_engine_cache():
    """Dispose all cached tenant engines."""
    for engine in tenant_engines.values():
        await engine.dispose()
    tenant_engines.clear()
    logger.info("Cleared tenant engine cache.")
