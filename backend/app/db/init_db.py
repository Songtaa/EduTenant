from app.config.settings import settings
from app.domains.auth.models.users import User
from app.domains.auth.schemas.user_schema import UserCreate
from app.domains.auth.models.tenant_user import TenantUser
from app.domains.auth.services.tenant_user_service import TenantUserService
from app.domains.auth.schemas.tenant_user import TenantUserCreate
from sqlalchemy.orm import Session
from app.domains.auth.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.db.base_class import APIBase
from sqlalchemy.future import select
from app.db.session import get_tenant_engine, master_async_engine
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from app.db.session import get_master_session, get_tenant_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.domains.auth.apis.users_router import create_user_Account
from app.domains.school.services.tenant import TenantRepository
import logging
from app.domains.school.schemas.tenant import TenantCreate
from app.domains.school.services.tenant import TenantService
from app.utils.seeder import seed_tenant_admin_user, seed_global_admin_user
from app.utils.schema_utils import SchemaFactory
from sqlalchemy import pool, MetaData, text


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    try:
        await init_public_schema()
        await seed_global_admin()

        if settings.INIT_DEFAULT_TENANT:
            await init_default_tenant()

    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise


async def init_public_schema() -> None:
    logger.info(f"Initializing global DB with connection URL: {master_async_engine.url}")

    # Extract only tables that belong to the 'public' schema
    public_metadata = MetaData()
    for table in APIBase.metadata.tables.values():
        if getattr(table, "schema", None) == "public":
            table.tometadata(public_metadata)

    # Use engine.begin() to get an AsyncConnection, NOT a session
    async with master_async_engine.begin() as conn:
        logger.info("Creating public schema tables...")
        await conn.run_sync(public_metadata.create_all)
        logger.info("Public schema tables created.")



async def seed_global_admin() -> None:
    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        full_name=settings.FIRST_SUPERUSER_NAME,
        user_role=settings.FIRST_SUPERUSER_ROLE,
        is_superuser=True,
    )

    async with get_master_session() as session:
        await seed_global_admin_user(
            session=session,
            user_data=user_in,
            user_model=User
        )


async def init_default_tenant() -> None:
    tenant_schema = settings.DEFAULT_TENANT_SCHEMA
    logger.info(f"Initializing default tenant: {tenant_schema}")

    tenant_data = TenantCreate(
        schema_name=settings.DEFAULT_TENANT_NAME,
        subdomain=tenant_schema,
        is_active=settings.INIT_DEFAULT_TENANT,
        billing_tier=settings.DEFAULT_BILLING_TIER,
    )

    tenant_admin = TenantUserCreate(
        email=settings.DEFAULT_TENANT_ADMIN_EMAIL,
        password=settings.DEFAULT_TENANT_ADMIN_PASSWORD,
        full_name=settings.DEFAULT_TENANT_ADMIN_NAME,
        user_role=settings.DEFAULT_TENANT_ADMIN_ROLE,
        is_superuser=True,
    )

    # Use master session to check if tenant already exists
    async with get_master_session() as session:
        tenant_service = TenantService(session)
        existing_tenant = await tenant_service.repository.get_by_subdomain(tenant_data.subdomain)

        if existing_tenant:
            logger.info(f"Tenant '{tenant_data.subdomain}' already exists. Skipping creation.")
            return

   
    async with master_async_engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{tenant_data.schema_name}"'))

    # Clone schema metadata
    factory = SchemaFactory(tenant_data.schema_name)
    metadata, _ = factory.clone()

    # Use tenant engine to create tables
    tenant_engine = get_tenant_engine(tenant_data.schema_name)
    logger.info(f"Tables for tenant schema: {list(metadata.tables.keys())}")
    async with tenant_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    # Now insert tenant record and create tenant admin
    async with get_master_session() as session:
        tenant_service = TenantService(session)
        created_tenant = await tenant_service.create_tenant(tenant_data)

    async with get_tenant_session(created_tenant.schema_name) as tenant_session:
        await seed_tenant_admin_user(
            session=tenant_session,
            tenant_user_data=tenant_admin,
            user_model=TenantUser
        )

    logger.info(f"Default tenant '{tenant_data.subdomain}' initialized successfully.")
