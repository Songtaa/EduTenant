import asyncio
from logging.config import fileConfig

from alembic import context
from app.config.settings import settings
from app.domains.auth.models.users import APIBase
from app.domains.auth.models.permission import APIBase
from app.domains.auth.models.role import APIBase
from app.domains.auth.models.role_permission import APIBase
from app.domains.auth.models.user_role import APIBase
from app.domains.auth.models.user_permissions import APIBase
from app.domains.school.models.tenant import APIBase
from app.domains.school.models.school import APIBase
from app.domains.school.models.student import APIBase
from app.domains.school.models.services import APIBase
from app.domains.auth.models.token_blocklist import APIBase
# from domains.kace.models.attendance import APIBase
# from domains.kace.models.classes import APIBase
# from domains.kace.models.class_students import APIBase
# from domains.kace.models.class_teachers import APIBase
# # from domains.kace.models.courseclass import APIBase
# from domains.kace.models.courses import APIBase
# from domains.kace.models.grades import APIBase
# from domains.kace.models.messages import APIBase
# from domains.kace.models.module_tutor import APIBase
# from domains.kace.models.modules import APIBase
# from domains.kace.models.notifications import APIBase
# from domains.kace.models.student import APIBase
# from domains.kace.models.parent import APIBase
# from domains.kace.models.permissions import APIBase
# from domains.kace.models.profiles import APIBase
# from domains.kace.models.role_permissions import APIBase
# from domains.kace.models.roles import APIBase
# from domains.kace.models.timetable import APIBase

from sqlmodel import SQLModel
import sqlmodel
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

database_url = str(settings.SQLALCHEMY_DATABASE_URI)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = APIBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
