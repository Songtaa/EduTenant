# app/core/tenant_bootstrapper.py

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text, MetaData
from app.utils.schema_utils import SchemaFactory
import logging

logger = logging.getLogger(__name__)

class TenantBootstrapper:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def schema_exists(self, schema_name: str) -> bool:
        async with self.engine.connect() as conn:
            result = await conn.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema")
                .bindparams(schema=schema_name)
            )
            return result.scalar() is not None

    async def bootstrap_if_needed(self, schema_name: str):
        if await self.schema_exists(schema_name):
            logger.info(f"Schema '{schema_name}' already exists. Skipping creation.")
            return

        await self.create_schema_and_tables(schema_name)

    async def create_schema_and_tables(self, schema_name: str):
        async with self.engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

        schema_factory = SchemaFactory(schema_name)
        metadata, _ = schema_factory.clone()

        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        logger.info(f"Initialized schema and tables for '{schema_name}'")
