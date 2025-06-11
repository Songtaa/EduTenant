from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from app.db.session import master_async_engine, get_tenant_engine
from app.domains.auth.models.users import User  # Import any models to trigger SQLModel metadata registration
from app.db.base_class import APIBase
from sqlalchemy.ext.asyncio import AsyncSession


async def create_schema(schema_name: str):
    """Create a new schema in the shared database (if not exists)."""
    async with master_async_engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        await conn.commit()

async def create_schema_tables(schema_name: str, session: AsyncSession):
    """Create all tenant-specific tables in the given schema."""
    engine: AsyncEngine = get_tenant_engine(schema_name)

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: APIBase.metadata.create_all(
                bind=sync_conn,
                checkfirst=True,
            ),
            # execution_options={"schema_translate_map": {"schema": schema_name}},
        )

async def drop_schema(schema_name: str, cascade: bool = True):
    """Drop a tenant schema from the shared database."""
    async with master_async_engine.begin() as conn:
        cascade_opt = "CASCADE" if cascade else ""
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" {cascade_opt}'))
        await conn.commit()
