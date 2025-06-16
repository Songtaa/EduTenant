from app.config.settings import settings
from app.domains.auth.models.users import User
from app.domains.auth.schemas.user_schema import UserCreate
from sqlalchemy.orm import Session
from app.domains.auth.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.db.base_class import APIBase
from sqlalchemy.future import select
from app.db.session import master_async_engine
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from app.db.session import get_master_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.domains.auth.apis.users_router import create_user_Account
from app.domains.school.services.tenant import TenantRepository
import logging
from app.domains.school.schemas.tenant import TenantCreate
from app.domains.school.services.tenant import TenantService
from app.utils.seeder import seed_admin_user


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    try:
        # --- GLOBAL DB SETUP (public schema) ---
        logger.info(f"Initializing global DB with connection URL: {master_async_engine.url}")

        async with master_async_engine.begin() as conn:
            logger.info("Creating public schema tables...")
            await conn.run_sync(APIBase.metadata.create_all)
            logger.info("Public schema tables created.")

        # --- GLOBAL ADMIN USER SETUP ---
        async with AsyncSession(master_async_engine) as session:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name=settings.FIRST_SUPERUSER_NAME,
                user_role=settings.FIRST_SUPERUSER_ROLE,
                is_superuser=True,
            )
            await seed_admin_user(session, user_in)

        # --- DEFAULT TENANT SETUP (Optional) ---
        if settings.INIT_DEFAULT_TENANT:
            logger.info(f"Initializing default tenant: {settings.DEFAULT_TENANT_SCHEMA}")

            tenant_data = TenantCreate(
                name=settings.DEFAULT_TENANT_NAME,
                subdomain=settings.DEFAULT_TENANT_SCHEMA,
                is_active=settings.INIT_DEFAULT_TENANT,
                billing_tier=settings.DEFAULT_BILLING_TIER
            )

            tenant_admin = UserCreate(
                email=settings.DEFAULT_TENANT_ADMIN_EMAIL,
                password=settings.DEFAULT_TENANT_ADMIN_PASSWORD,
                full_name=settings.DEFAULT_TENANT_ADMIN_NAME,
                user_role=settings.DEFAULT_TENANT_ADMIN_ROLE,
                is_superuser=True,
            )

            async with AsyncSession(master_async_engine) as session:
                tenant_service = TenantService(session)


                existing_tenant = await tenant_service.repository.get_by_subdomain(tenant_data.subdomain)
                if existing_tenant:
                    logger.info(f"Tenant '{tenant_data.domain}' already exists. Skipping creation.")
                else:
                    await tenant_service.create_tenant_with_admin(tenant_data, tenant_admin)
                    logger.info(f"Default tenant '{settings.DEFAULT_TENANT_SCHEMA}' initialized.")

    except Exception as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise



# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28

