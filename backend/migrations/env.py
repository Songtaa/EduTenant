import asyncio
from logging.config import fileConfig
import os

from alembic import context
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool, MetaData


from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from app.config.settings import settings
from app.db.base_class import APIBase

from app.domains.auth.models import (
    permission,
    user_permissions,
    user_role,
    users,
    refresh_token,
    role,
    role_permission,
    token_blocklist,
)

from app.domains.school.models import tenant_permission



database_url = str(settings.SQLALCHEMY_DATABASE_URI)
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


#Filter metadata to only public schema tables
public_metadata = MetaData()
for table in APIBase.metadata.tables.values():
    if getattr(table, "schema", None) == "public":
        table.tometadata(public_metadata)

target_metadata = public_metadata

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
# target_metadata = APIBase.metadata

def get_schema():
    """Get schema from multiple possible sources"""
    if context.get_x_argument(as_dictionary=True).get('schema'):
        return context.get_x_argument(as_dictionary=True).get('schema')
    if os.getenv('SCHEMA'):
        return os.getenv('SCHEMA')
    if hasattr(config, 'cmd_opts') and getattr(config.cmd_opts, 'x', None):
        return config.cmd_opts.x.split('=')[1] if '=' in config.cmd_opts.x else config.cmd_opts.x
    return None

def include_object(object, name, type_, reflected, compare_to):
    """Filter which tables/schemas get included in autogenerate"""
    if type_ == "table":
        schema = get_schema()
        model_schema = getattr(object, 'schema', None)
        return (schema == model_schema) or (model_schema is None and schema is None)
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    schema = get_schema()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        version_table_schema=schema
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

    schema = get_schema()
    
    async with connectable.connect() as connection:
        if schema:
            await connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            await connection.execute(text(f"SET search_path TO {schema}"))

        def run_migrations(conn):
            context.configure(
                connection=conn,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                version_table_schema=schema,
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