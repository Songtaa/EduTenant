import asyncio
from logging.config import fileConfig
import os
from typing import Optional

from alembic import context
from sqlalchemy import pool, MetaData, text
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection

from app.config.settings import settings
from app.db.base_class import APIBase

# Import all models to ensure they're registered with SQLAlchemy
from app.domains.auth.models.users import User
from app.domains.auth.models.tenant_user import TenantUser
from app.domains.auth.models.role import Role
from app.domains.auth.models.permission import Permission
from app.domains.auth.models.user_role import UserRole
from app.domains.auth.models.user_permissions import UserPermission
from app.domains.auth.models.role_permission import RolePermission
from app.domains.auth.models.refresh_token import RefreshToken
from app.domains.auth.models.token_blocklist import TokenBlocklist
from app.domains.school.models.tenant_permission import TenantPermission

# Alembic configuration
config = context.config
database_url = str(settings.SQLALCHEMY_DATABASE_URI)
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Filter metadata to only public schema tables
public_metadata = MetaData(schema="public")
for table in APIBase.metadata.tables.values():
    # Check both table.schema and __table_args__['schema']
    table_schema = getattr(table, "schema", None)
    table_args = getattr(table, "kwargs", {}) or {}
    if table_schema == "public" or table_args.get("schema") == "public":
        table.tometadata(public_metadata)

target_metadata = public_metadata

def get_schema() -> Optional[str]:
    """Get schema from multiple possible sources, defaulting to public"""
    if context.get_x_argument(as_dictionary=True).get('schema'):
        return context.get_x_argument(as_dictionary=True).get('schema')
    if os.getenv('SCHEMA'):
        return os.getenv('SCHEMA')
    if hasattr(config, 'cmd_opts') and getattr(config.cmd_opts, 'x', None):
        return config.cmd_opts.x.split('=')[1] if '=' in config.cmd_opts.x else config.cmd_opts.x
    return "public"  

def include_object(object, name, type_, reflected, compare_to) -> bool:
    """Filter which tables/schemas get included in autogenerate"""
    if type_ == "table":
       
        return getattr(object, "schema", None) == "public"
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        version_table_schema="public",  
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    print("Engine created, attempting connection...")  # Add this line

    async with connectable.connect() as connection:
        # Ensure public schema exists and is set as search path
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        await connection.execute(text("SET search_path TO public"))

        def run_migrations(conn: Connection) -> None:
            context.configure(
                connection=conn,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                version_table_schema="public",  
                compare_type=True,
                compare_server_default=True
            )
            with context.begin_transaction():
                context.run_migrations()

        await connection.run_sync(run_migrations)
    
    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()